# Babysitting a PR — full reference

Deep reference for [`scripts/babysit.py`](../scripts/babysit.py). Read [`references/babysit.md`](./babysit.md) first for the operational
flow; come here when you need a flag's exact behavior, the output schema, or how a decision is
made. **This file exists so you never have to read the source.** If something isn't here, run
`uv run scripts/babysit.py <subcommand> --help`.

## Subcommands

| command | blocks? | does                                                                                                                   |
| ------- | ------- | ---------------------------------------------------------------------------------------------------------------------- |
| `arm`   | no      | Resolve the PR, take a baseline snapshot, set the budget, print current state. Optional, watch/poll self-baseline.     |
| `poll`  | no      | One-shot: fetch, diff against the saved snapshot, print the delta, exit. Use for a deliberate "status right now".      |
| `watch` | yes     | Loop with adaptive backoff; block until a high-signal event or a stop condition, print the delta, exit. The workhorse. |

All three self-baseline: the first run on a fresh `--watcher` records current state and reports
nothing as "new". Run `arm` only when you want to start the baseline/budget clock noticeably
earlier than you start watching.

## Flags

| flag                  | subcommands | default             | meaning                                                                          |
| --------------------- | ----------- | ------------------- | -------------------------------------------------------------------------------- |
| `--pr <num\|url>`     | all         | current branch's PR | which PR                                                                         |
| `--repo <owner/repo>` | all         | current repo        | which repo                                                                       |
| `--watcher <id>`      | all         | `default`           | state namespace; one per concurrent watcher                                      |
| `--state <path>`      | all         | derived             | explicit snapshot path, overrides `--watcher`                                    |
| `--max-total <s>`     | all         | none                | total budget across every re-watch on this `--watcher`                           |
| `--reset-budget`      | all         | off                 | restart `--max-total` instead of preserving it                                   |
| `--json`              | arm, poll   | off                 | machine-readable output (watch is text-only)                                     |
| `--on <list>`         | poll, watch | `all`               | which events count: `fail,done,review,comment,state`                             |
| `--min-interval <s>`  | watch       | `8`                 | fastest poll gap                                                                 |
| `--max-interval <s>`  | watch       | `60`                | slowest poll gap                                                                 |
| `--max-wait <s>`      | watch       | `900`               | cap on a single watch call (per episode)                                         |
| `--comment-grace <s>` | watch       | `0`                 | after all checks finish, extra seconds to wait for late comments (0: settle now) |
| `--show-state`        | watch       | off                 | on a `QUIET` timeout, print the full state, not just a one-liner                 |

## Output

### Event lines

Printed above the verdict when there's something to show. Self-explanatory tags:

| tag         | meaning                               | format                                                 |
| ----------- | ------------------------------------- | ------------------------------------------------------ |
| `FAIL`      | a check went red                      | `FAIL    <name> [<conclusion>] <url>`                  |
| `FIXED`     | a red check recovered                 | `FIXED   <name> now green`                             |
| `DONE`      | all checks reached terminal           | `DONE    all checks finished (N ok, M red)`            |
| `BOTREVIEW` | automated code review to auto-address | `BOTREVIEW <Copilot\|login>[ <path>]: <state/excerpt>` |
| `REVIEW`    | a human review was submitted          | `REVIEW    <login>: <STATE> — <excerpt>`               |
| `COMMENT`   | human chatter or generic-bot comment  | `COMMENT   @<login>[ <path>]: <excerpt>`               |
| `STATE`     | merged / closed transition            | `STATE   -> <state> (merged)`                          |

A trailing `pending: <names>` line lists checks still running.

**`BOTREVIEW` vs `COMMENT`/`REVIEW`** is decided by the author login (never the comment body):

- `is_bot(login)` = login matches `/\[bot\]|bot|copilot|codeql|review|reviewer|sonar|snyk/i`.
- `is_review_tool(login)` = the narrower `/copilot|codeql|sonar|snyk|review|reviewer/i` (excludes generic `bot`).
- A **submitted review** or an **inline (on-diff) comment** by a bot -> `BOTREVIEW`; by a human -> `REVIEW`/`COMMENT`.
- An **issue comment** by a review tool -> `BOTREVIEW`; by a generic bot (e.g. `github-actions`, a
  changelog/label bot) or a human -> `COMMENT`.

When any `BOTREVIEW` is in the delta, the `>>` `EVENT` next-action points at
[`references/pull-requests.md`](./pull-requests.md) (auto-address unless the user opted out).

### The `>>` verdict line (always last)

`>> <OUTCOME>: <done|ongoing>. <next action>` — the entire protocol. `done` = terminal, stop.
`ongoing` = run `watch` again.

| outcome        | terminal | when                                                            |
| -------------- | -------- | --------------------------------------------------------------- |
| `ARMED`        | no       | `arm` finished, baseline saved                                  |
| `BASELINE`     | no       | `poll`'s first run; baseline saved, nothing reported as new     |
| `EVENT`        | no       | a high-signal event fired (and the PR is still open)            |
| `QUIET`        | no       | `poll` saw no change, or `watch` hit `--max-wait` with no event |
| `SETTLED`      | yes      | all checks done (and `--comment-grace` elapsed, default 0)      |
| `BUDGET SPENT` | yes      | `--max-total` exhausted                                         |
| `CLOSED`       | yes      | PR merged or closed                                             |

### `--json` schema

`poll`: `{delta, pending, ci_settled, signal, budget_left, outcome, terminal, next}` where
`delta` is `{new_fails, recovered, newly_done, ci_just_settled, new_reviews, new_comments,
new_review_comments, state_changed}`. `arm`: `{pr, repo, url, state, checks, ci_settled, outcome,
terminal, next}`. `watch` does not emit JSON.

## The watch lifecycle

1. **Opening burst.** Right after a push, automation fires fast: jobs queue and start, labels
   apply, bots wake. Mostly `queued -> running` churn. The loop polls fast (`--min-interval`) but
   only the snapshot updates — churn is **not** an event, so you aren't woken.
2. **Slow tail.** Quick jobs finish; slow ones (integration, CodeQL) linger. With no changes the
   gap backs off geometrically (`interval = min(interval * 1.6, --max-interval)`); any real change
   resets it to `--min-interval`. Reviews and comments usually land here.
3. **Settle.** A still-running check keeps watch alive (so a pending review check already means "a
   review is coming"). Once **every** check is terminal, watch returns `SETTLED` immediately
   (`--comment-grace` default 0). Set `--comment-grace N` to keep waiting N seconds for a lagging
   late comment after CI finishes; new comments/reviews reset that timer.

**Stop-condition precedence each iteration:** `BUDGET SPENT` (global, terminal) > `--max-wait`
(per-episode, returns `QUIET` ongoing) > `SETTLED` (terminal) > a high-signal event. The sleep
between polls is clamped so it never overshoots `--max-wait` or the budget deadline.

### --max-wait vs --max-total

- `--max-wait` bounds **one** `watch` call. Hitting it is normal and non-terminal (`QUIET:
ongoing`); the caller re-runs. For a sub-agent loop keep it modest (the default 900s is fine);
  for a detached background task set it equal to `--max-total` so the only exits are real events
  or terminal stops.
- `--max-total` bounds the **whole session**. It's stored as an absolute deadline in the snapshot
  on the first run that sets it, preserved across re-arms and re-watches on the same `--watcher`,
  so re-running does not refill it. `--reset-budget` starts it over. With no `--max-total`, there
  is no global cap (only `--max-wait` per episode and `SETTLED`).

## What's watched, and how it's detected

One `gh pr view ... --json statusCheckRollup,reviews,comments,...` call per poll, plus a
best-effort `gh api repos/{repo}/pulls/{pr}/comments` for inline review comments (if that call
fails, inline comments are skipped, the rest still works).

- **Checks** come from `statusCheckRollup`, normalizing both `CheckRun` (status/conclusion) and
  legacy `StatusContext` (state) into one shape keyed by check name.
  - **Red** = conclusion in `FAILURE, TIMED_OUT, ACTION_REQUIRED, STARTUP_FAILURE, STALE`.
  - **Still running** = status in `QUEUED, IN_PROGRESS, PENDING, WAITING, REQUESTED, EXPECTED`
    (or empty). `SUCCESS`/`SKIPPED`/`NEUTRAL` are terminal-OK.
  - **CI settled** = at least one check exists and all are terminal.
- **CodeQL / security scans** are just checks by name; no special-casing, they fail and surface
  like any other.
- **Reviews** come from `reviews`, keyed by id. Each review/comment is tagged `BOTREVIEW` /
  `REVIEW` / `COMMENT` by author login (see the Output section); Copilot authors are also shown as
  `Copilot`.
- **Comments** = issue comments (from `comments`) and inline review comments (from the api call),
  diffed by id so only genuinely new ones surface. Inline-by-bot and review-tool issue comments
  become `BOTREVIEW`; generic-bot and human issue comments stay `COMMENT`.

## State / snapshots

- One JSON snapshot per watcher: `$BABYSIT_STATE_DIR/<owner_repo>-pr<num>-<watcher>.json`
  (`BABYSIT_STATE_DIR` defaults to a `babysit/` dir under the system temp dir; `--state`
  overrides the full path).
- It holds the last-seen checks/reviews/comments (the diff cursor), `ci_settled`, and
  `deadline_ts` (the budget). Each `--watcher` has its own cursor, so concurrent watchers on the
  same PR don't clobber each other.
- Diffs are id-based, so a stale or hand-edited snapshot can't crash a poll, at worst it
  re-reports items as new once.

## Edge cases

- **No checks yet** (CI hasn't registered): `ci_settled` is false, so watch keeps waiting rather
  than declaring `SETTLED` over an empty set.
- **Draft PR**: watched normally; `draft` is recorded in state.
- **Already merged/closed** when you start: the first event-bearing run returns `CLOSED: done`.
- **`gh` not found / not authed / timeout**: the script exits non-zero with a one-line `babysit:`
  error on stderr instead of hanging.
