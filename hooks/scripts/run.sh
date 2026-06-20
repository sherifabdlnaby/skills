#!/usr/bin/env bash
# Generic hook launcher. Every hook entry in claude-hooks.json / cursor-hooks.json
# invokes `run.sh <worker.py>`, so interpreter selection lives here once instead of
# in a launcher per event. The worker is resolved next to this script and fed the
# stdin payload; it does the actual decision via hooklib (see hooklib.py).
#
# stdlib-only Python, so python3 is the path; uv is a fallback if python3 is absent.
# No interpreter available -> allow rather than wedge the agent (emit nothing, exit 0).
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKER="$DIR/${1:?usage: run.sh <worker.py>}"

if command -v python3 >/dev/null 2>&1; then
  exec python3 "$WORKER"
elif command -v uv >/dev/null 2>&1; then
  exec uv run --no-project python3 "$WORKER"
fi
# No interpreter available: drain stdin and allow.
cat >/dev/null 2>&1 || true
exit 0
