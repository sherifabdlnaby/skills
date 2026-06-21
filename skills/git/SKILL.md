---
name: git
description: >
  Load when planning or about to git commit, branch, push, rebase, resolve a merge conflict, open or stack a Pull Request (PR / stacked diff), review a PR, watch a PR CI (babysitting).
  Carries user's git convention for commits, branches, PRs, rebasing, and reviews. Load skill if you'll deal with Git at any point in the conversation future (as early as possible).
---

# Git

Git conventions guide!

Each action routes to a `references/` file holding the actual rules. Read the matching one before planning or acting, not after.
rules like commit grouping, branch naming, so reading them late means redoing it.

SKILL.md alone is not enough!!

If doing or planning several actions? Open several references.

## Contents

- [Always](#always): rules for every git action (AI disclosure, parallel reads, voice, commit scoping).
- [Router](#router): which `references/` file to open for your action.
- [AI Disclosure](#ai-disclosure): the verbatim footer for anything posted on GitHub.

## Always

These apply everytime

**Disclose AI.** Anything posted on GitHub on the user's behalf (PR body, comment, issue, ticket update) carries an **AI footer**. The PR-body template lives in [`references/pull-requests.md`](references/pull-requests.md); the posts templates, chosen by provenance (autonomous vs user-directed), live below. Use them as verbatim as possible, do not write from memory. A pre-shell hook backstops this: a `gh` post whose body lacks the footer is blocked, so add it before posting.

**Parallelize read-only calls.** Batch independent read-only `git`/`gh` calls (`status`, `diff`, `log`, `gh pr view/diff/checks`) into a single tool call; each sequential read is a roundtrip for nothing. Mutating commands (`commit`, `push`, `rebase`, `gh pr create/edit/merge`) stay sequential.

**Voice** for everything public (commit messages, PR titles and bodies, comments, issues):

- Omit needless words. Concise sentences, no padding paragraphs. (why: padding is filler that wastes the reader's time.)
- Emojis sparingly, only for catching user attention while glancing. (why: Too much emojis is childish, we are not children)
- NO em dashes in any public-facing text. Use commas, parentheses, or periods. (why: em dashes are a classic AI tell and rebel users from reading.)
- No vague reaffirmations like "for accountability", "for performance", "for resiliency" unless that reason is already in the conversation. (why: invented justification misrepresents the change and reads as AI filler.)
- Dry, low-key humor.
- Don't overdo formatting. Keep it balanced. (why: visual noise crowds out the content.)
- Voice does not apply to a user-supplied Human Note placed verbatim in a PR body.

When committing, plane for logical change per commit (exception: a small change sitting beside a big one). Commit as you go, using commits as checkpoints. Prefer several scoped commits over one mega-commit.

## Router

**Branches** (create, name, stack) -> [`references/branches.md`](references/branches.md)
Switching branches, naming rules, ticket references, switching with a dirty tree, stacked PRs, restacking (after merge, chain of 3+, mid-stack push), force-pushing.

**Committing** -> [`references/commits.md`](references/commits.md)
Pre-staging walk, file confirmation, message style, hook-failure handling, scoping, empty commits, CI refresh.

**Pull Requests** (open, update) -> [`references/pull-requests.md`](references/pull-requests.md)
Title format (including stacked PRs), body format, how to write descriptions, AI footers, post-create flow, linking PRs.

**Responding to review comments** (on your own PR) -> [`references/review-responses.md`](references/review-responses.md)
Classify the reviewer (automated bot/AI tool, an AI-disclosed agent behind a human account, or a human), then fix / push back / escalate, and reply to each with the AI footer.

**Rebasing, squashing, resolving conflicts** -> [`references/rebase.md`](references/rebase.md)
Safety rules before any history rewrite: backup-branch convention, force-with-lease. Stacked-PR restack mechanics and `--onto` (drop intermediate commits) live in [`references/branches.md`](references/branches.md), read that too.

**Reviewing someone else's PR** -> [`references/reviewing.md`](references/reviewing.md)
Review procedure.

**Watch a PR's CI and Automated Reviews** -> [`references/watch.md`](references/watch.md)
When you open a PR and the user asks you to watch it: spawn a cheap background sub-agent (an `Explore` agent or a sub-agent on a cheap model) to run the watch loop and ping you only on things needing early action (a failed check, a review/comment); fall back to a background task if you can't spawn one. Pass it any context-specific ignore rules. Automated code reviews (`BOTREVIEW`) are addressed automatically per [`references/pull-requests.md`](references/pull-requests.md) unless the user said not to; human chatter is judged and surfaced or held, never lost (a final digest reconciles it). Uses [`scripts/pr-watch.py`](scripts/pr-watch.py); never a sleep loop. Don't read the script, the docs are the contract.

## AI Disclosure

Every post on the user's behalf (comment, reply, issue) ends with this footer, after a `---`. Pick
the variant by **provenance**, so the reader knows whether a human stands behind the content.

**Autonomous**, you decided and acted without the user's input (a fix or push-back in a watch loop, etc.):

```markdown
---

_<sub>🤖 Posted by <Claude|Cursor|OpenCode> on behalf of @<GITHUB_USERNAME>, autonomous and not yet reviewed by them.</sub>_
```

**User-directed**, the user gave input on or approved the content:

```markdown
---

_<sub>🤖 Posted by <Claude|Cursor|OpenCode> on behalf of @<GITHUB_USERNAME>, with their input.</sub>_
```

When unsure, use the autonomous form; it claims less human oversight, the safer default.
