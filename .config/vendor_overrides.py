"""Apply skills-overrides.json to the frontmatter of vendored skills.

A sync replaces skills/vendor/ with upstream's files, so local frontmatter changes live in
skills-overrides.json and are applied again after every sync. Only frontmatter keys change; the
skill body stays as upstream wrote it. A null value removes the key.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERRIDES = ROOT / "skills-overrides.json"
VENDOR = ROOT / "skills" / "vendor"


def split_frontmatter(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("no frontmatter")
    end = lines.index("---", 1)
    return lines[1:end], "\n".join(lines[end:])


def without_key(lines: list[str], key: str) -> list[str]:
    # A key's block is its own line plus any indented continuation lines (YAML `|` or `>`).
    out: list[str] = []
    skipping = False
    for line in lines:
        if line.startswith(f"{key}:"):
            skipping = True
            continue
        if skipping and (line.startswith((" ", "\t")) or not line.strip()):
            continue
        skipping = False
        out.append(line)
    return out


def apply(text: str, keys: dict[str, object]) -> str:
    front, rest = split_frontmatter(text)
    for key, value in keys.items():
        front = without_key(front, key)
        if value is not None:
            front.insert(min(2, len(front)), f"{key}: {json.dumps(value)}")
    return "\n".join(["---", *front, rest])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix", action="store_true", help="write the overrides; without it, only check"
    )
    args = parser.parse_args()

    overrides: dict[str, dict[str, object]] = json.loads(
        OVERRIDES.read_text(encoding="utf-8")
    )
    stale: list[str] = []
    for skill, keys in overrides.items():
        path = VENDOR / skill / "SKILL.md"
        if not path.is_file():
            print(
                f"❌ skills-overrides.json names '{skill}', which is not vendored",
                file=sys.stderr,
            )
            return 1
        text = path.read_text(encoding="utf-8")
        wanted = apply(text, keys)
        if wanted != text:
            stale.append(skill)
            if args.fix:
                path.write_text(wanted, encoding="utf-8")
    if stale and not args.fix:
        print(
            f"❌ overrides not applied to: {', '.join(stale)}. Run: mise run skills:overrides --fix",
            file=sys.stderr,
        )
        return 1
    print(
        f"✅ overrides {'applied to' if stale else 'current for'} {len(overrides)} vendored skills"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
