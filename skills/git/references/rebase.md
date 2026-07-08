# Rebase, Squash, Conflicts

Covers rebasing, squashing, and resolving conflicts during a rebase. Stacked-PR restack procedures
(bottom merged, chain of 3+, mid-stack push) and `--onto` usage live in
[`references/branches.md`](./branches.md); this file holds the rules those rely on.

## Rules

- **Create a local backup branch before rebasing**, original name suffixed `-bk`
  (`git branch <branch>-bk`). Rebase rewrites history, so the backup is your only first-class
  recovery path if it goes wrong.
- **Force-push only with `--force-with-lease`** after a successful rebase, never plain `--force`
  without the user's confirmation.

## Verify before force-pushing

The rebase isn't done when it exits 0; it's done when the content provably survived:

```
git range-diff <branch>-bk...HEAD
```

Every commit should map to a counterpart with only expected changes (context-line drift is normal;
vanished commits or unexplained diffs are not). For a content-only check, `git diff <branch>-bk..HEAD`
should be empty after a pure rebase. Anything unexplained: stop and surface it, the backup still
has the original.

After the force-push is verified, delete the backup (`git branch -D <branch>-bk`) so stale `-bk`
branches don't accumulate.
