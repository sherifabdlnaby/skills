"""Adapters between each harness's hook protocol and the guard.

Every harness hands its pre-shell hook a JSON payload on stdin and reads a verdict
on stdout; only the shapes differ. An adapter reads the shell command (and the
directory it runs in) out of the payload, and writes a denial in the shape the
harness expects. Printing nothing lets the command run, in every protocol.

Hook configs name the protocol: `hooks/<config>.json` runs `run.sh <protocol>`.
Codex speaks the Claude Code protocol, so both share one adapter and one config.
Supporting a new harness is one more adapter in PROTOCOLS.
"""

from __future__ import annotations

import json
from typing import Any, Callable, NamedTuple


class Call(NamedTuple):
    command: str
    cwd: str | None


class Protocol(NamedTuple):
    read: Callable[[dict[str, Any]], Call | None]
    deny: Callable[[dict[str, Any], str], str]


def _claude_read(payload: dict[str, Any]) -> Call | None:
    """PreToolUse on the `Bash` tool: `tool_input.command`, session `cwd`."""
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    return Call(command, _str(payload.get("cwd"))) if isinstance(command, str) else None


def _claude_deny(payload: dict[str, Any], message: str) -> str:
    # Claude Code and Codex show permissionDecisionReason to the model and the user.
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": payload.get("hook_event_name", "PreToolUse"),
                "permissionDecision": "deny",
                "permissionDecisionReason": message,
            }
        }
    )


def _cursor_read(payload: dict[str, Any]) -> Call | None:
    """beforeShellExecution: top-level `command` and `cwd`.

    Cursor runs plugin hooks from the plugin's own directory, so the payload is the
    only way to find a relative `--body-file`. Its `cwd` is empty unless the agent set
    a working directory for the command; the shell then starts in the first workspace
    root. Good enough: after an earlier `cd` in the same shell, that root is a guess.
    """
    command = payload.get("command")
    if not isinstance(command, str):
        return None
    roots = payload.get("workspace_roots")
    root = roots[0] if isinstance(roots, list) and roots else None
    return Call(command, _str(payload.get("cwd")) or _str(root))


def _cursor_deny(payload: dict[str, Any], message: str) -> str:
    # Both fields carry the whole message: cursor-agent (2026.09) hands the model the
    # user_message of a denied shell command, not the agent_message.
    return json.dumps(
        {"permission": "deny", "agent_message": message, "user_message": message}
    )


PROTOCOLS: dict[str, Protocol] = {
    "claude": Protocol(_claude_read, _claude_deny),  # Claude Code, Codex
    "cursor": Protocol(_cursor_read, _cursor_deny),
}


def _str(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None
