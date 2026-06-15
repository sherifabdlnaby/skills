# Babysitting a PR

Watch a PR's CI, reviews, and comments and react the moment something happens, without sitting
in a sleep loop. Use [`scripts/babysit.py`](../scripts/babysit.py) (run with `uv run`).

    > **Don't read `babysit.py`.** Its output is self-documenting (the `>>` line below). If confused user --help, then use [details](./babysit-details.md), reading source code is last resort.

Watches: CI checks/failures, CodeQL, Copilot/human reviews, new comments (issue + inline).

## The output contract

`watch` blocks and returns only when something real happens (`queued -> running` churn never
wakes you). Lines are self-evident tags (`FAIL`, `REVIEW`, `COMMENT`, ...), and every run ends
with one `>>` line:

```
>> EVENT: ongoing. react to the lines above, then run watch again.
>> SETTLED: done. checks finished, no new activity. stop.
>> BUDGET SPENT: done. time budget used up. stop.
```

Protocol: **`ongoing`** -> act on any event, then run `watch` again. **`done`** -> report and stop.

**Automated reviews (`BOTREVIEW` lines): address them by default.** A `BOTREVIEW` tag means an
automated code review (Copilot, CodeQL, Sonar, a review bot). Unless the user said not to, react
to it automatically with the [`references/pull-requests.md`](./pull-requests.md) "Responding to review comments" flow
(fix what's right, push back on what's wrong, reply to each, AI footer). Plain `COMMENT` lines
(human chatter, bot greetings/labels) are surfaced only, never auto-actioned.

## How to run it

Both modes keep polling off your turn. Never `sleep`+re-run, never hold a blocking call in your turn.

**Preferred, background sub-agent.** Spawn a background `Explore` cheap agent with the template below;
it pings you only when something real happens.

**Fallback, background task.** If you can't spawn a sub-agent, launch `watch` as a background
command (Bash background mode). It exits on an event and the harness re-invokes you. Set
`--max-wait` equal to `--max-total` so it only exits on a real event or a terminal stop:

```
uv run scripts/babysit.py watch --pr <N> --repo <R> --watcher <id> --max-total <T> --max-wait <T>
```

`poll` is a one-shot "status right now". `arm` (optional) snapshots a baseline early.

### Sub-agent prompt example

> You babysit GitHub PR **#<NUM>** in **<OWNER/REPO>**. Run from `<git-skill-dir>`:
>
> ```
> uv run scripts/babysit.py watch --pr <NUM> --repo <OWNER/REPO> --watcher <UNIQUE_ID> --on all --max-total <SECONDS>
> ```
>
> The final `>>` line decides everything:
>
> - `>> ... done`: report what happened, then end.
> - `>> EVENT: ongoing`: report the event lines, then run the exact same command again.
> - `>> QUIET: ongoing`: run the exact same command again, silently (no report).
> - **Talk like a caveman.** Few words, exact file/check names and links: `CI red. test unit fail.
>   <link>` / `BOTREVIEW copilot. 3 note. foo.py. me fix.` / `PR merged. done.`

## Flags

- `--watcher <id>`: state namespace, one per concurrent watcher (snapshots don't collide).
- `--max-total <s>`: total budget across every re-watch on a `--watcher`; survives re-arm -> `BUDGET SPENT`.
- `--max-wait <s>`: cap per single `watch` call (default 900); times out as `QUIET: ongoing`.
- `--on fail,done,review,comment,state`: narrow what counts as an event.
- `--comment-grace <s>`: after all checks finish, seconds to wait for late comments (default 0: a
  still-running check already keeps watch alive, so it only waits while a review is genuinely coming).

On `FAIL` the script can't fix it: stop, fix and push, then re-run `watch` on the same `--watcher`.
