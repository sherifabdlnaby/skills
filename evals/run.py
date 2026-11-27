#!/usr/bin/env python3
"""Run headless Claude Code against a clean checkout of a ref and grade the outcome."""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import shutil
import signal
import statistics
import subprocess
import tempfile
import threading
import time
import tomllib
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SANDBOX = Path(__file__).with_name("sandbox")
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md")

KINDS = {
    "nav": {
        "max_turns": 30,
        "args": [
            "--allowedTools",
            "Read",
            "Grep",
            "Glob",
            "Bash(ls:*)",
            "Bash(cat:*)",
            "Bash(mise tasks:*)",
            "Bash(mise run * --help)",
            "Bash(git log:*)",
            "Bash(git status:*)",
            "Bash(jq:*)",
        ],
    },
    "task": {
        "max_turns": 100,
        "args": [
            "--permission-mode",
            "acceptEdits",
            "--allowedTools",
            "Read",
            "Edit",
            "Write",
            "Glob",
            "Grep",
            *(
                f"Bash({cmd}:*)"
                for cmd in (
                    "mise",
                    "git status",
                    "git diff",
                    "git log",
                    "git add",
                    "git rm",
                    "git mv",
                    "rm",
                    "ls",
                    "cat",
                    "jq",
                    "uv",
                    "python",
                    "python3",
                    "mkdir",
                    "cp",
                    "mv",
                    "sed",
                )
            ),
            "--disallowedTools",
            "Bash(git push:*)",
            "Bash(git commit:*)",
            "Bash(gh:*)",
        ],
    },
    # The sandbox is a throwaway project whose `origin` is a local folder and whose `gh` is a
    # stand-in, so the agent may commit, push, and post.
    "skill": {
        "max_turns": 30,
        "args": [
            "--permission-mode",
            "acceptEdits",
            "--allowedTools",
            "Skill",
            "Read",
            "Edit",
            "Write",
            "Glob",
            "Grep",
            *(f"Bash({cmd}:*)" for cmd in ("git", "gh", "ls", "cat", "jq", "mkdir")),
        ],
    },
}

# Clean room: only project settings (no user CLAUDE.md, plugins, or skills), and no auto-memory,
# which is keyed by the repository and so would follow the agent into a worktree.
CLEAN_ROOM = [
    "--setting-sources",
    "project",
    "--settings",
    '{"autoMemoryEnabled": false}',
]

# A skill loads through the Skill tool, or when the agent reads its SKILL.md.
SKILL_LOAD = r"^Skill (?:[\w-]+:)?{0}$|^Read \S*/{0}/SKILL\.md$"

# Counts with the tokenizer the skill READMEs use.
TOKENS_PY = (
    "import sys, tiktoken, token_estimates as t; from pathlib import Path; "
    "e = tiktoken.get_encoding(t.ENCODING_NAME); "
    "print(sum(t.token_count(Path(p), e) for p in sys.argv[1:]))"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ref",
        help="git ref to test (default: the working tree, uncommitted included)",
    )
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--trials", type=int, default=1, help="runs per case")
    parser.add_argument("--jobs", type=int, default=4, help="runs in parallel")
    parser.add_argument(
        "--case", action="append", dest="cases_filter", help="only this case id"
    )
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument(
        "--cases", type=Path, default=Path(__file__).with_name("cases.toml")
    )
    parser.add_argument("--label", help="results file prefix (default: the ref)")
    parser.add_argument(
        "--timeout", type=int, default=600, help="seconds per run, and per check"
    )
    parser.add_argument(
        "--regrade",
        type=Path,
        help="grade a results file again with the current cases (nav answers, skill tool calls); runs no model",
    )
    return parser.parse_args()


def git(*args: str, env: dict[str, str] | None = None) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


def snapshot_working_tree(tmp: Path) -> str:
    """Commit tracked and untracked-not-ignored files to a dangling commit, without touching the
    checkout's index or branches, so every run sees the working tree as its HEAD."""
    env = {**os.environ, "GIT_INDEX_FILE": str(tmp / "index")}
    git("add", "--all", env=env)
    tree = git("write-tree", env=env)
    return git("commit-tree", tree, "-p", "HEAD", "-m", "eval: working tree snapshot")


def add_worktree(path: Path, commit: str) -> Path:
    git("worktree", "add", "--detach", "--quiet", str(path), commit)
    subprocess.run(["mise", "trust"], cwd=path, check=True, capture_output=True)
    return path


def remove_worktree(path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(REPO), "worktree", "remove", "--force", str(path)],
        capture_output=True,
    )


def instruction_tokens(tree: Path) -> int:
    files = [str(tree / f) for f in INSTRUCTION_FILES if (tree / f).is_file()]
    out = subprocess.run(
        ["uv", "run", "--locked", "python", "-c", TOKENS_PY, *files],
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": str(REPO / ".config")},
        check=True,
        capture_output=True,
        text=True,
    )
    return int(out.stdout)


def shell(cmd: str, cwd: Path, timeout: int, env: dict[str, str] | None = None) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"passed": False, "output": f"timeout after {timeout}s"}
    return {
        "passed": proc.returncode == 0,
        "output": (proc.stdout + proc.stderr)[-2000:],
    }


def sandbox_env(box: Path) -> dict[str, str]:
    """The environment of a `skill` run: nothing of the owner's GitHub or git setup reaches it."""
    return {
        **os.environ,
        "PATH": f"{SANDBOX / 'bin'}{os.pathsep}{os.environ['PATH']}",  # the stand-in gh
        "GH_TOKEN": "eval-invalid",  # if a run reaches the real gh, it cannot post
        "GIT_CONFIG_GLOBAL": os.devnull,  # no signing, aliases, or hooks from the owner
        "GIT_CONFIG_NOSYSTEM": "1",
        "MISE_TRUSTED_CONFIG_PATHS": str(box),
    }


def describe(tool: dict) -> str:
    """`<Tool> <its main argument>`: the line that the regexes of a `skill` case match."""
    given = tool["input"]
    main = next(
        (given[k] for k in ("command", "file_path", "skill", "pattern") if k in given),
        json.dumps(given),
    )
    return f"{tool['name']} {main}"[:2000]


def ask_claude(
    case: dict,
    cwd: Path,
    args: argparse.Namespace,
    extra: tuple[str, ...] = (),
    env: dict[str, str] | None = None,
    decided=None,
) -> dict:
    """Run one headless session: the prompts in the case's `before`, then its `prompt`, each as a
    turn. Returns the last answer, the cost, and the tool calls in the order they finished.
    `decided` sees the calls after each one; when it returns true the session stops there,
    because nothing later can change the grade."""
    kind = KINDS[case["kind"]]
    session = str(uuid.uuid4())
    cmd = [
        "claude",
        "-p",
        "--model",
        args.model,
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--verbose",
        "--session-id",
        session,
        "--max-turns",
        str(case.get("max_turns", kind["max_turns"])),
        *CLEAN_ROOM,
        *kind["args"],
        *extra,
    ]
    env = {k: v for k, v in (env or os.environ).items() if k != "CLAUDECODE"}
    started = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    timed_out = threading.Event()
    timer = threading.Timer(args.timeout, lambda: (timed_out.set(), proc.kill()))
    timer.start()

    prompts = [*case.get("before", []), case["prompt"]]

    def say_next() -> None:
        if prompts and not stopped:
            turn = {"role": "user", "content": prompts.pop(0)}
            proc.stdin.write(json.dumps({"type": "user", "message": turn}) + "\n")
            proc.stdin.flush()
        elif not proc.stdin.closed:
            proc.stdin.close()

    calls: list[dict] = []
    pending: dict[
        str, str
    ] = {}  # tool call id -> its description, until its result arrives
    refused: set[str] = set()  # ids the permission rules denied
    noise: list[str] = []
    result = None
    stopped = False
    try:
        say_next()
        for line in proc.stdout:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                noise.append(line)
                continue
            kind_of = event.get("type")
            if kind_of == "result":
                result = event
                say_next()
            elif event.get("subtype") == "permission_denied":
                refused.add(event.get("tool_use_id"))
            if kind_of not in ("assistant", "user"):
                continue
            content = event["message"]["content"]
            blocks = content if isinstance(content, list) else []
            if kind_of == "assistant":
                for block in blocks:
                    if block.get("type") == "tool_use":
                        pending[block["id"]] = describe(block)
            elif not stopped:
                for block in blocks:
                    call = pending.pop(block.get("tool_use_id"), None)
                    if block.get("type") != "tool_result" or call is None:
                        continue
                    outcome = (
                        "refused"
                        if block["tool_use_id"] in refused
                        else "error"
                        if block.get("is_error")
                        else "ok"
                    )
                    calls.append({"call": call, "outcome": outcome})
                if decided and decided(calls):
                    stopped = True
                    proc.send_signal(signal.SIGINT)
                    threading.Timer(
                        15, proc.kill
                    ).start()  # if it does not stop by itself
        proc.wait()
    finally:
        timer.cancel()
        forget_session(session)

    record = {"calls": calls, "seconds": round(time.monotonic() - started, 1)}
    if timed_out.is_set():
        return record | {"error": f"timeout after {args.timeout}s"}
    if result is None:
        if stopped:
            return record | {"error": None, "answer": ""}
        return record | {"error": f"exit {proc.returncode}: {''.join(noise)[-2000:]}"}
    return record | {
        "error": result.get("subtype")
        if result.get("is_error") and not stopped
        else None,
        "answer": result.get("result", ""),
        "num_turns": result.get("num_turns"),
        "total_cost_usd": result.get("total_cost_usd"),
        "usage": result.get("usage"),
    }


def forget_session(session: str) -> None:
    """Delete the transcript Claude Code saved for a run, so eval sessions do not pile up in the
    owner's history. The transcript has to exist during the run: hooks read it."""
    projects = (
        Path(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")).expanduser() / "projects"
    )
    for transcript in projects.glob(f"*/{session}.jsonl"):
        transcript.unlink()
        shutil.rmtree(transcript.with_suffix(""), ignore_errors=True)  # its side files
        try:
            transcript.parent.rmdir()  # the project folder, when this was its only session
        except OSError:
            pass


def grade_nav(case: dict, answer: str) -> dict:
    def hits(patterns: list[str]) -> dict[str, bool]:
        return {p: bool(re.search(p, answer, re.I | re.S)) for p in patterns}

    must = hits(case["must"])
    must_not = hits(case.get("must_not", []))
    return {
        "checks": {"must": must, "must_not": must_not},
        "score": sum(must.values()) / len(must),
        "passed": all(must.values()) and not any(must_not.values()),
    }


def grade_task(case: dict, cwd: Path, timeout: int) -> dict:
    checks = {name: shell(cmd, cwd, timeout) for name, cmd in case["checks"].items()}
    passed = [c["passed"] for c in checks.values()]
    return {
        "checks": checks,
        "score": sum(passed) / len(passed),
        "passed": all(passed),
    }


def grade_skill(case: dict, calls: list[dict]) -> dict:
    """Pass when every skill in `load` was loaded and every page in `read` was opened before the
    agent acted, and no skill in `not_load` was loaded at all. The agent acts at the first call
    that matches `act` and ran, or that the permission rules refused. A call that failed, for
    example one a hook blocked, is not the act: the agent can still load the skill and try again."""

    def matches(pattern: str, call: str) -> bool:
        return bool(re.search(pattern, call, re.I | re.S))

    def loaded(skill: str, done: list[str]) -> bool:
        return any(matches(SKILL_LOAD.format(re.escape(skill)), call) for call in done)

    act = case.get("act")
    acted = next(
        (
            i
            for i, c in enumerate(calls)
            if act and c["outcome"] != "error" and matches(act, c["call"])
        ),
        None,
    )
    before = [c["call"] for c in calls[:acted] if c["outcome"] == "ok"]
    whole = [c["call"] for c in calls if c["outcome"] == "ok"]
    checks = {
        "load": {skill: loaded(skill, before) for skill in case.get("load", [])},
        "read": {
            page: any(matches(page, call) for call in before)
            for page in case.get("read", [])
        },
        "not_load": {
            skill: not loaded(skill, whole) for skill in case.get("not_load", [])
        },
    }
    flat = [ok for group in checks.values() for ok in group.values()]
    return {
        "checks": checks,
        "acted": acted is not None,
        "score": sum(flat) / len(flat),
        "passed": all(flat),
    }


def skill_decided(case: dict):
    """When a `skill` run can stop: at the act, or once every check passed. A case with `not_load`
    runs to its end, because only the whole run shows that a skill never loaded."""
    if "not_load" in case:
        return None

    def decided(calls: list[dict]) -> bool:
        grade = grade_skill(case, calls)
        return grade["acted"] or grade["passed"]

    return decided


def run_case(case: dict, trial: int, commit: str, tree: Path, tmp: Path, args) -> dict:
    record = {"case": case["id"], "kind": case["kind"], "trial": trial}
    try:
        record |= attempt(case, trial, commit, tree, tmp, args)
    except Exception as e:  # one broken run must not drop the others' records
        record |= {"error": repr(e), "score": 0.0, "passed": False}
    record["passed"] = record["passed"] and not record.get("error")
    return record


def attempt(case: dict, trial: int, commit: str, tree: Path, tmp: Path, args) -> dict:
    """One run of a case. `tree` is the clean checkout of the ref: `nav` runs read it, and `skill`
    runs load it as the plugin."""
    if case["kind"] == "nav":
        record = ask_claude(case, tree, args)
        return record | grade_nav(case, record.get("answer", ""))

    setup_failed = {"error": "setup failed", "score": 0.0, "passed": False}
    own = tmp / f"{case['id']}-{trial}"  # this run's folder
    if case["kind"] == "skill":
        env = sandbox_env(own)
        try:
            subprocess.run(
                [SANDBOX / "init.sh", own], env=env, check=True, capture_output=True
            )
            work = own / "work"
            setup = shell(case.get("setup", "true"), work, args.timeout, env)
            if not setup["passed"]:
                return {"setup": setup} | setup_failed
            record = ask_claude(
                case,
                work,
                args,
                extra=("--plugin-dir", str(tree)),
                env=env,
                decided=skill_decided(case),
            )
            return record | grade_skill(case, record["calls"])
        finally:
            shutil.rmtree(own, ignore_errors=True)

    try:
        add_worktree(own, commit)
        setup = shell(case.get("setup", "true"), own, args.timeout)
        if not setup["passed"]:
            return {"setup": setup} | setup_failed
        record = ask_claude(case, own, args)
        return record | grade_task(case, own, args.timeout)
    finally:
        remove_worktree(own)


def summary(records: list[dict]) -> list[str]:
    lines = [
        f"{'case':<24} {'kind':<5} {'pass':<5} {'score':>5} {'turns':>5} {'cost':>7} {'sec':>6}"
    ]
    for r in records:
        lines.append(
            f"{r['case']:<24} {r['kind']:<5} {'yes' if r['passed'] else 'NO':<5} "
            f"{r['score']:>5.2f} {r.get('num_turns') or '-':>5} "
            f"{r.get('total_cost_usd') or 0:>7.3f} {r.get('seconds', 0):>6.0f}"
            + (f"  ({r['error']})" if r.get("error") else "")
        )
    for kind in KINDS:
        rs = [r for r in records if r["kind"] == kind]
        if not rs:
            continue
        turns = [r["num_turns"] for r in rs if r.get("num_turns")]
        lines.append(
            f"{kind}: pass {sum(r['passed'] for r in rs)}/{len(rs)}"
            f", mean score {statistics.mean(r['score'] for r in rs):.2f}"
            f", median turns {statistics.median(turns) if turns else '-'}"
            f", cost ${sum(r.get('total_cost_usd') or 0 for r in rs):.2f}"
            f", n={len(rs)}"
        )
        if kind == "skill":  # one rate per check, across cases: `load git 7/9`
            rates = collections.defaultdict(list)
            for r in rs:
                for group, checks in r.get("checks", {}).items():
                    for name, ok in checks.items():
                        rates[f"{group} {name}"].append(ok)
            lines += [
                f"  {name:<44} {sum(oks)}/{len(oks)}"
                for name, oks in sorted(rates.items())
            ]
    return lines


def regrade(path: Path, cases: list[dict]) -> None:
    by_id = {c["id"]: c for c in cases}
    data = json.loads(path.read_text())
    for r in data["records"]:
        case = by_id.get(r["case"])
        if not case or r.get("error"):
            continue
        if case["kind"] == "nav":
            r |= grade_nav(case, r.get("answer", ""))
        elif case["kind"] == "skill":
            r |= grade_skill(case, r.get("calls", []))
    path.write_text(json.dumps(data, indent=2) + "\n")
    print("\n".join(summary(data["records"])))


def main() -> None:
    args = parse_args()
    cases = tomllib.loads(args.cases.read_text())["case"]
    if args.regrade:
        return regrade(args.regrade, cases)
    cases = [
        c
        for c in cases
        if (not args.cases_filter or c["id"] in args.cases_filter)
        and (not args.kind or c["kind"] == args.kind)
    ]
    if not cases:
        raise SystemExit("no cases match the filters")

    # Outside $HOME, so Claude Code does not load CLAUDE.md files from the owner's parent dirs.
    tmp = Path(tempfile.mkdtemp(prefix="skills-eval-"))
    tree = None
    try:
        commit = (
            git("rev-parse", "--verify", f"{args.ref}^{{commit}}")
            if args.ref
            else snapshot_working_tree(tmp)
        )
        tree = add_worktree(tmp / "tree", commit)
        tokens = instruction_tokens(tree)
        print(f"ref {args.ref or 'working tree'} ({commit[:12]}), model {args.model}")
        print(f"instruction tokens every session loads: {tokens}")

        runs = [(c, t) for t in range(args.trials) for c in cases]
        with ThreadPoolExecutor(args.jobs) as pool:
            records = list(
                pool.map(lambda ct: run_case(*ct, commit, tree, tmp, args), runs)
            )
    finally:
        if tree:
            remove_worktree(tree)
        shutil.rmtree(tmp, ignore_errors=True)
        subprocess.run(["git", "-C", str(REPO), "worktree", "prune"])

    print("\n".join(summary(records)))
    label = re.sub(r"[^\w.-]", "-", args.label or args.ref or "worktree")
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = REPO / "evals" / "results" / f"{label}-{args.model}-{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "ref": args.ref,
        "commit": commit,
        "model": args.model,
        "trials": args.trials,
        "instruction_tokens": tokens,
    }
    out.write_text(json.dumps({**meta, "records": records}, indent=2) + "\n")
    print(f"records: {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
