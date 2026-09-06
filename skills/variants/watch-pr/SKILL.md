---
name: watch-pr
description: Watch a PR until CI is green and its reviews are answered.
license: MIT
argument-hint: "[PR number or URL] [duration|forever] [humans] [poke] (defaults to current branch's PR, 30m)"
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# watch-pr

Load the **git** skill, then read its watch and review-responses references before acting.

Goal: get the PR to green with every review answered, without blocking your turn. Fix CI failures,
address bot reviews, answer human comments per review-responses, and escalate only what needs my
input while you keep making progress on everything else. Block waiting on me only once CI is green
and every bot review is addressed.

The sibling skills narrow this: `watch-pr-ci` (CI only) and `watch-pr-comments` (reviews only).

## Target PR

`$ARGUMENTS` may name the PR (number or URL). If empty, resolve the PR for the current branch:

```
gh pr view --json number,url,headRefName,state,isDraft
```

## Before the first watch

1. **Draft PR:** only when I said this repo has a review bot, or passed `poke` in `$ARGUMENTS`, run
   `poke` once, alongside the watch. Otherwise leave the draft alone; do not go looking for a bot.
2. **Existing review threads:** unresolved threads already on the PR are not news to the watch.
   Fetch them per review-responses [Batching](../../git/references/review-responses.md#batching)
   and address them first.

## The watch

```
python3 scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO> --watcher <id> --until quiet --max-total <s>
```

Run it through the cheap sub-agent the watch reference describes. React per the verdict: `EVENT`
means act and relaunch, `STALE` means one ⚠️ line for me and relaunch, `DONE` means digest and stop.

## Time Budget

`$ARGUMENTS` may include a duration (`30m`, `1h`, `2h`, …) or `forever` / `indefinitely`.

- **Duration** -> `--max-total <seconds>`. Default **30m** when neither a duration nor `forever` is given.
- **`forever`** -> `--until closed` and no `--max-total`; only a merge or close ends it.

## Human comments

Human reviews and comments are answered per review-responses: fix what is clearly right, push back
on what is not, and bring the real trade-offs to me instead of deciding them. With `humans` in
`$ARGUMENTS`, decide those too and post the reply as Agent Decided.
