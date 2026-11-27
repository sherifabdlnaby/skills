import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skill_structure.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def skill(root: Path, rel: str, up: str) -> None:
    name = rel.rsplit("/", 1)[-1]
    write(
        root / rel / "SKILL.md",
        f"---\nname: {name}\n---\nSee [guide](references/guide.md).\n",
    )
    write(root / rel / "references/guide.md", "# Guide\n")
    write(
        root / rel / "README.md", f"[All skills]({up})\n\nSee [`SKILL.md`](SKILL.md).\n"
    )


def marketplace(names: list[str]) -> str:
    return json.dumps({"plugins": [{"name": n, "source": "./"} for n in names]})


class SkillStructureTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        skill(self.root, "skills/alpha", "../")
        skill(self.root, "skills/variants/beta", "../../README.md")
        write(
            self.root / "README.md",
            "[alpha](skills/alpha/) | [beta](skills/variants/beta/)\n",
        )
        for path in (".claude-plugin", ".cursor-plugin", ".agents/plugins"):
            write(self.root / path / "marketplace.json", marketplace(["skills"]))
        write(
            self.root / ".cursor-plugin/plugin.json", json.dumps({"skills": ["skills"]})
        )

    def run_check(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, SCRIPT, "--root", self.root],
            capture_output=True,
            text=True,
        )

    def assert_fails(self, path: str, fix: str) -> None:
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(f"{path}: ", result.stdout)
        self.assertIn(f"Fix: {fix}", result.stdout)

    def test_well_formed_tree_passes(self) -> None:
        result = self.run_check()
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_vendored_skill_is_ignored(self) -> None:
        write(self.root / "skills/vendor/gamma/SKILL.md", "---\nname: other\n---\n")
        write(self.root / "skills/vendor/gamma/references/orphan.md", "# Orphan\n")
        self.assertEqual(self.run_check().returncode, 0)

    def test_skill_without_readme_fails(self) -> None:
        (self.root / "skills/alpha/README.md").unlink()
        self.assert_fails("skills/alpha/README.md", "add a README.md")

    def test_readme_without_skill_md_link_fails(self) -> None:
        write(self.root / "skills/alpha/README.md", "[All skills](../)\n")
        self.assert_fails(
            "skills/alpha/README.md", "add a link to [`SKILL.md`](SKILL.md)"
        )

    def test_readme_without_up_link_fails(self) -> None:
        write(self.root / "skills/variants/beta/README.md", "[`SKILL.md`](SKILL.md)\n")
        self.assert_fails(
            "skills/variants/beta/README.md", "add a link to [All skills](../../)"
        )

    def test_skill_missing_from_root_readme_fails(self) -> None:
        write(self.root / "README.md", "[alpha](skills/alpha/)\n")
        self.assert_fails("README.md", "add [beta](skills/variants/beta/)")

    def test_name_unlike_folder_fails(self) -> None:
        write(
            self.root / "skills/alpha/SKILL.md",
            "---\nname: alfa\n---\n[g](references/guide.md)\n",
        )
        self.assert_fails("skills/alpha/SKILL.md", "set `name: alpha`")

    def test_orphan_reference_fails(self) -> None:
        write(self.root / "skills/alpha/references/lost.md", "# Lost\n")
        self.assert_fails("skills/alpha/references/lost.md", "link it from SKILL.md")

    def test_reference_reached_through_another_page_passes(self) -> None:
        write(self.root / "skills/alpha/references/guide.md", "[deep](deep/more.md)\n")
        write(self.root / "skills/alpha/references/deep/more.md", "# More\n")
        self.assertEqual(self.run_check().returncode, 0)

    def test_marketplaces_that_disagree_fail(self) -> None:
        write(
            self.root / ".agents/plugins/marketplace.json",
            marketplace(["skills", "extra"]),
        )
        self.assert_fails(".agents/plugins/marketplace.json", "list the same plugins")

    def test_cursor_skills_not_a_list_fails(self) -> None:
        write(
            self.root / ".cursor-plugin/plugin.json", json.dumps({"skills": "skills"})
        )
        self.assert_fails(".cursor-plugin/plugin.json", 'write `"skills": [')


if __name__ == "__main__":
    unittest.main()
