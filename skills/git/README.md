# Git

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-2%2C374%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 2,374 tokens" />
  <img src="https://img.shields.io/badge/Total-12%2C384%20tokens-2ea44f?style=flat-square" alt="Total: 12,384 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                                                               |  Tokens |
| ------------------------------------------------------------------ | ------: |
| [`SKILL.md`](SKILL.md)                                             | `2,374` |
| [`references/branches.md`](references/branches.md)                 | `1,772` |
| [`references/commits.md`](references/commits.md)                   |   `567` |
| [`references/pull-requests.md`](references/pull-requests.md)       | `3,244` |
| [`references/rebase.md`](references/rebase.md)                     |   `643` |
| [`references/review-responses.md`](references/review-responses.md) | `1,485` |
| [`references/reviewing.md`](references/reviewing.md)               |   `229` |
| [`references/watch.md`](references/watch.md)                       | `2,070` |

<!-- token-estimates:end -->

This skill makes Git and GitHub work predictable across branches, commits, pull requests, rebases, reviews, and CI. It combines project-facing writing conventions with safeguards for operations that
can lose work, rewrite history, or publish unintended content.

[Read the canonical skill instructions.](SKILL.md)

## Workflow

The skill selects detailed guidance for the operation in progress:

- Branch work preserves a dirty tree, uses consistent ticket-based names, and supports both regular and stacked pull requests.
- Commits are coherent checkpoints built from an inspected staging area. Hook failures are fixed and retried rather than bypassed.
- Pull requests use concise titles, draft status by default, a stable review-oriented body, links where available, and a disclosure footer for AI-authored GitHub posts.
- Rebases preserve a recovery point when conflicts occur and use `range-diff` to verify content before a force-push.
- Reviews trace the whole change, classify feedback by source, answer in the original thread, and separate clear fixes from decisions that need human input.
- PR watching uses the included standard-library Python script to report only new CI, review, comment, and state events. Saved watcher state and adaptive polling avoid noisy sleep loops.
  The states of a watch are drawn in the [watch-pr README](../variants/watch-pr/README.md).

GitHub operations use `gh`. Independent reads are batched, while large bodies and GraphQL requests travel through files. Open PR body edits preserve current content unless a fresh generated or cached
body is known to be safe to replace.

## Safety Boundaries

The workflow does not commit to the default branch without approval, skip verification hooks, discard uncommitted work, or use a plain force-push without explicit approval. History rewrites use
`--force-with-lease` only after verification. Review feedback is judged on correctness and proportion; automated suggestions can be fixed or rejected, while unclear human design choices return to the
user.

## Use

The skill is intended to load whenever Git or GitHub work is planned. It can be requested with an operation such as `commit`, `branch`, `pr`, `rebase`, `review`, or `watch`, plus a PR number or URL
when relevant.
