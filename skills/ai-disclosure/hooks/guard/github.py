"""Find the GitHub posts in a command line and the body text each one carries.

A post is anything gh puts on GitHub as written text under the user's name: a PR,
an issue, a comment, a review, a review comment, a thread reply. Two shapes reach it:

- `gh pr|issue <verb>`: the body comes from `--body`, `--body-file`, or (when
  neither is given) a prompt or $EDITOR the guard never sees.
- `gh api`: REST writes to content paths with a `body` field, and GraphQL
  mutations with a `body` argument.

Each post comes back with its bodies. A body is incomplete when part of the text gh
would post never appears in the command: a pipe, an unexpanded variable, a file that
will not open, a prompt. Deciding what a body must contain is the caller's job.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Iterator, NamedTuple

import shell
from files import Files


class Body(NamedTuple):
    text: str  # what the guard can read of it
    complete: bool  # False when gh adds text the guard never sees


class Post(NamedTuple):
    what: str  # e.g. "gh pr comment", "gh api graphql"
    bodies: list[Body]


_UNSEEN = Body("", False)


# Commands that run the rest of their argv as another command.
_WRAPPERS = {
    "env",
    "command",
    "exec",
    "builtin",
    "nohup",
    "nice",
    "time",
    "timeout",
    "sudo",
    "xargs",
}
# A wrapper's own options and settings: `-i`, `NAME=value`, a duration.
_WRAPPER_ARG_RE = re.compile(r"^(-.*|[A-Za-z_][A-Za-z0-9_]*=.*|[0-9.]+[smhd]?)$")

# `gh <noun> <verb>` actions that post written text.
_POSTING = {
    ("pr", "create"),
    ("pr", "comment"),
    ("pr", "edit"),
    ("pr", "review"),
    ("issue", "create"),
    ("issue", "comment"),
    ("issue", "edit"),
}

# Of those, the actions that post a body even when no body flag is given: gh then
# prompts or opens $EDITOR. An edit or a review may carry no body at all (a label,
# a title, a bare approve).
_BODY_REQUIRED = {
    ("pr", "create"),
    ("pr", "comment"),
    ("issue", "create"),
    ("issue", "comment"),
}

# Flags that build the body somewhere the guard cannot follow: commit messages,
# a template, a replayed failed run, $EDITOR.
_OPAQUE_FLAGS = {
    "--fill",
    "-f",
    "--fill-first",
    "--fill-verbose",
    "--template",
    "-T",
    "--recover",
    "--editor",
    "-e",
}

# Nothing the agent wrote reaches GitHub: --dry-run prints, --delete-last removes,
# --web hands a browser to a person.
_EXEMPT_FLAGS = {"--dry-run", "--delete-last", "--web", "-w"}

# REST path segments under which a `body` field is written text: issues, PRs,
# comments, reviews, discussions, etc. Releases and other bodies fall outside.
_CONTENT_SEGMENTS = {"issues", "pulls", "comments", "reviews", "replies", "discussions"}

_WRITE_METHODS = {"POST", "PATCH", "PUT"}

# `gh api` flags that take a value; the rest are boolean.
_API_VALUE_FLAGS = {
    "-X": "method",
    "--method": "method",
    "-f": "raw-field",
    "--raw-field": "raw-field",
    "-F": "field",
    "--field": "field",
    "--input": "input",
    "-H": None,
    "--header": None,
    "-q": None,
    "--jq": None,
    "-t": None,
    "--template": None,
    "--hostname": None,
    "-p": None,
    "--preview": None,
    "--cache": None,
}


def posts(command_line: str, cwd: str | None) -> Iterator[tuple[shell.Command, Post]]:
    """Each GitHub post on a command line, with the command that makes it.

    Commands run in order, so a body file a heredoc writes earlier on the line is
    readable later. Malformed quoting yields nothing: the shell rejects it before gh runs.
    """
    line = shell.parse(command_line)
    if line is None:
        return
    files = Files(cwd)
    for command in line.commands:
        post = find_post(command, line.heredocs, files)
        if post:
            yield command, post
        files.run(command, line.heredocs)


def find_post(command: shell.Command, heredocs: list[str], files: Files) -> Post | None:
    """The GitHub post `command` makes, or None.

    gh runs when it is the command word, by name or full path, or sits behind a
    wrapper such as `env` or `timeout 60`. A `gh` anywhere else is an argument.
    """
    for i, token in enumerate(command.argv):
        if os.path.basename(token) == "gh":
            args = command.argv[i + 1 :]
            return (
                _api_post(args[1:], heredocs, files)
                if args[:1] == ["api"]
                else _cli_post(args, heredocs, files)
            )
        if not (token in _WRAPPERS or _WRAPPER_ARG_RE.match(token)):
            return None
    return None


# ── gh pr / gh issue ────────────────────────────────────────────────────────────


def _cli_post(args: list[str], heredocs: list[str], files: Files) -> Post | None:
    action = tuple(args[:2])
    if action not in _POSTING:
        return None
    flags = args[2:]
    what = "gh " + " ".join(action)

    if _EXEMPT_FLAGS.intersection(flags):
        return None
    if _OPAQUE_FLAGS.intersection(flags):
        return Post(what, [_UNSEEN])

    parts: list[Body] = []
    i = 0
    while i < len(flags):
        flag, value, i = _flag_value(flags, i, ("--body", "-b", "--body-file", "-F"))
        if flag in ("--body", "-b"):
            parts.append(_inline(value, heredocs))
        elif flag is not None:
            parts.append(_file(value, flags, heredocs, files))

    if not parts:
        return Post(what, [_UNSEEN]) if action in _BODY_REQUIRED else None
    # gh posts one body, so the parts are judged as one.
    return Post(
        what, [Body("\n".join(p.text for p in parts), all(p.complete for p in parts))]
    )


# ── gh api ──────────────────────────────────────────────────────────────────────


def _api_post(args: list[str], heredocs: list[str], files: Files) -> Post | None:
    endpoint = None
    method = None
    fields: list[tuple[str, str, bool]] = []  # (key, value, raw)
    input_path = None
    i = 0
    while i < len(args):
        token = args[i]
        name, value, i = _api_flag(args, i)
        if name is None:
            if endpoint is None and not token.startswith("-"):
                endpoint = token
            continue
        if name == "method":
            method = value.upper()
        elif name in ("raw-field", "field") and "=" in value:
            key, _, val = value.partition("=")
            fields.append((key, val, name == "raw-field"))
        elif name == "input":
            input_path = value

    if endpoint is None:
        return None
    path = endpoint.split("?", 1)[0].rstrip("/")
    is_graphql = path.split("/")[-1] == "graphql"
    if method is None:
        method = "POST" if (fields or input_path or is_graphql) else "GET"
    if method not in _WRITE_METHODS:
        return None

    what = "gh api " + endpoint
    payload: Any = None
    if input_path is not None:
        body = _file(input_path, args, heredocs, files)
        try:
            payload = json.loads(body.text) if body.complete else None
        except ValueError:
            payload = None
        if payload is None:
            return Post(what, [_UNSEEN])

    values: dict[str, Body] = {}
    for key, val, raw in fields:
        values[key] = (
            _file(val[1:], args, heredocs, files)
            if not raw and val.startswith("@")
            else _inline(val, heredocs)
        )

    if is_graphql:
        return _graphql_post(what, values, payload)

    if not set(path.split("/")) & _CONTENT_SEGMENTS:
        return None
    bodies = [v for k, v in values.items() if _is_body_key(k)]
    bodies.extend(Body(text, True) for text in _json_bodies(payload))
    return Post(what, bodies) if bodies else None


def _graphql_post(what: str, values: dict[str, Body], payload: Any) -> Post | None:
    variables: dict[str, Any] = {
        k: v for k, v in values.items() if k not in ("query", "operationName")
    }
    if isinstance(payload, dict):
        query = payload.get("query")
        if isinstance(payload.get("variables"), dict):
            variables.update(payload["variables"])
    else:
        # GraphQL's own `$variables` read as unexpanded shell, so the query is taken
        # as written; each body literal is checked for leftovers on its own below.
        query = values["query"].text if "query" in values else None
    if not isinstance(query, str) or not query:
        # Nothing readable to tell a read from a mutation that posts.
        return (
            Post(what, [_UNSEEN])
            if ("query" in values or payload is not None)
            else None
        )

    tokens = _graphql_tokens(query)
    if ("name", "mutation") not in tokens:
        return None

    bodies: list[Body] = []
    for i in range(len(tokens) - 2):
        if tokens[i] != ("name", "body") or tokens[i + 1] != ("punct", ":"):
            continue
        kind, value = tokens[i + 2]
        if kind == "string":
            bodies.append(Body(value, not shell.is_unresolved(value)))
        elif kind == "variable":
            bodies.append(_as_body(variables.get(value[1:])))
    for key, val in variables.items():
        if _is_body_key(key):
            bodies.append(_as_body(val))
        elif isinstance(val, (dict, list)):
            bodies.extend(Body(text, True) for text in _json_bodies(val))
    return Post(what, bodies) if bodies else None


_GRAPHQL_TOKEN_RE = re.compile(
    r'(?P<block>"""(?:\\"""|[^"]|"(?!""))*""")'
    r'|(?P<string>"(?:\\.|[^"\\\n])*")'
    r"|(?P<comment>#[^\n]*)"
    r"|(?P<variable>\$[_A-Za-z][_0-9A-Za-z]*)"
    r"|(?P<name>[_A-Za-z][_0-9A-Za-z]*)"
    r"|(?P<punct>[:{}()\[\]!=@,|&]|\.\.\.)"
    r"|(?P<other>\S)"
)


def _graphql_tokens(query: str) -> list[tuple[str, str]]:
    """Lex a GraphQL document; strings come back decoded, comments dropped."""
    tokens = []
    for match in _GRAPHQL_TOKEN_RE.finditer(query):
        kind = match.lastgroup or "other"
        text = match.group()
        if kind == "comment":
            continue
        if kind == "block":
            kind, text = "string", text[3:-3].replace('\\"""', '"""')
        elif kind == "string":
            try:
                text = json.loads(text, strict=False)
            except ValueError:
                text = text[1:-1]
        tokens.append((kind, text))
    return tokens


# ── shared helpers ──────────────────────────────────────────────────────────────


def _flag_value(
    flags: list[str], i: int, names: tuple[str, ...]
) -> tuple[str | None, str, int]:
    """Match `--flag value` or `--flag=value` at `flags[i]` against `names`."""
    token = flags[i]
    if token in names and i + 1 < len(flags):
        return token, flags[i + 1], i + 2
    for name in names:
        if name.startswith("--") and token.startswith(name + "="):
            return name, token[len(name) + 1 :], i + 1
    return None, "", i + 1


def _api_flag(args: list[str], i: int) -> tuple[str | None, str, int]:
    """Return `(kind, value, next_index)` for a `gh api` flag at `args[i]`.

    kind is None for a positional argument or a flag the guard does not read.
    """
    token = args[i]
    if token in _API_VALUE_FLAGS:
        if i + 1 >= len(args):
            return None, "", i + 1
        return _API_VALUE_FLAGS[token], args[i + 1], i + 2
    if token.startswith("--") and "=" in token:
        name, _, value = token.partition("=")
        if name in _API_VALUE_FLAGS:
            return _API_VALUE_FLAGS[name], value, i + 1
    # Short flag with the value attached: `-XPOST`, `-fbody=...`.
    if len(token) > 2 and token[:2] in _API_VALUE_FLAGS and not token.startswith("--"):
        return _API_VALUE_FLAGS[token[:2]], token[2:], i + 1
    return None, "", i + 1


def _inline(value: str, heredocs: list[str]) -> Body:
    """An inline argument, with any lifted heredoc spliced back in."""
    text, resolved = shell.splice(value, heredocs)
    return Body(text, resolved or not shell.is_unresolved(text))


def _file(path: str, argv: list[str], heredocs: list[str], files: Files) -> Body:
    """A body file's contents; `-` is stdin, readable only as an inline heredoc."""
    text = shell.stdin_heredoc(argv, heredocs) if path == "-" else files.read(path)
    return _UNSEEN if text is None else Body(text, True)


def _as_body(value: Any) -> Body:
    if isinstance(value, Body):
        return value
    return Body(value, True) if isinstance(value, str) else _UNSEEN


def _is_body_key(key: str) -> bool:
    return key == "body" or key.endswith("[body]")


def _json_bodies(value: Any) -> list[str]:
    """Every string under a `body` key, at any depth."""
    found = []
    if isinstance(value, dict):
        for key, val in value.items():
            if key == "body" and isinstance(val, str):
                found.append(val)
            else:
                found.extend(_json_bodies(val))
    elif isinstance(value, list):
        for item in value:
            found.extend(_json_bodies(item))
    return found
