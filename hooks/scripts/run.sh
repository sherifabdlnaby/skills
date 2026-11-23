#!/usr/bin/env bash
# Generic hook launcher. Every hook entry in claude-hooks.json / cursor-hooks.json
# invokes `run.sh <worker.py>`, so interpreter selection lives here once instead of
# in a launcher per event. The worker is resolved next to this script and fed the
# stdin payload; it does the actual decision via hooklib (see hooklib.py).
#
# stdlib-only Python, so python3 is the path; uv is the fallback when it is absent or fails.
# Version manager shims resolve python3 from the working directory; `/` keeps a local
# config out of it. Workers get the command's directory from the payload.
# No interpreter available -> allow rather than wedge the agent (emit nothing, exit 0).
set -u
# Builtins only: this runs on every shell command.
cd "${BASH_SOURCE[0]%/*}" || exit 0
WORKER="$PWD/${1:?usage: run.sh <worker.py>}"
IFS= read -r -d '' PAYLOAD
cd /

run() { command -v "$1" >/dev/null 2>&1 && printf '%s' "$PAYLOAD" | "$@" "$WORKER"; }
command -v python3 >/dev/null 2>&1 || command -v uv >/dev/null 2>&1 || exit 0
# Exit 1, not Python's 2: some harnesses block the tool call on 2.
run python3 || run uv run --no-project python3 || exit 1
