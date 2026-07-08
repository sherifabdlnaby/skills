---
description: Watch a PR's CI/reviews in the background and respond to review comments as they land. Add "forever" to keep watching until the PR merges or closes.
argument-hint: "[PR number or URL] [forever] (defaults to current branch's PR)"

---

Load the **git** skill, then read `references/watch.md` and `references/review-responses.md` before acting.

Goal: keep the PR under watch without blocking your turn, respond to review comments as they arrive, and debug and fix CI failures.
Get the PR to green and respond most bot comments automatically; defer decisions that need my input so you keep making progress on everything else. Only after CI is green and bot reviews are addressed may you block waiting on me.


## Target PR

`$ARGUMENTS` may name the PR (number or URL). If empty, resolve the PR for the current branch:

```
gh pr view --json number,url,headRefName,state
```

## Indefinite Mode

When `$ARGUMENTS` contains `forever` (or `indefinitely`), watch until the PR merges or closes:

- Run with **no `--max-total`**, so the watch never returns `BUDGET SPENT`.
- `SETTLED` is **not** a stop condition here: checks finishing and activity dying down still means the PR is open. Relaunch and keep watching for the next review or push.
- The **only** stop condition is `CLOSED` (merged or closed). When it fires, send the final digest and stop.
