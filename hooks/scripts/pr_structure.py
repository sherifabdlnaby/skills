#!/usr/bin/env python3
"""PR-structure soft nudge.

Companion to the PR-body skeleton in skills/git/references/pull-requests.md: each
structure block there carries a hidden `<!-- pr:x -->` marker. Wired to the
post-shell hook (PostToolUse:Bash / postToolUse:Shell); after a `gh pr create` or
`gh pr edit` that carried a body, it lists the markers the body is missing and
points the agent back to the skill guide. Informational only, it never blocks and
never rewrites: a PR may deviate from the skeleton on purpose, this just makes the
deviation a decision instead of an accident.

Body extraction is shared with gh_disclosure (same dir, launcher puts it on
sys.path). stdlib only. Exit 0 always; "no nudge" is emitting nothing.
"""

import re
import shlex
import sys

import hooklib
from gh_disclosure import extract_body

# The skeleton's structure receipts, in skeleton order. Whitespace-tolerant so a
# reformatted marker still counts.
MARKERS = {
    "pr:summary": "the one-line summary",
    "pr:changes": "changelog-style bullets (multi-change PRs)",
    "pr:review-guide": "where the reviewer should start",
    "pr:links": "ticket / docs / related-PR links",
}

# Only bodies of the PR itself carry the skeleton; comments and reviews don't.
BODY_ACTIONS = {("pr", "create"), ("pr", "edit")}


def marker_re(name):
    return re.compile(r"<!--\s*" + re.escape(name) + r"\s*-->")


def missing_markers(command):
    """Names of skeleton markers absent from a PR body posted by `command`.

    Returns [] when the command isn't a PR-body post or the body is uninspectable
    (editor mode, unreadable --body-file): no body seen, no nudge.
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return []

    for i in range(len(tokens) - 2):
        if tokens[i] != "gh":
            continue
        if (tokens[i + 1], tokens[i + 2]) not in BODY_ACTIONS:
            continue
        body = extract_body(tokens[i + 3 :])
        if body is None:
            return []
        return [name for name in MARKERS if not marker_re(name).search(body)]
    return []


def format_nudge(missing):
    bullets = "\n".join(f"- `<!-- {name} -->`: {MARKERS[name]}" for name in missing)
    return (
        "PR-structure nudge (informational, nothing was blocked): the PR body just "
        "posted is missing these skeleton blocks/markers:\n"
        f"{bullets}\n\n"
        "The body guide and skeleton live in the git skill, "
        "skills/git/references/pull-requests.md -> 'Body and Description'; follow it "
        "unless this PR deliberately deviates. If blocks are missing by accident, fix "
        "with `gh pr edit --body` (read the current body first, the flag replaces it "
        "whole)."
    )


def main():
    data = hooklib.load()
    if data is None:
        return 0

    command = hooklib.command(data)
    if not command:
        return 0

    missing = missing_markers(command)
    if not missing:
        return 0

    hooklib.post_context(data, format_nudge(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
