"""Tests for the version:check mise file task, run against throwaway git repos."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

TASK = Path(__file__).resolve().parents[1] / "mise" / "tasks" / "version" / "check"

ROOT_MANIFESTS = (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json")
NESTED_MANIFESTS = (
    "skills/.claude-plugin/plugin.json",
    "skills/.cursor-plugin/plugin.json",
)


class VersionCheckTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)
        self.git("init", "-q", "-b", "main")
        self.write(
            ".claude-plugin/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {"name": "root", "source": "./"},
                        {"name": "nested", "source": "./skills"},
                    ]
                }
            ),
        )
        for path in ROOT_MANIFESTS:
            self.write(
                path,
                manifest(
                    "root", "1.2.3", skills=["./skills/"], hooks="./hooks/hooks.json"
                ),
            )
        for path in NESTED_MANIFESTS:
            self.write(
                path,
                manifest(
                    "nested",
                    "0.1.0",
                    skills=["./nested"],
                    hooks="nested/hooks/hooks.json",
                ),
            )
        self.write("hooks/hooks.json", "{}\n")
        self.write("skills/top/SKILL.md", "top\n")
        self.write("skills/nested/SKILL.md", "nested\n")
        self.write("README.md", "not shipped\n")
        self.commit("base")
        self.git("update-ref", "refs/remotes/origin/main", "HEAD")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, path, text):
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)

    def commit(self, message):
        self.git("add", "-A")
        self.git(
            "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message
        )

    def run_task(self, fix=False, bump=None):
        env = {
            k: v
            for k, v in os.environ.items()
            if not k.startswith("usage_") and k != "BASE_REF"
        }
        if fix:
            env["usage_fix"] = "true"
        if bump:
            env["usage_bump"] = bump
        return subprocess.run(
            ["bash", str(TASK)], cwd=self.repo, env=env, capture_output=True, text=True
        )

    def versions(self, paths):
        return [json.loads((self.repo / p).read_text())["version"] for p in paths]

    def test_unchanged_content_passes(self):
        self.write("README.md", "edited, still not shipped\n")
        self.commit("docs")
        self.assertEqual(self.run_task().returncode, 0)

    def test_changed_content_without_bump_fails_naming_both_manifests(self):
        self.write("skills/top/SKILL.md", "changed\n")
        self.commit("change")
        result = self.run_task()
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "root (.claude-plugin/plugin.json, .cursor-plugin/plugin.json)",
            result.stderr,
        )
        self.assertIn("mise run version:check --fix", result.stderr)

    def test_fix_bumps_only_the_affected_plugin_and_then_passes(self):
        self.write("hooks/hooks.json", '{"changed": true}\n')
        self.commit("change")
        self.assertEqual(self.run_task(fix=True).returncode, 0)
        self.assertEqual(self.versions(ROOT_MANIFESTS), ["1.2.4", "1.2.4"])
        self.assertEqual(self.versions(NESTED_MANIFESTS), ["0.1.0", "0.1.0"])
        self.commit("bump")
        self.assertEqual(self.run_task().returncode, 0)

    def test_second_fix_is_a_no_op(self):
        self.write("skills/top/SKILL.md", "changed\n")
        self.run_task(fix=True)
        before = {
            p: (self.repo / p).read_text() for p in ROOT_MANIFESTS + NESTED_MANIFESTS
        }
        self.run_task(fix=True)
        after = {p: (self.repo / p).read_text() for p in before}
        self.assertEqual(after, before)

    def test_fix_keeps_manifest_formatting(self):
        self.write("skills/top/SKILL.md", "changed\n")
        original = (self.repo / ROOT_MANIFESTS[0]).read_text()
        self.run_task(fix=True)
        self.assertEqual(
            (self.repo / ROOT_MANIFESTS[0]).read_text(),
            original.replace("1.2.3", "1.2.4"),
        )

    def test_bump_minor_raises_an_earlier_patch_bump(self):
        self.write("skills/top/SKILL.md", "changed\n")
        self.run_task(fix=True)
        self.run_task(fix=True, bump="minor")
        self.assertEqual(self.versions(ROOT_MANIFESTS), ["1.3.0", "1.3.0"])

    def test_fix_aligns_split_manifests(self):
        self.write("skills/top/SKILL.md", "changed\n")
        self.write(
            ROOT_MANIFESTS[1],
            manifest("root", "1.2.9", skills=["./skills/"], hooks="./hooks/hooks.json"),
        )
        self.run_task(fix=True)
        self.assertEqual(self.versions(ROOT_MANIFESTS), ["1.2.9", "1.2.9"])

    def test_nested_plugin_change_bumps_both_plugins(self):
        self.write("skills/nested/SKILL.md", "changed\n")
        self.commit("change")
        self.run_task(fix=True)
        self.assertEqual(self.versions(ROOT_MANIFESTS), ["1.2.4", "1.2.4"])
        self.assertEqual(self.versions(NESTED_MANIFESTS), ["0.1.1", "0.1.1"])

    def test_fix_counts_uncommitted_changes(self):
        self.write("skills/top/SKILL.md", "changed, not committed\n")
        self.run_task(fix=True)
        self.assertEqual(self.versions(ROOT_MANIFESTS), ["1.2.4", "1.2.4"])

    def test_fix_counts_untracked_files(self):
        self.write("skills/nested/new.md", "untracked\n")
        self.run_task(fix=True)
        self.assertEqual(self.versions(NESTED_MANIFESTS), ["0.1.1", "0.1.1"])


def manifest(name, version, skills, hooks):
    return (
        json.dumps(
            {"name": name, "version": version, "skills": skills, "hooks": hooks},
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    unittest.main()
