"""The disclosure rule: every GitHub post on the user's behalf carries an AI disclosure line.

The guard checks that the line is there, not which tier it names or where it sits:
picking the tier (how much human judgment stands behind the post) and placing the
line are the agent's calls, taught by the ai-disclosure skill. Requiring the tier
emoji is what forces the tier call to be made.
"""

from __future__ import annotations

import re
from typing import NamedTuple

import github
import shell

# `_<sub>` + a tier emoji (🤖 Agent Decided / 📋 Human Planned / 🤝 Human Guided) + the
# rest of the line + `</sub>_`, on one line. The skeleton only: the wording belongs to the
# skill, so older wordings keep passing and editing an older post's body still works.
DISCLOSURE_RE = re.compile(r"_<sub>\s*[\U0001f916\U0001f4cb\U0001f91d][^\n]*?</sub>_")

# `AI_DISCLOSURE=off`, in the hook's environment or as a prefix on one command.
OPT_OUT_VAR = "AI_DISCLOSURE"
OPT_OUT_VALUE = "off"

_SKILL = (
    "Load the `ai-disclosure` skill: it has the disclosure line, where it goes, and how to pick the tier "
    "(how much human judgment stands behind this post)."
)

_OPT_OUT = (
    "Opt out only with a reason (the user waived the line, or the repo forbids it): put "
    f"`{OPT_OUT_VAR}={OPT_OUT_VALUE}` in front of `gh` for this one command."
)

MISSING = (
    "Blocked by the ai-disclosure hook: {what} posts to GitHub on the user's behalf, but "
    "the body has no AI disclosure line (`_<sub>\U0001f916|\U0001f4cb|\U0001f91d <tier>: <tool> "
    "\u00b7 <model></sub>_`). " + _SKILL + " Add it, then retry. " + _OPT_OUT
)

# Separate from MISSING on purpose: "your disclosure is missing" sends the agent to rewrite
# a line that may already be right, when the real problem is how the body is passed.
UNREADABLE = (
    "Blocked by the ai-disclosure hook: {what} posts a body this hook cannot read, so it "
    "cannot check it for an AI disclosure. This is not a claim that the disclosure is "
    "wrong. Pass the body where the hook can read it: a file (`--body-file <path>`, or "
    "`-F body=@<path>` / `-F query=@<path>` for `gh api`), an inline `--body '<text>'`, "
    "or an inline heredoc into `--body-file -`. The hook cannot read: `--fill`, "
    "`--template`, `--recover`, `--editor`, a missing body flag (gh then prompts), a pipe "
    "into stdin, `$VAR` or `$(...)` in the body, a path it cannot open, or a file the same "
    "command writes other than from a heredoc (`cat > <path> <<'EOF'`). "
    + _SKILL
    + " "
    + _OPT_OUT
)


class Denial(NamedTuple):
    kind: str  # "missing" or "unreadable"
    message: str  # for the agent: why, and how to fix it


def check(command_line: str, cwd: str | None) -> Denial | None:
    """Return why `command_line` must not run, or None to let it through."""
    missing: list[str] = []
    unreadable: list[str] = []
    for command, post in github.posts(command_line, cwd):
        if _opted_out(command):
            continue
        for body in post.bodies:
            if DISCLOSURE_RE.search(body.text):
                continue  # a visible disclosure posts, whatever the unseen part adds
            (missing if body.complete else unreadable).append(post.what)

    # A concrete fix first: a missing disclosure outranks a body passed the wrong way.
    if missing:
        return Denial("missing", MISSING.format(what=_names(missing)))
    if unreadable:
        return Denial("unreadable", UNREADABLE.format(what=_names(unreadable)))
    return None


def _opted_out(command: shell.Command) -> bool:
    target = f"{OPT_OUT_VAR}={OPT_OUT_VALUE}"
    if target in command.env:
        return True
    # `env AI_DISCLOSURE=off gh ...`
    argv = command.argv
    return argv[:1] == ["env"] and "gh" in argv and target in argv[1 : argv.index("gh")]


def _names(whats: list[str]) -> str:
    unique = list(dict.fromkeys(whats))
    return "`" + "`, `".join(unique) + "`"
