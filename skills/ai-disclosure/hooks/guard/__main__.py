"""Hook entry point: `python3 hooks/guard <protocol>` with the payload on stdin.

Exits 0 in every case; the verdict is what it prints. A payload it cannot parse
lets the command run: that is the harness misbehaving, not a post to judge.
Harness hooks reach this through run.sh, which owns the session-wide opt-out.
"""

from __future__ import annotations

import json
import sys

import disclosure
import harness


def main() -> int:
    protocol = harness.PROTOCOLS.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if protocol is None:
        sys.stderr.write(f"usage: guard <{'|'.join(harness.PROTOCOLS)}>\n")
        return 0
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    call = protocol.read(payload) if isinstance(payload, dict) else None
    if call is None:
        return 0

    denial = disclosure.check(call.command, call.cwd)
    if denial is not None:
        print(protocol.deny(payload, denial.message))
    return 0


if __name__ == "__main__":
    sys.exit(main())
