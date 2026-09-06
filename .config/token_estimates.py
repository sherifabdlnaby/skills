#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import tiktoken

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
VENDOR_DIR = SKILLS_DIR / "vendor"
LOCK = ROOT / "skills-lock.json"
START_MARKER = "<!-- token-estimates:start -->"
END_MARKER = "<!-- token-estimates:end -->"
ENCODING_NAME = "o200k_base"

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
    files: tuple[FileEstimate, ...]

    @property
    def name(self) -> str:
        return self.directory.relative_to(SKILLS_DIR).as_posix()

    @property
    def vendored(self) -> bool:
        return self.directory.is_relative_to(VENDOR_DIR)

    @property
    def skill_tokens(self) -> int:
        return next(file.tokens for file in self.files if file.path.name == "SKILL.md")

    @property
    def total_tokens(self) -> int:
        return sum(file.tokens for file in self.files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate skill token estimates")
    parser.add_argument("--fix", action="store_true", help="write stale reports")
    return parser.parse_args()


def token_count(path: Path, encoding: tiktoken.Encoding) -> int:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return len(encoding.encode(text, disallowed_special=()))


def collect_estimates() -> tuple[SkillEstimate, ...]:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    skill_directories = {path.parent for path in SKILLS_DIR.rglob("SKILL.md")}
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
        estimates.append(SkillEstimate(directory, tuple(files)))

    return tuple(estimates)


def upstream_sources() -> dict[str, str]:
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
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


def report_intro(skill_tokens: int, total_tokens: int, *, plural: bool = False) -> str:
    skill_label = "All SKILL.md" if plural else "SKILL.md"
    total_label = "All Markdown" if plural else "Total"
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


def skill_block(estimate: SkillEstimate) -> str:
    rows = []
    for file in estimate.files:
        relative_path = file.path.relative_to(estimate.directory).as_posix()
        rows.append(
            (f"[`{relative_path}`]({quote(relative_path)})", f"{file.tokens:,}")
        )
    table = markdown_table(("File", "Tokens"), rows, {1})
    return "\n\n".join(
        (
            START_MARKER,
            report_intro(estimate.skill_tokens, estimate.total_tokens),
            table,
            END_MARKER,
        )
    )


def summary_table(
    estimates: tuple[SkillEstimate, ...], base: Path, *, sources: dict[str, str] | None
) -> str:
    headers = ("Skill", "SKILL.md", "Total")
    right = {1, 2}
    if sources is not None:
        headers = ("Skill", "Upstream", "SKILL.md", "Total")
        right = {2, 3}
    rows: list[tuple[str, ...]] = []
    for estimate in estimates:
        link = quote(estimate.directory.relative_to(base).as_posix())
        cells = [f"[`{estimate.name.removeprefix('vendor/')}`]({link}/)"]
        if sources is not None:
            source = sources[estimate.directory.name]
            cells.append(f"[{source}](https://github.com/{source})")
        cells.extend((f"{estimate.skill_tokens:,}", f"{estimate.total_tokens:,}"))
        rows.append(tuple(cells))
    return markdown_table(headers, rows, right)


def files_table(estimates: tuple[SkillEstimate, ...], base: Path) -> str:
    rows: list[tuple[str, ...]] = []
    for estimate in estimates:
        for file in estimate.files:
            link = quote(file.path.relative_to(base).as_posix())
            name = file.path.relative_to(estimate.directory).as_posix()
            rows.append(
                (
                    f"`{estimate.name.removeprefix('vendor/')}`",
                    f"[`{name}`]({link})",
                    f"{file.tokens:,}",
                )
            )
    return markdown_table(("Skill", "File", "Tokens"), rows, {2})


def collection_report(
    estimates: tuple[SkillEstimate, ...], base: Path, *, sources: dict[str, str] | None
) -> tuple[str, ...]:
    return (
        report_intro(
            sum(estimate.skill_tokens for estimate in estimates),
            sum(estimate.total_tokens for estimate in estimates),
            plural=True,
        ),
        summary_table(estimates, base, sources=sources),
        "### Files",
        files_table(estimates, base),
    )


def root_block(estimates: tuple[SkillEstimate, ...]) -> str:
    details = "\n\n".join(
        (
            "<details>",
            "<summary><strong>Token estimates</strong></summary>",
            *collection_report(estimates, ROOT, sources=None),
            "</details>",
        )
    )
    return "\n\n".join((START_MARKER, details, END_MARKER))


def vendor_readme(estimates: tuple[SkillEstimate, ...]) -> str:
    body = collection_report(estimates, VENDOR_DIR, sources=upstream_sources())
    return "\n\n".join((VENDOR_HEADER, *body)) + "\n"


def replace_generated_block(content: str, block: str) -> str | None:
    starts = content.count(START_MARKER)
    ends = content.count(END_MARKER)
    if starts == ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise ValueError("expected one complete token estimate block")
    pattern = re.compile(
        f"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}", re.DOTALL
    )
    match = pattern.search(content)
    if match is None:
        raise ValueError("token estimate block markers are out of order")
    return f"{content[: match.start()]}{block}{content[match.end() :]}"


def insert_after_heading(content: str, block: str) -> str:
    heading = re.search(r"(?m)^# .+\n", content)
    if heading is None:
        return f"{block}\n\n{content.lstrip()}"
    return f"{content[: heading.end()]}\n{block}\n\n{content[heading.end() :].lstrip()}"


def skill_readme(estimate: SkillEstimate, block: str) -> str:
    path = estimate.directory / "README.md"
    if not path.exists() or path.is_symlink():
        raise ValueError(f"{path.relative_to(ROOT)} must be a regular README")
    content = path.read_text(encoding="utf-8")
    replaced = replace_generated_block(content, block)
    return replaced if replaced is not None else insert_after_heading(content, block)


def root_readme(block: str) -> str:
    content = (ROOT / "README.md").read_text(encoding="utf-8")
    replaced = replace_generated_block(content, block)
    if replaced is not None:
        return replaced

    anchor = "\n## Skills\n"
    if anchor not in content:
        raise ValueError("README.md has no Skills section")
    return content.replace(anchor, f"\n{block}{anchor}", 1)


def main() -> int:
    args = parse_args()
    estimates = collect_estimates()
    owned = tuple(estimate for estimate in estimates if not estimate.vendored)
    vendored = tuple(estimate for estimate in estimates if estimate.vendored)

    expected = {
        ROOT / "README.md": root_readme(root_block(estimates)),
        VENDOR_DIR / "README.md": vendor_readme(vendored),
    }
    expected.update(
        {
            estimate.directory / "README.md": skill_readme(
                estimate, skill_block(estimate)
            )
            for estimate in owned
        }
    )
    stale = [
        path
        for path, content in expected.items()
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]

    if not stale:
        print("Token estimates are current.")
        return 0
    if not args.fix:
        print("Token estimates are stale:", file=sys.stderr)
        for path in stale:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
        print("Run `mise run tokens --fix`.", file=sys.stderr)
        return 1

    for path in stale:
        path.write_text(expected[path], encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
