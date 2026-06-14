# Rebase, Squash, Conflicts

Covers the safety rules that apply before any history rewrite: rebasing, squashing, resolving conflicts during a rebase. Stacked-PR restack procedures (bottom merged, chain of 3+, mid-stack push) and `--onto` usage live in `references/branches.md`; this file holds the rules those rely on.

## Rules

- **Create a local backup branch before rebasing**, original name suffixed `-bk` (`git branch <branch>-bk`). Rebase rewrites history, so the backup is your only recovery path if it goes wrong.
- **Force-push only with `--force-with-lease`** after a successful rebase, never plain `--force` without the user's confirmation. Rebase produces new commits, so the push needs a force; lease aborts if upstream moved while plain `--force` clobbers it.
