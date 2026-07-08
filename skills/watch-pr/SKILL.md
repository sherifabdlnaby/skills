---
name: watch-pr
description: Watch a PR's CI/reviews and respond as they land.
license: MIT
argument-hint: "[PR number or URL] [forever] (defaults to current branch's PR)"
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# watch-pr

Load the [**git**](../git/SKILL.md) skill, then read its [watch](../git/references/watch.md) and [review-responses](../git/references/review-responses.md) references before acting.

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
