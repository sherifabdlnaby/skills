---
name: review
description: Review code against the coding skill: your own work before handoff, someone else's PR, or the review comments on your PR.
license: MIT
argument-hint: "[loose|balanced|strict] [PR number or URL]"
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# review

The rules live in the **coding** skill. Load it first. This skill sets how strictly to apply them and what to do with each finding. A finding names the coding rule it breaks; it does not restate it.

Commands in this skill are the usual call, cached for speed, not the tool's surface. For anything they do not cover, read `--help` or the current docs, then act.

## Pick the use

`$ARGUMENTS` may hold a level and a target. The target picks the use; read its reference **before** acting.

**Your own work, before handoff** (no PR given, or a PR by the user with no open review threads) -> [`references/own.md`](references/own.md)
Scope, who fixes and who reports, a redesign-sized finding, the handoff note.

**Someone else's PR** -> [`references/others-pr.md`](references/others-pr.md)
One wide read, checkout, trace, run when cheap, CI, proof of the change, the verdict-first report, Conventional Comments, posting one review.

**Review comments on the user's PR** (open threads) -> [`references/responses.md`](references/responses.md)
Judge each comment at the level: fix, push back with the cost, or escalate; then post through the **git** skill.

A target that fits none: ask. Unattended, review your own work.

## Every review

Own work and someone else's PR run all five steps. Comments on the user's PR run only step 5, on each comment: the round is a small fix, so the handoff pass does not rerun.

1. **Comments and docs.** Run the **no-comments** and **no-docs** skills on the scope, unless they already ran on it in this session. Docs stay only where they are load-bearing.
2. **Big picture, then lines.** First the approach, the scope, the structure, and the fit with the system. Then each changed line.
3. **Look past the diff.** For each deleted line, name what it guaranteed and find where the new code still does. For each changed signature, return shape, or precondition, read its callers.
4. **Verify before you raise.** Each finding gets a concrete failure: the input, state, or next change that goes wrong. Confirm it in the code. Drop it only with proof: a quoted line, a guard, or why
   it cannot happen. "Unlikely" is not proof.
5. **Judge each finding** at the level below.

## Levels

`loose | balanced | strict`. Default: `strict` on our own work, `balanced` on someone else's PR and on comments left on ours.

Every coding rule applies at every level. The level never waives a rule. It sets how much a breach must cost before you raise it. Cost is the work to change it after merge:

- **Cheap later**: a rename, a refactor, anything an agent can sweep in one pass that nobody else depends on.
- **Costly later**: persisted state and data formats, migrations, anything released that others depend on (an API, a CLI flag, a config key, an event), a structure that later changes must work
  around.

The levels:

- **`loose`**: raise only what you are sure of and what is costly later. The rest passes in silence.
- **`balanced`**: add likely findings, and cheap breaches that cost each reader time. One finding per pattern, with its other places named.
- **`strict`**: raise every breach. Add your own opinions that no coding rule covers.

Each finding is:

- **A breach** (names the coding rule and its cost here) or **an opinion** (no rule covers it; marked `opinion:`, `strict` only, never blocks).
- **Overall** (on no line: the approach, the scope, a missing piece) or **inline** (on a line). Overall findings come first; order the rest by cost.
- **Blocking** when it breaks behavior or is costly later, at every level. `strict` also blocks on every other breach.

## Attended and unattended

Attended: ask only where a reference says to. Unattended (a cron, an afk run, a trigger): act where a coding rule decides, never wait for an answer, and put what coding leaves open and costly in the
final report.

## Compatibility

Needs: `gh` (authenticated) for the PR uses. Hosts: any with a shell and git.
