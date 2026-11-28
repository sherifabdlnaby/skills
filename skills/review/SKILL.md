---
name: review
description: Review code against the coding skill: your own work before handoff, someone else's PR, or the review comments on your PR.
license: MIT
argument-hint: "[loose|balanced|strict] [PR number or URL]"
metadata:
  author: sherifabdlnaby
  version: "0.3.0"
---

# review

The rules live in the **coding** skill; load it first. This skill sets how hard to apply them. A finding names the rule it breaks and does not restate it.

## Use

`$ARGUMENTS` may hold a level and a target. The target, or the task that loaded this skill, picks the use and the default level:

- **Own work** (no PR, or the user's PR with no open review threads): `strict`. See [Own work](#own-work).
- **Someone else's PR**: `balanced`. Read [`references/others-pr.md`](references/others-pr.md) **before** you act.
- **Replies** (review comments on the user's PR, e.g. handed over by watch-pr): `balanced`. See [Replies](#replies).

## Every review

Replies run only step 4, on each comment.

1. **no-comments, no-docs.** Run both skills on the scope, unless this session already did. When you may not edit (a reviewer, not the author), turn their edits into findings, then discard
   the edits.
2. **Past the diff.** A deleted line is a Chesterton's fence: name what it guaranteed and where the new code still does. For a changed signature, return shape, or precondition, read its callers.
3. **Tests.** Hold the diff's tests, and the ones it lacks, to coding's Tests rules. Run them.
4. **Repro, then raise.** Each finding has a repro: the input, state, or next change that fails, confirmed in the code. Drop one only on proof (a quoted line, a guard). "Unlikely" is not proof.
   Then judge it at the level.

## Levels

Every coding rule applies at every level. The level sets how much a breach must cost before you raise it. Cost is the work to change it after merge:

- **One-way door**: persisted state, migrations, released contracts (an API, a CLI flag, a config key, an event), a structure that later changes must work around.
- **Two-way door**: a rename or refactor that an agent sweeps in one pass.

The levels add up:

- **`loose`**: broken behavior and one-way doors, when you are sure.
- **`balanced`**: also likely findings, and two-way breaches that cost every reader time. One finding per pattern, its sites named.
- **`strict`**: every breach, and your opinions.

A finding is:

- A **breach** (the rule, and its cost here) or an **opinion** (no rule covers it; prefixed `opinion:`, `strict` only, never blocks).
- **Overall** (the approach, the scope, a missing piece) or **inline** (on a line). Overall first, the rest by cost.
- **Blocking** when it breaks behavior or is a one-way door. At `strict`, every breach blocks.

## Own work

Scope: the files you were given, else the branch diff from its merge-base, working tree included.

- **The author fixes, a non-author reports.** You wrote the code: fix each breach. You did not (e.g. a subagent, a cron run on someone's branch): report and edit nothing. The user's ask
  overrides.
- **Redesign first.** When an overall finding means a different approach, fix no line it would replace. Present it and wait.
- **Opinions** go to the user to pick.
- **Handoff note**, one short block: the level, what the review fixed, what is open (overall first), the opinions. Leave out what passed.

## Replies

The **git** skill fetches the round and posts. Here, triage each comment as a finding at the level: you would raise it, fix it. You would not, push back with the cost. It asks to break a
coding rule, push back and name the rule.

## Unattended

A cron, an afk run, a trigger. Act where a coding rule decides. What a use sends to the user (an opinion, a redesign) stays **open**: unapplied, and in the final report.
