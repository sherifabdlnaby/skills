#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import tiktoken

import layout

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DIFF_MARKER = "<!-- token-estimates:diff -->"
ENCODING_NAME = "o200k_base"

SKILLS_HEADER = """# Skills

What each skill costs an agent's context window. The [project README](../README.md) says what each one does."""

VENDOR_HEADER = """# Vendored skills

Skills other people wrote, copied in by `mise run skills:sync` from the sources pinned in
[`skills-lock.json`](../../skills-lock.json). Nothing here is edited or written up by us — each
skill's own `SKILL.md` is its documentation."""


@dataclass(frozen=True)
class FileEstimate:
    path: Path
    tokens: int


@dataclass(frozen=True)
class SkillEstimate:
    directory: Path
    name: str
    vendored: bool
    files: tuple[FileEstimate, ...]

    @property
    def skill_tokens(self) -> int:
        return next(file.tokens for file in self.files if file.path.name == "SKILL.md")

    @property
    def total_tokens(self) -> int:
        return sum(file.tokens for file in self.files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate skill token estimates")
    parser.add_argument("--fix", action="store_true", help="write stale reports")
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="tree to measure (default: this repository)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print a snapshot instead of writing reports",
    )
    parser.add_argument(
        "--diff",
        type=Path,
        metavar="SNAPSHOT",
        help="print a PR comment comparing --root against a --json snapshot",
    )
    return parser.parse_args()


def token_count(path: Path, encoding: tiktoken.Encoding) -> int:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return len(encoding.encode(text, disallowed_special=()))


def collect_estimates(root: Path) -> tuple[SkillEstimate, ...]:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    skills_dir = root / "skills"
    skill_directories = set(layout.skills(root))
    estimates: list[SkillEstimate] = []

    for directory in sorted(skill_directories):
        files: list[FileEstimate] = []
        # Markdown only: scripts, assets and config in a skill package are run or parsed by a tool,
        # so they cost nothing against the context window.
        for path in sorted(directory.rglob("*.md")):
            if (
                not path.is_file()
                or path.is_symlink()
                or path == directory / "README.md"
            ):
                continue
            owner = next(
                (parent for parent in path.parents if parent in skill_directories), None
            )
            if owner == directory:
                files.append(FileEstimate(path, token_count(path, encoding)))
        estimates.append(
            SkillEstimate(
                directory,
                directory.relative_to(skills_dir).as_posix(),
                layout.is_vendored(root, directory),
                tuple(files),
            )
        )

    return tuple(estimates)


def upstream_sources(root: Path) -> dict[str, str]:
    lock = json.loads((root / "skills-lock.json").read_text(encoding="utf-8"))
    return {name: entry["source"] for name, entry in lock["skills"].items()}


def badge(label: str, tokens: int, color: str) -> str:
    encoded_label = quote(label, safe="")
    encoded_value = quote(f"{tokens:,} tokens", safe="")
    url = f"https://img.shields.io/badge/{encoded_label}-{encoded_value}-{color}?style=flat-square"
    return f'  <img src="{url}" alt="{label}: {tokens:,} tokens" />'


def markdown_table(
    headers: tuple[str, ...], rows: list[tuple[str, ...]], right: set[int]
) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [
            max(width, len(cell)) for width, cell in zip(widths, row, strict=True)
        ]

    def render(row: tuple[str, ...]) -> str:
        cells = []
        for index, (cell, width) in enumerate(zip(row, widths, strict=True)):
            cells.append(cell.rjust(width) if index in right else cell.ljust(width))
        return f"| {' | '.join(cells)} |"

    separators = tuple(
        "-" * (width - 1) + ":" if index in right else "-" * width
        for index, width in enumerate(widths)
    )
    return "\n".join(
        (render(headers), render(separators), *(render(row) for row in rows))
    )


def count(tokens: int) -> str:
    # Monospace keeps the digits on a common width, so a column of them lines up when rendered.
    return f"`{tokens:,}`"


def signed(delta: int) -> str:
    return f"`{delta:+,}`" if delta else "`0`"


def report_intro(skill_tokens: int, total_tokens: int) -> str:
    skill_label = "All SKILL.md"
    total_label = "All Markdown"
    return "\n".join(
        (
            "<p>",
            badge(skill_label, skill_tokens, "2f80ed"),
            badge(total_label, total_tokens, "2ea44f"),
            "</p>",
            "",
            f"Token estimates use tiktoken's `{ENCODING_NAME}` encoding. `SKILL.md` is the entry prompt; the total adds every",
            "other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather",
            "than read, so they are left out.",
        )
    )


def display_name(estimate: SkillEstimate, base: Path) -> str:
    # Inside skills/vendor/ the prefix is the directory you are already reading.
    return (
        estimate.name.removeprefix("vendor/")
        if base.name == "vendor"
        else estimate.name
    )


def summary_rows(
    estimates: tuple[SkillEstimate, ...], base: Path, *, sources: dict[str, str] | None
) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for estimate in estimates:
        link = quote(estimate.directory.relative_to(base).as_posix())
        cells = [f"[`{display_name(estimate, base)}`]({link}/)"]
        if sources is not None:
            source = sources[estimate.directory.name]
            cells.append(f"[{source}](https://github.com/{source})")
        cells.extend((count(estimate.skill_tokens), count(estimate.total_tokens)))
        rows.append(tuple(cells))
    return rows


def files_table(estimates: tuple[SkillEstimate, ...], base: Path) -> str:
    rows: list[tuple[str, ...]] = []
    for estimate in estimates:
        for file in estimate.files:
            link = quote(file.path.relative_to(base).as_posix())
            name = file.path.relative_to(estimate.directory).as_posix()
            rows.append(
                (
                    f"`{display_name(estimate, base)}`",
                    f"[`{name}`]({link})",
                    count(file.tokens),
                )
            )
    return markdown_table(("Skill", "File", "Tokens"), rows, {2})


def totals(estimates: tuple[SkillEstimate, ...]) -> tuple[int, int]:
    return (
        sum(estimate.skill_tokens for estimate in estimates),
        sum(estimate.total_tokens for estimate in estimates),
    )


def vendor_readme(estimates: tuple[SkillEstimate, ...], vendor_dir: Path) -> str:
    skill_tokens, total_tokens = totals(estimates)
    body = (
        report_intro(skill_tokens, total_tokens),
        markdown_table(
            ("Skill", "Upstream", "SKILL.md", "Total"),
            summary_rows(
                estimates, vendor_dir, sources=upstream_sources(vendor_dir.parents[1])
            ),
            {2, 3},
        ),
        "### Files",
        files_table(estimates, vendor_dir),
    )
    return "\n\n".join((VENDOR_HEADER, *body)) + "\n"


def skills_readme(
    owned: tuple[SkillEstimate, ...],
    vendored: tuple[SkillEstimate, ...],
    skills_dir: Path,
) -> str:
    skill_tokens, total_tokens = totals((*owned, *vendored))
    vendor_skill, vendor_total = totals(vendored)
    vendor_row = (
        f"[`vendor/`](vendor/README.md) ({len(vendored)} skills)",
        count(vendor_skill),
        count(vendor_total),
    )
    rows = [*summary_rows(owned, skills_dir, sources=None), vendor_row]
    body = (
        report_intro(skill_tokens, total_tokens),
        markdown_table(("Skill", "SKILL.md", "Total"), rows, {1, 2}),
        "### Files",
        files_table(owned, skills_dir),
    )
    return "\n\n".join((SKILLS_HEADER, *body)) + "\n"


def snapshot(estimates: tuple[SkillEstimate, ...]) -> dict[str, dict[str, int]]:
    return {
        estimate.name: {
            "skill": estimate.skill_tokens,
            "total": estimate.total_tokens,
        }
        for estimate in estimates
    }


def diff_comment(
    before: dict[str, dict[str, int]], after: dict[str, dict[str, int]]
) -> str | None:
    gone = {"skill": 0, "total": 0}
    rows: list[tuple[str, ...]] = []
    for name in sorted(before.keys() | after.keys()):
        old = before.get(name, gone)
        new = after.get(name, gone)
        skill_delta = new["skill"] - old["skill"]
        total_delta = new["total"] - old["total"]
        if not skill_delta and not total_delta:
            continue
        label = f"`{name}`"
        if name not in before:
            label += " 🆕"
        elif name not in after:
            label += " 🗑️"
        rows.append(
            (
                label,
                count(new["skill"]),
                signed(skill_delta),
                count(new["total"]),
                signed(total_delta),
            )
        )

    if not rows:
        return None

    return "\n".join(
        (
            DIFF_MARKER,
            "### 🪙 Token estimates",
            "",
            markdown_table(
                ("Skill", "SKILL.md", "Δ", "All Markdown", "Δ"), rows, {1, 2, 3, 4}
            ),
        )
    )


def write_reports(
    root: Path, estimates: tuple[SkillEstimate, ...], *, fix: bool
) -> int:
    owned = tuple(estimate for estimate in estimates if not estimate.vendored)
    vendored = tuple(estimate for estimate in estimates if estimate.vendored)
    vendor_dir = root / "skills" / "vendor"

    expected = {
        root / "skills" / "README.md": skills_readme(owned, vendored, root / "skills"),
        vendor_dir / "README.md": vendor_readme(vendored, vendor_dir),
    }
    stale = [
        path
        for path, content in expected.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]

    if not stale:
        print("Token estimates are current.")
        return 0
    if not fix:
        print("Token estimates are stale:", file=sys.stderr)
        for path in stale:
            print(f"  {path.relative_to(root)}", file=sys.stderr)
        print("Run `mise run tokens --fix`.", file=sys.stderr)
        return 1

    for path in stale:
        path.write_text(expected[path], encoding="utf-8")
        print(f"Updated {path.relative_to(root)}")
    return 0


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    estimates = collect_estimates(root)

    if args.json:
        json.dump(snapshot(estimates), sys.stdout, indent=2)
        print()
        return 0
    if args.diff is not None:
        before = json.loads(args.diff.read_text(encoding="utf-8"))
        comment = diff_comment(before, snapshot(estimates))
        # Empty stdout is the signal that there is no comment to make; the note is for a human.
        if comment is None:
            print("No skill changed size.", file=sys.stderr)
        else:
            print(comment)
        return 0
    return write_reports(root, estimates, fix=args.fix)


if __name__ == "__main__":
    raise SystemExit(main())
