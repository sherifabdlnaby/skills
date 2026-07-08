#!/usr/bin/env python3
"""Rebase backup guard.

Enforces the git skill's one unrecoverable-failure rule (references/rebase.md):
create a local `<branch>-bk` backup branch before any rebase. Wired to the
pre-shell hook (PreToolUse:Bash / beforeShellExecution); denies a command that
*starts* a rebase while no backup ref exists, telling the agent the exact command
to run instead. Compliance is the override: create the backup (even inline,
`git branch x-bk && git rebase ...`) and the same rebase sails through.

Never blocks mid-rebase plumbing (--continue/--abort/--skip), and fails open on
anything it can't determine (no cwd, detached HEAD, git errors): a guard that
can't see clearly must not get in the way. stdlib only. Exit 0 always.
"""

import shlex
import subprocess
import sys

import hooklib

# Mid-rebase / no-op flags: the rebase already started (backup ship has sailed)
# or nothing is being rewritten.
RESUME_FLAGS = {
    "--continue",
    "--abort",
    "--skip",
    "--quit",
    "--edit-todo",
    "--show-current-patch",
}

GIT_TIMEOUT = 3  # seconds; a hung git must not hang the hook


def starts_rebase(tokens):
    """True when the command line starts a new rebase."""
    for i, token in enumerate(tokens[:-1]):
        if token == "git" and "rebase" in tokens[i + 1 :]:
            return not RESUME_FLAGS.intersection(tokens)
    return False


def git(cwd, *args):
    """Run git in cwd; return stdout or None on any failure (-> fail open)."""
    try:
        proc = subprocess.run(
            ["git", "-C", cwd, *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def backup_missing(command, cwd):
    """True iff `command` starts a rebase and no backup branch exists.

    Returns (missing, branch); branch is None whenever missing is False.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False, None

    if not starts_rebase(tokens):
        return False, None
    if any(token.endswith("-bk") for token in tokens):
        return False, None  # backup created or referenced in the same line

    if not cwd:
        return False, None
    branch = git(cwd, "branch", "--show-current")
    if not branch:
        return False, None  # detached HEAD or git error: fail open

    ref = git(cwd, "show-ref", "--verify", f"refs/heads/{branch}-bk")
    if ref is not None:
        return False, None
    return True, branch


def main():
    data = hooklib.load()
    if data is None:
        return 0

    command = hooklib.command(data)
    if not command:
        return 0

    cwd = data.get("cwd") if isinstance(data.get("cwd"), str) else None
    missing, branch = backup_missing(command, cwd)
    if not missing:
        return 0

    hooklib.deny(
        data,
        (
            "Rebase backup guard: no backup branch exists for the branch you are "
            f"about to rewrite. Per the git skill (references/rebase.md), create it "
            f"first, then rerun:\n\n"
            f"  git branch {branch}-bk && {command}\n\n"
            "The backup is the only recovery path if the rebase goes wrong."
        ),
        "Blocked a rebase with no backup branch.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
