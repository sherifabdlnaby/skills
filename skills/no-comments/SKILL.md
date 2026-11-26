---
name: no-comments
description: Apply the coding skill's comment rules to a diff.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# no-comments

The rules live in the **coding** skill, under Code Comments. Load it first. This skill only enforces them.

Scope: the files or diff you were given, else the current diff against the base branch, working tree included.

1. Run the `comment-sicko` subagent on the scope (a plugin may prefix its name, e.g. `skills:comment-sicko`). If it is not available, do its pass yourself: every comment off the keep list is deleted.
2. Check its report against our keep list, which is wider than its own. Restore a deleted comment only when a keep item applies. Check every `IMPORTANT` or `do not remove` claim in the code before you
   keep or delete it.
3. Delete what fails. For each `MUST KILL` flag in scope, rename, extract, or type the code until it needs no comment. A flag outside the scope goes in the report.
4. Report: comments deleted, comments restored and why, reshapes done, and flags left open.
