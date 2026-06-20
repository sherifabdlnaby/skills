# Watching a PR

Watch a PR's CI, reviews, and comments and react the moment something happens, no sleep loop.
Use [`scripts/pr-watch.py`](../scripts/pr-watch.py) (stdlib only, run with `python3`).

> **Don't read `pr-watch.py`.** In doubt, check `python3 scripts/pr-watch.py <subcommand> --help`.
> Source is last resort.

Watches: CI checks/failures, CodeQL, Copilot/human reviews, new comments (issue + inline).

## How it works

Each poll snapshots the PR and diffs it against the last one saved on disk, so only new things
surface. `queued -> running` churn updates the snapshot silently and never
wakes you, that's the point: the noisy opening burst stays quiet. State lives per `--watcher`, so
several watchers can follow the same PR without clobbering each other.

Two subcommands: `watch` (the workhorse: blocks until a real event or a stop condition) and `poll`
(one-shot "status right now"). Both self-baseline, the first run on a fresh `--watcher` records
current state and reports nothing as new, so there's no separate setup step.

Two filters stack: the script surfaces only real events (mechanical); the watcher sub-agent judges
which are worth interrupting you for and reconciles the rest into a final digest (semantic).

## The output contract

`watch` blocks and returns only when something real happens. Event lines are self-evident tags,
and every run ends with one `>>` verdict line that decides everything:

```
>> EVENT: ongoing. react to the lines above, then run watch again.
>> SETTLED: done. checks finished, no new activity. stop.
>> BUDGET SPENT: done. time budget used up. stop.
>> CLOSED: done. PR merged/closed. stop.
>> QUIET: ongoing. no event yet; run the same watch again.
```

Protocol: **`ongoing`** -> act on any event lines, then run `watch` again. **`done`** -> report and stop.

### Event tags

| tag         | meaning                                |
| ----------- | -------------------------------------- |
| `FAIL`      | a check went red                       |
| `FIXED`     | a red check recovered                  |
| `DONE`      | checks reached a terminal state        |
| `BOTREVIEW` | automated code review to auto-address  |
| `REVIEW`    | a human review was submitted           |
| `COMMENT`   | human chatter or generic-bot comment   |
| `STATE`     | merged / closed transition             |

A trailing `pending: <names>` line lists checks still running. The watcher wakes on every change
(even one check passing) so it stays current; deciding what reaches you is its job, not the script's.

Each review/comment is a self-contained block, so the agent can decide without a follow-up fetch:
the tag, `@author (bot|human)`, the state or file path, the `#id`, the URL, then a few body lines.

```
BOTREVIEW Copilot (bot) COMMENTED · #2023457056
            https://github.com/o/r/pull/42#pullrequestreview-2023457056
            Consider null-checking foo before the deref on line 88.
COMMENT   @octocat (human) path/to/file.go · #1583153997
            https://github.com/o/r/pull/42#discussion_r1583153997
            Could we pull this into a helper?
```

**Automated reviews (`BOTREVIEW`): address them by default.** A `BOTREVIEW` is an automated code
review (Copilot, CodeQL, Sonar, a review bot). Bot-ness comes from GitHub's `user.type` (login
pattern as a fallback), never the comment body. Unless the user said not to, react with the
[`pull-requests.md`](./pull-requests.md) "Responding to review comments" flow (fix what's right,
push back on what's wrong, reply to each, AI footer). Plain `COMMENT` lines (human chatter, bot
greetings/labels) are surfaced only, never auto-actioned, though a bot author is still flagged.

On `FAIL` the script can't fix it: stop, fix and push, then re-run `watch` on the same `--watcher`.

## How to run it

Keep polling off your own turn: never `sleep`+re-run, never hold a blocking `watch` call in your turn.

**Preferred, background sub-agent.** Spawn a *cheap* background watcher: an `Explore` agent or a
sub-agent on a cheap model (Haiku, Composer, nano, ...). It only reads, judges, and relays, so a
cheap model suffices. It pings you only when something needs early action.

**Tell it what to ignore.** Paste this conversation's context into the prompt's Hold list: known-flaky
checks, expected bot noise (dependabot, changelog), a reviewer you'll handle yourself. It can only
skip what you mark safe; given nothing, it falls back to the generic noise rules.

**Fallback, background task.** If you can't spawn a sub-agent, launch `watch` yourself as a
background command (Bash background mode). It exits on an event and the harness re-invokes *you*, so
you apply the same notify / hold / digest judgment on each wake-up:

```
python3 scripts/pr-watch.py watch --pr <N> --repo <R> --watcher <id> --max-total <T>
```

### Sub-agent prompt example

> You watch GitHub PR **#<NUM>** in **<OWNER/REPO>** from `<git-skill-dir>`. Run `watch` as a
> **background task** (never blocking) so you can answer me mid-run; on each `>>` line, judge it and
> relaunch in the background.
>
> ```
> python3 scripts/pr-watch.py watch --pr <NUM> --repo <OWNER/REPO> --watcher <UNIQUE_ID> --on all --max-total <SECONDS>
> ```
>
> Track every event so you can answer if I ask, but **ping me only for**: a red check, a `BOTREVIEW`,
> a human review requesting changes or asking a question, a merge/close, or anything you can't
> confidently call noise. When unsure, ping.
>
> **Hold silently** (note it, don't ping): bot greetings, label/coverage/changelog chatter, a bare
> LGTM or approval, a superseded comment, a single check passing, plus <ignore-list>. Holding is
> never hiding.
>
> On a terminal `>>` (`SETTLED`/`CLOSED`/`BUDGET SPENT`), stop and send a **digest**: what you pinged
> about, what you held (counts, not a dump), the final state (CI, reviews, merged?), and flag
> anything held that turned out to matter.
>
> **Terse, few words**, exact names + links, no full sentences: `CI red. unit-test fail. <link>` /
> `BOTREVIEW copilot. null-check foo.go:88. <link>` / `held: 3 label-bot, 1 LGTM. CI green. me done.`

## Flags

- `--watcher <id>`: state namespace, one per concurrent watcher (snapshots don't collide).
- `--max-total <s>`: total budget across every re-watch on a `--watcher`; survives re-runs (stored
  as an absolute deadline) -> `BUDGET SPENT`. No `--max-total` means no global cap.
- `--max-wait <s>`: cap on a single `watch` call; hitting it is non-terminal (`QUIET: ongoing`, the
  caller re-runs). Defaults to `--max-total` if set, else 900, so a detached background task only
  exits on a real event or a terminal stop.
- `--on fail,done,review,comment,state`: narrow what counts as an event (default all). `done` covers
  any check finishing or recovering as well as the full settle, so the watcher tracks every change.
- `--min-interval` / `--max-interval`: poll gap bounds (8s / 60s). Quiet stretches back off
  geometrically toward the max; any change snaps back to the min to handle the opening burst.
- `--comment-grace <s>`: after all checks finish, seconds to wait for late comments (default 0: a
  still-running check already keeps watch alive, so it only waits while a review is coming).
  New activity resets the timer so an active discussion isn't cut off.
- `--reset-budget`: restart `--max-total` instead of preserving it.

## Notes

- **No checks yet**: watch keeps waiting rather than declaring `SETTLED` over an empty set.
- **Already merged/closed** when you start: the first run returns `CLOSED: done`.
- **`gh` missing / not authed / timeout**: the script exits non-zero with a one-line `pr-watch:`
  error on stderr instead of hanging.
- `--json` (poll only) emits the machine-readable delta; `watch` is text-only.
