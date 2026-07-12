---
name: git
description: >
  Load when git or GitHub work is anywhere in the conversation's future, as early as possible: commit, branch, push, rebase, resolve a merge conflict, open or stack a Pull Request (PR / stacked diff), respond to review comments, review a PR, watch a PR CI (babysitting).
  Carries the user's git conventions for commits, branches, PRs, rebasing, and reviews.
license: MIT
argument-hint: "[commit|branch|pr|rebase|review|watch]"
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# Git

Route first: each action's actual rules live in a `references/` file. Open the matching one before planning or acting; rules like commit grouping and branch naming shape the plan, so reading them late means redoing it. Several actions, several references.

## Router

**Branches** (create, name, stack) -> [`references/branches.md`](references/branches.md)
Switching branches, naming rules, ticket references, switching with a dirty tree, stacked PRs, restacking (after merge, chain of 3+, mid-stack push), force-pushing.

**Committing** -> [`references/commits.md`](references/commits.md)
Pre-staging walk, file confirmation, message style, hook-failure handling, scoping, empty commits, CI refresh.

**Pull Requests** (open, update) -> [`references/pull-requests.md`](references/pull-requests.md)
Title format (including stacked PRs), body format, how to write descriptions, AI footers, post-create flow, linking PRs.

**Responding to review comments** (on your own/target PR) -> [`references/review-responses.md`](references/review-responses.md)
Classify the reviewer (automated bot/AI tool, an AI-disclosed agent behind a human account, or a human), then fix / push back / escalate; replies, thread resolution, re-requesting review.

**Rebasing, squashing, resolving conflicts** -> [`references/rebase.md`](references/rebase.md)
Backup-branch convention, force-with-lease, range-diff verification, conflict procedure, non-interactive squash recipes. Stacked-PR restack mechanics and `--onto` (drop intermediate commits) live in [`references/branches.md`](references/branches.md), read that too.

**Reviewing someone else's PR** -> [`references/reviewing.md`](references/reviewing.md)
Procedure, review lenses, severity tiers, posting mechanics.

**Watch a PR's CI and automated reviews** -> [`references/watch.md`](references/watch.md)
Spawning the cheap background watcher sub-agent (and the background-task fallback), hot/cold polling, what to relay vs hold, auto-addressing bot reviews, the final digest. Uses `scripts/pr-watch.py`, never a sleep loop.

## Always

**Disclose AI.** Anything posted on GitHub on the user's behalf (PR body, comment, issue, ticket update) carries an **AI footer**.
The PR-body template lives in [`references/pull-requests.md`](references/pull-requests.md);
the post templates, chosen by who made the specific decision (Agent Decided vs Human Guided),
live in [AI Disclosure](#ai-disclosure) below.
Use them as verbatim as possible, do not write from memory.

**Parallelize read-only calls.** Batch independent read-only `git`/`gh` calls
(`status`, `diff`, `log`, `gh pr view/diff/checks`) into a single tool call; each
sequential read is a roundtrip for nothing. Mutating commands (`commit`, `push`,
`rebase`, `gh pr create/edit/merge`) stay sequential.

**Voice** for everything public (commit messages, PR titles and bodies, comments, issues):

- Omit needless words. Concise sentences, no padding paragraphs.
- Emojis sparingly, only where one helps the reader catch something while glancing.
- NO em dashes in any public-facing text. Use commas, parentheses, or periods. (why: em dashes are a classic AI tell and repel readers.)
- No vague reaffirmations like "for accountability", "for performance", "for resiliency" unless that reason is already in the conversation. (why: invented justification misrepresents the change.)
- Dry, low-key humor.
- Don't overdo formatting. Keep it balanced. (why: visual noise crowds out the content.)
- A user-supplied Human Note is exempt: it goes in the PR body verbatim.

## AI Disclosure

Every post on the user's behalf (comment, reply, issue) ends with this footer, after a `---`. Pick
the variant by who made the specific decision behind the post. A request to handle a task, fix an
issue, or open a PR does not count as guidance on the decisions the agent makes while doing it.

**Agent Decided** (🤖): the agent chose the position, change, or response without the user's
direction on that specific decision.

- `<Claude|Cursor|OpenCode>`: the tool you're running as.
- `<MODEL>`: the friendly name of the model you're running, e.g. `Opus 4.8`.

```markdown
---

_<sub>🤖 Agent Decided: Posted by <Claude|Cursor|OpenCode> (<MODEL>) autonomously on behalf of @<GITHUB_USERNAME>.</sub>_
```

**Human Guided** (🤝): the user chose or materially directed the specific decision. This does not
mean they reviewed the final wording or implementation.

```markdown
---

_<sub>🤝 Human Guided Response: Posted by <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

When unsure, use Agent Decided.
