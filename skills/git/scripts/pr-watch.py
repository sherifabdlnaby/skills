#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Watch a GitHub PR: poll CI, reviews, and comments, return only what changed.

Built for an agent to run. It does the predictable, token-heavy part: poll, diff
against a saved snapshot, and report only the delta. The agent does the thinking.

Subcommands
  watch   Block until something worth reacting to happens (or a stop condition),
          print it, exit. The one a watcher runs in a loop.
  flick   Draft PR: flick it to ready under a [WIP] title so review bots start,
          then back to draft with the original title.
Every run ends with one `>>` line, of four kinds:
  EVENT   ongoing: act on the lines above, then run watch again
  STALE   ongoing: nothing changed for a stretch; tell the user, then run watch again
  DONE    stop: the --until condition, a merge/close, or the budget
  QUIET   ongoing: the episode cap passed; run the same watch again

Stop conditions come from --until:
  green   all checks passed
  quiet   green, no pending review request, no activity for --comment-grace
  closed  only a merge/close ends it
A time budget (--max-total) ends any of them.

What counts as an event: a check going red or recovering, all checks finishing, a
review, a comment, a merge/close. A single check passing or a job starting only
updates the snapshot; the noisy opening burst stays quiet.

Each watcher keeps its OWN snapshot (via --watcher), so several agents can watch
the same PR without clobbering cursors. The first run on a fresh --watcher reports
the current standing (red checks now) and baselines reviews and comments, so old
history never surfaces as news.

A push changes the head SHA. The check baseline, the budget, and the stale clock
all reset with it, so a fix gets a full window and a re-failing check is reported.

Cadence is self-paced: hot (10-30s gaps) while something changed within the last
5 minutes, a flat 60s after that, and back to hot on any change.

Everything is stdlib; `gh` does auth and API. Run with plain `python3`.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCHEMA = 3

# Conclusions that mean a check is red. SKIPPED / NEUTRAL / SUCCESS are fine.
# CANCELLED counts: a cancelled required check blocks the merge until it reruns.
FAIL_CONCLUSIONS = {
    "FAILURE",
    "ERROR",
    "TIMED_OUT",
    "ACTION_REQUIRED",
    "STARTUP_FAILURE",
    "STALE",
    "CANCELLED",
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

HOT_WINDOW = 300.0  # seconds since the last change before the cadence cools down
NO_CHECKS_GRACE = 120.0  # a PR with no checks at all counts as green after this
WIP = "[WIP]"


# --------------------------------------------------------------------------- gh


def run_gh(args: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        die("gh not found on PATH. Install GitHub CLI.")
    except subprocess.TimeoutExpired:
        die(f"gh timed out: gh {' '.join(args)}")


def gh(args: list[str], check: bool = True) -> str:
    """Run a gh command, return stdout. Exits on failure unless check=False."""
    proc = run_gh(args)
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


def die(msg: str) -> None:
    print(f"pr-watch: {msg}", file=sys.stderr)
    sys.exit(2)


# ------------------------------------------------------------------- resolving


def resolve(pr: str | None, repo: str | None) -> tuple[int, str, str]:
    """Return (pr_number, base owner/repo, url). Defaults to the current branch's PR.

    The repo comes from the PR URL: on a fork PR `headRepository` is the fork, and
    reviews and comments live on the base repo."""
    args = ["pr", "view", "--json", "number,url"]
    if pr:
        args.insert(2, pr)
    if repo:
        args += ["--repo", repo]
    data = gh_json(args)
    if not data:
        die(
            "could not resolve a PR. Pass --pr <num|url> or run on a branch with an open PR."
        )
    url = data.get("url", "")
    m = re.search(r"github\.com/([^/]+/[^/]+)/pull/", url)
    base = m.group(1) if m else repo
    if not base:
        die("could not determine owner/repo. Pass --repo <owner/repo>.")
    return int(data["number"]), base, url


# -------------------------------------------------------------------- snapshot


def rest(repo: str, path: str) -> list[dict]:
    """Best-effort paginated GET of a REST list endpoint -> list of dicts (empty on
    any failure). `--paginate` merges every page into one JSON array; reshaping is
    done in Python (a `--jq` stream would emit JSON Lines that won't parse)."""
    out = gh_json(["api", f"repos/{repo}/{path}", "--paginate"], check=False)
    return [c for c in out if isinstance(c, dict)] if isinstance(out, list) else []


PR_FIELDS = "number,url,state,mergedAt,isDraft,reviewDecision,statusCheckRollup,title,headRefOid,reviewRequests"


def fetch_snapshot(pr: int, repo: str, url: str) -> dict:
    """One normalized picture of the PR: checks, reviews, comments, state.

    PR state + checks come from `gh pr view`. Reviews and comments come from REST,
    which (unlike `gh pr view`) carries `user.type` (the bot flag) and `html_url`
    per item, so each line the agent sees is self-contained."""
    data = gh_json(["pr", "view", str(pr), "--repo", repo, "--json", PR_FIELDS]) or {}

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

    requests = []
    for rr in data.get("reviewRequests") or []:
        login = rr.get("login") or rr.get("slug") or rr.get("name") or "?"
        requests.append({"login": login, "is_bot": rr.get("__typename") == "Bot"})

    def author(c: dict) -> dict:
        u = c.get("user") or {}
        return {"author": u.get("login") or "?", "is_bot": u.get("type") == "Bot"}

    reviews: dict[str, dict] = {}
    for r in rest(repo, f"pulls/{pr}/reviews"):
        if r.get("id") is None:
            continue
        reviews[str(r["id"])] = {
            **author(r),
            "state": r.get("state") or "",
            "sha": r.get("commit_id") or "",
            "at": r.get("submitted_at") or "",
            "body": trim_body(r.get("body")),
            "url": r.get("html_url") or "",
        }

    comments: dict[str, dict] = {}
    for c in rest(repo, f"issues/{pr}/comments"):
        comments[str(c.get("id"))] = {
            **author(c),
            "at": c.get("created_at") or "",
            "body": trim_body(c.get("body")),
            "url": c.get("html_url") or "",
        }

    review_comments: dict[str, dict] = {}
    for c in rest(repo, f"pulls/{pr}/comments"):
        review_comments[str(c.get("id"))] = {
            **author(c),
            "path": c.get("path") or "",
            "at": c.get("created_at") or "",
            "body": trim_body(c.get("body")),
            "url": c.get("html_url") or "",
        }

    return {
        "schema": SCHEMA,
        "repo": repo,
        "pr": pr,
        "url": data.get("url") or url,
        "title": data.get("title") or "",
        "pr_state": data.get("state") or "OPEN",
        "merged": bool(data.get("mergedAt")),
        "draft": bool(data.get("isDraft")),
        "head_sha": data.get("headRefOid") or "",
        "review_decision": data.get("reviewDecision") or "",
        "review_requests": requests,
        "checks": checks,
        "reviews": reviews,
        "comments": comments,
        "review_comments": review_comments,
        "ts": time.time(),
    }


def trim_body(body: str | None, n: int = 600) -> str:
    """Stored body, capped but newline-preserving so `snippet` can show a few lines."""
    if not body:
        return ""
    return body if len(body) <= n else body[: n - 1] + "…"


def snippet(body: str, max_lines: int = 4, width: int = 100) -> list[str]:
    """A few non-blank lines of a body for display; trailing `…` if more was cut."""
    if not body:
        return []
    lines = [ln.rstrip() for ln in body.splitlines() if ln.strip()]
    shown = [
        ln if len(ln) <= width else ln[: width - 1] + "…" for ln in lines[:max_lines]
    ]
    if len(lines) > max_lines:
        shown.append("…")
    return shown


def is_fail(check: dict) -> bool:
    return check.get("conclusion", "") in FAIL_CONCLUSIONS


def is_terminal(check: dict) -> bool:
    """A check has finished (passed, failed, or skipped), not still running."""
    status = check.get("status", "")
    return status not in PENDING_STATUS and status != ""


def checks_finished(snap: dict) -> bool:
    return bool(snap["checks"]) and all(
        is_terminal(ck) for ck in snap["checks"].values()
    )


def red_checks(snap: dict) -> list[str]:
    return [n for n, c in snap["checks"].items() if is_fail(c)]


def count_checks(snap: dict) -> tuple[int, int]:
    """(ok, red) counts over a snapshot's checks; ok = finished and not red (excludes pending)."""
    checks = snap["checks"].values()
    return (
        sum(1 for c in checks if is_terminal(c) and not is_fail(c)),
        sum(1 for c in checks if is_fail(c)),
    )


def pending_checks(snap: dict) -> list[str]:
    return [n for n, c in snap["checks"].items() if not is_terminal(c)]


def is_review_bot(item: dict) -> bool:
    return bool(item.get("is_bot"))


def pending_bot_reviews(snap: dict) -> list[str]:
    return [r["login"] for r in snap.get("review_requests", []) if is_review_bot(r)]


def is_copilot(login: str) -> bool:
    return "copilot" in login.lower()


def classify(item: dict, kind: str) -> str:
    """Line tag for a review/comment. kind: 'review' (submitted), 'inline' (on the
    diff), 'issue' (PR conversation). BOTREVIEW = an automated code review to
    address; a bot's PR-conversation comment is plain COMMENT (labels, CI chatter,
    greetings) and stays the watcher's call."""
    if kind == "review":
        return "BOTREVIEW" if item.get("is_bot") else "REVIEW"
    if kind == "inline":
        return "BOTREVIEW" if item.get("is_bot") else "COMMENT"
    return "COMMENT"


def has_botreview(d: dict) -> bool:
    return any(classify(r, "review") == "BOTREVIEW" for r in d["new_reviews"]) or any(
        classify(c, "inline") == "BOTREVIEW" for c in d["new_review_comments"]
    )


def event_next(d: dict) -> str:
    if d["new_fails"]:
        return "fix the red check(s), push, then run watch again."
    if has_botreview(d):
        return "address the BOTREVIEW per references/review-responses.md, then run watch again."
    return "react to the lines above, then run watch again."


# ------------------------------------------------------------------------ diff


def diff(old: dict | None, new: dict) -> dict:
    """High-signal delta between two snapshots. Empty lists => nothing notable.
    A head SHA change resets the check baseline: every check on the new head is new."""
    old = old or {}
    pushed = bool(old.get("head_sha")) and new["head_sha"] != old["head_sha"]
    oc = {} if pushed else old.get("checks", {})
    nc = new["checks"]
    new_fails, recovered = [], []
    for name, ck in nc.items():
        was = oc.get(name)
        if is_fail(ck) and (was is None or not is_fail(was)):
            new_fails.append(
                {"name": name, "url": ck["url"], "conclusion": ck["conclusion"]}
            )
        if was and is_fail(was) and not is_fail(ck) and is_terminal(ck):
            recovered.append(name)

    def added(key):
        o = old.get(key, {})
        return [{"id": k, **v} for k, v in new[key].items() if k not in o]

    was_finished = bool(old) and not pushed and checks_finished(old)
    return {
        "pushed": pushed,
        "checks_moved": any(nc.get(n) != oc.get(n) for n in set(nc) | set(oc)),
        "new_fails": new_fails,
        "recovered": recovered,
        "ci_just_settled": checks_finished(new) and not was_finished,
        "new_reviews": added("reviews"),
        "new_comments": added("comments"),
        "new_review_comments": added("review_comments"),
        "state_changed": bool(old)
        and (
            new["pr_state"] != old.get("pr_state")
            or new["merged"] != old.get("merged", False)
        ),
    }


def empty_delta() -> dict:
    return {
        "pushed": False,
        "checks_moved": False,
        "new_fails": [],
        "recovered": [],
        "ci_just_settled": False,
        "new_reviews": [],
        "new_comments": [],
        "new_review_comments": [],
        "state_changed": False,
    }


def standing(snap: dict) -> dict:
    """Delta for a fresh watcher: what is red right now, nothing else. Reviews and
    comments already on the PR are history, not news."""
    d = empty_delta()
    d["new_fails"] = [
        {"name": n, "url": c["url"], "conclusion": c["conclusion"]}
        for n, c in snap["checks"].items()
        if is_fail(c)
    ]
    return d


def has_signal(d: dict, on: set[str]) -> bool:
    """Did anything the caller asked to be woken for happen? A single check
    passing is not a signal (the pending line on the next event shows progress)."""
    if "fail" in on and d["new_fails"]:
        return True
    if "done" in on and (d["ci_just_settled"] or d["recovered"]):
        return True
    if "review" in on and d["new_reviews"]:
        return True
    if "comment" in on and (d["new_comments"] or d["new_review_comments"]):
        return True
    if "state" in on and d["state_changed"]:
        return True
    return False


def any_change(d: dict) -> bool:
    """Anything moved on the PR, signal or not; resets the cadence and the stale clock."""
    return any(bool(v) for k, v in d.items())


INDENT = " " * 12  # continuation lines align under the tag column


def who(item: dict) -> str:
    """`@login (bot)` / `Copilot (bot)` / `@login (human)`: author plus a bot flag."""
    name = "Copilot" if is_copilot(item["author"]) else f"@{item['author']}"
    return f"{name} ({'bot' if item.get('is_bot') else 'human'})"


def render_item(tag: str, head_extra: str, item: dict) -> list[str]:
    """A multi-line block: tag/author/id header, the URL, then a body snippet.
    Self-contained enough for the agent to act without a follow-up fetch."""
    head = f"  {tag:9} {who(item)}"
    if head_extra:
        head += f" {head_extra}"
    head += f" · #{item['id']}"
    out = [head]
    if item.get("url"):
        out.append(f"{INDENT}{item['url']}")
    out += [f"{INDENT}{ln}" for ln in snippet(item.get("body", ""))]
    return out


def render(snap: dict, d: dict, note: str = "", extra: list[str] | None = None) -> str:
    head = f"PR #{snap['pr']} {snap['repo']} {snap['pr_state']}"
    if snap["merged"] and snap["pr_state"] != "MERGED":
        head += " MERGED"
    if snap.get("draft"):
        head += " DRAFT"
    lines = [head + (f"  {note}" if note else "")]
    lines += extra or []
    if d["pushed"]:
        lines.append(f"  PUSH    head is now {snap['head_sha'][:7]}, checks restarted")
    for f in d["new_fails"]:
        lines.append(f"  FAIL    {f['name']} [{f['conclusion']}]")
        if f.get("url"):
            lines.append(f"{INDENT}{f['url']}")
    for n in d["recovered"]:
        lines.append(f"  FIXED   {n} now green")
    if d["ci_just_settled"]:
        ok, bad = count_checks(snap)
        lines.append(f"  DONE    all checks finished ({ok} ok, {bad} red)")
    for r in d["new_reviews"]:
        lines += render_item(classify(r, "review"), r.get("state", ""), r)
    for c in d["new_comments"]:
        lines += render_item(classify(c, "issue"), "", c)
    for c in d["new_review_comments"]:
        lines += render_item(classify(c, "inline"), c.get("path", ""), c)
    if d["state_changed"]:
        lines.append(
            f"  STATE   -> {snap['pr_state']}{' (merged)' if snap['merged'] else ''}"
        )
    pend = pending_checks(snap)
    if pend:
        lines.append(f"  pending: {', '.join(sorted(pend))}")
    bots = pending_bot_reviews(snap)
    if bots:
        lines.append(f"  review pending: {', '.join(sorted(bots))}")
    return "\n".join(lines)


def is_closed(snap: dict) -> bool:
    return bool(snap["merged"]) or snap["pr_state"] not in ("OPEN", "")


def verdict(name: str, terminal: bool, nxt: str) -> str:
    """The one self-documenting line that ends every run: outcome, whether the
    session is over, and the next action. The agent obeys this; nothing else to learn."""
    return f">> {name}: {'done' if terminal else 'ongoing'}. {nxt}"


def minutes(s: float) -> str:
    return f"{int(s // 60)}m" if s >= 60 else f"{int(s)}s"


# --------------------------------------------------------------------- state io


def state_dir() -> Path:
    return Path(
        os.environ.get("WATCH_STATE_DIR") or Path(tempfile.gettempdir()) / "watch"
    )


def state_path(repo: str, pr: int, watcher: str, override: str | None) -> Path:
    if override:
        return Path(override)
    return state_dir() / f"{repo.replace('/', '_')}-pr{pr}-{watcher}.json"


def flick_marker(repo: str, pr: int) -> Path:
    return state_dir() / f"{repo.replace('/', '_')}-pr{pr}-flick.json"


def load_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_state(p: Path) -> dict | None:
    st = load_json(p)
    return st if st and st.get("schema") == SCHEMA else None


def save_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data))


# ------------------------------------------------------------------- settling


def settled_kind(snap: dict, last_change: float) -> str | None:
    """'red', 'green', or None while checks are still running. A PR with no checks at
    all counts as green once nothing has changed for NO_CHECKS_GRACE."""
    if snap["checks"]:
        if not checks_finished(snap):
            return None
        return "red" if red_checks(snap) else "green"
    return "green" if time.time() - last_change >= NO_CHECKS_GRACE else None


def red_key(snap: dict) -> str:
    """Identity of a red settle, reported once per head + set of red checks."""
    return snap["head_sha"] + ":" + ",".join(sorted(red_checks(snap)))


# ------------------------------------------------------------------------ flick


def bot_items_on_head(snap: dict) -> int:
    """Bot reviews and inline comments made against the current head."""
    n = sum(
        1
        for r in snap["reviews"].values()
        if r.get("is_bot") and r.get("sha") == snap["head_sha"]
    )
    return n + sum(1 for c in snap["review_comments"].values() if c.get("is_bot"))


def revert_flick(pr: int, repo: str, marker: dict) -> list[str]:
    """Undo a flick: back to draft, original title, review requests it caused removed.
    Best effort per step; what could not be undone is named on stderr."""
    done: list[str] = []

    def step(args: list[str], label: str, by_hand: str) -> None:
        if run_gh(["pr", *args, str(pr), "--repo", repo]).returncode == 0:
            done.append(label)
        else:
            print(
                f"PR #{pr} {repo} could not {by_hand}; do it by hand", file=sys.stderr
            )

    step(["ready", "--undo"], "draft", "convert back to draft")
    step(
        ["edit", "--title", marker["title"]],
        "title",
        f"restore the title {marker['title']!r}",
    )
    data = (
        gh_json(
            ["pr", "view", str(pr), "--repo", repo, "--json", "reviewRequests"],
            check=False,
        )
        or {}
    )
    was = set(marker.get("reviewers_before", []))
    added = [
        rr.get("login") or rr.get("slug") or rr.get("name")
        for rr in data.get("reviewRequests") or []
        if rr.get("__typename") != "Bot"
    ]
    added = [a for a in added if a and a not in was]
    if added:
        step(
            ["edit", "--remove-reviewer", ",".join(added)],
            f"removed reviewers {', '.join(added)}",
            "remove the review requests it caused",
        )
    return done


def load_flick(repo: str, pr: int) -> dict:
    return load_json(flick_marker(repo, pr)) or {"flickd": []}


def save_flick(repo: str, pr: int, data: dict) -> None:
    save_json(flick_marker(repo, pr), data)


def revert_leftover_flick(pr: int, repo: str, snap: dict) -> list[str]:
    """A flick that died mid-way leaves its flip in the marker; any later run puts
    the PR back before doing its own work, so a flip never outlives its process."""
    data = load_flick(repo, pr)
    inflight = data.pop("inflight", None)
    if not inflight:
        return []
    lines = []
    if not snap["draft"] and snap["title"].startswith(WIP):
        done = revert_flick(pr, repo, inflight)
        lines.append(f"  REVERT  leftover flick undone: {', '.join(done) or 'nothing'}")
    save_flick(repo, pr, data)
    return lines


def cmd_flick(a) -> int:
    """Flick a draft: ready under a [WIP] title, --hold seconds, back to draft.
    Whether a review bot picked it up is the watcher's call, not this command's.
    The marker file makes the revert survive a killed process and keeps the
    flick to one per head."""
    pr, repo, url = resolve(a.pr, a.repo)
    before = fetch_snapshot(pr, repo, url)
    head = f"PR #{pr} {repo}"
    for ln in revert_leftover_flick(pr, repo, before):
        print(ln)
        before = fetch_snapshot(pr, repo, url)
    data = load_flick(repo, pr)

    def noflick(why: str) -> int:
        print(head)
        print(verdict("NOFLICK", True, why))
        return 0

    if is_closed(before):
        return noflick("PR merged/closed. nothing to flick.")
    if not before["draft"]:
        return noflick("not a draft; review bots already had their chance.")
    if bot_items_on_head(before) or pending_bot_reviews(before):
        return noflick("a bot review already exists or is pending on this head.")
    if before["head_sha"] in data["flickd"]:
        return noflick(
            "this head was flicked already; chasing further is the user's call."
        )

    title = before["title"]
    wip = title if title.startswith(WIP) else f"{WIP} {title}"
    if a.dry_run:
        print(
            f"{head} DRAFT  would: retitle to {wip!r}, mark ready, wait {int(a.hold)}s, revert"
        )
        print(verdict("DRYRUN", True, "nothing changed."))
        return 0

    inflight = {
        "title": title,
        "started": time.time(),
        "reviewers_before": [r["login"] for r in before["review_requests"]],
    }
    data["inflight"] = inflight
    data["flickd"] = sorted(set(data["flickd"]) | {before["head_sha"]})
    save_flick(repo, pr, data)
    gh(["pr", "edit", str(pr), "--repo", repo, "--title", wip])
    gh(["pr", "ready", str(pr), "--repo", repo])
    print(f"{head} ready as {wip!r} for {int(a.hold)}s")
    try:
        time.sleep(a.hold)
    finally:
        done = revert_flick(pr, repo, inflight)
        data.pop("inflight", None)
        save_flick(repo, pr, data)
        print(f"{head} reverted: {', '.join(done) or 'nothing'}")
    print(
        verdict(
            "FLICKED",
            True,
            "a bot review, if any, lands as BOTREVIEW on the watch.",
        )
    )
    return 0


# ----------------------------------------------------------------------- watch


def bounds(a, last_change: float) -> tuple[float, float]:
    """(min, max) poll gap for the current cadence phase.

    Hot (10-30s) while something changed within the last HOT_WINDOW seconds, cold
    (flat 60s) after. Explicit --min/--max-interval flags override their side."""
    hot = (time.time() - last_change) < HOT_WINDOW
    lo = a.min_interval if a.min_interval is not None else (10.0 if hot else 60.0)
    hi = a.max_interval if a.max_interval is not None else (30.0 if hot else 60.0)
    return lo, max(lo, hi)


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


def cmd_watch(a) -> int:
    pr, repo, url = resolve(a.pr, a.repo)
    sp = state_path(repo, pr, a.watcher, a.state)
    old = load_state(sp)
    on = parse_on(a.on)
    grace = (
        a.comment_grace
        if a.comment_grace is not None
        else (120.0 if a.until == "quiet" else 0.0)
    )
    start = time.time()

    # Budget and stale clock persist per watcher; a push resets both (below).
    budget = a.max_total if a.max_total else (old or {}).get("budget")
    deadline = (old or {}).get("deadline") if old and not a.max_total else None
    if budget and deadline is None:
        deadline = start + budget
    stale_step = (budget * a.stale_pct / 100.0) if budget else a.stale
    last_change = (old or {}).get("last_change_ts") or start
    stale_steps = (old or {}).get("stale_steps", 0)
    red_reported = (old or {}).get("red_reported", "")
    interval, _ = bounds(a, last_change)
    polls = 0

    snap = old or fetch_snapshot(pr, repo, url)
    extra = revert_leftover_flick(pr, repo, snap)
    d = empty_delta() if old else standing(snap)

    def finish(name: str, terminal: bool, nxt: str, delta: dict, note: str) -> int:
        snap.update(
            budget=budget,
            deadline=deadline,
            last_change_ts=last_change,
            stale_steps=stale_steps,
            red_reported=red_reported,
        )
        save_json(sp, snap)
        print(render(snap, delta, note=note, extra=extra))
        print(verdict(name, terminal, nxt))
        return 0

    while True:
        note = f"(+{int(time.time() - start)}s, polls={polls})"
        if is_closed(snap):
            return finish(
                "DONE",
                True,
                f"PR {'merged' if snap['merged'] else 'closed'}. stop.",
                d,
                note,
            )
        if deadline is not None and time.time() >= deadline:
            return finish("DONE", True, "time budget used up. stop.", d, note)
        kind = settled_kind(snap, last_change)
        if has_signal(d, on):
            if d["new_fails"]:
                red_reported = red_key(snap)
            return finish("EVENT", False, event_next(d), d, note)
        if "fail" in on and kind == "red" and red_reported != red_key(snap):
            red_reported = red_key(snap)
            d["new_fails"] = standing(snap)["new_fails"]
            return finish(
                "EVENT",
                False,
                "checks finished with failures. fix, push, then run watch again.",
                d,
                note,
            )
        if kind == "green" and a.until == "green":
            ok, _ = count_checks(snap)
            return finish("DONE", True, f"all checks passed ({ok} ok). stop.", d, note)
        if (
            kind == "green"
            and a.until == "quiet"
            and not pending_bot_reviews(snap)
            and time.time() - last_change >= grace
        ):
            return finish(
                "DONE",
                True,
                f"checks green, no review pending, quiet for {minutes(grace)}. stop.",
                d,
                note,
            )
        quiet_for = time.time() - last_change
        if stale_step > 0 and math.floor(quiet_for / stale_step) > stale_steps:
            stale_steps = math.floor(quiet_for / stale_step)
            left = (
                "no budget"
                if deadline is None
                else f"{minutes(max(0.0, deadline - time.time()))} of budget left"
            )
            return finish(
                "STALE",
                False,
                f"nothing changed for {minutes(quiet_for)}, {left}. tell the user (⚠️ line: what is "
                "pending, your call: stop / keep / extend), then run watch again.",
                d,
                note,
            )
        if time.time() - start >= a.max_wait:
            return finish(
                "QUIET",
                False,
                "no event within this episode; run the same watch again.",
                d,
                note,
            )

        lo, hi = bounds(a, last_change)
        nap = min(max(lo, min(interval, hi)), a.max_wait - (time.time() - start) + 0.1)
        if deadline is not None:
            nap = min(nap, max(0.0, deadline - time.time()) + 0.1)
        time.sleep(max(nap, 0.0))
        polls += 1
        new = fetch_snapshot(pr, repo, url)
        d = diff(snap, new)
        if any_change(d):
            last_change = time.time()
            stale_steps = 0
        if d["pushed"] and budget:
            deadline = time.time() + budget
        snap = new
        # Adaptive backoff within the phase bounds: changes reset to the fast end
        # (handle the opening burst), quiet stretches slow toward the top.
        interval = lo if any_change(d) else min(interval * 1.6, hi)


# ------------------------------------------------------------------------ main


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pr-watch",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    def target(sp):
        sp.add_argument("--pr", help="PR number or URL (default: current branch's PR)")
        sp.add_argument("--repo", help="owner/repo (default: current repo)")

    w = sub.add_parser("watch", help="block until an event or a stop condition")
    target(w)
    w.add_argument(
        "--watcher",
        default="default",
        help="state namespace; one per concurrent watcher",
    )
    w.add_argument("--state", help="explicit snapshot path (overrides --watcher)")
    w.add_argument(
        "--until",
        choices=["green", "quiet", "closed"],
        default="quiet",
        help="stop condition: green = all checks passed; quiet = green + no review "
        "pending + no activity for --comment-grace; closed = only merge/close (default quiet)",
    )
    w.add_argument(
        "--on",
        default="all",
        help="wake on: fail,done,review,comment,state (default all)",
    )
    w.add_argument(
        "--max-total",
        type=float,
        default=None,
        help="time budget in seconds, persisted per --watcher across re-runs and reset by a "
        "push; ends with DONE when used up (default: none)",
    )
    w.add_argument(
        "--stale-pct",
        type=float,
        default=30.0,
        help="with a budget: percent of it without any change before a STALE nudge, "
        "repeated at each step (default 30)",
    )
    w.add_argument(
        "--stale",
        type=float,
        default=1800.0,
        help="without a budget: seconds without any change before a STALE nudge, "
        "repeated at each step (default 1800; 0 disables)",
    )
    w.add_argument(
        "--max-wait",
        type=float,
        default=540.0,
        help="cap per episode, seconds; returns QUIET and expects a re-run. Fits under a "
        "10-minute tool timeout (default 540)",
    )
    w.add_argument(
        "--comment-grace",
        type=float,
        default=None,
        help="with --until quiet: seconds of no activity after green before DONE (default 120)",
    )
    w.add_argument(
        "--min-interval",
        type=float,
        default=None,
        help="override the fastest poll gap, seconds (default: 10 while active, 60 when quiet)",
    )
    w.add_argument(
        "--max-interval",
        type=float,
        default=None,
        help="override the slowest poll gap, seconds (default: 30 while active, 60 when quiet)",
    )
    w.set_defaults(func=cmd_watch)

    pk = sub.add_parser(
        "flick", help="draft PR: flick it to ready under [WIP], then back to draft"
    )
    target(pk)
    pk.add_argument(
        "--hold", type=float, default=10.0, help="seconds to stay ready (default 10)"
    )
    pk.add_argument(
        "--dry-run", action="store_true", help="print what would happen, change nothing"
    )
    pk.set_defaults(func=cmd_flick)
    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
