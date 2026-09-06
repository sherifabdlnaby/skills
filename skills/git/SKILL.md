---
name: git
description: >
  Load when planning or about to git commit, branch, push, rebase, resolve a merge conflict, open PR, stack PRs (also when gh-stack drives the stack), or write/update the description of a Pull Request (PR / stacked diff), respond to review comments, review a PR, or watch/babysit a PR's CI.
  Carries the user's git conventions and style you are expected to match. Load as early as possible, the moment git or GitHub work is anywhere in the chat's future.
license: MIT
argument-hint: "[commit|branch|pr|rebase|review|watch]"
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# Git

Route first: each action's actual rules live in a `references/` file. Open the matching one before planning or acting; rules like commit grouping and branch naming shape the plan, so reading them late
means redoing it. Several actions, several references.

## Router

**Branches** (create, name, stack) -> [`references/branches.md`](references/branches.md) Switching branches, naming rules, ticket references, switching with a dirty tree, stacked PRs (conventions
here, mechanics via the gh-stack skill), the gh-stack/manual path probe, cascade conflicts and verification, manual restacking fallback (after merge, chain of 3+, mid-stack push), force-pushing.

**Committing** -> [`references/commits.md`](references/commits.md)
Pre-staging walk, file confirmation, message style, hook-failure handling, scoping, empty commits, CI refresh.

**Pull Requests** (open, update) -> [`references/pull-requests.md`](references/pull-requests.md) Pre-flight survey, title format (including the stacked `[n/N]` marker), body skeleton and how to write
descriptions, AI footers, post-create flow, finishing PRs after `gh stack submit`, linking PRs, updating a body without clobbering it.

**Responding to review comments** (on your own/target PR) -> [`references/review-responses.md`](references/review-responses.md) Classify the reviewer (automated bot/AI tool, an AI-disclosed agent
behind a human account, or a human), then fix / push back / escalate; in-thread replies, thread resolution, re-requesting review, batching a round into one GraphQL query and one aliased mutation,
where a PR stands.

**Rebasing, squashing, resolving conflicts** -> [`references/rebase.md`](references/rebase.md)
Conflict-time snapshot (`ORIG_HEAD`), force-with-lease, unconditional range-diff verification, editor-free squash recipes.
Stacked-PR restack mechanics and `--onto` (drop intermediate commits) live in [`references/branches.md`](references/branches.md), read that too.

**Reviewing someone else's PR** -> [`references/reviewing.md`](references/reviewing.md)
Procedure: gather context, check out locally, trace the change, deliver a summary and review guide.

**Watch a PR's CI and automated reviews** -> [`references/watch.md`](references/watch.md) Spawning the cheap background watcher sub-agent (and the background-task fallback), hot/cold polling, what to
relay vs hold, auto-addressing bot reviews, the final digest. Uses `scripts/pr-watch.py`, never a sleep loop.

## Always

**Disclose AI.** Anything posted on GitHub on the user's behalf (PR body, comment, issue, ticket update) carries an **AI footer**.
The PR-body template lives in [`references/pull-requests.md`](references/pull-requests.md);
the post templates, chosen by who made the specific decision (Agent Decided vs Human Guided),
live in [AI Disclosure](#ai-disclosure) below.
Use them as verbatim as possible, do not write from memory.

**Reach for `gh` first.** Every GitHub action goes through the `gh` CLI; the GitHub MCP server is
the fallback for what `gh` cannot do.

**Parallelize read-only calls.** Batch independent read-only `git`/`gh` calls
(`status`, `diff`, `log`, `gh pr view/diff/checks`) into a single tool call; each
sequential read is a roundtrip for nothing. Mutating commands (`commit`, `push`,
`rebase`, `gh pr create/edit/merge`) stay sequential.

**Fewer round-trips, smaller payloads.** Batching is the first lever; these are the next four,
your call when a one-off is cheaper:

- **One wide fetch, many narrow reads.** Anything you'll consult more than once in a task (PR JSON, `gh stack view --json`, a review-thread query) goes to a temp file once, and each step reads its
  slice with `jq`. Re-fetch after anything you did that changes it (push, edit, reply, resolve); or if time passed and you've been idle, a snapshot is not a live view.
- **Ask for an answer, not a payload.** A count or a single field leaves as `--jq '.x'`; a yes/no leaves as an exit code (`git diff --quiet`, `git merge-base --is-ancestor`). JSON you read with your
  own eyes is a payload.
- **Same-shape mutations ride one request.** GraphQL aliases: every reply, resolve, or title edit of a round in one `gh api graphql`. Aliases fail independently, so read the per-alias `errors[].path`,
  not the exit code.
- **Bodies travel by file.** PR body or GraphQL query to a file, then `--body-file` / `-F query=@file`. (why: shell quoting eats backticks and `$`, and a file stays editable for the next update.) The
  disclosure guard denies a body it cannot read, so `--fill`, `--template`, `--editor`, a piped `--body-file -`, and `--body "$VAR"` are all refused.

**Resolve once per session, reuse everywhere.** One line for all three:

```bash
gh repo view --json nameWithOwner,defaultBranchRef --jq '"repo  \(.nameWithOwner)\ntrunk \(.defaultBranchRef.name)"'; gh api user --jq '"user  \(.login)"'
```

Carry `<OWNER/REPO>`, `<trunk>` and `<GITHUB_USERNAME>` through the session from that.

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
The PR-body variant in [`references/pull-requests.md`](references/pull-requests.md) follows the same rule.

Placeholders, the same in every footer:

- `<Claude|Cursor|OpenCode>`: the tool you're running as.
- `<MODEL>`: the friendly name of the model you're running, e.g. `Opus 4.8`.
- `<GITHUB_USERNAME>`: resolve once per session with `gh api user --jq '.login'`.

**Agent Decided** (🤖): the agent chose the position, change, or response without the user's
direction on that specific decision. A PR is Agent Decided unless the user and you went back and
forth on the implementation.

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
