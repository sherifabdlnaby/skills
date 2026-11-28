#!/usr/bin/env python3
"""Skill reminder after git and PR commands.

Wired to the post-shell hook (PostToolUse:Bash / Cursor postToolUse:Shell). After
`git commit`, `git push`, `gh pr create`, `gh pr ready`, or `gh stack submit`, it adds
one note to the agent's context: load the git and coding skills if they are not
loaded yet, and run the coding skill's diff clean once at handoff, not on each
commit or push. It stays quiet when the session transcript shows both skills
loaded, and speaks at most once per session. It never blocks. stdlib only. Exit 0.
"""

from __future__ import annotations

import json
import re
import sys

import hooklib

STATE_FILE = hooklib.STATE_DIR / "skill_reminder.json"

TRIGGER = re.compile(
    r"(?:^|[;&|(]\s*|\s)(?:git\s+(?:-C\s+\S+\s+)?(?:commit|push)|gh\s+pr\s+(?:create|ready)|gh\s+stack\s+submit)\b"
)
# A skill load in a Claude Code transcript: a Skill tool call, or a slash command the user typed.
LOADED = re.compile(
    r'"skill"\s*:\s*"(?:[\w-]+:)?(git|coding)"|<command-name>/(?:[\w-]+:)?(git|coding)</command-name>'
)
SKILLS = {"git", "coding"}

MESSAGE = (
    "Reminder: load the git and coding skills if you have not loaded them in this session. "
    "The coding skill's diff clean (no-comments, no-docs) runs once at handoff, when the PR "
    "or change is code-ready and goes to the user or to review. It does not run on each "
    "commit or push."
)


def triggered(command: str | None) -> bool:
    return bool(command) and bool(TRIGGER.search(command))


def loaded_skills(transcript_path: str | None) -> set[str]:
    if not transcript_path:
        return set()
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    except OSError:
        return set()
    return {name for match in LOADED.finditer(text) for name in match.groups() if name}


def session_key(data: dict) -> str | None:
    for key in ("session_id", "conversation_id"):
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def already_reminded(key: str | None) -> bool:
    if key is None:
        return False
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            seen = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(seen, list) and key in seen


def mark_reminded(key: str | None) -> None:
    if key is None:
        return
    try:
        with open(STATE_FILE, encoding="utf-8") as fh:
            seen = json.load(fh)
        if not isinstance(seen, list):
            seen = []
    except (OSError, json.JSONDecodeError):
        seen = []
    seen = [*seen[-199:], key]  # bounded: old sessions fall off
    try:
        hooklib.STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as fh:
            json.dump(seen, fh)
    except OSError:
        pass


def main() -> int:
    data = hooklib.load()
    if data is None or not triggered(hooklib.command(data)):
        return 0
    if SKILLS <= loaded_skills(data.get("transcript_path")):
        return 0
    key = session_key(data)
    if already_reminded(key):
        return 0
    mark_reminded(key)
    hooklib.post_context(data, MESSAGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
