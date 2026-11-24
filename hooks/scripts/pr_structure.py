#!/usr/bin/env python3
"""PR-structure guard.

Companion to the PR-body skeleton in skills/git/references/pr-body.md: every block
there leaves a receipt. A written block keeps its hidden `<!-- pr:x -->` marker; a
dropped one is named, with a reason, in a single `<!-- pr:dropped x: why | y: why -->`
line. Wired to the pre-shell hook (PreToolUse:Bash / beforeShellExecution): a
`gh pr create` or `gh pr edit` whose body lacks a receipt for any block is denied,
and the denial names the blocks.

Escape hatch: a body carrying a `<!-- pr:skeleton-off: <reason> -->` marker passes
untouched. For a body merged into a repo PULL_REQUEST_TEMPLATE or any imposed
shape, where the receipts may not survive. The reason keeps it a conscious choice.

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

# The skeleton's blocks, in body order. Human Note is absent on purpose: it is the
# user's to open, so its absence is never the agent's call.
BLOCKS = (
    "summary",
    "proof",
    "changes",
    "breaking",
    "review-guide",
    "not-checked",
    "your-call",
    "why-it-works",
    "decisions",
    "how-to-test",
    "examples",
    "follow-ups",
    "links",
)

# Only bodies of the PR itself carry the skeleton; comments and reviews don't.
BODY_POSTS = {"gh pr create", "gh pr edit"}

# Sentinel from missing_receipts: a PR body was posted, but its text never reached us.
UNREADABLE = object()

# Whitespace-tolerant so a reformatted marker still counts.
MARKER_RE = re.compile(r"<!--\s*pr:([a-z-]+)\s*-->")
DROPPED_RE = re.compile(r"<!--\s*pr:dropped\b(.*?)-->", re.DOTALL)
BYPASS_RE = re.compile(r"<!--\s*pr:skeleton-off\b.*?-->", re.DOTALL)


def receipts(body):
    """Return `(written, dropped)`: block names by receipt kind.

    A dropped entry with no reason is left out of `dropped`, so it counts as
    missing: the reason is what makes the drop a decision.
    """
    written = set(MARKER_RE.findall(body))
    dropped = set()
    for match in DROPPED_RE.finditer(body):
        for entry in match.group(1).split("|"):
            name, _, reason = entry.partition(":")
            if name.strip() and reason.strip():
                dropped.add(name.strip())
    return written, dropped


def missing_receipts(command, cwd):
    """Blocks with no receipt in the PR body posted by `command`, in body order.

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
        written, dropped = receipts(body.text)
        missing = [name for name in BLOCKS if name not in written | dropped]
        return UNREADABLE if missing and not body.complete else missing
    return []


UNREADABLE_REASON = (
    "PR-structure guard: this command posts a PR body the guard cannot read, so it "
    "cannot check the body for its receipts. Pass the body as a file "
    "(`--body-file <path>`), inline (`--body '<text>'`), or as an inline heredoc into "
    "`--body-file -`, then retry."
)


def format_reason(missing):
    return (
        "PR-structure guard: the PR body has no receipt for these blocks: "
        f"{', '.join(missing)}. Every block of the skeleton is either written, "
        "keeping its `<!-- pr:<block> -->` marker, or dropped with a reason in one "
        "hidden line, `<!-- pr:dropped <block>: <reason> | <block>: <reason> -->`. A "
        "dropped entry without a reason does not count. Rules and skeleton: the git "
        "skill, skills/git/references/pr-body.md. A body shaped by a repo PR template, "
        "or one you did not write, carries `<!-- pr:skeleton-off: <reason> -->` "
        "instead. Fix the body, then retry."
    )


def main():
    data = hooklib.load()
    if data is None:
        return 0

    command = hooklib.command(data)
    if "gh" not in command:  # runs on every shell command; skip the parse for most
        return 0

    missing = missing_receipts(command, hooklib.cwd(data))
    if missing is UNREADABLE:
        hooklib.deny(
            data, UNREADABLE_REASON, "Blocked a PR body this hook could not read."
        )
    elif missing:
        hooklib.deny(
            data,
            format_reason(missing),
            "Blocked a PR body missing structure receipts.",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
