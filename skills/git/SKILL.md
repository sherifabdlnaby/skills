---
name: git
description: >
  Load when planning or about to git commit, branch, push, rebase, resolve a merge conflict, open or stack a Pull Request (PR / stacked diff), review a PR, poll a PR CI (babysitting).
  Carries user's git for commits, branches, PRs, rebasing, and reviews. Load skill if you'll deal with Git at any point in the conversation future (as early as possible).
---

# Git

Git conventions guide!

Each action routes to a `references/` file holding the actual rules. Read the matching one before planning or acting, not after.
rules like commit grouping, branch naming, so reading them late means redoing it.

SKILL.md alone is not enough!!

If doing or planning several actions? Open several references.

## Always

These apply everytime

**Disclose AI.** Anything posted on GitHub on the user's behalf (PR body, comment, issue, ticket update) carries an **AI footer**. Two formats, PR bodies vs. posts; PR template live in `references/pull-requests.md`, a generic template lives below. Use the template as verbatim as possible, do not write it from memory.

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

**Branches** (create, name, stack) -> `references/branches.md`
Switching branches, naming rules, ticket references, switching with a dirty tree, stacked PRs, restacking (after merge, chain of 3+, mid-stack push), force-pushing.

**Committing** -> `references/commits.md`
Pre-staging walk, file confirmation, message style, hook-failure handling, scoping, empty commits, CI refresh.

**Pull Requests** (open, update, respond to review) -> `references/pull-requests.md`
Title format (including stacked PRs), body format, how to write descriptions, AI footers, post-create flow, responding to review comments, linking PRs.

**Rebasing, squashing, resolving conflicts** -> `references/rebase.md`
Safety rules before any history rewrite: backup-branch convention, force-with-lease. Stacked-PR restack mechanics and `--onto` (drop intermediate commits) live in `references/branches.md`, read that too.

**Reviewing someone else's PR** -> `references/reviewing.md`
Review procedure. The AI posts footer applies (template in `references/pull-requests.md`).

**Babysit a PR's CI and Automated Reviews** -> `references/babysit.md`
When you open a PR and the user asks you to babysit it: watch CI checks/failures, CodeQL, Copilot reviews, and new comments, and surface events ASAP. Automated code reviews (`BOTREVIEW`) are addressed automatically per `references/pull-requests.md` unless the user said not to; human chatter is only surfaced. Uses `scripts/babysit.py` run from a background sub-agent or background task; never a sleep loop. Don't read the script, the docs are the contract.


## AI Disclosure

```markdown
---

_<sub>Posted by <Claude|Cursor|OpenCode> on behalf of @<GITHUB_USERNAME></sub>_
```
