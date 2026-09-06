#!/usr/bin/env python3
"""AI-disclosure guard for GitHub posts.

Single source of truth for the rule "anything posted to GitHub on the user's
behalf carries an AI footer" (see skills/git/SKILL.md -> AI Disclosure). Wired to
the pre-shell hook (PreToolUse:Bash / beforeShellExecution) so it catches the case
where the agent forgets the footer; it does NOT pick the footer variant (who made
the specific decision is the agent's call) and never rewrites the command, it only
blocks when a posted body is missing disclosure.

Cross-tool stdin/stdout plumbing (Claude vs Cursor payload shapes, the deny
verdicts) lives in hooklib; this file owns only the disclosure decision. stdlib
only. Exit 0 always; "allow" is emitting nothing, "deny" is hooklib.deny().

The body usually arrives as `--body "$(cat <<'EOF' ... EOF)"`, which shlex cannot
parse as shell does: it re-reads the heredoc content as quoted text, so a `"..."`
pair anywhere in the body closes the outer quote and splits the value mid-body.
Heredoc bodies are therefore lifted out of the raw string first (see
`split_heredocs`) and spliced back into the flag value, so the guard checks the
text gh will actually post. A body we still cannot resolve denies with its own
reason rather than claiming the footer is missing.

The guard fails closed. gh has many ways to supply a body the guard cannot see
(`--fill` off commit messages, `--template`, `--editor`, a prompt when no body flag
is given, a real pipe into `--body-file -`), and every one of them would post an
undisclosed body. All of them deny, and the denial names the ways that do work.
"""

import re
import shlex
import sys

import hooklib

# A valid footer line per SKILL.md -> AI Disclosure: `_<sub>` + a decision-source
# emoji (🤖 Agent Decided / 🤝 Human Guided) + attribution ("on behalf of @user")
# + `</sub>_`.
# We validate the skeleton, not the full template text, so the templates stay owned
# by SKILL.md and the agent keeps the decision-source choice; requiring one of the
# two emojis is what forces that choice to be made at all.
FOOTER_RE = re.compile(
    r"_<sub>\s*(?:\U0001f916|\U0001f91d)\s.*?\bon behalf of @[A-Za-z0-9-]+\b.*?</sub>_",
    re.DOTALL,
)

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

# Of POSTING, the actions that end up with a body no matter what: given no body flag,
# gh prompts or opens $EDITOR, and whatever it posts was never shown to the guard.
# `pr edit` and `pr review` are absent because a label, reviewer, title or bare
# approve carries no body at all.
BODY_REQUIRED = {
    ("pr", "create"),
    ("pr", "comment"),
    ("issue", "create"),
    ("issue", "comment"),
}

# Flags that build the body somewhere the guard cannot follow.
OPAQUE_FLAGS = {
    # assembled from commit messages
    "--fill",
    "-f",
    "--fill-first",
    "--fill-verbose",
    # starting text pulled from a template
    "--template",
    "-T",
    # replayed from a failed run's saved input
    "--recover",
    # $EDITOR writes it
    "--editor",
    "-e",
}

# Nothing the agent authored reaches GitHub: --dry-run prints instead of posting,
# --delete-last removes a comment, and --web hands a browser to a person, who is
# accountable for what they type there.
EXEMPT_FLAGS = {"--dry-run", "--delete-last", "--web", "-w"}

REASON = (
    "AI-disclosure guard: this command posts a body to GitHub but the body has no "
    "valid disclosure footer (`_<sub>\U0001f916|\U0001f91d ... on behalf of @user ... </sub>_`). "
    "Per the git skill (SKILL.md -> AI Disclosure), append the footer after a `---`, "
    "picking who made the specific decision: \U0001f916 Agent Decided (you chose "
    "without the user's direction on that decision), \U0001f91d Human Guided (the "
    "user chose or materially directed that decision). A general request to handle "
    "the task does not make it Human Guided. For a PR body use the `Created with ...` "
    "footer in references/pull-requests.md. Add it, then retry."
)

# Distinct from REASON on purpose: "I cannot see your body" and "your footer is
# missing" are different problems, and reporting the second for the first sends the
# agent off rewriting a footer that was already correct.
REASON_UNREADABLE = (
    "AI-disclosure guard: this command posts a body to GitHub that the guard cannot "
    "read, so it cannot check the body for a disclosure footer. This is NOT a claim "
    "that your footer is wrong. Pass the body one of these ways instead: write it to a "
    "file and use `--body-file <path>`, put it inline as `--body '<text>'`, or feed an "
    "inline heredoc with `--body-file - <<'EOF' ... EOF`. None of these ever reach the "
    "guard, so none of them are allowed: `--fill`, `--fill-first`, `--fill-verbose`, "
    "`--template`, `--recover`, `--editor`, leaving out the body flag entirely (gh then "
    "prompts for one), piping a body into `--body-file -`, a `--body-file` path that "
    'cannot be opened, and `--body "$VAR"` or `--body "$(...)"`. Fix the command, '
    "then retry."
)

# `<<DELIM` / `<<'DELIM'` / `<<-DELIM`, excluding the `<<<` herestring.
HEREDOC_RE = re.compile(
    r"<<(?!<)-?[ \t]*(?:'([^']*)'|\"([^\"]*)\"|([A-Za-z_][A-Za-z0-9_]*))"
)

# Stand-in for a lifted heredoc. Shell-inert and shlex-atomic so it survives
# tokenisation as (part of) a single token wherever the operator stood.
PLACEHOLDER = "__GH_DISCLOSURE_HEREDOC_{}__"
PLACEHOLDER_RE = re.compile(r"__GH_DISCLOSURE_HEREDOC_(\d+)__")

# Expansions whose value lives outside the command string. Anything still matching
# after heredoc splicing means the body text never reached us.
UNRESOLVED_RE = re.compile(r"\$\(|\$\{|\$[A-Za-z_]|`")

# extract_body sentinel: a body flag was given, but its text is not recoverable.
UNREADABLE = object()


def split_heredocs(command):
    """Lift heredoc bodies out of `command`.

    Returns `(sanitized, bodies)` where each heredoc body is replaced by a
    placeholder token carrying its index in `bodies`. The rest of the line the
    operator sat on is preserved, so the sanitized string still tokenises as the
    same command.
    """
    bodies = []
    out = []
    pos = 0
    while True:
        match = HEREDOC_RE.search(command, pos)
        if match is None:
            out.append(command[pos:])
            return "".join(out), bodies

        out.append(command[pos : match.start()])
        out.append(PLACEHOLDER.format(len(bodies)))
        delim = match.group(1) or match.group(2) or match.group(3)

        newline = command.find("\n", match.end())
        if newline == -1:  # operator with no body at all
            bodies.append("")
            out.append(command[match.end() :])
            return "".join(out), bodies

        out.append(command[match.end() : newline])
        body, pos = _take_heredoc_body(command, newline + 1, delim)
        bodies.append(body)


def tokenize(command):
    """Return `(tokens, heredoc_bodies)` for `command`, or None on malformed quoting.

    The pair belongs together: tokens carry placeholders that only `extract_body`
    can redeem against the bodies. Shared with pr_structure, which reads the same
    body out of the same command.
    """
    sanitized, bodies = split_heredocs(command)
    try:
        return shlex.split(sanitized), bodies
    except ValueError:
        return None  # malformed quoting; let the tool's own handling deal with it


def _take_heredoc_body(command, start, delim):
    """Return `(body, offset_after_terminator)` for the heredoc opened at `start`."""
    lines = []
    pos = start
    while pos < len(command):
        newline = command.find("\n", pos)
        end = len(command) if newline == -1 else newline
        line = command[pos:end]
        # Forgiving on indentation (bash only strips tabs, and only for `<<-`): the
        # cost of over-matching a terminator is a shorter body, whereas missing one
        # swallows the rest of the command.
        if line.strip() == delim:
            return "\n".join(lines), len(command) if newline == -1 else newline + 1
        lines.append(line)
        if newline == -1:
            break
        pos = newline + 1
    return "\n".join(lines), len(command)  # unterminated; take what we have


def _splice(text, bodies):
    """Return `(text, resolved)` with heredoc placeholders replaced by their bodies."""
    resolved = False

    def replace(match):
        nonlocal resolved
        index = int(match.group(1))
        if 0 <= index < len(bodies):
            resolved = True
            return bodies[index]
        return match.group(0)

    return PLACEHOLDER_RE.sub(replace, text), resolved


def _stdin_heredoc(tokens, bodies):
    """Body of the heredoc feeding this action's stdin, or None if it is a real pipe.

    Only heredocs written on the action's own argument list count, so an unrelated
    heredoc elsewhere in a compound command is never mistaken for the body.
    """
    for token in tokens:
        spliced, resolved = _splice(token, bodies)
        if resolved:
            return spliced
    return None


def _read_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def extract_body(tokens, bodies):
    """Return posted body text, UNREADABLE, or None if there is no body to check.

    Handles `--body`/`-b`/`--body=...` inline and `--body-file`/`-F <path>` (read the
    file). Inline values get any lifted heredoc spliced back in. Anything whose text
    never reaches us is UNREADABLE: an unevaluated expansion, a `--body-file` path that
    will not open, a real pipe into `--body-file -`. None means no body flag was given
    at all, which the caller judges against the action.
    """
    body_parts = []
    unreadable = False
    i = 0
    while i < len(tokens):
        t = tokens[i]
        value = None
        if t in ("--body", "-b") and i + 1 < len(tokens):
            value = tokens[i + 1]
            i += 2
        elif t.startswith("--body="):
            value = t[len("--body=") :]
            i += 1
        elif t in ("--body-file", "-F") and i + 1 < len(tokens):
            path, i = tokens[i + 1], i + 2
            if path == "-":  # body on stdin: readable only as an inline heredoc
                stdin_body = _stdin_heredoc(tokens, bodies)
                if stdin_body is None:
                    unreadable = True  # a real pipe; its text never reaches us
                    continue
                body_parts.append(stdin_body)
                continue
            text = _read_file(path)
            if text is None:
                unreadable = True
                continue
            body_parts.append(text)
            continue
        elif t.startswith("--body-file="):
            text, i = _read_file(t[len("--body-file=") :]), i + 1
            if text is None:
                unreadable = True
                continue
            body_parts.append(text)
            continue
        else:
            i += 1
            continue

        spliced, resolved = _splice(value, bodies)
        body_parts.append(spliced)
        if not resolved and UNRESOLVED_RE.search(spliced):
            unreadable = True

    joined = "\n".join(body_parts)
    # A footer we can see is one gh will post: whatever the part we cannot read adds,
    # the visible text still carries the footer. Only fall back when it does not.
    if unreadable and not FOOTER_RE.search(joined):
        return UNREADABLE
    return joined if body_parts else None


def deny_reason(command):
    """Return the reason to block `command`, or None to allow it."""
    parsed = tokenize(command)
    if parsed is None:
        return None
    tokens, bodies = parsed

    # Find a `gh <noun> <verb>` posting action anywhere in the (possibly compound) line.
    for i in range(len(tokens) - 2):
        if tokens[i] != "gh":
            continue
        action = (tokens[i + 1], tokens[i + 2])
        if action not in POSTING:
            continue
        args = tokens[i + 3 :]

        if EXEMPT_FLAGS.intersection(args):
            return None
        if OPAQUE_FLAGS.intersection(args):
            return REASON_UNREADABLE

        body = extract_body(args, bodies)
        if body is UNREADABLE:
            return REASON_UNREADABLE
        if body is None:
            # No body flag. A create or comment still gets one, from a prompt or
            # $EDITOR; an edit or review with no body posts none.
            return REASON_UNREADABLE if action in BODY_REQUIRED else None
        return None if FOOTER_RE.search(body) else REASON
    return None


def main():
    data = hooklib.load()
    if data is None:
        return 0  # no parseable payload -> allow

    command = hooklib.command(data)
    if not command:
        return 0

    reason = deny_reason(command)
    if reason is None:
        return 0

    user_message = (
        "Blocked a GitHub post whose body this hook could not read."
        if reason is REASON_UNREADABLE
        else "Blocked a GitHub post missing its AI-disclosure footer."
    )
    hooklib.deny(data, reason, user_message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
