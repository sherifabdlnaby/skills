"""Where the skills live, read from the plugin manifests: the only place that says so."""

from __future__ import annotations

import json
from pathlib import Path

MARKETPLACE = ".claude-plugin/marketplace.json"
MANIFEST = ".claude-plugin/plugin.json"


def plugins(root: Path) -> list[Path]:
    """The root folder of each plugin the marketplace lists."""
    marketplace = json.loads((root / MARKETPLACE).read_text(encoding="utf-8"))
    return [(root / plugin["source"]).resolve() for plugin in marketplace["plugins"]]


def skills(root: Path) -> list[Path]:
    """Each skill folder a plugin ships, once. A manifest's `skills` entry is a skill
    folder or a folder of skill folders."""
    found: set[Path] = set()
    for plugin in plugins(root):
        manifest = json.loads((plugin / MANIFEST).read_text(encoding="utf-8"))
        paths = manifest.get("skills", [])
        for path in [paths] if isinstance(paths, str) else paths:
            folder = (plugin / path).resolve()
            if (folder / "SKILL.md").is_file():
                found.add(folder)
            else:
                found.update(p.parent for p in folder.glob("*/SKILL.md"))
    return sorted(found)


def is_vendored(root: Path, skill: Path) -> bool:
    """True when a folder named `vendor` sits between the repo root and the skill.
    The linters' `**/vendor/**` exclude in .config/hk.pkl uses the same convention."""
    return "vendor" in skill.relative_to(root).parts[:-1]
