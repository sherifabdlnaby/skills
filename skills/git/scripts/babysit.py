#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Babysit a GitHub PR: poll CI, reviews, and comments, return only what changed.

Built for an agent to run (directly, or from a cheap background sub-agent). It does
the predictable, token-heavy part: poll, diff against a saved snapshot, and report
only the delta. The agent does the thinking.

Subcommands
  arm     Resolve the PR, snapshot the current state as a baseline, print a summary.
  poll    One-shot: fetch, diff vs the saved snapshot, update it, print the delta.
  watch   Loop with adaptive backoff; block until a high-signal event (or deadline),
          then print the delta and exit. This is the one a background agent runs.

Why a snapshot file: diffing needs a "last seen". Each watcher keeps its OWN snapshot
(via --watcher), so several agents can babysit the same PR without clobbering cursors.

High-signal events (what wakes the agent in `watch`):
  FAIL      a check went red (CI, CodeQL, anything)
  DONE      all checks reached a terminal state (the "CI finished" milestone)
  REVIEW    a review was submitted (Copilot or human)
  COMMENT   a new issue comment or inline review comment
  STATE     the PR merged / closed
Plain churn (queued -> running, a job starting) updates the snapshot silently and does
NOT wake the agent. That is the point: the noisy opening burst stays quiet.

Everything is stdlib; `gh` does auth and API. Run via `uv run` (shebang handles it).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCHEMA = 1

# Conclusions that mean a check is red. SKIPPED / NEUTRAL / SUCCESS are fine.
FAIL_CONCLUSIONS = {
    "FAILURE",
    "TIMED_OUT",
    "ACTION_REQUIRED",
    "STARTUP_FAILURE",
    "STALE",
}
# A check is still running while in one of these (or has no status yet).
PENDING_STATUS = {
    "QUEUED",
    "IN_PROGRESS",
    "PENDING",
    "WAITING",
    "REQUESTED",
    "EXPECTED",
}

COPILOT_LOGINS = {
    "copilot",
    "copilot-pull-request-reviewer",
    "github-copilot",
    "github-advanced-security",
}

# Bot detection is by AUTHOR login only, never comment body (a human saying "review" is not a bot).
# BOT_RE: is this author automated at all. REVIEW_TOOL_RE: is it specifically a code-review tool
# (the subset that makes a plain issue comment react-worthy, excluding generic bots like
# github-actions that only post greetings/labels/CI chatter).
BOT_RE = re.compile(r"\[bot\]|bot|copilot|codeql|review|reviewer|sonar|snyk", re.I)
REVIEW_TOOL_RE = re.compile(r"copilot|codeql|sonar|snyk|review|reviewer", re.I)


# --------------------------------------------------------------------------- gh


def gh(args: list[str], check: bool = True) -> str:
    """Run a gh command, return stdout. Raises on failure unless check=False."""
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        die("gh not found on PATH. Install GitHub CLI.")
    except subprocess.TimeoutExpired:
        die(f"gh timed out: gh {' '.join(args)}")
    if check and proc.returncode != 0:
        die(f"gh failed: gh {' '.join(args)}\n{proc.stderr.strip()}")
    return proc.stdout


def gh_json(args: list[str], check: bool = True):
    out = gh(args, check=check)
    if not out.strip():
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        if check:
            die(f"gh returned non-JSON for: gh {' '.join(args)}")
        return None


# ------------------------------------------------------------------- resolving


def resolve(pr: str | None, repo: str | None) -> tuple[int, str, str]:
    """Return (pr_number, owner/repo, url). Defaults to the current branch's PR."""
    fields = "number,url,headRepository,headRepositoryOwner"
    args = ["pr", "view", "--json", fields]
    if pr:
        args.insert(2, pr)
    if repo:
        args += ["--repo", repo]
    data = gh_json(args)
    if not data:
        die(
            "could not resolve a PR. Pass --pr <num|url> or run on a branch with an open PR."
        )
    now = repo
    if not now:
        owner = (data.get("headRepositoryOwner") or {}).get("login")
        name = (data.get("headRepository") or {}).get("name")
        if owner and name:
            now = f"{owner}/{name}"
    if not now:
        # Fall back to the URL: https://github.com/<owner>/<repo>/pull/<n>
        m = re.search(r"github\.com/([^/]+/[^/]+)/pull/", data.get("url", ""))
        now = m.group(1) if m else None
    if not now:
        die("could not determine owner/repo. Pass --repo <owner/repo>.")
    return int(data["number"]), now, data["url"]


# -------------------------------------------------------------------- snapshot


def fetch_snapshot(pr: int, repo: str, url: str) -> dict:
    """One normalized picture of the PR: checks, reviews, comments, state."""
    fields = "number,url,state,mergedAt,isDraft,reviewDecision,statusCheckRollup,reviews,comments,title"
    data = gh_json(["pr", "view", str(pr), "--repo", repo, "--json", fields]) or {}

    checks: dict[str, dict] = {}
    for c in data.get("statusCheckRollup") or []:
        if c.get("__typename") == "StatusContext":
            name = c.get("context") or "?"
            state = (c.get("state") or "").upper()
            status = "COMPLETED" if state not in PENDING_STATUS and state else state
            concl = state if state in FAIL_CONCLUSIONS or state == "SUCCESS" else ""
            link = c.get("targetUrl") or ""
        else:  # CheckRun
            name = c.get("name") or "?"
            status = (c.get("status") or "").upper()
            concl = (c.get("conclusion") or "").upper()
            link = c.get("detailsUrl") or ""
        checks[name] = {"status": status, "conclusion": concl, "url": link}

    reviews: dict[str, dict] = {}
    for r in data.get("reviews") or []:
        rid = str(
            r.get("id")
            or f"{r.get('submittedAt')}:{(r.get('author') or {}).get('login')}"
        )
        reviews[rid] = {
            "author": (r.get("author") or {}).get("login") or "?",
            "state": r.get("state") or "",
            "at": r.get("submittedAt") or "",
            "excerpt": excerpt(r.get("body")),
        }

    comments: dict[str, dict] = {}
    for c in data.get("comments") or []:
        comments[str(c.get("id"))] = {
            "author": (c.get("author") or {}).get("login") or "?",
            "at": c.get("createdAt") or "",
            "excerpt": excerpt(c.get("body")),
            "url": c.get("url") or "",
        }

    # Inline review comments live on a separate endpoint; best-effort.
    review_comments: dict[str, dict] = {}
    api = gh_json(
        [
            "api",
            f"repos/{repo}/pulls/{pr}/comments",
            "--paginate",
            "--jq",
            ".[] | {id,login:.user.login,at:.created_at,path,body,url:.html_url}",
        ],
        check=False,
    )
    if api is not None:
        rows = api if isinstance(api, list) else [api]
        for c in rows:
            if not isinstance(c, dict):
                continue
            review_comments[str(c.get("id"))] = {
                "author": c.get("login") or "?",
                "at": c.get("at") or "",
                "path": c.get("path") or "",
                "excerpt": excerpt(c.get("body")),
                "url": c.get("url") or "",
            }

    settled = bool(checks) and all(is_terminal(ck) for ck in checks.values())

    return {
        "schema": SCHEMA,
        "repo": repo,
        "pr": pr,
        "url": data.get("url") or url,
        "title": data.get("title") or "",
        "pr_state": data.get("state") or "OPEN",
        "merged": bool(data.get("mergedAt")),
        "draft": bool(data.get("isDraft")),
        "review_decision": data.get("reviewDecision") or "",
        "checks": checks,
        "reviews": reviews,
        "comments": comments,
        "review_comments": review_comments,
        "ci_settled": settled,
        "ts": time.time(),
    }


def excerpt(body: str | None, n: int = 140) -> str:
    if not body:
        return ""
    s = " ".join(body.split())
    return s if len(s) <= n else s[: n - 1] + "…"


def is_fail(check: dict) -> bool:
    return check.get("conclusion", "") in FAIL_CONCLUSIONS


def is_terminal(check: dict) -> bool:
    """A check has finished (passed, failed, or skipped), not still running."""
    return (
        check.get("status", "") not in PENDING_STATUS and check.get("status", "") != ""
    )


def count_checks(snap: dict) -> tuple[int, int]:
    """(ok, red) counts over a snapshot's checks; ok = finished and not red (excludes pending)."""
    checks = snap["checks"].values()
    return (
        sum(1 for c in checks if is_terminal(c) and not is_fail(c)),
        sum(1 for c in checks if is_fail(c)),
    )


def is_copilot(login: str) -> bool:
    lo = login.lower().rstrip("]").replace("[bot", "")
    return lo in COPILOT_LOGINS or "copilot" in lo


def is_bot(login: str) -> bool:
    return bool(BOT_RE.search(login or ""))


def is_review_tool(login: str) -> bool:
    return bool(REVIEW_TOOL_RE.search(login or ""))


def classify(author: str, kind: str) -> str:
    """Line tag for a review/comment. kind: 'review' (submitted), 'inline' (on the diff),
    'issue' (PR conversation). BOTREVIEW = an automated code review to address automatically."""
    if kind == "review":
        return "BOTREVIEW" if is_bot(author) else "REVIEW"
    if kind == "inline":
        return "BOTREVIEW" if is_bot(author) else "COMMENT"
    return "BOTREVIEW" if is_review_tool(author) else "COMMENT"  # issue comment


def has_botreview(d: dict) -> bool:
    return (
        any(classify(r["author"], "review") == "BOTREVIEW" for r in d["new_reviews"])
        or any(
            classify(c["author"], "inline") == "BOTREVIEW"
            for c in d["new_review_comments"]
        )
        or any(classify(c["author"], "issue") == "BOTREVIEW" for c in d["new_comments"])
    )


def event_next(d: dict) -> str:
    if has_botreview(d):
        return "auto-address BOTREVIEW per references/pull-requests.md (unless told not to), then run watch again."
    return "react to the lines above, then run watch again."


# ------------------------------------------------------------------------ diff


def diff(old: dict | None, new: dict) -> dict:
    """High-signal delta between two snapshots. Empty lists => nothing notable."""
    old = old or {}
    oc, nc = old.get("checks", {}), new["checks"]
    new_fails, recovered, newly_done = [], [], []
    for name, ck in nc.items():
        was = oc.get(name)
        if is_fail(ck) and (was is None or not is_fail(was)):
            new_fails.append(
                {"name": name, "url": ck["url"], "conclusion": ck["conclusion"]}
            )
        terminal_now = is_terminal(ck)
        was_terminal = was and is_terminal(was)
        if terminal_now and not was_terminal and not is_fail(ck):
            newly_done.append(name)
        if was and is_fail(was) and not is_fail(ck) and terminal_now:
            recovered.append(name)

    def added(key):
        o = old.get(key, {})
        return [{"id": k, **v} for k, v in new[key].items() if k not in o]

    ci_just_settled = new["ci_settled"] and not old.get("ci_settled", False)
    state_changed = old and (
        new["pr_state"] != old.get("pr_state")
        or new["merged"] != old.get("merged", False)
    )

    return {
        "new_fails": new_fails,
        "recovered": recovered,
        "newly_done": newly_done,
        "ci_just_settled": ci_just_settled,
        "new_reviews": added("reviews"),
        "new_comments": added("comments"),
        "new_review_comments": added("review_comments"),
        "state_changed": bool(state_changed),
    }


def has_signal(d: dict, on: set[str]) -> bool:
    """Did anything the agent asked to be woken for happen?"""
    if "fail" in on and d["new_fails"]:
        return True
    if "done" in on and (d["ci_just_settled"] or d["newly_done"] or d["recovered"]):
        return True
    if "review" in on and d["new_reviews"]:
        return True
    if "comment" in on and (d["new_comments"] or d["new_review_comments"]):
        return True
    if "state" in on and d["state_changed"]:
        return True
    return False


# ------------------------------------------------------------------ rendering


def pending_checks(snap: dict) -> list[str]:
    return [
        n
        for n, c in snap["checks"].items()
        if c["status"] in PENDING_STATUS or c["status"] == ""
    ]


def render(snap: dict, d: dict, note: str = "") -> str:
    head = f"PR #{snap['pr']} {snap['repo']} {snap['pr_state']}"
    if snap["merged"] and snap["pr_state"] != "MERGED":
        head += " MERGED"
    lines = [head + (f"  {note}" if note else "")]
    for f in d["new_fails"]:
        lines.append(f"  FAIL    {f['name']} [{f['conclusion']}] {f['url']}")
    for n in d["recovered"]:
        lines.append(f"  FIXED   {n} now green")
    if d["ci_just_settled"]:
        ok, bad = count_checks(snap)
        lines.append(f"  DONE    all checks finished ({ok} ok, {bad} red)")
    elif d["newly_done"]:
        lines.append(f"  DONE    {', '.join(d['newly_done'])}")
    for r in d["new_reviews"]:
        who = "Copilot" if is_copilot(r["author"]) else r["author"]
        line = f"  {classify(r['author'], 'review'):9} {who}: {r['state']}"
        if r.get("excerpt"):
            line += f" — {r['excerpt']}"
        lines.append(line)
    for c in d["new_comments"]:
        who = "Copilot" if is_copilot(c["author"]) else f"@{c['author']}"
        lines.append(
            f"  {classify(c['author'], 'issue'):9} {who}: {c.get('excerpt', '')}"
        )
    for c in d["new_review_comments"]:
        who = "Copilot" if is_copilot(c["author"]) else f"@{c['author']}"
        lines.append(
            f"  {classify(c['author'], 'inline'):9} {who} {c.get('path', '')}: {c.get('excerpt', '')}"
        )
    if d["state_changed"]:
        lines.append(
            f"  STATE   -> {snap['pr_state']}{' (merged)' if snap['merged'] else ''}"
        )
    pend = pending_checks(snap)
    if pend:
        lines.append(f"  pending: {', '.join(sorted(pend))}")
    return "\n".join(lines)


def is_closed(snap: dict) -> bool:
    return bool(snap["merged"]) or snap["pr_state"] not in ("OPEN", "")


def verdict(name: str, terminal: bool, nxt: str) -> str:
    """The one self-documenting line that ends every run: outcome, whether the
    session is over, and the next action. The agent obeys this; nothing else to learn."""
    return f">> {name}: {'done' if terminal else 'ongoing'}. {nxt}"


# --------------------------------------------------------------------- state io


def state_path(repo: str, pr: int, watcher: str, override: str | None) -> Path:
    if override:
        return Path(override)
    base = (
        os.environ.get("BABYSIT_STATE_DIR") or Path(tempfile.gettempdir()) / "babysit"
    )
    slug = repo.replace("/", "_")
    return Path(base) / f"{slug}-pr{pr}-{watcher}.json"


def load_state(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def resolve_deadline(
    old: dict | None, max_total: float | None, reset: bool
) -> float | None:
    """Absolute wall-clock deadline, persisted so it spans every re-arm / re-watch.

    Set once (at arm, or first watch) from --max-total and preserved across episodes
    using the SAME --watcher. --reset-budget restarts it.
    """
    if old and old.get("deadline_ts") and not reset:
        return old["deadline_ts"]
    if max_total and max_total > 0:
        return time.time() + max_total
    return None


def budget_left(deadline: float | None) -> float | None:
    return None if deadline is None else deadline - time.time()


def save_state(p: Path, snap: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(snap))


def die(msg: str) -> None:
    print(f"babysit: {msg}", file=sys.stderr)
    sys.exit(2)


# -------------------------------------------------------------------- commands


def prepare(a) -> tuple[int, str, str, Path, dict | None]:
    """Shared command setup: resolve the PR and load this watcher's prior snapshot."""
    pr, repo, url = resolve(a.pr, a.repo)
    sp = state_path(repo, pr, a.watcher, a.state)
    return pr, repo, url, sp, load_state(sp)


def cmd_arm(a) -> int:
    pr, repo, url, sp, old = prepare(a)
    snap = fetch_snapshot(pr, repo, url)
    snap["deadline_ts"] = resolve_deadline(old, a.max_total, a.reset_budget)
    save_state(sp, snap)
    nxt = "baseline saved; run `watch` to begin reacting to events."
    if a.json:
        print(
            json.dumps(
                {
                    "pr": pr,
                    "repo": repo,
                    "url": url,
                    "state": str(sp),
                    "checks": len(snap["checks"]),
                    "ci_settled": snap["ci_settled"],
                    "outcome": "ARMED",
                    "terminal": False,
                    "next": nxt,
                }
            )
        )
        return 0
    ok, bad = count_checks(snap)
    pend = pending_checks(snap)
    print(f"armed PR #{pr} {repo} {snap['pr_state']}: {snap['title']}")
    print(f"  {url}")
    print(
        f"  checks: {len(snap['checks'])} ({ok} ok, {bad} red, {len(pend)} pending)"
        + (f" — pending: {', '.join(sorted(pend))}" if pend else "")
    )
    left = budget_left(snap["deadline_ts"])
    if left is not None:
        print(
            f"  budget: {int(left)}s total remaining (spans every re-watch on watcher '{a.watcher}')"
        )
    print(f"  watcher snapshot: {sp}")
    print(verdict("ARMED", False, nxt))
    return 0


def cmd_poll(a) -> int:
    pr, repo, url, sp, old = prepare(a)
    snap = fetch_snapshot(pr, repo, url)
    snap["deadline_ts"] = resolve_deadline(old, a.max_total, a.reset_budget)
    d = diff(old, snap)
    save_state(sp, snap)
    on = parse_on(a.on)
    left = budget_left(snap["deadline_ts"])
    signal = has_signal(d, on)

    if left is not None and left <= 0:
        name, terminal, nxt = "BUDGET SPENT", True, "time budget used up. stop."
    elif is_closed(snap):
        name, terminal, nxt = "CLOSED", True, "PR merged/closed. stop."
    elif old is None:
        name, terminal, nxt = (
            "BASELINE",
            False,
            "baseline saved; run `watch` to react to changes.",
        )
    elif signal:
        name, terminal, nxt = "EVENT", False, event_next(d)
    else:
        name, terminal, nxt = "QUIET", False, "nothing new since last check."

    if a.json:
        print(
            json.dumps(
                {
                    "delta": d,
                    "pending": pending_checks(snap),
                    "ci_settled": snap["ci_settled"],
                    "signal": signal,
                    "budget_left": None if left is None else int(left),
                    "outcome": name,
                    "terminal": terminal,
                    "next": nxt,
                }
            )
        )
        return 0
    if name in ("BASELINE", "EVENT"):
        print(
            render(
                snap,
                d,
                note=None if name == "EVENT" else "(first poll, baseline saved)",
            )
        )
    elif name in ("QUIET",):
        pend = pending_checks(snap)
        extra = f" pending: {', '.join(sorted(pend))}" if pend else " all checks done"
        print(f"PR #{pr} {repo} {snap['pr_state']} no change.{extra}")
    else:  # BUDGET SPENT / CLOSED
        print(f"PR #{pr} {repo} {snap['pr_state']}")
    print(verdict(name, terminal, nxt))
    return 0


def cmd_watch(a) -> int:
    pr, repo, url, sp, old = prepare(a)
    on = parse_on(a.on)
    start = time.time()
    interval = a.min_interval
    deadline = resolve_deadline(old, a.max_total, a.reset_budget)
    snap = old or fetch_snapshot(pr, repo, url)
    snap["deadline_ts"] = deadline
    save_state(sp, snap)
    if is_closed(snap):
        print(render(snap, empty_delta(), note="(already closed)"))
        print(verdict("CLOSED", True, "PR merged/closed. stop."))
        return 0
    settled_since: float | None = time.time() if snap["ci_settled"] else None
    polls = 0

    while True:
        waited = time.time() - start
        # Global budget: spans every episode (terminal, stop for good).
        if deadline is not None and time.time() >= deadline:
            print(render(snap, empty_delta(), note=f"(polls={polls})"))
            print(verdict("BUDGET SPENT", True, "time budget used up. stop."))
            return 0
        # Per-episode cap: not terminal, the caller is expected to re-run watch.
        if waited >= a.max_wait:
            print(
                render(
                    snap,
                    diff(None, snap) if a.show_state else empty_delta(),
                    note=f"(no event in {int(waited)}s, polls={polls})",
                )
            )
            print(verdict("QUIET", False, "no event yet; run the same watch again."))
            return 0

        # Comment tail is bounded: once CI is done, wait at most --comment-grace
        # for late reviews/comments, then stop instead of polling forever.
        if (
            settled_since is not None
            and (time.time() - settled_since) >= a.comment_grace
        ):
            print(
                render(
                    snap,
                    empty_delta(),
                    note=f"(quiet {int(a.comment_grace)}s after CI done)",
                )
            )
            print(verdict("SETTLED", True, "checks finished, no new activity. stop."))
            return 0

        nap = min(interval, a.max_wait - waited + 0.1)
        if deadline is not None:
            nap = min(nap, max(0.0, deadline - time.time()) + 0.1)
        time.sleep(nap)
        polls += 1
        new = fetch_snapshot(pr, repo, url)
        new["deadline_ts"] = deadline
        d = diff(snap, new)
        save_state(sp, new)

        if new["ci_settled"] and settled_since is None:
            settled_since = time.time()
        # New activity (comment/review) extends the tail so an active discussion
        # isn't cut off mid-stream, still capped by --max-wait overall.
        if d["new_comments"] or d["new_review_comments"] or d["new_reviews"]:
            settled_since = time.time() if new["ci_settled"] else None

        if is_closed(new):
            print(render(new, d, note=f"(+{int(time.time() - start)}s, polls={polls})"))
            print(verdict("CLOSED", True, "PR merged/closed. stop."))
            return 0
        if has_signal(d, on):
            print(render(new, d, note=f"(+{int(time.time() - start)}s, polls={polls})"))
            print(verdict("EVENT", False, event_next(d)))
            return 0

        snap = new
        # Adaptive backoff: changes reset to fast (handle the opening burst),
        # quiet stretches slow down toward --max-interval.
        if any_change(d):
            interval = a.min_interval
        else:
            interval = min(interval * 1.6, a.max_interval)


def empty_delta() -> dict:
    return {
        "new_fails": [],
        "recovered": [],
        "newly_done": [],
        "ci_just_settled": False,
        "new_reviews": [],
        "new_comments": [],
        "new_review_comments": [],
        "state_changed": False,
    }


def any_change(d: dict) -> bool:
    return (
        any(
            d[k]
            for k in (
                "new_fails",
                "recovered",
                "newly_done",
                "new_reviews",
                "new_comments",
                "new_review_comments",
            )
        )
        or d["state_changed"]
    )


def parse_on(on: str) -> set[str]:
    valid = {"fail", "done", "review", "comment", "state"}
    if not on or on == "all":
        return valid
    picked = {x.strip().lower() for x in on.split(",") if x.strip()}
    bad = picked - valid
    if bad:
        die(
            f"unknown --on values: {', '.join(bad)}. valid: {', '.join(sorted(valid))} (or 'all')"
        )
    return picked


# ------------------------------------------------------------------------ main


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="babysit",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--pr", help="PR number or URL (default: current branch's PR)")
        sp.add_argument("--repo", help="owner/repo (default: current repo)")
        sp.add_argument(
            "--watcher",
            default="default",
            help="state namespace; give each concurrent watcher its own id",
        )
        sp.add_argument("--state", help="explicit snapshot path (overrides --watcher)")
        sp.add_argument(
            "--max-total",
            type=float,
            default=None,
            help="total wall-clock budget in seconds, counted across EVERY re-watch "
            "on this --watcher; set once, returns BUDGET SPENT when exhausted",
        )
        sp.add_argument(
            "--reset-budget",
            action="store_true",
            help="restart the --max-total budget instead of preserving it",
        )

    a = sub.add_parser("arm", help="snapshot a baseline")
    common(a)
    a.add_argument("--json", action="store_true", help="machine-readable output")
    a.set_defaults(func=cmd_arm)

    po = sub.add_parser("poll", help="one-shot delta vs saved snapshot")
    common(po)
    po.add_argument(
        "--on", default="all", help="signal filter: fail,done,review,comment,state"
    )
    po.add_argument("--json", action="store_true", help="machine-readable output")
    po.set_defaults(func=cmd_poll)

    w = sub.add_parser("watch", help="block until a high-signal event or deadline")
    common(w)
    w.add_argument(
        "--on",
        default="all",
        help="wake on: fail,done,review,comment,state (default all)",
    )
    w.add_argument(
        "--min-interval", type=float, default=8.0, help="fastest poll gap, seconds"
    )
    w.add_argument(
        "--max-interval", type=float, default=60.0, help="slowest poll gap, seconds"
    )
    w.add_argument(
        "--max-wait", type=float, default=900.0, help="hard cap per episode, seconds"
    )
    w.add_argument(
        "--comment-grace",
        type=float,
        default=0.0,
        help="after all checks finish, seconds to keep waiting for late comments "
        "(default 0: settle now; a still-running check already keeps watch alive)",
    )
    w.add_argument(
        "--show-state",
        action="store_true",
        help="on timeout, print full state instead of just a one-liner",
    )
    w.set_defaults(func=cmd_watch)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
