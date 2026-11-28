#!/usr/bin/env python3
"""Skill reminder after git and PR commands.

Wired to the post-shell hook (PostToolUse:Bash / Cursor postToolUse:Shell). After
`git commit`, `git push`, `gh pr create`, `gh pr ready`, or `gh stack submit`, it adds
one short note to the agent's context. It never blocks and keeps no state.
stdlib only. Exit 0.
"""

from __future__ import annotations

import re
import sys

import hooklib

TRIGGER = re.compile(
    r"(?:^|[;&|(]\s*|\s)(?:git(?:\s+-[cC]\s+\S+|\s+--?[\w-]+(?:=\S+)?)*\s+(?:commit|push)|gh\s+pr\s+(?:create|ready)|gh\s+stack\s+submit)\b"
)

MESSAGE = (
    "Reminder: load the git and coding skills if not loaded. Run coding's handoff pass "
    "(no-comments, no-docs, review) once at handoff, when the PR is code-ready, not on every commit or push."
)


def triggered(command: str | None) -> bool:
    return bool(command) and bool(TRIGGER.search(command))


def main() -> int:
    data = hooklib.load()
    if data is not None and triggered(hooklib.command(data)):
        hooklib.post_context(data, MESSAGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
