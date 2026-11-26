#!/usr/bin/env python3
"""PR-structure guard.

Companion to the PR-body skeleton in skills/git/references/pr-body.md: every body
carries the same required parts, and each one keeps its hidden `<!-- pr:x -->`
marker. A body with no visual says so, with a reason, in
`<!-- pr:no-visuals: <reason> -->`. Wired to the pre-shell hook (PreToolUse:Bash /
beforeShellExecution): a `gh pr create` or `gh pr edit` whose body misses a marker
is denied, and the denial names the parts.

Escape hatch: a body carrying a `<!-- pr:skeleton-off: <reason> -->` marker passes
untouched. For a body merged into a repo PULL_REQUEST_TEMPLATE or any imposed
shape, where the markers may not survive. The reason keeps it a conscious choice.

Command parsing and body extraction come from the ai-disclosure guard
(skills/ai-disclosure/hooks/guard), so both read the same body out of
the same command, heredocs and `gh api` included. A PR body this guard cannot read
is denied with its own reason. stdlib only. Exit 0 always; "allow" is emitting
nothing, "deny" is hooklib.deny().
"""

import os
import re
import sys

import hooklib

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        *("..", "..", "skills", "ai-disclosure", "hooks", "guard"),
    ),
)
import github  # noqa: E402

# The parts every body carries, in body order.
REQUIRED = ("summary", "visuals", "changes", "decisions")

# Only bodies of the PR itself carry the skeleton; comments and reviews don't.
BODY_POSTS = {"gh pr create", "gh pr edit"}

# Sentinel from missing_parts: a PR body was posted, but its text never reached us.
UNREADABLE = object()

# Whitespace-tolerant so a reformatted marker still counts.
MARKER_RE = re.compile(r"<!--\s*pr:([a-z-]+)\s*-->")
NO_VISUALS_RE = re.compile(r"<!--\s*pr:no-visuals\s*:(.*?)-->", re.DOTALL)
BYPASS_RE = re.compile(r"<!--\s*pr:skeleton-off\b.*?-->", re.DOTALL)


def marked(body):
    """Return the names of the parts `body` carries a marker for.

    The visuals opt-out counts as `visuals` only with a reason: the reason is what
    makes a body without a visual a decision.
    """
    found = set(MARKER_RE.findall(body))
    if any(match.group(1).strip() for match in NO_VISUALS_RE.finditer(body)):
        found.add("visuals")
    return found


def missing_parts(command, cwd):
    """Required parts with no marker in the PR body posted by `command`, in body order.

    Returns [] when the command isn't a PR-body post or the body opted out, and
    UNREADABLE when gh would post a body we never see (editor mode, an unreadable
    --body-file, an opaque shell expansion).
    """
    for _, post in github.posts(command, cwd):
        if post.what not in BODY_POSTS:
            continue
        (body,) = post.bodies  # gh posts one PR body
        if BYPASS_RE.search(body.text):
            return []
        found = marked(body.text)
        missing = [name for name in REQUIRED if name not in found]
        return UNREADABLE if missing and not body.complete else missing
    return []


UNREADABLE_REASON = (
    "PR-structure guard: this command posts a PR body the guard cannot read, so it "
    "cannot check the body for its markers. Pass the body as a file "
    "(`--body-file <path>`), inline (`--body '<text>'`), or as an inline heredoc into "
    "`--body-file -`, then retry."
)


def format_reason(missing):
    return (
        "PR-structure guard: the PR body misses these required parts: "
        f"{', '.join(missing)}. Each one keeps its hidden `<!-- pr:<part> -->` marker "
        "from the skeleton. A body with no visual carries "
        "`<!-- pr:no-visuals: <reason> -->` in place of the visuals marker. Rules and "
        "skeleton: the git skill, skills/git/references/pr-body.md. A body shaped by a "
        "repo PR template, or one you did not write, carries "
        "`<!-- pr:skeleton-off: <reason> -->` instead. Write the part, then retry."
    )


def main():
    data = hooklib.load()
    if data is None:
        return 0

    command = hooklib.command(data)
    if "gh" not in command:  # runs on every shell command; skip the parse for most
        return 0

    missing = missing_parts(command, hooklib.cwd(data))
    if missing is UNREADABLE:
        hooklib.deny(
            data, UNREADABLE_REASON, "Blocked a PR body this hook could not read."
        )
    elif missing:
        hooklib.deny(
            data,
            format_reason(missing),
            "Blocked a PR body missing required parts.",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
