"""Read a shell command line into the simple commands bash would run.

The guard only ever sees the command as text, before the shell runs it. This module
turns that text into tokens close enough to what each program receives as argv:

- Heredoc bodies are lifted out before tokenizing and spliced back on demand.
  shlex re-reads heredoc text as quoted shell, so a `"` anywhere in a body would
  otherwise close the outer quote and split the body mid-text.
- Unquoted newlines and control operators (`;`, `&&`, `|`, etc.) split the line into
  simple commands, so the arguments of one command never bleed into the next.
- Comments and backslash-newline continuations are dropped the way bash drops them.

Expansions (`$VAR`, `$(...)`, backticks) are left unevaluated: their value never
reaches the guard, and callers decide what an unresolved value means.
"""

from __future__ import annotations

import re
import shlex
from typing import NamedTuple

# `<<DELIM` / `<<'DELIM'` / `<<-DELIM`, excluding the `<<<` herestring.
_HEREDOC_RE = re.compile(
    r"<<(?!<)-?[ \t]*(?:'([^']*)'|\"([^\"]*)\"|([A-Za-z_][A-Za-z0-9_]*))"
)

# Stand-in for a lifted heredoc: shell-inert and shlex-atomic, so it survives
# tokenizing as (part of) one token wherever the operator stood.
_PLACEHOLDER = "__AI_DISCLOSURE_HEREDOC_{}__"
_PLACEHOLDER_RE = re.compile(r"__AI_DISCLOSURE_HEREDOC_(\d+)__")

_SEPARATORS = {";", ";;", "&", "&&", "|", "||", "|&", "(", ")"}

# An expansion whose value lives outside the command text.
_UNRESOLVED_RE = re.compile(r"\$(?:$|[({A-Za-z_0-9@*#?!-])|`")

_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


class Command(NamedTuple):
    """One simple command: leading `NAME=value` assignments, then its argv."""

    env: list[str]
    argv: list[str]


class Line(NamedTuple):
    commands: list[Command]
    heredocs: list[str]


def parse(text: str) -> Line | None:
    """Split `text` into simple commands, or None when its quoting is malformed."""
    sanitized, heredocs = _lift_heredocs(text)
    lexer = shlex.shlex(_normalize(sanitized), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    # `#` only starts a comment at a word start; _normalize handles it.
    lexer.commenters = ""
    try:
        tokens = list(lexer)
    except ValueError:
        return None

    commands = []
    current: list[str] = []
    for token in tokens + [";"]:
        if token in _SEPARATORS:
            if current:
                commands.append(_split_env(current))
            current = []
        else:
            current.append(token)
    return Line(commands, heredocs)


def splice(text: str, heredocs: list[str]) -> tuple[str, bool]:
    """Return `(text, resolved)` with heredoc placeholders replaced by their bodies."""
    resolved = False

    def replace(match: re.Match[str]) -> str:
        nonlocal resolved
        index = int(match.group(1))
        if index < len(heredocs):
            resolved = True
            return heredocs[index]
        return match.group(0)

    return _PLACEHOLDER_RE.sub(replace, text), resolved


def stdin_heredoc(argv: list[str], heredocs: list[str]) -> str | None:
    """Body of the heredoc feeding this command's stdin, or None for a real pipe.

    Only a heredoc written on the command's own argv counts, so one feeding another
    command on the same line is never mistaken for this command's input.
    """
    for token in argv:
        text, resolved = splice(token, heredocs)
        if resolved:
            return text
    return None


def is_unresolved(text: str) -> bool:
    """True when `text` still holds an expansion the shell would replace."""
    return bool(_UNRESOLVED_RE.search(text))


def _split_env(tokens: list[str]) -> Command:
    i = 0
    while i < len(tokens) and _ASSIGNMENT_RE.match(tokens[i]):
        i += 1
    return Command(tokens[:i], tokens[i:])


def _lift_heredocs(text: str) -> tuple[str, list[str]]:
    """Replace each heredoc body with a placeholder; return the text and the bodies.

    The rest of the line the operator sits on is kept, so the result still
    tokenizes as the same command.
    """
    bodies: list[str] = []
    out: list[str] = []
    pos = 0
    while True:
        match = _HEREDOC_RE.search(text, pos)
        if match is None:
            out.append(text[pos:])
            return "".join(out), bodies

        out.append(text[pos : match.start()])
        out.append(_PLACEHOLDER.format(len(bodies)))
        delim = match.group(1) or match.group(2) or match.group(3)

        newline = text.find("\n", match.end())
        if newline == -1:  # operator with no body
            bodies.append("")
            out.append(text[match.end() :])
            return "".join(out), bodies

        out.append(text[match.end() : newline + 1])
        body, pos = _take_heredoc_body(text, newline + 1, delim)
        bodies.append(body)


def _take_heredoc_body(text: str, start: int, delim: str) -> tuple[str, int]:
    """Return `(body, offset_after_terminator)` for the heredoc that opens at `start`."""
    lines = []
    pos = start
    while pos < len(text):
        newline = text.find("\n", pos)
        end = len(text) if newline == -1 else newline
        line = text[pos:end]
        # Forgiving on indentation (bash strips only tabs, only for `<<-`): matching a
        # terminator too early gives a shorter body, missing one swallows the rest of
        # the line.
        if line.strip() == delim:
            return "\n".join(lines), end
        lines.append(line)
        pos = end + 1
    return "\n".join(lines), len(text)  # unterminated: take what is there


def _normalize(text: str) -> str:
    """Apply the bash rules shlex lacks: newlines end a command, `#` starts a
    comment at a word start, and backslash-newline joins two lines."""
    out: list[str] = []
    quote = ""
    i = 0
    while i < len(text):
        char = text[i]
        if quote == "'":
            if char == "'":
                quote = ""
            out.append(char)
        elif char == "\\" and i + 1 < len(text):
            if text[i + 1] != "\n":  # backslash-newline is a continuation: drop both
                out.append(text[i : i + 2])
            i += 2
            continue
        elif quote == '"':
            if char == '"':
                quote = ""
            out.append(char)
        elif char in "'\"":
            quote = char
            out.append(char)
        elif char == "\n":
            out.append(" ; ")
        elif char == "#" and (
            not out or out[-1][-1:] in ("", " ", "\t", ";", "&", "|", "(", ")")
        ):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        else:
            out.append(char)
        i += 1
    return "".join(out)
