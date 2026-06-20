"""Shared plumbing for Claude Code / Cursor hook workers.

Both tools hand a hook a JSON payload on stdin and read a JSON verdict on stdout;
only the *shapes* of those two payloads differ. This module owns those shapes so
each worker implements only its decision, not the cross-tool glue. Workers live
next to this file and `import hooklib` (the launcher runs them from this dir, so
it is on sys.path). stdlib only.

  Claude PreToolUse:   {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                        "tool_input": {"command": "..."}, ...}
  Cursor beforeShell:  {"command": "...", "cwd": "...", ...}

Verdict convention: emit nothing to ALLOW (both tools fall through to their normal
permission flow); emit the tool-specific JSON to DENY.
"""

from __future__ import annotations

import json
import sys


def load():
    """Parse the stdin payload. Returns the dict, or None if unparsable (-> allow)."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None


def is_claude(data):
    """True for a Claude Code payload, False for a Cursor one."""
    return "tool_input" in data or "hook_event_name" in data


def command(data):
    """Shell command string for a Bash/shell hook, or None.

    Claude: tool_input.command   Cursor: command
    """
    ti = data.get("tool_input")
    if isinstance(ti, dict) and isinstance(ti.get("command"), str):
        return ti["command"]
    if isinstance(data.get("command"), str):
        return data["command"]
    return None


def file_path(data):
    """Edited file path for a Write/Edit hook, or None.

    Claude: tool_input.file_path   Cursor: file_path
    """
    ti = data.get("tool_input")
    if isinstance(ti, dict) and isinstance(ti.get("file_path"), str):
        return ti["file_path"]
    if isinstance(data.get("file_path"), str):
        return data["file_path"]
    return None


def allow():
    """Allow the action: emit nothing; both tools fall through to normal flow."""
    return


def deny(data, reason, user_message=None):
    """Block the action, emitting the verdict shape the sending tool expects.

    `reason` is shown to the agent (both tools); `user_message` is the human-facing
    line on Cursor only (Claude surfaces `reason` to both).
    """
    if is_claude(data):
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": data.get("hook_event_name", "PreToolUse"),
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
    else:  # Cursor
        print(
            json.dumps(
                {
                    "permission": "deny",
                    "agent_message": reason,
                    "user_message": user_message or "Blocked by a hook.",
                }
            )
        )
