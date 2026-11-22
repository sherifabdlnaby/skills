"""The hooks as each harness runs them: a payload into run.sh, a verdict out.

Payloads are recorded samples (tests/fixtures/<harness>.json) with the command
swapped in, so a change to how an adapter reads or answers its harness shows here.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

TESTS = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(TESTS, "..", "..", "skills", "ai-disclosure", "hooks", "run.sh")
FIXTURES = os.path.join(TESTS, "fixtures", "ai-disclosure")

DISCLOSURE = "_<sub>🤖 Agent Decided: Codex · GPT 5.5 (high)</sub>_"

# harness -> (protocol argument from its hook config, payload key path of the command)
HARNESSES = {
    "claude": ("claude", ("tool_input", "command")),
    "codex": ("claude", ("tool_input", "command")),
    "cursor": ("cursor", ("command",)),
}


def payload(harness: str, command: str, cwd: str = None) -> str:
    """The fixture with `command` swapped in, and the session directory moved to `cwd`."""
    with open(os.path.join(FIXTURES, harness + ".json"), encoding="utf-8") as fh:
        data = json.load(fh)
    *parents, key = HARNESSES[harness][1]
    target = data
    for name in parents:
        target = target[name]
    target[key] = command
    if (
        cwd and "workspace_roots" in data
    ):  # Cursor leaves `cwd` empty and names the workspace
        data["workspace_roots"] = [cwd]
    elif cwd:
        data["cwd"] = cwd
    return json.dumps(data)


def run(harness: str, command: str, env=None, cwd: str = None) -> str:
    result = subprocess.run(
        [RUN, HARNESSES[harness][0]],
        input=payload(harness, command, cwd),
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return result.stdout


def denial(harness: str, output: str):
    """The agent-facing reason of a denial, or None when the command may run."""
    if not output.strip():
        return None
    verdict = json.loads(output)
    if HARNESSES[harness][0] == "cursor":
        if (
            verdict["permission"] != "deny"
            or verdict["user_message"] != verdict["agent_message"]
        ):
            raise AssertionError(output)
        return verdict["user_message"]
    hook = verdict["hookSpecificOutput"]
    if (hook["hookEventName"], hook["permissionDecision"]) != ("PreToolUse", "deny"):
        raise AssertionError(output)
    return hook["permissionDecisionReason"]


def sandbox_path(tools, extra=None) -> str:
    """A PATH holding only `tools` from this machine, plus `extra` scripts."""
    bindir = tempfile.mkdtemp()
    for tool in tools:
        found = shutil.which(tool)
        if found:
            os.symlink(found, os.path.join(bindir, tool))
    for name, script in (extra or {}).items():
        path = os.path.join(bindir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(script)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return bindir


class EveryHarness(unittest.TestCase):
    def test_verdicts(self):
        cases = [
            (False, "ls -la"),
            (False, "gh pr view 7"),
            (False, f"gh pr comment 7 --body 'Done.\n\n---\n{DISCLOSURE}'"),
            (True, "gh pr comment 7 --body 'Done.'"),
            (True, "gh api repos/o/r/pulls/7/comments/1/replies -f body=ok"),
            (True, "git push &&\\\ngh pr create --title t --body x"),
        ]
        for harness in HARNESSES:
            for blocked, command in cases:
                with self.subTest(harness=harness, command=command):
                    reason = denial(harness, run(harness, command))
                    self.assertEqual(reason is not None, blocked)
                    if blocked:
                        self.assertIn("`ai-disclosure` skill", reason)
                        self.assertIn("AI_DISCLOSURE=off", reason)

    def test_relative_body_file(self):
        with tempfile.TemporaryDirectory() as workspace:
            with open(os.path.join(workspace, "body.md"), "w", encoding="utf-8") as fh:
                fh.write(f"Done.\n\n---\n{DISCLOSURE}\n")
            command = "gh pr comment 7 --body-file body.md"
            for harness in HARNESSES:
                with self.subTest(harness=harness):
                    self.assertIsNone(
                        denial(harness, run(harness, command, cwd=workspace))
                    )

    def test_session_opt_out(self):
        env = dict(os.environ, AI_DISCLOSURE="off")
        for harness in HARNESSES:
            with self.subTest(harness=harness):
                self.assertIsNone(
                    denial(harness, run(harness, "gh pr comment 7 --body x", env))
                )


class WithoutTheGuard(unittest.TestCase):
    """When Python cannot run the guard, a possible post is blocked, never let through."""

    BASE_TOOLS = ["sh", "cat", "dirname", "grep"]

    def run_without(self, extra=None):
        env = {"PATH": sandbox_path(self.BASE_TOOLS, extra)}
        for harness in HARNESSES:
            yield (
                harness,
                run(harness, "gh pr comment 7 --body x", env),
                run(harness, "ls", env),
            )

    def test_no_python(self):
        for harness, post, other in self.run_without():
            with self.subTest(harness=harness):
                self.assertIn("xcode-select --install", denial(harness, post))
                self.assertIsNone(denial(harness, other))

    def test_guard_crash(self):
        for harness, post, other in self.run_without(
            {"python3": "#!/bin/sh\nexit 1\n"}
        ):
            with self.subTest(harness=harness):
                self.assertIn("guard failed", denial(harness, post))
                self.assertIsNone(denial(harness, other))


if __name__ == "__main__":
    unittest.main()
