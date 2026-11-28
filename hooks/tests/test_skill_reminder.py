"""When the skill reminder speaks after git and PR commands, and when it stays quiet."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import skill_reminder  # noqa: E402


class Triggers(unittest.TestCase):
    def test_handoff_and_commit_commands_trigger(self):
        for command in (
            "git commit -m 'x'",
            "git -C repo push -u origin HEAD",
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
            None,
        ):
            with self.subTest(command=command):
                self.assertFalse(skill_reminder.triggered(command))


class Reminder(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        patch = mock.patch.object(skill_reminder, "STATE_FILE", self.dir / "state.json")
        patch.start()
        self.addCleanup(patch.stop)
        mkdir = mock.patch.object(skill_reminder.hooklib, "STATE_DIR", self.dir)
        mkdir.start()
        self.addCleanup(mkdir.stop)

    def transcript(self, *skills):
        path = self.dir / "t.jsonl"
        lines = [
            json.dumps({"name": "Skill", "input": {"skill": f"skills:{s}"}})
            for s in skills
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def run_hook(self, payload):
        out = io.StringIO()
        with (
            mock.patch("sys.stdin", io.StringIO(json.dumps(payload))),
            redirect_stdout(out),
        ):
            skill_reminder.main()
        return out.getvalue()

    def payload(self, transcript, session="s1"):
        return {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git push"},
            "session_id": session,
            "transcript_path": transcript,
        }

    def test_speaks_when_a_skill_is_missing(self):
        out = self.run_hook(self.payload(self.transcript("git")))
        self.assertIn("load the git and coding skills", out)
        self.assertIn("once at handoff", out)

    def test_quiet_when_both_skills_are_loaded(self):
        self.assertEqual(
            self.run_hook(self.payload(self.transcript("git", "coding"))), ""
        )

    def test_speaks_once_per_session(self):
        transcript = self.transcript()
        self.assertNotEqual(self.run_hook(self.payload(transcript)), "")
        self.assertEqual(self.run_hook(self.payload(transcript)), "")
        self.assertNotEqual(self.run_hook(self.payload(transcript, session="s2")), "")

    def test_cursor_shape(self):
        payload = {
            "tool_name": "Shell",
            "tool_input": {"command": "gh pr ready 3"},
            "tool_output": "",
            "conversation_id": "c1",
        }
        self.assertIn('"additional_context"', self.run_hook(payload))


if __name__ == "__main__":
    unittest.main()
