"""What the AI-disclosure guard lets through and what it blocks, one command line at a time."""

import os
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import gh_disclosure  # noqa: E402

ALLOW, MISSING, UNREADABLE = "allow", "missing", "unreadable"

DISCLOSURE = "_<sub>🤖 Agent Decided: Claude Code · Opus 5.5 (high)</sub>_"
BODY = "Looks good.\n<sub>&emsp;╰</sub> " + DISCLOSURE


def verdict(command, cwd):
    reason = gh_disclosure.deny_reason(textwrap.dedent(command).strip("\n"), cwd)
    if reason is None:
        return ALLOW
    return UNREADABLE if reason is gh_disclosure.REASON_UNREADABLE else MISSING


class Case(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cwd = tmp.name
        os.mkdir(os.path.join(self.cwd, "sub"))
        for name, text in (
            ("good.md", BODY),
            ("sub/good.md", BODY),
            ("bad.md", "no disclosure"),
        ):
            with open(os.path.join(self.cwd, name), "w", encoding="utf-8") as fh:
                fh.write(text)

    def assertVerdicts(self, cases):
        for expected, command in cases:
            with self.subTest(command=command):
                self.assertEqual(verdict(command, self.cwd), expected)


class BodyFiles(Case):
    def test_paths_resolve_against_the_command_directory(self):
        self.assertVerdicts(
            [
                (ALLOW, "gh pr comment 7 --body-file good.md"),
                (ALLOW, "gh pr comment 7 --body-file=good.md"),
                (ALLOW, f"gh pr comment 7 --body-file {self.cwd}/good.md"),
                (MISSING, "gh pr comment 7 --body-file bad.md"),
                (UNREADABLE, "gh pr comment 7 --body-file nope.md"),
            ]
        )

    def test_paths_follow_a_cd_on_the_line(self):
        self.assertVerdicts(
            [
                (ALLOW, f"cd {self.cwd}/sub && gh pr comment 7 --body-file good.md"),
                (ALLOW, "cd sub; gh pr comment 7 --body-file ./good.md"),
                (ALLOW, "cd sub && cd .. && gh pr comment 7 --body-file sub/good.md"),
                (UNREADABLE, "cd $DIR && gh pr comment 7 --body-file good.md"),
                (UNREADABLE, "cd - && gh pr comment 7 --body-file good.md"),
                (ALLOW, f"cd $DIR && gh pr comment 7 --body-file {self.cwd}/good.md"),
            ]
        )

    def test_files_written_earlier_on_the_line(self):
        self.assertVerdicts(
            [
                (
                    ALLOW,
                    f"""
                    cat > new.md <<'EOF'
                    {BODY}
                    EOF
                    gh pr comment 7 --body-file new.md
                    """,
                ),
                (
                    ALLOW,
                    f"""
                    cat <<'EOF' > {self.cwd}/new.md && gh pr comment 7 --body-file new.md
                    {BODY}
                    EOF
                    """,
                ),
                (
                    ALLOW,
                    f"""
                    tee new.md >/dev/null <<'EOF'
                    {BODY}
                    EOF
                    gh pr comment 7 --body-file new.md
                    """,
                ),
                # A disclosure on disk must not stand in for what the line writes over it.
                (
                    MISSING,
                    """
                    cat > good.md <<'EOF'
                    no disclosure
                    EOF
                    gh pr comment 7 --body-file good.md
                    """,
                ),
                (
                    UNREADABLE,
                    """
                    cat >> good.md <<'EOF'
                    more
                    EOF
                    gh pr comment 7 --body-file good.md
                    """,
                ),
                (
                    UNREADABLE,
                    "printf 'hi' > good.md && gh pr comment 7 --body-file good.md",
                ),
                (
                    UNREADABLE,
                    "gh api user > good.md; gh pr comment 7 --body-file good.md",
                ),
                (
                    UNREADABLE,
                    "echo hi | tee -a good.md && gh pr comment 7 --body-file good.md",
                ),
                (
                    ALLOW,
                    "echo hi 2>&1 >/dev/null && gh pr comment 7 --body-file good.md",
                ),
                (ALLOW, "gh pr comment 7 --body-file good.md > good.md"),
            ]
        )


class Heredocs(Case):
    def test_a_post_after_a_heredoc_is_still_checked(self):
        self.assertVerdicts(
            [
                (
                    MISSING,
                    """
                    cat > notes.txt <<'EOF'
                    scratch
                    EOF
                    gh pr comment 7 --body 'no disclosure'
                    """,
                ),
            ]
        )

    def test_inline_heredoc_bodies(self):
        self.assertVerdicts(
            [
                (
                    ALLOW,
                    f"""
                    gh pr comment 7 --body "$(cat <<'EOF'
                    Has "quotes" and a $dollar inside.

                    ---
                    {DISCLOSURE}
                    EOF
                    )"
                    """,
                ),
                (
                    ALLOW,
                    f"""
                    gh pr comment 7 --body-file - <<'EOF'
                    {BODY}
                    EOF
                    """,
                ),
                (
                    MISSING,
                    """
                    gh pr comment 7 --body-file - <<'EOF'
                    no disclosure
                    EOF
                    """,
                ),
            ]
        )


if __name__ == "__main__":
    unittest.main()


class DisclosureLine(Case):
    """Any placement the skill teaches passes; a body without a tier line does not."""

    def assertBodies(self, cases):
        for expected, body in cases:
            with self.subTest(body=body):
                path = os.path.join(self.cwd, "body.md")
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(body)
                self.assertEqual(
                    verdict("gh pr comment 7 --body-file body.md", self.cwd), expected
                )

    def test_placements(self):
        chip = f'<table align="right"><tr><td>\n\n{DISCLOSURE}\n\n</td></tr></table>\n\nSummary.'
        self.assertBodies(
            [
                (ALLOW, chip),
                (ALLOW, f"Fixed.\n<sub>&emsp;╰</sub> {DISCLOSURE}"),
                (ALLOW, f"Fixed.\n\n---\n\n{DISCLOSURE}"),
            ]
        )

    def test_older_wording_still_passes(self):
        self.assertBodies(
            [
                (
                    ALLOW,
                    "Fixed.\n\n_<sub>📋 Human Planned: Posted by Claude (Opus 5.5) on behalf of @octocat.</sub>_",
                ),
                (
                    ALLOW,
                    "_<sub>🤝 Human Guided PR: Created with Cursor (Composer) on behalf of @octocat.</sub>_\n\n---\n\nBody.",
                ),
            ]
        )

    def test_a_tier_emoji_alone_is_not_a_disclosure(self):
        self.assertBodies(
            [
                (MISSING, "Fixed 🤖"),
                (MISSING, "_<sub>Claude Code · Opus 5.5</sub>_"),
                (MISSING, "_<sub>🤖 Agent Decided\nClaude Code</sub>_"),
            ]
        )
