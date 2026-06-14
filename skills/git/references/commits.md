# Commits

Covers: pre-staging checks, file confirmation, message style, hook failures, scoping, empty commits.

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

- Follow project's commit style, or style referenced in this conversation.
- No consistent style referenced? Default to conventional commits. 
- Apply [SKILL.md](../SKILL.md) voice rules. One extra: never reference "the user", "as discussed", or the PR itself. Commit messages outlive PRs and chat, so cross-references goes outdated.

## Scoping

One logical change per commit (exception: a small change sitting beside a big one). Commit as you go, using commits as checkpoints. Prefer several scoped commits over one mega-commit.

## Pre-commit hooks

1. `git commit`; hooks fire automatically.
2. On failure, fix the cause (not `--no-verify`). Re-stage the fix, then make a new commit (not `--amend`, see safety rules).
3. If a formatter hook rewrites files, re-stage the rewrite and retry once.
4. If it rewrites again on retry, the hook is non-idempotent: surface it.

## Empty commits

Fine for retriggering CI or unsticking a stuck check. Use `--allow-empty` with a clear message (e.g. `Retrigger CI`), and tell the user in chat so it doesn't look accidental.
