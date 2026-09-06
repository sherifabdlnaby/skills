---
name: watch-pr-ci
description: Watch a PR's CI until it is green, fixing what goes red.
license: MIT
argument-hint: "[PR number or URL] [duration|forever] (defaults to current branch's PR, 30m)"
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# watch-pr-ci

Same contract as [watch-pr](../watch-pr/SKILL.md) (target PR, time budget, the sub-agent, the
verdict reactions), narrowed to CI. Skip the poke and the existing-threads pass; reviews do not wake
you and are not addressed.

```
python3 scripts/pr-watch.py watch --pr <N> --repo <OWNER/REPO> --watcher <id> --until green --on fail,done,state --max-total <s>
```

On a red check: debug from its link, fix, push, relaunch. On `DONE`: a one-line digest, what went
red and what fixed it.
