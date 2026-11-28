"""Which commands get the skill reminder, and its shape for each tool."""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import skill_reminder  # noqa: E402


def run_hook(payload):
    out = io.StringIO()
    with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))):
        with redirect_stdout(out):
            skill_reminder.main()
    return out.getvalue()


class Triggers(unittest.TestCase):
    def test_handoff_and_commit_commands_trigger(self):
        for command in (
            "git commit -m 'x'",
            "git -C repo push -u origin HEAD",
            "git -c user.email=a@b -c user.name=a commit -m x",
            "git --no-pager -C repo commit --amend",
            "mise run check && git commit -q -m x",
            "gh pr create --draft --title t --body-file b.md",
            "gh pr ready 12",
            "gh stack submit --auto",
        ):
            with self.subTest(command=command):
                self.assertTrue(skill_reminder.triggered(command))

    def test_other_commands_do_not(self):
        for command in (
            "git status",
            "git log --oneline",
            "gh pr view 3",
            "echo commit",
            "git log --grep commit",
            None,
        ):
            with self.subTest(command=command):
                self.assertFalse(skill_reminder.triggered(command))


class Output(unittest.TestCase):
    def test_claude_shape(self):
        out = run_hook(
            {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "git push"},
            }
        )
        self.assertIn('"additionalContext"', out)
        self.assertIn("once at handoff", out)

    def test_cursor_shape(self):
        out = run_hook(
            {
                "tool_name": "Shell",
                "tool_input": {"command": "gh pr ready 3"},
                "tool_output": "",
            }
        )
        self.assertIn('"additional_context"', out)

    def test_quiet_on_other_commands(self):
        self.assertEqual(
            run_hook({"tool_name": "Bash", "tool_input": {"command": "git status"}}), ""
        )


if __name__ == "__main__":
    unittest.main()
