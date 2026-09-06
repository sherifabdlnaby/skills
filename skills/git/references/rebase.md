# Rebase and Conflicts

Rebasing and resolving conflicts during a rebase. Stacked-PR restack procedures
(bottom merged, chain of 3+, mid-stack push) and the cascade form of the conflict and verify steps
live in [`branches.md`](./branches.md); this file holds the rules those rely on.

## Rules

- **Run the rebase bare.** No backup up front. A clean replay never needs one, and `ORIG_HEAD` holds
  the pre-rebase tip either way. Snapshot at the conflict, see [Conflicts](#conflicts).
- **Force-push only with `--force-with-lease`**, never plain `--force` without the user's confirmation.
- **Verify before every force-push**, see [Verify](#verify).

## Conflicts

It stopped when the command exits non-zero and `git status` reads `rebase in progress`.

Snapshot before the first `git add`:

```
git branch <branch>-bk ORIG_HEAD
```

(why: `ORIG_HEAD` is the pre-rebase tip, and the next `reset`, `merge` or `pull` overwrites it.
Unstaging one file mid-resolution is enough to lose it.)

Then resolve, `git add`, `git rebase --continue`. `git rebase --abort` puts the branch back and makes
the snapshot redundant, so delete it.

`-bk` is a recovery artifact, not the verify baseline. It becomes the baseline only when `ORIG_HEAD`
was overwritten before you reached verification.

## Verify

A rebase isn't done when it exits 0; it's done when the content provably survived. Run this after
every rebase, conflict or not:

```
git range-diff ORIG_HEAD...HEAD
```

`=` marks a commit that came through identically, `!` one whose content changed, and a lone `<` or
`>` a commit that exists on only one side. Context-line drift behind a `!` is normal. Vanished
commits and unexplained diffs are not: stop and surface them, `ORIG_HEAD` still has the original.

A clean exit is not evidence on its own. `rerere` replays a resolution you made once without
stopping, so content can change with no conflict to notice.

Once the force-push is verified, delete any snapshot (`git branch -D <branch>-bk`) so stale `-bk`
branches don't accumulate.
