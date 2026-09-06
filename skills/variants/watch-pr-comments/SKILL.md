---
name: watch-pr-comments
description: Watch a PR's reviews and comments and answer them as they land.
license: MIT
argument-hint: "[PR number or URL] [duration|forever] [humans] (defaults to current branch's PR, 30m)"
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# watch-pr-comments

Same contract as [watch-pr](../watch-pr/SKILL.md) (target PR, time budget, the flick for drafts, the
existing-threads pass, the sub-agent, the `humans` word), narrowed to reviews. CI is not yours here:
a red check does not wake you, and green is not a stop.

```
python3 <git-skill-dir>/scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO> --watcher <id> --until closed --on review,comment,state --max-total <s>
```

Address `BOTREVIEW` items as they land, human comments per the watch-pr rule. On `DONE`: digest of
what was answered, what was pushed back on, what waits on me.
