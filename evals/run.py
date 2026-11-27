#!/usr/bin/env python3
"""Run headless Claude Code against a clean checkout of a ref and grade the outcome."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import tempfile
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
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
}

# Clean room: only project settings (no user CLAUDE.md, plugins, or skills), and no auto-memory,
# which is keyed by the repository and so would follow the agent into a worktree.
CLEAN_ROOM = [
    "--setting-sources",
    "project",
    "--settings",
    '{"autoMemoryEnabled": false}',
]

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
        help="grade the nav answers stored in a results file again with the current cases; runs no model",
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


def shell(cmd: str, cwd: Path, timeout: int) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
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


def ask_claude(case: dict, cwd: Path, args: argparse.Namespace) -> dict:
    kind = KINDS[case["kind"]]
    cmd = [
        "claude",
        "-p",
        case["prompt"],
        "--model",
        args.model,
        "--output-format",
        "json",
        "--max-turns",
        str(case.get("max_turns", kind["max_turns"])),
        *CLEAN_ROOM,
        *kind["args"],
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=args.timeout
        )
    except subprocess.TimeoutExpired:
        return {"error": f"timeout after {args.timeout}s", "seconds": args.timeout}
    seconds = round(time.monotonic() - started, 1)
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "error": f"exit {proc.returncode}: {(proc.stderr or proc.stdout)[-2000:]}",
            "seconds": seconds,
        }
    return {
        "error": out.get("subtype") if out.get("is_error") else None,
        "answer": out.get("result", ""),
        "is_error": out.get("is_error"),
        "num_turns": out.get("num_turns"),
        "total_cost_usd": out.get("total_cost_usd"),
        "duration_ms": out.get("duration_ms"),
        "usage": out.get("usage"),
        "seconds": seconds,
    }


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


def run_case(
    case: dict, trial: int, commit: str, nav_tree: Path | None, tmp: Path, args
) -> dict:
    record = {"case": case["id"], "kind": case["kind"], "trial": trial}
    try:
        record |= attempt(case, trial, commit, nav_tree, tmp, args)
    except Exception as e:  # one broken run must not drop the others' records
        record |= {"error": repr(e), "score": 0.0, "passed": False}
    record["passed"] = record["passed"] and not record.get("error")
    return record


def attempt(
    case: dict, trial: int, commit: str, nav_tree: Path | None, tmp: Path, args
) -> dict:
    record: dict = {}
    if case["kind"] == "nav":
        record |= ask_claude(case, nav_tree, args)
        record |= grade_nav(case, record.get("answer", ""))
    else:
        tree = tmp / f"{case['id']}-{trial}"
        try:
            add_worktree(tree, commit)
            setup = (
                shell(case["setup"], tree, args.timeout) if "setup" in case else None
            )
            record["setup"] = setup
            if setup and not setup["passed"]:
                record |= {"error": "setup failed", "score": 0.0, "passed": False}
                return record
            record |= ask_claude(case, tree, args)
            record |= grade_task(case, tree, args.timeout)
        finally:
            remove_worktree(tree)
    return record


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
    return lines


def regrade(path: Path, cases: list[dict]) -> None:
    by_id = {c["id"]: c for c in cases if c["kind"] == "nav"}
    data = json.loads(path.read_text())
    for r in data["records"]:
        if r["case"] in by_id and not r.get("error"):
            r |= grade_nav(by_id[r["case"]], r.get("answer", ""))
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
    nav_tree = None
    try:
        commit = (
            git("rev-parse", "--verify", f"{args.ref}^{{commit}}")
            if args.ref
            else snapshot_working_tree(tmp)
        )
        nav_tree = add_worktree(tmp / "nav", commit)
        tokens = instruction_tokens(nav_tree)
        print(f"ref {args.ref or 'working tree'} ({commit[:12]}), model {args.model}")
        print(f"instruction tokens every session loads: {tokens}")

        runs = [(c, t) for t in range(args.trials) for c in cases]
        with ThreadPoolExecutor(args.jobs) as pool:
            records = list(
                pool.map(lambda ct: run_case(*ct, commit, nav_tree, tmp, args), runs)
            )
    finally:
        if nav_tree:
            remove_worktree(nav_tree)
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
