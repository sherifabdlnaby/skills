# Watching a PR

Watch a PR's CI, reviews, and comments and react when something happens, no sleep loop.
[`scripts/pr-watch.py`](../scripts/pr-watch.py) (stdlib only, `python3`; `<git-skill-dir>` below is the base
directory the harness printed when this skill loaded) polls, diffs against a per-watcher snapshot, and prints only what changed. Don't read
its source. The defaults are the contract; every flag is in [`watch-flags.md`](./watch-flags.md),
open it only when the commands below do not fit.

## The contract

Every run ends with one `>>` line, of four kinds:

```
>> EVENT: ongoing. <what to do>, then run watch again.
>> STALE: ongoing. nothing changed for 22m, 40m of budget left. tell the user ..., then run watch again.
>> DONE: done. <reason>. stop.
>> QUIET: ongoing. no event within this episode; run the same watch again.
```

Event lines above the verdict are self-evident tags: `PUSH`, `FAIL`, `FIXED`, `DONE` (all checks
finished), `BOTREVIEW` (an automated code review), `REVIEW` (human), `COMMENT`, `STATE`, `REVERT`
(a leftover flick undone). Each review or comment is a self-contained block with author, `(bot|human)`,
id, URL, and body lines. Trailing `pending:` and `review pending:` lines say what is still expected.

**`BOTREVIEW`: address it by default**, unless the user said not to, per
[review-responses.md](./review-responses.md). `FAIL`: fix, push, run the same watch again; the push
resets the check baseline, the budget, and the stale clock by itself.

The first run on a fresh `--watcher` reports the standing (red checks now). Reviews already on the
PR are history and stay silent: what still needs an answer among them comes from
[review-responses.md, Batching](./review-responses.md#batching), before the first watch.

## Modes

```
python3 <git-skill-dir>/scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO> --watcher <id> [--max-total <s>] \
    --until green --on fail,done,state          # green CI, nothing else
    --until quiet                               # green CI, nothing pending, then quiet (default)
    --until closed --on review,comment,state    # reviews, CI is not mine
```

`--pr` and `--repo` default to the current branch's PR. `--until quiet` waits for pending review-bot
requests (Copilot shows up as one) and then for a short silence, so a bot review landing right after
the last check is not missed. No mode waits for review threads to be answered; answering them is
your work as the `EVENT`s arrive. `--max-total` is the budget; without it the watch runs until
`--until` or a merge/close.

## Who runs the loop

Two harness facts (verified 2026-09 on Claude Code and Cursor): a background shell wakes the agent that
started it when it exits; a background shell started by a sub-agent does not survive the
sub-agent's turn. So a sub-agent runs `watch` in the **foreground** and its return is the ping.

**A cheap sub-agent** (Haiku, Composer, the cheapest the harness offers) runs the loop. It does not
read the PR or the diff; it relays. It holds noise, judges nothing it cannot judge from the lines
themselves, and fetches one review item only when a comment is not obvious on its face. Two things
are foreground or not: the shell call inside the sub-agent is always foreground, under the tool
timeout (Claude Code caps a call at 10 minutes; the 540s default `--max-wait` already fits, so set
the tool's timeout at its maximum). The sub-agent itself runs in the background in Claude Code, so
the parent keeps working, and in the foreground in Cursor, where the parent waits on it; that is the
price of a clean context there.

The brief, short: the Hold list from this conversation (known-flaky checks, expected noise, a
reviewer the user handles), and:

> From `<git-skill-dir>`, run `python3 scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO>
> --watcher <id> [--max-total <s>]` in the foreground, tool timeout at its maximum, same
> `WATCH_STATE_DIR` as mine if I set one. The `>>` line's "run watch again" is written for me; you:
> on `QUIET` run it again (the budget or the PR's close is what ends this); on `EVENT` return with
> the lines that need action (a red check, a `BOTREVIEW`, a human review requesting changes or asking
> a question, anything you cannot call noise); hold bot greetings, label and coverage chatter, a bare
> LGTM, and run again; on `STALE` or `DONE` return with the line and a digest: what you surfaced,
> what you held (counts), the final state. A comment you cannot read on its face: one item by its
> id, `gh api repos/<OWNER/REPO>/pulls/<N>/comments/<id>` (inline) or `.../pulls/<N>/reviews/<id>`,
> nothing more. Terse, exact names and links.

The parent reacts, then relaunches the same watcher, same `--watcher` id.

**Fallback:** run `watch` as your own background command; the harness wakes you with the verdict.

## Draft PRs and review bots

Review bots skip drafts. In a mode that answers bot reviews, a draft is always flicked, alongside
the watch rather than before it:

```
python3 <git-skill-dir>/scripts/pr-watch.py flick --pr <N> --repo <OWNER/REPO>
```

Mechanical, no judgment: mark ready, ten seconds, back to draft with the human review requests the
flip caused removed. One flick per head commit. A marker file records the flip, and any later `watch`
or `flick` run reverts a leftover one first, so a killed process never leaves a PR ready. A flick you
run on the user's nudge, where a human may notice the PR, takes `--wip` to carry `[WIP]` on the title
for the duration. Its own `>>` line: `FLICKED` (done, nothing more to do), `NOFLICK` with the reason
(not a draft, merged, a bot review already there or pending on this head, or this head flicked
already: nothing to do, the review came or is coming), `DRYRUN`.

The flick is assumed to be enough: the review, if one comes, lands as `BOTREVIEW` on the watch, and
outside a watch it arrives on GitHub like any other review; `--until closed --on review,comment,state`
picks it up when the user wants it answered. Anything beyond the flick is chasing (holding the PR
open, flicking again, waiting on a bot that has not shown up), and chasing happens only on the user's
word that the repo has a bot, never inferred from its history. The user naming the bot, in any
sentence, is that word. Marking ready notifies reviewers once.

## The stale nudge

`STALE` comes at the first poll past each 30% of the budget without any change (every 30 minutes
without a budget) and resets on activity. Print one line for the user and keep watching:

```
⚠️ PR #42 quiet 22m, 40m of budget left. pending: e2e (queued), review by Copilot. My call: keep.
```

The facts are in the verdict and the pending lines; the call is yours: stop, keep, or extend.
Never block on a question here; the user answers when they look.
