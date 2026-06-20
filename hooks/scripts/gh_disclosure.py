#!/usr/bin/env python3
"""AI-disclosure guard for GitHub posts.

Single source of truth for the rule "anything posted to GitHub on the user's
behalf carries an AI footer" (see skills/git/SKILL.md -> AI Disclosure). Wired to
the pre-shell hook (PreToolUse:Bash / beforeShellExecution) so it catches the case
where the agent forgets the footer; it does NOT pick the footer variant (provenance
is the agent's call) and never rewrites the command, it only blocks when a posted
body is missing disclosure.

Cross-tool stdin/stdout plumbing (Claude vs Cursor payload shapes, the deny
verdicts) lives in hooklib; this file owns only the disclosure decision. stdlib
only. Exit 0 always; "allow" is emitting nothing, "deny" is hooklib.deny().
"""

import shlex
import sys

import hooklib

# Marker shared by every disclosure footer in SKILL.md: each one begins with a
# robot emoji. We check for the marker, not the full template, so the templates
# stay owned by SKILL.md and the agent keeps the provenance choice.
MARKER = "\U0001f916"  # 🤖

# gh subcommands that post human-readable content to GitHub. (action verbs only;
# `gh pr edit` is gated only when it carries a body, handled via body extraction.)
POSTING = {
    ("pr", "create"),
    ("pr", "comment"),
    ("pr", "edit"),
    ("pr", "review"),
    ("issue", "create"),
    ("issue", "comment"),
}

REASON = (
    "AI-disclosure guard: this command posts a body to GitHub but the body has no "
    "disclosure footer (no \U0001f916 robot-emoji marker). Per the git skill "
    "(SKILL.md -> AI Disclosure), append the footer after a `---`, picking the "
    "variant by provenance: the autonomous form when you acted without the user's "
    "input, the user-directed form when they gave input or approved. For a PR body "
    "use the `created with assistance from ...` footer in references/pull-requests.md. "
    "Add it, then retry."
)


def extract_body(tokens):
    """Return posted body text from a gh posting command, or None if none/uninspectable.

    Handles `--body`/`-b`/`--body=...` inline and `--body-file`/`-F <path>` (read the
    file). Returns None for editor mode (no body flag) or an unreadable body file, so
    we never false-block something we can't see.
    """
    body_parts = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("--body", "-b") and i + 1 < len(tokens):
            body_parts.append(tokens[i + 1])
            i += 2
            continue
        if t.startswith("--body="):
            body_parts.append(t[len("--body=") :])
            i += 1
            continue
        if t in ("--body-file", "-F") and i + 1 < len(tokens):
            path = tokens[i + 1]
            if path == "-":  # body piped on stdin, can't inspect
                return None
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    body_parts.append(fh.read())
            except OSError:
                return None  # unreadable -> don't false-block
            i += 2
            continue
        if t.startswith("--body-file="):
            path = t[len("--body-file=") :]
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as fh:
                    body_parts.append(fh.read())
            except OSError:
                return None
            i += 1
            continue
        i += 1
    return "\n".join(body_parts) if body_parts else None


def needs_disclosure(command):
    """True iff `command` posts a GitHub body that lacks the disclosure marker."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False  # malformed quoting; let the tool's own handling deal with it

    # Find a `gh <noun> <verb>` posting action anywhere in the (possibly compound) line.
    for i in range(len(tokens) - 2):
        if tokens[i] != "gh":
            continue
        action = (tokens[i + 1], tokens[i + 2])
        if action in POSTING:
            body = extract_body(tokens[i + 3 :])
            if body is not None and MARKER not in body:
                return True
            # body present+marked, or editor/unreadable -> this action is fine
            return False
    return False


def main():
    data = hooklib.load()
    if data is None:
        return 0  # no parseable payload -> allow

    command = hooklib.command(data)
    if not command or not needs_disclosure(command):
        return 0

    hooklib.deny(
        data, REASON, "Blocked a GitHub post missing its AI-disclosure footer."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
