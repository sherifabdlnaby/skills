"""Shared plumbing for Claude Code / Cursor hook workers.

Both tools hand a hook a JSON payload on stdin and read a JSON verdict on stdout;
only the *shapes* of those two payloads differ. This module owns those shapes so
each worker implements only its decision, not the cross-tool glue. Workers live
next to this file and `import hooklib` (the launcher runs them from this dir, so
it is on sys.path). stdlib only.

  Claude PreToolUse:   {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                        "tool_input": {"command": "..."}, ...}
  Cursor preToolUse:   {"tool_name": "Shell", "tool_input": {"command": "..."},
                        "tool_use_id": "...", ...}
  Cursor postToolUse:  {..., "tool_output": "...", "tool_use_id": "..."}
  Cursor beforeShell:  {"command": "...", "cwd": "...", ...}

Verdict convention: emit nothing to ALLOW (both tools fall through to their normal
permission flow); emit the tool-specific JSON to DENY or REWRITE.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent / ".state"
PENDING_FILE = STATE_DIR / "pending_rewrites.json"


def load():
    """Parse the stdin payload. Returns the dict, or None if unparsable (-> allow)."""
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None


def is_claude(data):
    """True for Claude Code payloads, False for Cursor.

    Do not key off tool_input alone; Cursor preToolUse/postToolUse also carry it.
    """
    tool = data.get("tool_name")
    if tool == "Bash":
        return True
    if tool == "Shell":
        return False

    event = data.get("hook_event_name", "")
    if event in ("preToolUse", "postToolUse", "postToolUseFailure"):
        return False
    if event in ("beforeShellExecution", "afterShellExecution"):
        return False
    if event in ("PreToolUse", "PostToolUse"):
        return True
    return False


def is_post_tool_use(data):
    """True when the payload is from a post-tool hook (Cursor postToolUse)."""
    return "tool_output" in data


def command(data):
    """Shell command string for a Bash/shell hook, or None.

    Claude: tool_input.command   Cursor pre/post: tool_input.command
    Cursor beforeShell: command
    """
    ti = data.get("tool_input")
    if isinstance(ti, dict) and isinstance(ti.get("command"), str):
        return ti["command"]
    if isinstance(data.get("command"), str):
        return data["command"]
    return None


def tool_input(data):
    """Return a copy of the tool input dict, or None."""
    ti = data.get("tool_input")
    if isinstance(ti, dict):
        return dict(ti)
    cmd = data.get("command")
    if isinstance(cmd, str):
        return {"command": cmd}
    return None


def tool_use_id(data):
    """Stable id for correlating pre/post hooks (Cursor)."""
    value = data.get("tool_use_id")
    return value if isinstance(value, str) and value else None


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


def _read_pending():
    try:
        with open(PENDING_FILE, encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_pending(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PENDING_FILE, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def save_pending_context(tool_use_id, message):
    """Store additional context for a Cursor postToolUse hook."""
    pending = _read_pending()
    pending[tool_use_id] = message
    _write_pending(pending)


def pop_pending_context(tool_use_id):
    """Return and remove stored context for this tool_use_id, if any."""
    pending = _read_pending()
    message = pending.pop(tool_use_id, None)
    if pending:
        _write_pending(pending)
    elif PENDING_FILE.exists():
        try:
            PENDING_FILE.unlink()
        except OSError:
            pass
    return message


def allow_rewrite(data, updated_input, additional_context=None):
    """Allow with a modified tool input; notify the agent via additional context.

    Claude: `additionalContext` on the same PreToolUse response.
    Cursor: stash context for the paired postToolUse hook (tool_use_id required).
    """
    if is_claude(data):
        output = {
            "hookSpecificOutput": {
                "hookEventName": data.get("hook_event_name", "PreToolUse"),
                "permissionDecision": "allow",
                "updatedInput": updated_input,
            }
        }
        if additional_context:
            output["hookSpecificOutput"]["additionalContext"] = additional_context
        print(json.dumps(output))
        return

    payload = {"permission": "allow", "updated_input": updated_input}
    print(json.dumps(payload))

    use_id = tool_use_id(data)
    if use_id and additional_context:
        save_pending_context(use_id, additional_context)


def emit_additional_context(message):
    """Emit postToolUse additional_context (Cursor)."""
    print(json.dumps({"additional_context": message}))


def post_context(data, message):
    """Emit post-tool additional context in the sending tool's shape.

    Claude PostToolUse: hookSpecificOutput.additionalContext.
    Cursor postToolUse: additional_context.
    """
    if is_claude(data):
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": data.get("hook_event_name", "PostToolUse"),
                        "additionalContext": message,
                    }
                }
            )
        )
    else:
        emit_additional_context(message)
