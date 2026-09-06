# Branches and Stacked PRs

`<trunk>` below is the repo's default branch, usually `main`. Resolve it once per session, see
[SKILL.md](../SKILL.md).

## Safety rules

These are hard; the failure modes are silent or unrecoverable.

- **Never commit to `<trunk>`** unless the user told you to.
- **Force-push is `--force-with-lease`.** Plain `--force` needs the user's word.
- **History rewrites (rebase, force-push)** follow [`rebase.md`](./rebase.md): snapshot at the first conflict, range-diff before every force-push.
- **Never auto-rebase a `<trunk>` that has diverged locally.** Stop and surface it. Divergence signals an unexpected upstream change, and auto-rebasing can silently drop or duplicate commits.
- **Never discard uncommitted work** when switching branches. It's the user's only copy.

## When to branch

1. New feature unrelated to the previous chat? Branch off `<trunk>`.
2. Branch without asking only when intent is clearly new work ("let's start", "build a new feature", "open a PR for…").
3. Already on a non-trunk branch? Check its commits. If they don't match the intended work, ask: branch off current or off `<trunk>`?
4. Before branching off `<trunk>`: `git fetch`, then fast-forward it. If fast-forward fails (diverged), stop and surface it (see safety rules).

## Naming

With a ticket or issue (when the user supplied one):

- **Single PR, ticket:** `<TICKET>-<slug>`, e.g. `CPR-1234-autoscale-zone-1`
- **Stack, ticket:** `<TICKET>/<n>-<slug>`, `<n>` from 1, e.g. `CPR-1234/1-autoscale-zone-x`, `CPR-1234/2-autoscale-zone-y`
- **No ticket:** `<slug>`, or `<n>-<slug>` in a stack, e.g. `autoscale-zone-x`

Slug rules:

- Lowercase kebab-case. Allowed: ASCII letters, digits, hyphens; `/` only in the stack form `<TICKET>/<n>-<slug>`.
- No uppercase, underscores, dots, or other punctuation. Max 4 words.
- Derive from the work, not the file. Lead with the noun; verbs are implied.

Where the ticket comes from, in order:

1. **Inherit** the current branch's ticket when branching off it, unless the user says it's a different ticket.
2. **Referenced** ticket the user mentioned this conversation.
3. Otherwise, ask.

## Switching with a dirty tree

1. `git status`.
2. If dirty, stash with a descriptive message: `agent: pre-switch <reason>`.
3. Do the work on the other branch.
4. Restore the stash on return.
5. If the stash doesn't reapply cleanly, leave it in place and surface it (never discard, see safety rules).

The gh-stack navigation commands (`checkout`, `up`, `down`, `top`, `bottom`) are switches: same
procedure. Restacking refuses a dirty tree too, so stash the same way before one.

`gh stack add` is the deliberate exception. It keeps the working tree, which is how a dirty tree
splits into layers: stage this layer, commit, `add` the next, stage the rest there. Commit or stash
first when the new layer must start clean.

## Stacked PRs

Conventions live here; mechanics belong to the **gh-stack skill if it exists**. Load it for stacked
work on GitHub: it creates the layers, pushes, submits, restacks, and merges. This page's naming,
when-to-stack, title marker, and body rules still apply on top of it.

- Suggest stacking when it fits; confirm first, unless the user told you before to stack.
- In a stack, each branch is created from the previous one, not from `<trunk>`.
- Each PR's base is the branch directly below it, the bottom one's is `<trunk>`. `gh stack` sets this; by hand it's `--base`.
- Title marker `[n/N]` and the stack links: see [`pull-requests.md`](./pull-requests.md).

**Which path:** run `gh stack view --json`. Exit 0 is gh-stack, and this is the stack. Exit 2 is
gh-stack with no stack here yet (`gh stack init`, or `gh stack checkout <pr>` to adopt branches that
already exist). An unknown command, or exit 9, is the manual path below. This is also the one call to
read stack state from; nothing else needs to reconstruct it.

### With gh-stack

Pass names from the Naming rules above. `gh stack` uses them verbatim and its own `<topic>/<concern>`
suggestion yields to them. `gh stack submit --auto` generates titles and bodies, so finish them per
[After `gh stack submit`](./pull-requests.md#after-gh-stack-submit).

**Restacking** is `gh stack rebase`, then verify, then `gh stack push`. `gh stack sync` fetches,
rebases and pushes in one command, so verification cannot gate it: use sync to pull merged state
down, and verify after the fact. Sync restores every branch and exits 3 on a conflict, so the only
thing it ever pushes unverified is a clean cascade, and the way a clean cascade still changes content
is a `rerere` replay. That is what to look for.

**Conflict during a cascade** (`gh stack rebase` exit 3). It stopped part-way up, so the branches
below it are already rewritten and their current tips are not originals. Snapshot before the first
`git add`:

- the stopped branch: `git branch <b>-bk ORIG_HEAD`
- each branch already rebased below it: `git branch <b>-bk <b>@{1}`
- branches above it, untouched: `git branch <b>-bk <b>`

`<b>@{1}` is one move ago, which is the pre-rebase tip only while nothing else has moved the branch.
Confirm with `git reflog show <b> -n 2`: `rebase (finish)` on top, or `@{1}` is the wrong SHA.

A `gh stack sync` exit 3 is the opposite case. Sync restores every branch before exiting, so nothing
moved and there is nothing to snapshot. Run `gh stack rebase` to recreate the conflict, then follow
the above.

**Verifying a cascade.** `ORIG_HEAD` holds only the last branch rebased, so check each rebased branch
against its own reflog: `git range-diff <b>@{1}...<b>`, same `rebase (finish)` check. Reading the
output is [`rebase.md`](./rebase.md#verify).

### Without gh-stack

Entered from the probe above: the extension is missing, or GitHub reports stacked PRs unavailable.
Restack by hand. Restacking is rebasing, so [`rebase.md`](./rebase.md) applies in full, snapshot and
verify included. Infer the stack from branch names when they match the convention; otherwise trace by
parent. Three cases:

**Bottom PR merged:** rebase PR-2 onto `<trunk>` with `--onto` to drop PR-1's commits, retarget its base to `<trunk>` (`gh pr edit`), verify, force-push. `--onto` needs PR-1's old tip as the exclusion
point (`git rebase --onto <trunk> PR-1 PR-2`), so read that SHA before the merged branch is deleted; once it's gone the boundary is unrecoverable.

**Chain of 3+:** restack bottom-up in one turn. Branch 2 onto `<trunk>`, branch 3 onto the new branch 2, branch 4 onto the new branch 3, and so on. Each branch: rebase, verify, force-push, retarget
base.

**Change pushed mid-stack:** rebase every branch above the changed one onto its new parent, verify and force-push each.
