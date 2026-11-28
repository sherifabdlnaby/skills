#!/usr/bin/env python3
"""Check the skill layout invariants AGENTS.md states; each violation names its fix."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import layout

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
# Claude Code, Cursor and Codex each read their marketplace from a fixed path.
MARKETPLACES = (
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)
LINK = re.compile(r"\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
NAME = re.compile(r"^name:\s*['\"]?(.*?)['\"]?\s*$", re.MULTILINE)

Violation = tuple[Path, str, str]  # path, what is wrong, fix


def own_skills(root: Path) -> list[Path]:
    return [s for s in layout.skills(root) if not layout.is_vendored(root, s)]


def index_folder(root: Path, skill: Path) -> Path:
    """The nearest folder above the skill that holds a README.md: the one its README links up to."""
    for folder in skill.parents:
        if folder == root or (folder / "README.md").is_file():
            return folder
    raise ValueError(f"{skill} is outside {root}")


def links(markdown: Path) -> Iterator[Path]:
    """Local targets of the inline Markdown links in a file, resolved against it."""
    for target in LINK.findall(markdown.read_text(encoding="utf-8")):
        target = target.split("#", 1)[0]
        if target and not re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
            yield (markdown.parent / target).resolve()


def readme_present(root: Path) -> Iterator[Violation]:
    for skill in own_skills(root):
        if not (skill / "README.md").is_file():
            up = index_folder(root, skill).relative_to(root).as_posix()
            yield (
                skill / "README.md",
                "missing",
                f"add a README.md for humans that links to SKILL.md and up to {up}/",
            )


def readme_links(root: Path) -> Iterator[Violation]:
    for skill in own_skills(root):
        readme = skill / "README.md"
        if not readme.is_file():
            continue
        targets = set(links(readme))
        if (skill / "SKILL.md").resolve() not in targets:
            yield readme, "no link to SKILL.md", "add a link to [`SKILL.md`](SKILL.md)"
        index = index_folder(root, skill)
        if not targets & {index, index / "README.md"}:
            up = Path(*[".."] * len(skill.relative_to(index).parts))
            yield (
                readme,
                f"no link up to {index.relative_to(root).as_posix()}/",
                f"add a link to [All skills]({up.as_posix()}/)",
            )


def root_readme_lists(root: Path) -> Iterator[Violation]:
    readme = root / "README.md"
    targets = set(links(readme))
    for skill in own_skills(root):
        if skill.resolve() not in targets:
            rel = skill.relative_to(root).as_posix()
            yield (
                readme,
                f"no link to {rel}/",
                f"add [{skill.name}]({rel}/) to the skill list",
            )


def name_matches_folder(root: Path) -> Iterator[Violation]:
    for skill in own_skills(root):
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        front = text.split("---", 2)[1] if text.startswith("---") else ""
        match = NAME.search(front)
        name = match.group(1) if match else None
        if name != skill.name:
            yield (
                skill / "SKILL.md",
                f"frontmatter name is {name!r}, folder is {skill.name!r}",
                f"set `name: {skill.name}` or rename the folder",
            )


def references_reachable(root: Path) -> Iterator[Violation]:
    for skill in own_skills(root):
        pages = {p.resolve() for p in (skill / "references").rglob("*.md")}
        if not pages:
            continue
        seen: set[Path] = set()
        queue = [(skill / "SKILL.md").resolve()]
        while queue:
            page = queue.pop()
            if page in seen or not page.is_file() or page.suffix != ".md":
                continue
            seen.add(page)
            queue.extend(t for t in links(page) if t.is_relative_to(skill.resolve()))
        for orphan in sorted(pages - seen):
            yield (
                orphan,
                "not reachable by links from SKILL.md",
                "link it from SKILL.md or a page SKILL.md reaches, or delete it",
            )


def marketplaces_agree(root: Path) -> Iterator[Violation]:
    listed = {
        path: [
            p["name"]
            for p in json.loads((root / path).read_text(encoding="utf-8"))["plugins"]
        ]
        for path in MARKETPLACES
    }
    reference, names = next(iter(listed.items()))
    for path, other in listed.items():
        if set(other) != set(names):
            yield (
                root / path,
                f"lists {sorted(other)}, {reference} lists {sorted(names)}",
                "list the same plugins in every marketplace file",
            )
    cursor = json.loads(
        (root / ".cursor-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    for plugin in cursor["plugins"]:
        manifest = root / plugin["source"] / ".cursor-plugin/plugin.json"
        if not isinstance(
            json.loads(manifest.read_text(encoding="utf-8")).get("skills"), list
        ):
            yield (
                manifest,
                "`skills` is not a list",
                'write `"skills": ["<path>", ...]` (Cursor needs a list)',
            )


RULES: tuple[Callable[[Path], Iterator[Violation]], ...] = (
    readme_present,
    readme_links,
    root_readme_lists,
    name_matches_folder,
    references_reachable,
    marketplaces_agree,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="tree to check (default: this repository)",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    violations = [v for rule in RULES for v in rule(root)]
    for path, what, fix in violations:
        print(f"{path.relative_to(root).as_posix()}: {what}. Fix: {fix}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
