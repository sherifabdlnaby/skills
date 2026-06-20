---
description: Like /watch-pr, but with no time budget — keep watching and responding until the PR merges or closes.
argument-hint: "[PR number or URL] (defaults to current branch's PR)"
---

Same flow as `/watch-pr` (load the **git** skill, read `references/watch.md` and `references/review-responses.md`, resolve the PR from `$ARGUMENTS` or the current branch, spawn a cheap background watcher, respond to review comments per `references/review-responses.md`).

The only difference: **run indefinitely.** Watch until the PR merges or closes, not until a time budget runs out.

- Run the watcher with **no `--max-total`** (and no `--max-wait` cap beyond the default), so it never returns `BUDGET SPENT`.
- On every non-terminal `>>` verdict (`EVENT` / `QUIET`), relaunch the watcher in the background. Keep doing this across turns; do not stop just because the PR went quiet.
- `SETTLED` is **not** a stop condition here: checks finishing and activity dying down still means the PR is open. Re-baseline and keep watching for the next review or push.
- The **only** stop condition is `CLOSED` (merged or closed). When that fires, report the final digest and stop.
