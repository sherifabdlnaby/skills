#!/usr/bin/env python3
"""Rebase snapshot guard.

Enforces the git skill's conflict rule (references/rebase.md): once a rebase has
stopped on a conflict, snapshot the pre-rebase tip (`git branch <branch>-bk
ORIG_HEAD`) before the first move of the resolution. Wired to the pre-shell hook
(PreToolUse:Bash / beforeShellExecution). While a rebase is in progress and no
snapshot exists, it denies the commands that begin a resolution or overwrite
ORIG_HEAD, naming the exact command to run first. A snapshot created on the same
line (`git branch x-bk ORIG_HEAD && git add ...`) sails through.

Starting a rebase, or one that replays clean, is never touched: the snapshot is
lazy by design, and `git rebase --abort` is always allowed. Fails open on anything
it cannot determine (no cwd, git errors): a guard that cannot see clearly must not
get in the way. stdlib only. Exit 0 always.
"""

import os
import shlex
import subprocess
import sys

import hooklib

# git subcommands that begin a resolution or overwrite ORIG_HEAD.
RESOLVING = {
    "add",
    "rm",
    "mv",
    "reset",
    "restore",
    "checkout",
    "stash",
    "merge",
    "pull",
    "cherry-pick",
}
RESUMING = {"--continue", "--skip"}

# Global git options that take a value, so the subcommand is the token after it.
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}

GIT_TIMEOUT = 3  # seconds; a hung git must not hang the hook


def subcommands(tokens):
    """Yield (subcommand, rest) for every `git ...` invocation on the line."""
    for i, token in enumerate(tokens):
        if token != "git":
            continue
        j = i + 1
        while j < len(tokens) and tokens[j].startswith("-"):
            j += 2 if tokens[j] in GIT_OPTS_WITH_VALUE else 1
        if j < len(tokens):
            yield tokens[j], tokens[j + 1 :]


def resolves(tokens):
    """True when the command line makes a move a stopped rebase must be snapshotted before."""
    for sub, rest in subcommands(tokens):
        if sub in RESOLVING:
            return True
        if sub == "rebase" and RESUMING.intersection(rest):
            return True
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


def rebasing_branch(cwd):
    """Name of the branch a stopped rebase is rewriting, or None when no rebase is in progress."""
    for state_dir in ("rebase-merge", "rebase-apply"):
        path = git(cwd, "rev-parse", "--git-path", state_dir)
        if not path:
            continue
        path = os.path.join(cwd, path) if not os.path.isabs(path) else path
        try:
            with open(os.path.join(path, "head-name"), encoding="utf-8") as fh:
                head = fh.read().strip()
        except OSError:
            continue
        if head.startswith("refs/heads/"):
            return head[len("refs/heads/") :]
    return None


def snapshot_missing(command, cwd):
    """Returns (missing, branch); branch is None whenever missing is False."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False, None

    if not resolves(tokens):
        return False, None
    if any(token.endswith("-bk") for token in tokens):
        return False, None  # snapshot created or referenced on the same line
    if not cwd:
        return False, None

    branch = rebasing_branch(cwd)
    if not branch:
        return False, None
    if (
        git(cwd, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}-bk")
        is not None
    ):
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
    missing, branch = snapshot_missing(command, cwd)
    if not missing:
        return 0

    hooklib.deny(
        data,
        (
            f"Rebase snapshot guard: a rebase is stopped on `{branch}` and no snapshot "
            "exists. Per the git skill (references/rebase.md), snapshot the pre-rebase "
            "tip first, then rerun:\n\n"
            f"  git branch {branch}-bk ORIG_HEAD && {command}\n\n"
            "ORIG_HEAD is overwritten by the next reset, merge or pull; the snapshot "
            "is the recovery path."
        ),
        "Blocked a conflict resolution with no rebase snapshot.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
