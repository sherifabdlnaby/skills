# Watching a PR

Watch a PR's CI, reviews, and comments and react when something happens, no sleep loop.
[`scripts/pr-watch.py`](../scripts/pr-watch.py) (stdlib only, `python3`, run from the git skill's
directory) polls, diffs against a per-watcher snapshot, and prints only what changed. Don't read
its source. The defaults are the contract; every flag is in [`watch-flags.md`](./watch-flags.md),
open it only when the commands below do not fit.

## The contract

Every run ends with one `>>` line. Four kinds, four reactions:

```
>> EVENT: ongoing. <what to do>, then run watch again.     act, then run the same watch again
>> STALE: ongoing. nothing changed for 22m, 40m of budget left. ...   nudge the user, then run again
>> DONE: done. <reason>. stop.                             digest, stop
>> QUIET: ongoing. no event within this episode; ...       run the same watch again
```

Event lines above the verdict are self-evident tags: `PUSH`, `FAIL`, `FIXED`, `DONE` (all checks
finished), `BOTREVIEW` (an automated code review), `REVIEW` (human), `COMMENT`, `STATE`, `REVERT`
(a leftover poke undone). Each review or comment is a self-contained block with author, `(bot|human)`,
id, URL, and body lines. Trailing `pending:` and `review pending:` lines say what is still expected.

**`BOTREVIEW`: address it by default**, unless the user said not to, per
[review-responses.md](./review-responses.md). `FAIL`: fix, push, run the same watch again; the push
resets the check baseline, the budget, and the stale clock by itself.

The first run on a fresh `--watcher` reports the standing (red checks now). Reviews already on the
PR are history and stay silent: what still needs an answer among them comes from
[review-responses.md, Batching](./review-responses.md#batching), before the first watch.

## Modes

```
python3 scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO> --watcher <id> [--max-total <s>] \
    --until green --on fail,done,state          # green CI, nothing else
    --until quiet                               # green CI and reviews answered (default)
    --until closed --on review,comment,state    # reviews answered, CI is not mine
```

`--until quiet` waits for pending review-bot requests (Copilot shows up as one) and then for a short
silence, so a bot review landing right after the last check is not missed. `--max-total` is the
budget; without it the watch runs until `--until` or a merge/close.

## Who runs the loop

Two harness facts (verified on Claude Code and Cursor): a background shell wakes the agent that
started it when it exits; a background shell started by a sub-agent does not survive the
sub-agent's turn. So a sub-agent runs `watch` in the **foreground** and its return is the ping.

**A cheap sub-agent** (Haiku, Composer, the cheapest the harness offers) runs the loop. It does not
read the PR or the diff; it relays. It holds noise, judges nothing it cannot judge from the lines
themselves, and fetches one review thread only when a comment is not obvious on its face. Claude
Code runs it in the background, so the parent keeps working. Cursor runs it in the foreground, so
the parent waits on it; that is the price of a clean context there. Foreground `watch` calls sit
under the tool timeout: Claude Code caps a call at 10 minutes, hence `--max-wait 540`; set the
tool's timeout at its maximum.

The brief, short: the command, the Hold list from this conversation (known-flaky checks, expected
noise, a reviewer the user handles), and:

> On `QUIET` run it again. On `EVENT` return with the lines that need action (a red check, a
> `BOTREVIEW`, a human review requesting changes or asking a question, anything you cannot call
> noise); hold bot greetings, label and coverage chatter, a bare LGTM, and run again. On `STALE`
> or `DONE` return with the line and a digest: what you surfaced, what you held (counts), the final
> state. Terse, exact names and links.

The parent reacts, then relaunches the same watcher, same `--watcher` id.

**Fallback:** run `watch` as your own background command; the harness wakes you with the verdict.

## Draft PRs and review bots

Review bots skip drafts. When the mode answers bot reviews and the PR is a draft, flick it once
before the first watch:

```
python3 scripts/pr-watch.py poke --pr <N> --repo <OWNER/REPO>
```

Mechanical, no judgment: `[WIP]` on the title, mark ready, ten seconds, back to draft with the
original title and the human review requests the flip caused removed. One flick per head commit. A
marker file records the flip, and any later `watch` or `poke` run reverts a leftover one first, so a
killed process never leaves a PR ready.

Whether a bot picked it up is the watcher's call: a review that started lands as `BOTREVIEW`; none
after a few minutes on a repo you know has a bot means the flick was too short for it. Then hold the
PR open yourself, `gh pr ready <N>` now and `gh pr ready --undo <N>` once the review is in. Either
way marking ready notifies reviewers once, and the `[WIP]` title is what tells them to wait.

## The stale nudge

`STALE` comes at each 30% of the budget without any change (every 30 minutes without a budget) and
resets on activity. Print one line for the user and keep watching:

```
⚠️ PR #42 quiet 22m, 40m of budget left. pending: e2e (queued), review by Copilot. My call: keep.
```

The facts are in the verdict and the pending lines; the call is yours: stop, keep, or extend.
Never block on a question here; the user answers when they look.
