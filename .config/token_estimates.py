#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import tiktoken

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
README_SOURCES = ROOT / ".config" / "skill-readmes"
START_MARKER = "<!-- token-estimates:start -->"
END_MARKER = "<!-- token-estimates:end -->"
ENCODING_NAME = "o200k_base"


@dataclass(frozen=True)
class FileEstimate:
    path: Path
    tokens: int


@dataclass(frozen=True)
class SkillEstimate:
    directory: Path
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
    return parser.parse_args()


def token_count(path: Path, encoding: tiktoken.Encoding) -> int | None:
    data = path.read_bytes()
    if b"\0" in data:
        return None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return len(encoding.encode(text, disallowed_special=()))


def collect_estimates() -> tuple[SkillEstimate, ...]:
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    skill_directories = {path.parent for path in SKILLS_DIR.rglob("SKILL.md")}
    source_directories = {
        SKILLS_DIR / source.relative_to(README_SOURCES).with_suffix("")
        for source in README_SOURCES.rglob("*.md")
    }
    orphan_sources = source_directories - skill_directories
    if orphan_sources:
        paths = ", ".join(
            str(path.relative_to(ROOT)) for path in sorted(orphan_sources)
        )
        raise ValueError(f"README sources have no matching skill: {paths}")
    estimates: list[SkillEstimate] = []

    for directory in sorted(skill_directories):
        files: list[FileEstimate] = []
        for path in sorted(directory.rglob("*")):
            if (
                not path.is_file()
                or path.is_symlink()
                or path == directory / "README.md"
            ):
                continue
            owner = next(
                (parent for parent in path.parents if parent in skill_directories), None
            )
            if owner != directory:
                continue
            tokens = token_count(path, encoding)
            if tokens is not None:
                files.append(FileEstimate(path, tokens))
        estimates.append(SkillEstimate(directory, tuple(files)))

    return tuple(estimates)


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


def report_intro(
    skill_tokens: int, total_tokens: int, *, all_skills: bool = False
) -> str:
    skill_label = "All SKILL.md" if all_skills else "SKILL.md"
    total_label = "All files" if all_skills else "Total"
    return "\n".join(
        (
            "<p>",
            badge(skill_label, skill_tokens, "2f80ed"),
            badge(total_label, total_tokens, "2ea44f"),
            "</p>",
            "",
            f"Token estimates use tiktoken's `{ENCODING_NAME}` encoding. `SKILL.md` is the entry prompt; total includes every",
            "UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.",
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


def root_block(estimates: tuple[SkillEstimate, ...]) -> str:
    skill_total = sum(estimate.skill_tokens for estimate in estimates)
    package_total = sum(estimate.total_tokens for estimate in estimates)
    summary_rows: list[tuple[str, ...]] = []
    file_rows: list[tuple[str, ...]] = []

    for estimate in estimates:
        skill_path = estimate.directory.relative_to(ROOT).as_posix()
        summary_rows.append(
            (
                f"[`{skill_path.removeprefix('skills/')}`]({quote(skill_path)}/)",
                f"{estimate.skill_tokens:,}",
                f"{estimate.total_tokens:,}",
            )
        )
        for file in estimate.files:
            file_path = file.path.relative_to(ROOT).as_posix()
            file_rows.append(
                (
                    f"`{skill_path.removeprefix('skills/')}`",
                    f"[`{file.path.relative_to(estimate.directory).as_posix()}`]({quote(file_path)})",
                    f"{file.tokens:,}",
                )
            )

    summary = markdown_table(("Skill", "SKILL.md", "Total"), summary_rows, {1, 2})
    files = markdown_table(("Skill", "File", "Tokens"), file_rows, {2})
    details = "\n\n".join(
        (
            "<details>",
            "<summary><strong>Token estimates</strong></summary>",
            report_intro(skill_total, package_total, all_skills=True),
            summary,
            "### Files",
            files,
            "</details>",
        )
    )
    return "\n\n".join((START_MARKER, details, END_MARKER))


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


def skill_readme(estimate: SkillEstimate, block: str) -> str:
    path = estimate.directory / "README.md"
    source = README_SOURCES / estimate.directory.relative_to(SKILLS_DIR).with_suffix(
        ".md"
    )
    if source.exists():
        content = source.read_text(encoding="utf-8")
        source_skill = (
            f"../../../{estimate.directory.relative_to(ROOT).as_posix()}/SKILL.md"
        )
        content = content.replace(f"]({source_skill})", "](SKILL.md)")
    else:
        if not path.exists() or path.is_symlink():
            raise ValueError(
                f"{path.relative_to(ROOT)} must be a regular human-facing README"
            )
        content = path.read_text(encoding="utf-8")

    replaced = replace_generated_block(content, block)
    if replaced is not None:
        return replaced

    heading = re.search(r"(?m)^# .+\n", content)
    if heading is None:
        return f"{block}\n\n{content.lstrip()}"
    return f"{content[: heading.end()]}\n{block}\n\n{content[heading.end() :].lstrip()}"


def root_readme(block: str) -> str:
    path = ROOT / "README.md"
    content = path.read_text(encoding="utf-8")
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
    expected = {ROOT / "README.md": root_readme(root_block(estimates))}
    expected.update(
        {
            estimate.directory / "README.md": skill_readme(
                estimate, skill_block(estimate)
            )
            for estimate in estimates
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
