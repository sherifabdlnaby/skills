---
description: Watch a PR's CI/reviews in the background and respond to review comments as they land.
argument-hint: "[PR number or URL] (defaults to current branch's PR)"
---

Load the **git** skill, then read `references/watch.md` and `references/review-responses.md` before acting.

Goal: keep a PR under watch without blocking your turn, and respond to review comments as they arrive, and debug CI Failures and fix them.
Our goal is to get the PR to green, and resolve most bot comments automatically. Defer decisions that needs my input so you can make progress addressing all coming comments.
After CI is green, and bot reviews are addressed, only then you can block and wait for my input.

## Target PR

`$ARGUMENTS` may name the PR (number or URL). If empty, resolve the PR for the current branch:

```
gh pr view --json number,url,headRefName,state
```
