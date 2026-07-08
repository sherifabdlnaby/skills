#!/usr/bin/env python3
"""Apply git skill shell defaults before execution.

Rewrites shell commands that omit conventions from skills/git:
- git push --force / -f  ->  --force-with-lease

Wired to PreToolUse:Shell / PreToolUse:Bash for rewrites. Cursor also uses
postToolUse:Shell to inject additional_context (Claude gets additionalContext
on the same PreToolUse response). stdlib only.
"""

from __future__ import annotations

import shlex
import sys

import hooklib


def _has_draft(tokens):
    return "--draft" in tokens or "--no-draft" in tokens


def _has_assignee(tokens):
    for token in tokens:
        if token == "--assignee" or token.startswith("--assignee="):
            return True
    return False


def rewrite_force_push(command):
    """Replace bare --force / -f on git push with --force-with-lease."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return command, []

    if "git" not in tokens or "push" not in tokens:
        return command, []
    if "--force-with-lease" in tokens:
        return command, []

    changes = []
    new_tokens = []
    replaced = False
    for token in tokens:
        if not replaced and token == "--force":
            new_tokens.append("--force-with-lease")
            changes.append("replaced --force with --force-with-lease")
            replaced = True
        elif not replaced and token == "-f":
            new_tokens.append("--force-with-lease")
            changes.append("replaced -f with --force-with-lease")
            replaced = True
        else:
            new_tokens.append(token)

    if not changes:
        return command, []
    return shlex.join(new_tokens), changes


def rewrite(command):
    """Apply all shell default rewrites; return (new_command, change_descriptions)."""
    changes = []
    updated = command

    updated, part = rewrite_force_push(updated)
    changes.extend(part)

    return updated, changes


def format_additional_context(original, updated, changes):
    """Build agent-facing context describing what the hook changed."""
    bullets = "\n".join(f"- {change}" for change in changes)
    return (
        "Git shell-defaults hook rewrote this command before execution "
        "(skills/git conventions):\n"
        f"{bullets}\n\n"
        f"Original: `{original}`\n"
        f"Executed: `{updated}`"
    )


def pre_main(data):
    original = hooklib.command(data)
    if not original:
        return 0

    updated, changes = rewrite(original)
    if not changes or updated == original:
        return 0

    tool_input = hooklib.tool_input(data)
    if not tool_input or "command" not in tool_input:
        return 0

    tool_input["command"] = updated
    context = format_additional_context(original, updated, changes)
    hooklib.allow_rewrite(data, tool_input, context)
    return 0


def post_main(data):
    if hooklib.is_claude(data):
        return 0

    use_id = hooklib.tool_use_id(data)
    if not use_id:
        return 0

    context = hooklib.pop_pending_context(use_id)
    if context:
        hooklib.emit_additional_context(context)
    return 0


def main():
    data = hooklib.load()
    if data is None:
        return 0

    if hooklib.is_post_tool_use(data):
        return post_main(data)
    return pre_main(data)


if __name__ == "__main__":
    sys.exit(main())
