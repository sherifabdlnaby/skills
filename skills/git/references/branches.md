# Branches and Stacked PRs

Covers: Switching branches, naming and slugs, ticket inheritance, switching with a dirty tree, stacked PRs and restacking, force-pushing.

## Safety rules

These are hard; the failure modes are silent or unrecoverable.

- **Never commit to `main`** unless the user told you to, and it makes sense to do so.
- **Force-push only with `--force-with-lease`**, never plain `--force` without asking first. Lease aborts if upstream moved; plain `--force` silently overwrites other people's commits.
- **Never auto-rebase a `main` that has diverged locally.** Stop and surface it. Divergence signals an unexpected upstream change, and auto-rebasing can silently drop or duplicate commits.
- **Never discard uncommitted work** when switching branches. It's the user's only copy.

## When to branch

1. New feature unrelated to the previous chat? Branch off `main`.
2. Branch without asking only when intent is clearly new work ("let's start", "build a new feature", "open a PR for…").
3. Already on a non-main branch? Check its commits. If they don't match the intended work, ask: branch off current or off `main`?
4. Before branching off `main`: `git fetch`, then fast-forward `main`. If fast-forward fails (diverged), stop and surface it (see safety rules).

## Naming

Ticket OR Issue Cases ( When user supply a ticket ):

- **Single PR, ticket:** `<TICKET>-<slug>` — `CPR-1234-autoscale-zone-1`
- **Stack, ticket:** `<TICKET>/<n>-<slug>`, `<n>` from 1 — `CPR-1234/1-autoscale-zone-x`, `CPR-1234/2-autoscale-zone-y`
- **No ticket:** `<slug>` (or `<n>-<slug>` in a stack) — `autoscale-zone-x`

Slug rules:

- Lowercase kebab-case. Allowed: ASCII letters, digits, hyphens; `/` only as the stack-index separator or namespace separator.
- No uppercase, underscores, dots, or other punctuation. Max 4 words.
- Derive from the work, not the file. Lead with the noun or action keyword; verbs are implied.

Where the ticket comes from, in order:

1. **Inherit** the current branch's ticket when branching off it, unless the user says it's a different ticket.
2. **Referenced** ticket the user mentioned this conversation.
3. Otherwise ask.

## Switching with a dirty tree

1. `git status`.
2. If dirty, stash with a descriptive message: `agent: pre-switch <reason>`.
3. Do the work on the other branch.
4. Restore the stash on return.
5. If the stash won't reapply cleanly, leave it in place and surface it (never discard, see safety rules).

## Stacked PRs

- Suggest stacking when it fits; confirm first, unless the user told you before to stack.
- In a stack, each branch is created from the previous one, not from `main`.
- The bottom PR targets `main`; every PR above sets `--base` to the branch directly below.
- Infer the stack from branch names when they match the convention; otherwise trace by parent.
- Title marker `[n/N]` and the stack-link footer: see [`references/pull-requests.md`](./pull-requests.md).

Restacking is rebasing, so the backup-branch rule in [`references/rebase.md`](./rebase.md) applies. Three cases:

**Bottom PR merged:** rebase PR-2 onto `main` with `--onto` to drop PR-1's commits, retarget its base to `main` (`gh pr edit`), force-push (`--force-with-lease`).

**Chain of 3+:** restack bottom-up in one turn. Branch 2 onto `main`, branch 3 onto the new branch 2, branch 4 onto the new branch 3, and so on. Each branch: rebase, force-push, retarget base.

**Change pushed mid-stack:** rebase every branch above the changed one onto its new parent, force-push each (`--force-with-lease`).
