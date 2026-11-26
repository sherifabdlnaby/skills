"""Which PR bodies the PR-structure guard lets through, one command line at a time."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import pr_structure  # noqa: E402

VISUALS = "<!-- pr:visuals -->"
ALL = " ".join(f"<!-- pr:{name} -->" for name in pr_structure.REQUIRED)


class MissingParts(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cwd = tmp.name
        for name, text in (
            ("full.md", ALL),
            ("partial.md", "<!-- pr:summary -->"),
        ):
            with open(os.path.join(self.cwd, name), "w", encoding="utf-8") as fh:
                fh.write(text)

    def missing(self, command):
        return pr_structure.missing_parts(command, self.cwd)

    def test_complete_bodies_pass(self):
        no_visuals = ALL.replace(VISUALS, "<!-- pr:no-visuals: text-only change -->")
        for command in (
            "gh pr create --title t --body-file full.md",
            f"gh pr edit 3 --body '{no_visuals}'",
            "gh pr create --title t --body '<!-- pr:skeleton-off: one-liner -->'",
            "gh pr create --title t --body-file - <<'EOF'\n" + ALL + "\nEOF",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.missing(command), [])

    def test_missing_parts_are_named_in_body_order(self):
        missing = self.missing("gh pr create --title t --body-file partial.md")
        self.assertEqual(missing, list(pr_structure.REQUIRED[1:]))

    def test_visuals_opt_out_needs_a_reason(self):
        for opt_out in ("<!-- pr:no-visuals: -->", "<!-- pr:no-visuals -->"):
            with self.subTest(opt_out=opt_out):
                body = ALL.replace(VISUALS, opt_out)
                self.assertEqual(
                    self.missing(f"gh pr edit 3 --body '{body}'"), ["visuals"]
                )

    def test_body_follows_a_cd(self):
        os.mkdir(os.path.join(self.cwd, "sub"))
        os.rename(
            os.path.join(self.cwd, "full.md"), os.path.join(self.cwd, "sub", "full.md")
        )
        self.assertEqual(
            self.missing("cd sub && gh pr create --title t --body-file full.md"), []
        )

    def test_unreadable_body_is_its_own_verdict(self):
        for command in (
            "gh pr create --title t --body-file nowhere.md",
            'gh pr create --title t --body "$BODY"',
            "gh pr create --fill",
        ):
            with self.subTest(command=command):
                self.assertIs(self.missing(command), pr_structure.UNREADABLE)

    def test_other_posts_are_not_checked(self):
        for command in (
            "gh pr comment 3 --body 'thanks'",
            "gh issue create --title t --body 'bug'",
            "gh pr view 3",
            "git push",
        ):
            with self.subTest(command=command):
                self.assertEqual(self.missing(command), [])


class SkeletonMatchesHook(unittest.TestCase):
    def test_skeleton_markers_are_the_required_parts_in_order(self):
        page = os.path.join(
            os.path.dirname(__file__),
            *("..", "..", "skills", "git", "references", "pr-body.md"),
        )
        with open(page, encoding="utf-8") as fh:
            text = fh.read()
        skeleton = (
            text.split("## Skeleton", 1)[1]
            .split("```markdown", 1)[1]
            .split("```\n", 1)[0]
        )
        self.assertEqual(
            tuple(pr_structure.MARKER_RE.findall(skeleton)), pr_structure.REQUIRED
        )


if __name__ == "__main__":
    unittest.main()
