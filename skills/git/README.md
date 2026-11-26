# Git

[All skills](../)

This skill makes Git and GitHub work predictable across branches, commits, pull requests, rebases, reviews, and CI. It combines project-facing writing conventions with safeguards for operations that
can lose work, rewrite history, or publish unintended content.

[Read the canonical skill instructions.](SKILL.md)

## Workflow

The skill selects detailed guidance for the operation in progress:

- Branch work preserves a dirty tree, uses consistent ticket-based names, and supports both regular and stacked pull requests.
- Commits are coherent checkpoints built from an inspected staging area. Hook failures are fixed and retried rather than bypassed.
- Pull requests use concise titles, draft status by default, links where available, and an AI disclosure on every GitHub post. The body is a short handoff for a reader who was not in the session:
  one screen stays open, and the record of who decided what (a person or the agent) is folded under it. It starts with the point, in plain words and the project's own terms, and carries a visual
  only when a small view (a tree, a diagram, a shaped `diff`, a screenshot) makes a point clearer than prose. The same ideas exist as on-demand skills: [wait-what](../wait-what/) for plain
  language and the vendored [show-me](../vendor/show-me/) for visuals.
- Rebases preserve a recovery point when conflicts occur and use `range-diff` to verify content before a force-push.
- Reviews trace the whole change, classify feedback by source, answer in the original thread, and separate clear fixes from decisions that need human input.
- PR watching uses the harness's own PR-watch tool when it has one (e.g. T3 Code). Otherwise it uses the included standard-library Python script to report only new CI, review, comment, and state
  events. Saved watcher state and adaptive polling avoid noisy sleep loops. The states of a watch are drawn in the [watch-pr README](../variants/watch-pr/README.md).

GitHub operations use `gh`. Independent reads are batched, while large bodies and GraphQL requests travel through files. Open PR body edits preserve current content unless a fresh generated or cached
body is known to be safe to replace.

## Safety Boundaries

The workflow does not commit to the default branch without approval, skip verification hooks, discard uncommitted work, or use a plain force-push without explicit approval. History rewrites use
`--force-with-lease` only after verification. Review feedback is judged on correctness and proportion; automated suggestions can be fixed or rejected, while unclear human design choices return to the
user.

## Use

The skill is intended to load whenever Git or GitHub work is planned. It can be requested with an
operation such as `commit`, `branch`, `pr`, `attach`, `rebase`, `review`, or `watch`, plus a PR number or URL
when relevant.
