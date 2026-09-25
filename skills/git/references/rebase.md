# Rebase, Merge and Conflicts

Bringing trunk into a branch, and resolving the conflicts of a rebase or merge. Stacked-PR restack procedures
(bottom merged, chain of 3+, mid-stack push) and the cascade form of the conflict and verify steps
live in [`branches.md`](./branches.md); this file holds the rules those rely on.

## Rules

- **Rebase when you can.** At the first logic hunk (see [Conflicts](#conflicts))
- **`git pull --ff-only`.** A diverged branch stops and is surfaced
- **Run the rebase bare.** No backup up front. A clean replay never needs one, and `ORIG_HEAD` holds
  the pre-rebase tip either way. Snapshot at the conflict, see [Conflicts](#conflicts).
- **Force-push only with `--force-with-lease`**, never plain `--force` without the user's confirmation.
- **Verify before every force-push**, see [Verify](#verify).

## Conflicts

**Resolve mechanical hunks yourself; ask on logic conflicts.** Imports, formatting, lockfiles, and edits that
sit side by side without touching each other's lines should be resolved. A hunk where both sides changed
behavior may need to ask the user, with both sides and your proposed fix.

### During a rebase

It stopped when the command exits non-zero and `git status` reads `rebase in progress`.

Snapshot before the first `git add`:

```
git branch <branch>-bk ORIG_HEAD
```

(why: `ORIG_HEAD` is the pre-rebase tip, and the next `reset`, `merge` or `pull` overwrites it.
A bare `git reset` to unstage everything is enough to lose it; git gives no warning.)

Then resolve, `git add`, `GIT_EDITOR=true git rebase --continue` (it keeps the commit message; a bare
`--continue` opens an editor and hangs the tool call). `git rebase --abort` puts the branch back and makes
the snapshot redundant, so delete it.

`-bk` is a recovery artifact, not the verify baseline. It becomes the baseline when you ran `reset`, `merge` or
`pull` while resolving: then verify with `git range-diff <branch>-bk...HEAD`.

### During a merge

Resolve, `git add`, `GIT_EDITOR=true git merge --continue` (it keeps the default merge message).
`git merge --abort` puts the branch back. No snapshot: the pre-merge tip stays as `HEAD^1`.

## Verify

### After a merge

```
git diff HEAD^1 HEAD   # what the merge brought into the branch
git diff HEAD^2 HEAD   # what the branch keeps over trunk
```

Every line should trace to the other side. When one does not, or you resolved a logic hunk, run the
repo's tests and checks before you push.

### After a rebase

A rebase isn't done when it exits 0; it's done when the content provably survived. Run this after
every rebase, conflict or not:

```
git range-diff ORIG_HEAD...HEAD
```

`=` marks a commit that came through identically, `!` one whose content changed, and a lone `<` or
`>` a commit that exists on only one side. Context-line drift behind a `!` is normal. Vanished
commits (except the ones a squash folds on purpose) and unexplained diffs are not: stop and surface them, `ORIG_HEAD` still has the original.

A clean exit is not evidence on its own. `rerere` replays a resolution you made once without
stopping, so content can change with no conflict to notice.

Once the force-push is verified, delete any snapshot (`git branch -D <branch>-bk`) so stale `-bk`
branches don't accumulate.
