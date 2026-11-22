"""What a body file holds at the moment gh reads it.

The guard runs before the command line does, so a path is read as it will stand when
gh runs, not as it stands now. The commands ahead of gh on the same line change that:

- `cd` moves the directory a relative path resolves against.
- A heredoc written to a file (`cat > f <<'EOF'`, `tee f <<'EOF'`) is that file's
  content, though the file does not exist yet.
- Any other write to a file (`printf ... > f`, `>>`, `tee -a`, etc.) leaves its
  content unknown. What is on disk now is stale, so it is never read in its place.
"""

from __future__ import annotations

import os

import shell

# Redirections whose target is a file the command writes.
_OVERWRITE = {">", ">|", "&>"}
_APPEND = {">>", "&>>"}


class Files:
    def __init__(self, cwd: str | None):
        self._cwd = cwd  # None once a `cd` goes where the guard cannot follow
        self._written: dict[str, str | None] = {}  # path -> content, None when unknown

    def run(self, command: shell.Command, heredocs: list[str]) -> None:
        """Apply what `command`, run ahead of a post on the same line, does to files."""
        argv = command.argv
        if argv[:1] == ["cd"]:
            self._cd(argv[1:])
            return
        for path, content in _writes(argv, heredocs):
            key = self._resolve(path)
            if key is not None:
                self._written[key] = content

    def read(self, path: str) -> str | None:
        """The text gh reads from `path`, or None when the guard cannot know it."""
        key = self._resolve(path)
        if key is None:
            return None
        if key in self._written:
            return self._written[key]
        try:
            with open(key, encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError:
            return None

    def _cd(self, args: list[str]) -> None:
        target = args[0] if args else "~"
        self._cwd = None if target == "-" else self._resolve(target)

    def _resolve(self, path: str) -> str | None:
        if shell.is_unresolved(path):
            return None
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            if self._cwd is None:
                return None
            path = os.path.join(self._cwd, path)
        return os.path.normpath(path)


def _writes(argv: list[str], heredocs: list[str]) -> list[tuple[str, str | None]]:
    """The files `argv` writes, each with its content when a heredoc supplies it."""
    targets: list[tuple[str, bool]] = []  # (path, overwritten with stdin)
    words: list[str] = []
    i = 0
    while i < len(argv):
        token, target = argv[i], argv[i + 1] if i + 1 < len(argv) else None
        # `>&` names a file unless it duplicates a descriptor: `2>&1`, `>&-`.
        is_file = (
            token in _OVERWRITE
            or token in _APPEND
            or (token == ">&" and target and not target.isdigit() and target != "-")
        )
        if is_file and target is not None:
            targets.append((target, token not in _APPEND))
            i += 2
            continue
        words.append(token)
        i += 1

    args = [w for w in words if not shell.splice(w, heredocs)[1]]
    if args[:1] == ["tee"]:
        # `tee <paths>` copies stdin into each path; an option (`-a`, etc.) makes it unknown.
        plain = not any(a.startswith("-") for a in args[1:])
        targets.extend((path, plain) for path in args[1:])
    # stdout is the heredoc unchanged only for a bare `cat` or `tee`.
    passes_stdin = args == ["cat"] or args[:1] == ["tee"]
    content = shell.stdin_heredoc(words, heredocs) if passes_stdin else None
    return [(path, content if whole else None) for path, whole in targets]
