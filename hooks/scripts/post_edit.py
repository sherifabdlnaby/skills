#!/usr/bin/env python3
"""Post-edit worker. No-op placeholder.

Wired to PostToolUse:Write|Edit (Claude) and afterFileEdit (Cursor). Consumes the
payload and allows. Replace main()'s body with your logic, e.g. run a formatter on
the changed file (`hooklib.file_path(data)`). Cross-tool plumbing lives in hooklib;
this file owns only the post-edit decision. stdlib only.
"""

import sys

import hooklib


def main():
    data = hooklib.load()
    if data is None:
        return 0
    # path = hooklib.file_path(data)  # the file just written/edited, when you need it
    hooklib.allow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
