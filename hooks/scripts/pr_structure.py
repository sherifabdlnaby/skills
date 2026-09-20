#!/usr/bin/env python3
"""PR-structure guard.

Companion to the PR-body skeleton in skills/git/references/pr-body.md: every block
there leaves a receipt. A written block keeps its hidden `<!-- pr:x -->` marker; a
dropped one is named, with a reason, in a single `<!-- pr:dropped x: why | y: why -->`
line. Wired to the pre-shell hook (PreToolUse:Bash / beforeShellExecution): a
`gh pr create` or `gh pr edit` whose body lacks a receipt for any block is denied,
and the denial names the blocks. A skip is then a decision with a reason, never an
oversight.

Escape hatch: a body carrying a `<!-- pr:skeleton-off: <reason> -->` marker passes
untouched. For a body merged into a repo PULL_REQUEST_TEMPLATE or any imposed
shape, where the receipts may not survive. The reason keeps it a conscious choice.

Command parsing and body extraction are shared with gh_disclosure (same dir,
launcher puts it on sys.path), so both hooks read the same body out of the same
command, heredocs included. A body this guard cannot read stays quiet here:
gh_disclosure already denies it with the right reason. stdlib only. Exit 0 always;
"allow" is emitting nothing, "deny" is hooklib.deny().
"""

import re
import sys

import hooklib
from gh_disclosure import UNREADABLE, extract_body, tokenize

# The skeleton's blocks, in body order. Human Note is absent on purpose: it is the
# user's to open, so its absence is never the agent's call.
BLOCKS = (
    "summary",
    "visuals",
    "changes",
    "breaking",
    "review-guide",
    "decisions",
    "how-to-test",
    "verification",
    "examples",
    "follow-ups",
    "links",
)

# Only bodies of the PR itself carry the skeleton; comments and reviews don't.
BODY_ACTIONS = {("pr", "create"), ("pr", "edit")}

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


def missing_receipts(command):
    """Blocks with no receipt in the PR body posted by `command`, in body order.

    Returns [] when the command isn't a PR-body post, the body opted out, or the
    body is uninspectable (editor mode, unreadable --body-file, opaque shell
    expansion): gh_disclosure denies those with a reason of its own.
    """
    parsed = tokenize(command)
    if parsed is None:
        return []
    tokens, bodies = parsed

    for i in range(len(tokens) - 2):
        if tokens[i] != "gh":
            continue
        if (tokens[i + 1], tokens[i + 2]) not in BODY_ACTIONS:
            continue
        body = extract_body(tokens[i + 3 :], bodies)
        if body is None or body is UNREADABLE:
            return []
        if BYPASS_RE.search(body):
            return []
        written, dropped = receipts(body)
        return [name for name in BLOCKS if name not in written | dropped]
    return []


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
    if not command:
        return 0

    missing = missing_receipts(command)
    if not missing:
        return 0

    hooklib.deny(
        data, format_reason(missing), "Blocked a PR body missing structure receipts."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
