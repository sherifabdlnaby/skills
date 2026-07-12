---
name: review
description: Gate the work behind a local reviewer panel.
license: MIT
argument-hint: "[number of reviewers, default 2]"
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# review

The task isn't done until it passes a reviewer panel. Implement as usual, then run the gate before declaring done.

## Panel

`$ARGUMENTS` = reviewer count, default 2:

- `1` → fork reviewer only.
- `2` → 1 independent + 1 fork.
- `N` → N−1 independents with distinct lenses (correctness, functionality, simplification, security, tests) + 1 fork.

Functionality = does the diff actually do what was asked? Flag missing behavior,
scope creep (unasked behavior), and asked-for behavior built wrong. Give this
reviewer the intent — the task description, plus any linked issue/PRD/spec —
alongside the diff.

Reviewer types:

- **Fork** — an agent forked from this session, carrying the full conversation context. Always on the session model.
- **Independent** — fresh context: give it only the task description and the branch diff vs merge-base.

Cross-model: If you are Claude, and have access to Open AI Model (like in Cursor), then prefer cross-model reviewers as long as they're not a weaker model.
For example, Opus 4.8 <-> GPT 5.5

## Gate

1. Run the panel in parallel.
2. Triage findings: fix the real ones; reject with a stated reason (you have context reviewers lack).
3. One re-review round, of the fixes only.
4. Gate opens. Contested or rejected findings go in the final summary.
