#!/usr/bin/env python3
"""PR-structure soft nudge.

Companion to the PR-body skeleton in skills/git/references/pull-requests.md: each
structure block there carries a required hidden `<!-- pr:x -->` marker. Wired to
the post-shell hook (PostToolUse:Bash / postToolUse:Shell); after a
`gh pr create` or `gh pr edit` that carried a body, it lists missing markers and
points the agent back to the skill guide. A marker stays when its block does not
apply; the block instead says why it is not applicable. Informational only, this
hook never blocks or rewrites.

Escape hatch: a body carrying a `<!-- pr:skeleton-off: <reason> -->` marker
silences the nudge entirely. Use it when the body deliberately follows a
different shape, a repo PULL_REQUEST_TEMPLATE or any imposed template, so the
skeleton doesn't apply. The reason keeps it a conscious choice, not a reflex.

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
    "pr:changes": "changelog-style bullets or why they do not apply",
    "pr:review-guide": "where the reviewer should start or why no guide is needed",
    "pr:links": "relevant links or why there are none",
}

# Only bodies of the PR itself carry the skeleton; comments and reviews don't.
BODY_ACTIONS = {("pr", "create"), ("pr", "edit")}

# Deliberate escape hatch. A body carrying this marker opted out of the skeleton
# (repo PR template, or any imposed shape); the nudge stays silent. Matches with
# or without a trailing reason so a bare marker still bypasses; the skill asks
# for a reason to keep the opt-out conscious.
BYPASS_RE = re.compile(r"<!--\s*pr:skeleton-off\b.*?-->", re.DOTALL)


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
        if BYPASS_RE.search(body):
            return []
        return [name for name in MARKERS if not marker_re(name).search(body)]
    return []


def format_nudge(missing):
    bullets = "\n".join(f"- `<!-- {name} -->`: {MARKERS[name]}" for name in missing)
    return (
        "PR-structure nudge (informational, nothing was blocked): the PR body just "
        "posted is missing these required structure markers:\n"
        f"{bullets}\n\n"
        "The body guide and skeleton live in the git skill, "
        "skills/git/references/pull-requests.md -> 'Body and Description'. Every "
        "marker stays in every PR body. If a block does not apply, keep its marker "
        "and add a short `Not applicable: ...` sentence explaining why. Fix with "
        "`gh pr edit --body` (read the current body first, the flag replaces it whole)."
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
