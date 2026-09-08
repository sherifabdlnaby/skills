# Watching a PR

Watch a PR's CI, reviews, and comments and react when something happens, no sleep loop.
[`scripts/pr-watch.py`](../scripts/pr-watch.py) (stdlib only, `python3`; `<git-skill-dir>` below is the
base directory the harness printed when this skill loaded) polls, diffs against a per-watcher
snapshot, and prints only what changed. Don't read its source. Every run ends in one `>>` line that
names the next action, and that line is the contract; `--help` has the rest.

## Steps

1. **Launch the watch and the flick in one batch:**

   ```bash
   python3 <git-skill-dir>/scripts/pr-watch.py watch --pr <PR_URL> --watcher <id>
   python3 <git-skill-dir>/scripts/pr-watch.py flick --pr <PR_URL>
   ```

   Name the PR by its URL, which carries the repo with it, and coin a fresh `--watcher` id for every
   watch you start: an id reaches an existing snapshot, with that watcher's baseline and its spent
   budget.

   The flick is what gets a draft looked at, since review bots skip drafts. Anywhere it is not
   wanted it answers `NOFLICK` in a second, so it is cheaper to send than to reason about. One per
   head commit: a push earns the pair again.

2. **Do what the `>>` line says.** Every run ends in exactly one, `EVENT`, `STALE`, `QUIET` or
   `DONE`, carrying the next action. What it refers to sits above it, one tagged line each: `PUSH`,
   `FAIL`, `FIXED`, `DONE` (checks finished, not the verdict), `BOTREVIEW` (automated) and `REVIEW`
   (human), `COMMENT`, `STATE`, `FLICK`, `REVERT`, closing with `pending:` and `review pending:` for
   what has yet to arrive. Review and comment lines come as self-contained blocks (author,
   `(bot|human)`, id, URL, body), so acting on one rarely needs a fetch.

3. **Run the same watch command again**, same `--watcher`, until a `>>` line says to stop.

Reviews already on the PR when the first watch starts are history and stay silent. Whatever among
them still needs an answer is work to do before step 1, per
[review-responses.md, Batching](./review-responses.md#batching).

## Other modes

The default (`--until quiet`) ends on green CI with nothing pending. Two others earn their flag:

```bash
--until green --on fail,done,state          # CI only, done when it is green
--until closed --on review,comment,state    # reviews only, CI is somebody else's
```

`--max-total <s>` puts a budget on the whole watch. Every other flag is in
[`watch-flags.md`](./watch-flags.md).

## Who runs the loop

**A cheap sub-agent** (Haiku, Composer, the cheapest the harness offers) runs the loop. It relays
rather than reviews: it never reads the PR or the diff, holds noise, and fetches one review item only
when a comment is not obvious on its face.

**Dispatch it in the background**, so the parent keeps working and the sub-agent's return is the
ping. On Cursor, foreground: the parent waits on it, which is the price of a clean context there.

Inside the sub-agent the shell call is **foreground**, with the tool timeout at its maximum (Claude
Code caps a call at 10 minutes, which the 540s default `--max-wait` fits). Two harness facts behind
that (verified 2026-09 on Claude Code and Cursor): a background shell wakes the agent that started
it when it exits, and a background shell started by a sub-agent does not survive the sub-agent's
turn.

The brief, short: the Hold list from this conversation (known-flaky checks, expected noise, a
reviewer the user handles), and:

> From `<git-skill-dir>`, run `python3 scripts/pr-watch.py watch --pr <PR_URL>
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

## Chasing

One flick is the whole invitation. Holding the PR open, flicking the same head again, waiting on a
bot that has not shown up: that is **chasing**, and it happens only on the user's word that the repo
has a bot, never inferred from its history. The user naming the bot, in any sentence, is that word.
Marking ready notifies reviewers once, which is the cost being spent each time.

A flick the user asked for, where a human may notice the PR mid-flip, takes `--wip` to carry `[WIP]`
on the title for the ten seconds it is ready.

## The stale nudge

`STALE` says nothing has changed for a while. Print one line for the user and keep watching:

```text
⚠️ PR #42 quiet 22m, 40m of budget left. pending: e2e (queued), review by Copilot. My call: keep.
```

The facts are in the verdict and the `pending:` lines; the call is yours: stop, keep, or extend.
Never block on a question here; the user answers when they look.
