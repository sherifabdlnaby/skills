---
name: no-comments
description: Apply the coding skill's comment rules to a diff.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# no-comments

The rules live in the **coding** skill, under Code Comments. Load it first. This skill only enforces them.

Scope: the files or diff you were given, else the current diff against the base branch, working tree included.

1. Run the `comment-sicko` subagent on the scope, on the Sonnet model (a plugin may prefix its name, e.g. `skills:comment-sicko`). If it is not available, do its pass yourself: every comment off the
   keep list is deleted.
2. Audit its report and diff. Revert any edit to code (not comments) or to files outside the scope. Restore a deleted comment only when a keep item clearly applies (comment-sicko's list is narrower
   than ours); when in doubt, it stays deleted. On a bad report, revert it and rerun once with the failure named. A second bad report: stop and report it open.
3. Delete what fails. For each `MUST KILL` flag in scope, make the smallest root-cause fix: rename, extract, or type the code until it needs no comment. No symptom guards. A flag outside the scope
   goes in the report.
4. For an `IMPORTANT` or `do not remove` comment whose claim holds, offer the cheapest type, test, or lint that encodes it. Encode it and delete the comment after the user approves; otherwise keep it
   and report it open.
5. Report: comments deleted, comments restored and why, reshapes done, encodings offered or done, and flags left open.
