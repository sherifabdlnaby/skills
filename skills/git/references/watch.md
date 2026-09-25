# Watching a PR

Watch a PR's CI, reviews, and comments, and react when something changes. No sleep loop.

- The tool is [`scripts/pr-watch.py`](../scripts/pr-watch.py) (`python3`, stdlib only).
- `<git-skill-dir>` below is the base directory the harness printed when this skill loaded.
- It polls the PR, compares with its last snapshot, and prints only what changed.
- Don't read its source. The defaults below are the contract. All flags are in
  [`watch-flags.md`](./watch-flags.md); open it only when the commands below do not fit.

## Flow

1. **Pick a mode** (see [Modes](#modes)). Reviews already on the PR do not show up in the watch.
2. **Draft PR?** In a mode that answers bot reviews, flick it (see [Draft PRs](#draft-prs-and-review-bots)).
3. **Start a cheap sub-agent** to run the watch (see [Who runs the loop](#who-runs-the-loop)).
4. **React** to what it returns, then start the same watcher again, with the same `--watcher` id.

## Modes

```
python3 <git-skill-dir>/scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO> --watcher <id> [--max-total <s>] \
    --until green --on fail,done,state          # green CI, nothing else
    --until quiet                               # green CI, nothing pending, then quiet (default)
    --until closed --on review,comment,state    # reviews, CI is not mine
```

- `--pr` and `--repo` default to the current branch's PR.
- `--until quiet` also waits for pending review-bot requests (Copilot shows up as one), then for a
  short silence. So a bot review that lands right after the last check is not missed.
- No mode waits for review threads to be answered. Answering them is your work, as events arrive.
- `--max-total` is the time budget. Without it, the watch runs until `--until` is met or the PR is
  merged or closed.

## Reading the output

Every run ends with one `>>` line:

| Verdict | Example                                                                                                    | What to do                                            |
| ------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `EVENT` | `>> EVENT: ongoing. <what to do>, then run watch again.`                                                   | Act on it, then run again.                            |
| `STALE` | `>> STALE: ongoing. nothing changed for 22m, 40m of budget left. tell the user ..., then run watch again.` | Tell the user ([nudge](#the-stale-nudge)), run again. |
| `QUIET` | `>> QUIET: ongoing. no event within this episode; run the same watch again.`                               | Run the same watch again.                             |
| `DONE`  | `>> DONE: done. <reason>. stop.`                                                                           | Stop.                                                 |

Event lines above the verdict start with a tag:

- `PUSH`: a new head commit; checks restarted.
- `FAIL`: a check went red. `FIXED`: a red check is green again.
- `DONE`: all checks finished.
- `BOTREVIEW`: an automated code review. **Answer it by default**, unless the user said not to.
- `REVIEW`: a human review.
- `COMMENT`: a comment.
- `STATE`: the PR was closed, merged, or reopened.
- `REVERT`: a leftover flick was undone.

Each review or comment comes as a block: author, `(bot|human)`, id, URL, and the body. At the end,
`pending:` and `review pending:` lines say what is still expected.

- **On `FAIL`:** fix, push, run the same watch again. The push resets the check baseline, the
  budget, and the stale clock.
- **First run on a new `--watcher`:** it reports where the PR stands now (for example, red checks).

## Who runs the loop

**A cheap sub-agent** (Haiku, Composer, the cheapest the harness offers) runs the loop:

- **The sub-agent runs in the background**, so the user can keep talking to you and ask for status
  while it watches. Its return is the ping.
- **Its shell call runs in the background when possible, then fall back to foreground**, with the tool timeout at its maximum. In some harnesses
  (Cursor), a background shell started by a sub-agent ends when the sub-agent's turn ends.
- It relays. It does not read the PR or the diff.
- It holds back noise and judges only what the lines themselves show.
- It fetches one review item only when a comment is not clear on its own.

Give it a short brief: what to hold back from this conversation (known-flaky checks, expected noise,
a reviewer the user handles), and this:

> From `<git-skill-dir>`, run `python3 scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO>
> --watcher <id> [--max-total <s>]` in the foreground, tool timeout at its maximum, same
> `WATCH_STATE_DIR` as mine if I set one. The `>>` line's "run watch again" is written for me. You:
>
> - On `QUIET`: run it again. The budget or the PR closing ends this.
> - On `EVENT`: return with the lines that need action: a red check, a `BOTREVIEW`, a human review
>   that requests changes or asks a question, anything you cannot call noise. Hold bot greetings,
>   label and coverage chatter, and a bare LGTM, and run again.
> - On `STALE` or `DONE`: return with the line and a digest: what you surfaced, what you held
>   (counts), the final state.
> - A comment you cannot read on its face: fetch that one item by its id,
>   `gh api repos/<OWNER/REPO>/pulls/<N>/comments/<id>` (inline) or `.../pulls/<N>/reviews/<id>`,
>   nothing more.
>
> Terse, exact names and links.

**Fallback:** run `watch` as your own background command. The harness wakes you with the verdict.

## Draft PRs and review bots

Review bots skip drafts. flick a draft, at the same time
as the watch (not before it):

```
python3 <git-skill-dir>/scripts/pr-watch.py flick --pr <N> --repo <OWNER/REPO>
```

What a flick does:

- Marks the PR ready, waits ten seconds, and sets it back to draft.
- Removes the human review requests that the flip caused. Marking ready still notifies reviewers once (we accept that).
- Runs once per head commit.
- Add `--wip` when you flick on the user's nudge and a human may see the PR. It puts `[WIP]` on the
  title while the PR is ready.

Its `>>` line:

- `FLICKED`: done, nothing more to do.
- `NOFLICK` with a reason: not a draft, merged, a bot review is already there or pending on this
  head, or this head was already flicked. Nothing to do.
- `DRYRUN`.

One flick is usually enough:
- More than one flick is **chasing**: holding the PR open, flicking again, waiting on a bot that has
  not shown up. Chase only when the user says the repo has a bot. Naming the bot, in any sentence,
  counts. Never guess it from the repo's history.

## The stale nudge

- `STALE` comes when nothing changed for 30% of the budget (every 30 minutes with no budget). It
  resets on any activity.
- Print one line for the user and keep watching:

  ```
  ⚠️ PR #42 quiet 22m, 40m of budget left. pending: e2e (queued), review by Copilot. My call: keep.
  ```

- The facts come from the verdict and the `pending` lines. The call is yours: stop, keep, or extend.
- Never block on a question here. The user answers when they look.
