"""What the guard lets through and what it blocks, one command line at a time."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "skills",
        "ai-disclosure",
        "hooks",
        "guard",
    ),
)

import disclosure  # noqa: E402

ALLOW, MISSING, UNREADABLE = "allow", "missing", "unreadable"

DISCLOSURE = "_<sub>🤖 Agent Decided: Claude Code · Opus 5.5 (high)</sub>_"
BODY = "Looks good.\n<sub>&emsp;╰</sub> " + DISCLOSURE


def verdict(command: str, cwd: str = None) -> str:
    denial = disclosure.check(command, cwd)
    return ALLOW if denial is None else denial.kind


class Case(unittest.TestCase):
    def assertVerdicts(self, cases, cwd=None):
        for expected, command in cases:
            with self.subTest(command=command):
                self.assertEqual(
                    verdict(textwrap.dedent(command).strip("\n"), cwd), expected
                )


class DisclosureShape(Case):
    def test_any_placement_the_skill_teaches(self):
        chip = f'<table align="right"><tr><td>\n\n{DISCLOSURE}\n\n</td></tr></table>\n\nSummary'
        self.assertVerdicts(
            [
                (ALLOW, f"gh pr comment 1 --body '{BODY}'"),
                (ALLOW, f"gh pr create --title t --body '{chip}'"),
                (ALLOW, f"gh pr comment 1 --body 'Looks good.\n\n---\n\n{DISCLOSURE}'"),
            ]
        )

    def test_older_wordings_still_pass(self):
        self.assertVerdicts(
            [
                (
                    ALLOW,
                    "gh issue comment 3 --body '_<sub>🤝 Human Guided: Posted by Cursor (Opus 5.5) on behalf of @a-b.</sub>_'",
                ),
                (
                    ALLOW,
                    "gh pr create --title t --body '_<sub>📋 Human Planned PR: Created with Codex (GPT 5.5).</sub>_'",
                ),
            ]
        )

    def test_a_line_without_a_tier_is_not_a_disclosure(self):
        self.assertVerdicts(
            [
                (MISSING, "gh pr comment 1 --body 'Looks good.'"),
                (MISSING, "gh pr comment 1 --body 'Fixed 🤖'"),
                (
                    MISSING,
                    "gh pr comment 1 --body '_<sub>Claude Code · Opus 5.5</sub>_'",
                ),
                (
                    MISSING,
                    "gh pr comment 1 --body '_<sub>🤖 Agent Decided\nClaude Code</sub>_'",
                ),
                (MISSING, "gh pr comment 1 --body ''"),
            ]
        )


class GhCli(Case):
    def test_posting_actions(self):
        self.assertVerdicts(
            [
                (MISSING, "gh pr create --title t --body x"),
                (MISSING, "gh pr comment 7 --body x"),
                (MISSING, "gh pr edit 7 --body x"),
                (MISSING, "gh pr review 7 --comment --body x"),
                (MISSING, "gh issue create --title t --body x"),
                (MISSING, "gh issue comment 7 --body x"),
                (MISSING, "gh issue edit 7 --body x"),
                (MISSING, "gh pr comment 7 -b x"),
                (MISSING, "gh pr comment 7 --body=x"),
                (MISSING, "/opt/homebrew/bin/gh pr comment 7 --body x"),
                (MISSING, "GH_REPO=o/r gh pr comment 7 --body x"),
                (MISSING, "env -i HOME=/tmp gh pr comment 7 --body x"),
                (MISSING, "timeout 60 gh pr comment 7 --body x"),
                (MISSING, "command gh pr comment 7 --body x"),
                (MISSING, "gh pr -R o/r comment 7 --body x"),
                (MISSING, "gh issue --repo o/r comment 7 --body x"),
                (MISSING, "gh pr --repo=o/r comment 7 --body x"),
                (MISSING, "gh pr -Ro/r comment 7 --body x"),
            ]
        )

    def test_no_body_to_check(self):
        self.assertVerdicts(
            [
                (ALLOW, "gh pr view 7 --comments"),
                (ALLOW, "gh pr -R o/r view 7"),
                (ALLOW, "gh pr edit 7 --add-label bug --title 'New title'"),
                (ALLOW, "gh pr review 7 --approve"),
                (ALLOW, "gh issue edit 7 --add-assignee @me"),
                (ALLOW, "gh pr merge 7 --squash --body 'commit message, not a post'"),
                (ALLOW, "gh release create v1 --notes 'notes'"),
                (ALLOW, "gh pr comment 7 --body x --dry-run"),
                (ALLOW, "gh pr comment 7 --delete-last --yes"),
                (ALLOW, "gh issue create --web"),
                (ALLOW, "echo gh pr create"),
                (ALLOW, "grep -rn 'gh pr create --body' ."),
            ]
        )

    def test_body_gh_would_get_elsewhere(self):
        self.assertVerdicts(
            [
                (UNREADABLE, "gh pr create --title t"),  # gh prompts for it
                (UNREADABLE, "gh pr comment 7"),
                (UNREADABLE, "gh pr create --fill"),
                (
                    UNREADABLE,
                    "gh pr create --template .github/pull_request_template.md",
                ),
                (UNREADABLE, "gh issue comment 7 --editor"),
                (UNREADABLE, 'gh pr comment 7 --body "$BODY"'),
                (UNREADABLE, 'gh pr comment 7 --body "$(cat notes.md)"'),
                (UNREADABLE, "gh pr comment 7 --body `cat notes.md`"),
                (UNREADABLE, "cat notes.md | gh pr comment 7 --body-file -"),
                (UNREADABLE, "gh pr comment 7 --body-file /nonexistent/body.md"),
            ]
        )

    def test_visible_disclosure_wins_over_an_unseen_part(self):
        self.assertVerdicts(
            [(ALLOW, f'gh pr comment 7 --body "$(cat notes.md)\n\n---\n{DISCLOSURE}"')]
        )


class BodyPassing(Case):
    def test_heredocs(self):
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
                    MISSING,
                    """
                    gh pr comment 7 --body "$(cat <<'EOF'
                    Has "quotes" but no disclosure.
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
                    gh pr comment 7 --body-file - <<EOF
                    no disclosure
                    EOF
                    """,
                ),
            ]
        )

    def test_body_files_resolve_against_the_session_directory(self):
        with tempfile.TemporaryDirectory() as cwd:
            with open(os.path.join(cwd, "good.md"), "w", encoding="utf-8") as fh:
                fh.write(BODY)
            with open(os.path.join(cwd, "bad.md"), "w", encoding="utf-8") as fh:
                fh.write("no disclosure")
            self.assertVerdicts(
                [
                    (ALLOW, "gh pr create --title t --body-file good.md"),
                    (ALLOW, "gh pr create --title t -F good.md"),
                    (ALLOW, "gh pr create --title t --body-file=good.md"),
                    (ALLOW, f"gh pr create --title t --body-file {cwd}/good.md"),
                    (MISSING, "gh pr create --title t --body-file bad.md"),
                ],
                cwd=cwd,
            )

    def test_body_files_follow_a_cd_on_the_line(self):
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, "sub"))
            with open(
                os.path.join(root, "sub", "good.md"), "w", encoding="utf-8"
            ) as fh:
                fh.write(BODY)
            self.assertVerdicts(
                [
                    (ALLOW, f"cd {root}/sub && gh pr comment 7 --body-file good.md"),
                    (ALLOW, "cd sub; gh pr comment 7 --body-file ./good.md"),
                    (
                        ALLOW,
                        "cd sub && cd .. && gh pr comment 7 --body-file sub/good.md",
                    ),
                    (UNREADABLE, "gh pr comment 7 --body-file good.md"),
                    (UNREADABLE, "cd $DIR && gh pr comment 7 --body-file good.md"),
                    (UNREADABLE, "cd - && gh pr comment 7 --body-file good.md"),
                    (
                        ALLOW,
                        f"cd $DIR && gh pr comment 7 --body-file {root}/sub/good.md",
                    ),
                ],
                cwd=root,
            )

    def test_body_files_written_earlier_on_the_line(self):
        with tempfile.TemporaryDirectory() as cwd:
            # A disclosure on disk must not stand in for what the line writes over it.
            with open(os.path.join(cwd, "stale.md"), "w", encoding="utf-8") as fh:
                fh.write(BODY)
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
                        cat <<'EOF' > {cwd}/new.md && gh pr comment 7 --body-file new.md
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
                        gh api repos/o/r/issues/7/comments -F body=@new.md
                        """,
                    ),
                    (
                        MISSING,
                        """
                        cat > stale.md <<'EOF'
                        no disclosure
                        EOF
                        gh pr comment 7 --body-file stale.md
                        """,
                    ),
                    (
                        UNREADABLE,
                        """
                        cat >> stale.md <<'EOF'
                        more
                        EOF
                        gh pr comment 7 --body-file stale.md
                        """,
                    ),
                    (
                        UNREADABLE,
                        "printf 'hi' > stale.md && gh pr comment 7 --body-file stale.md",
                    ),
                    (
                        UNREADABLE,
                        "gh api user > stale.md; gh pr comment 7 --body-file stale.md",
                    ),
                    (
                        UNREADABLE,
                        "echo hi | tee -a stale.md && gh pr comment 7 --body-file stale.md",
                    ),
                    (
                        ALLOW,
                        "echo hi 2>&1 >/dev/null && gh pr comment 7 --body-file stale.md",
                    ),
                    (ALLOW, "gh pr comment 7 --body-file stale.md > stale.md"),
                ],
                cwd=cwd,
            )


class CommandLines(Case):
    def test_every_post_on_the_line_is_checked(self):
        self.assertVerdicts(
            [
                (
                    ALLOW,
                    f"gh pr comment 1 --body '{BODY}' && gh pr comment 2 --body '{BODY}'",
                ),
                (
                    MISSING,
                    f"gh pr comment 1 --body '{BODY}' && gh pr comment 2 --body x",
                ),
                (MISSING, f"gh pr comment 1 --body x; gh pr comment 2 --body '{BODY}'"),
                (MISSING, f"gh pr comment 1 --body x\ngh pr comment 2 --body '{BODY}'"),
                (MISSING, f"gh pr comment 1 --body '{BODY}'\ngh pr comment 2 --body x"),
                (MISSING, "(cd repo && gh pr comment 1 --body x)"),
                (MISSING, "gh pr comment 1 \\\n  --body x"),
            ]
        )

    def test_shell_comments_are_not_commands(self):
        self.assertVerdicts(
            [
                (ALLOW, "ls  # gh pr create later"),
                (ALLOW, "# gh pr comment 1 --body x\nls"),
                (ALLOW, f"gh pr comment 1 --body 'see #12 {BODY}'"),
                (
                    ALLOW,
                    f"gh api repos/o/r/issues/1/comments -f body=issue#12 -f 'x={BODY}' -X GET",
                ),
            ]
        )

    def test_malformed_quoting_is_left_to_the_shell(self):
        self.assertVerdicts([(ALLOW, "gh pr comment 1 --body 'unterminated")])


class OptOut(Case):
    def test_prefix_opts_out_one_command(self):
        self.assertVerdicts(
            [
                (ALLOW, "AI_DISCLOSURE=off gh pr comment 1 --body x"),
                (ALLOW, "env AI_DISCLOSURE=off gh pr comment 1 --body x"),
                (MISSING, "AI_DISCLOSURE=on gh pr comment 1 --body x"),
                (
                    MISSING,
                    "AI_DISCLOSURE=off gh pr comment 1 --body x && gh pr comment 2 --body x",
                ),
                (MISSING, "export AI_DISCLOSURE=off; gh pr comment 2 --body x"),
            ]
        )


class GhApiRest(Case):
    def test_content_writes(self):
        self.assertVerdicts(
            [
                (MISSING, "gh api repos/o/r/issues/7/comments -f body=hi"),
                (
                    MISSING,
                    "gh api repos/{owner}/{repo}/pulls/7/comments -f body=hi -f commit_id=abc -f path=a.py -F line=3",
                ),
                (MISSING, "gh api repos/o/r/pulls/7/comments/99/replies -f body=hi"),
                (
                    MISSING,
                    "gh api -X PATCH repos/o/r/issues/comments/99 -f body=edited",
                ),
                (
                    MISSING,
                    "gh api --method=POST /repos/o/r/pulls/7/reviews -f event=COMMENT -f body=hi",
                ),
                (
                    MISSING,
                    "gh api repos/o/r/pulls/7/reviews -f body="
                    + json.dumps(BODY)
                    + " -f 'comments[][body]=inline'",
                ),
                (ALLOW, f"gh api repos/o/r/issues/7/comments -f body='{BODY}'"),
                (
                    ALLOW,
                    f"gh api repos/o/r/issues/7/comments -f body='{BODY}' --jq .html_url",
                ),
            ]
        )

    def test_not_a_post(self):
        self.assertVerdicts(
            [
                (ALLOW, "gh api user --jq .login"),
                (ALLOW, "gh api repos/o/r/issues/7/comments --paginate"),
                (ALLOW, "gh api repos/o/r/issues/7/comments -X GET -f per_page=100"),
                (ALLOW, "gh api -X DELETE repos/o/r/issues/comments/99"),
                (ALLOW, "gh api repos/o/r/issues/7/labels -f 'labels[]=bug'"),
                (ALLOW, "gh api -X PATCH repos/o/r/issues/7 -f state=closed"),
                (ALLOW, "gh api repos/o/r/releases -f tag_name=v1 -f body=notes"),
                (
                    ALLOW,
                    "gh api repos/o/r/statuses/abc -f state=success -f description=ok",
                ),
            ]
        )

    def test_body_from_files(self):
        with tempfile.TemporaryDirectory() as cwd:
            with open(os.path.join(cwd, "reply.md"), "w", encoding="utf-8") as fh:
                fh.write(BODY)
            with open(os.path.join(cwd, "review.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "event": "COMMENT",
                        "body": BODY,
                        "comments": [{"path": "a", "body": "no disclosure"}],
                    },
                    fh,
                )
            with open(os.path.join(cwd, "ok.json"), "w", encoding="utf-8") as fh:
                json.dump({"body": BODY}, fh)
            self.assertVerdicts(
                [
                    (ALLOW, "gh api repos/o/r/issues/7/comments -F body=@reply.md"),
                    (ALLOW, "gh api repos/o/r/issues/7/comments --input ok.json"),
                    (MISSING, "gh api repos/o/r/pulls/7/reviews --input review.json"),
                    (
                        UNREADABLE,
                        "gh api repos/o/r/issues/7/comments -F body=@missing.md",
                    ),
                    (
                        UNREADABLE,
                        "gh api repos/o/r/issues/7/comments --input missing.json",
                    ),
                    (
                        UNREADABLE,
                        "jq -n '{body: 1}' | gh api repos/o/r/issues/7/comments --input -",
                    ),
                    (
                        ALLOW,
                        "gh api repos/o/r/issues/7/comments -f body=@reply.md -X GET",
                    ),
                ],
                cwd=cwd,
            )


class GhApiGraphql(Case):
    def test_mutations_with_a_body(self):
        reply = 'addPullRequestReviewThreadReply(input: {{pullRequestReviewThreadId: "T1", body: {}}}) {{ comment {{ id }} }}'
        good = json.dumps(BODY)
        self.assertVerdicts(
            [
                (
                    MISSING,
                    "gh api graphql -f query='mutation { "
                    + reply.format('"hi"')
                    + " }'",
                ),
                (
                    ALLOW,
                    "gh api graphql -f query='mutation { " + reply.format(good) + " }'",
                ),
                (
                    MISSING,
                    "gh api graphql -f query='mutation { r1: "
                    + reply.format(good)
                    + " r2: "
                    + reply.format('"no"')
                    + " }'",
                ),
                (
                    ALLOW,
                    "gh api graphql -f query='mutation { r1: "
                    + reply.format(good)
                    + " r2: "
                    + reply.format(good)
                    + " }'",
                ),
                (
                    ALLOW,
                    'gh api graphql -f query=\'mutation { addComment(input: {subjectId: "I1", body: """\n'
                    + BODY
                    + '\n"""}) { clientMutationId } }\'',
                ),
            ]
        )

    def test_variables(self):
        query = "mutation($id: ID!, $text: String!) { addComment(input: {subjectId: $id, body: $text}) { clientMutationId } }"
        self.assertVerdicts(
            [
                (MISSING, f"gh api graphql -f query='{query}' -f id=I1 -f text=hi"),
                (ALLOW, f"gh api graphql -f query='{query}' -f id=I1 -f text='{BODY}'"),
                (UNREADABLE, f"gh api graphql -f query='{query}' -f id=I1"),
                (
                    MISSING,
                    "gh api graphql -f query='mutation($input: AddCommentInput!) { addComment(input: $input) { clientMutationId } }'"
                    " -f 'input[subjectId]=I1' -f 'input[body]=hi'",
                ),
            ]
        )

    def test_not_a_post(self):
        self.assertVerdicts(
            [
                (ALLOW, "gh api graphql -f query='query { viewer { login } }'"),
                (
                    ALLOW,
                    'gh api graphql -f query=\'{ repository(owner: "o", name: "r") { issue(number: 1) { body } } }\'',
                ),
                (
                    ALLOW,
                    "gh api graphql -f query='query($n: Int!) { viewer { login } }' -F n=1 -f body=notused",
                ),
                (
                    ALLOW,
                    "gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: \"T1\"}) { thread { id } } }'",
                ),
                (
                    ALLOW,
                    "gh api graphql -f query='# mutation in a comment\nquery { viewer { login } }'",
                ),
            ]
        )

    def test_query_files(self):
        with tempfile.TemporaryDirectory() as cwd:
            with open(os.path.join(cwd, "round.graphql"), "w", encoding="utf-8") as fh:
                fh.write(
                    'mutation {\n  r1: addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: "T1", body: "no"}) { comment { id } }\n}\n'
                )
            with open(os.path.join(cwd, "payload.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "query": 'mutation($body: String!) { addComment(input: {subjectId: "I1", body: $body}) { clientMutationId } }',
                        "variables": {"body": BODY},
                    },
                    fh,
                )
            self.assertVerdicts(
                [
                    (MISSING, "gh api graphql -F query=@round.graphql"),
                    (ALLOW, "gh api graphql --input payload.json"),
                    (UNREADABLE, "gh api graphql -F query=@missing.graphql"),
                ],
                cwd=cwd,
            )


if __name__ == "__main__":
    unittest.main()
