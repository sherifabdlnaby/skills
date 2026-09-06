# Commits

## Safety rules

- **Never `--no-verify`** unless the user asked. Hooks catch leaks, formatting, and typos at the cheapest moment; skipping just defers them to CI or review.
- **Never blanket-add** (`git add -A`, `git add .`) without checking `git status` first. It stages files you didn't intend, the common path to leaking secrets or committing scratch files.
- **Never `--amend` a hook-failed commit.** The failed commit didn't happen, so amending would modify the previous one. Make a new commit.

## Before staging

1. `git status`. Confirm the tree holds only intended changes.
2. Unrelated edits leaked in? Don't commit them.
3. If a staged file only makes sense alongside another modified file, stage both so changes are as atomic as possible.

## Before committing

For each staged file, articulate why it's there. Can't explain one? Unstage it, investigate, then include it deliberately or drop it. If the staged set looks mixed, surface it and let the user decide:

> "Staged: X, Y, Z. X and Y are the change. Z is unrelated, want me to drop it or split the commit?"

## Message

- Follow the repo's commit style only if already known (stated in this conversation, or set by a skill). Don't infer it from `git log` (wastes time and tokens).
- None known? Default to conventional commits.
- Never reference "the user", "as discussed", or the PR itself. Commit messages outlive PRs and chat, so cross-references go stale.

## Scoping

A commit is a coherent set: one milestone of the work, whatever size that turns out to be. Commit as
you go, using them as checkpoints. Neither extreme is the goal, so don't collapse a branch into one
mega-commit, and don't split a single change into commits too small to mean anything on their own.
A PR is not the unit; several commits per PR is normal.

## Pre-commit hooks

1. `git commit`; hooks fire automatically.
2. On failure, fix the cause (not `--no-verify`). Re-stage the fix, then make a new commit (not `--amend`, see safety rules).
3. If a formatter hook rewrites files, re-stage the rewrite and retry once.
4. If it rewrites again on retry, the hook is non-idempotent: surface it.

## Squash

`git rebase -i` opens an editor and hangs the tool call. Both recipes avoid it. Both rewrite
history, so [`rebase.md`](./rebase.md#verify) verification applies.

Everything since `<base>` into one commit:

```
git reset --soft <base> && git commit
```

Fixups folded into the commits they belong to:

```
git commit --fixup <sha>
GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash <base>
```

`GIT_SEQUENCE_EDITOR=:` accepts the generated plan without opening anything.

## Empty commits

Fine for retriggering CI or unsticking a stuck check. Use `--allow-empty` with a clear message (e.g. `Retrigger CI`), and tell the user in chat so it doesn't look accidental.
