---
name: no-docs
description: Apply the coding skill's docs rules to changed docs.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# no-docs

The rules live in the **coding** skill, under Docs and UI strings. Load it first. This skill only enforces them.

Scope: the docs and UI strings you were given, else those in the current diff against the base branch, working tree included.

1. Read each changed line as its layer's reader. Name that reader: a user, an API caller, a maintainer.
2. Cut what that reader takes for granted, what belongs to another layer, what repeats the code, and history. Rewrite text that a change made stale, instead of adding to it.
3. Fix words and names: no `C13` words, real symbols and commands, no counts that rot.
4. Report: lines cut, lines rewritten, and anything left that needs a human decision.
