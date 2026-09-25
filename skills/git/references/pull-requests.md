# Pull Requests

Covers: pre-flight, title (with the stacked `[n/N]` marker), `gh pr create` flags, post-create lines, finishing PRs after `gh stack submit`, updating an open PR.

Mechanics for opening and updating PRs. The body has its own page, [`pr-body.md`](./pr-body.md).
Read it before you draft.

Apply [SKILL.md](../SKILL.md) voice rules to every title, body, and comment.

`<trunk>` is the repo's default branch, usually `main`.

## Opening a PR: pre-flight

In a stack, `gh stack submit --auto` opens the PRs and this section does not run; see
[After `gh stack submit`](#after-gh-stack-submit). By hand, one call:

```bash
BASE=<trunk, or the branch below in a stack>
{ echo "== tree";     git status --short
  echo "== upstream"; git rev-parse --abbrev-ref '@{u}' 2>/dev/null || echo "none (git push -u origin HEAD)"
  echo "== commits";  git log --oneline "$BASE"..HEAD; }
```

Read the answers: clean tree, or only intended changes; the branch is the one you mean; upstream set,
else push it; the intended commits are present and nothing else is.

Two more, batched with it:

- `gh api user --jq '.login'`: cache as `<GITHUB_USERNAME>` for the AI footer.
- Repo template or PR instructions? `PULL_REQUEST_TEMPLATE*` under `.github/` or the root, and the repo's own agent
  instructions. Either one changes the body shape: see **Repo template** under [Receipts](./pr-body.md#receipts).

## Title

- **With ticket:** `<TICKET>: <Title>`, e.g. `XYZ-1234: Add autoscale zone 1`
- **Without ticket:** `<Title>`, e.g. `Add autoscale zone 1`

One line, first letter capitalized, no trailing period.
Join multiple changes with `+`: `XYZ-1234: Add autoscale + clean up dead config`.

### Stacked PR position marker

Add `[n/N]` to mark position: `n` is this PR's 1-indexed position. `N` is a real number only when the
user stated the count, and the literal letter `N` otherwise.
Place it after the ticket and before the colon; with no ticket, prefix the title.

- **Ticket, count stated:** `XYZ-1234 [1/3]: Add autoscale zone 1`
- **Ticket, not stated:** `XYZ-1234 [1/N]: Add autoscale zone 1`
- **No ticket, count stated:** `[1/3] Add autoscale zone 1`
- **No ticket, not stated:** `[1/N] Add autoscale zone 1`

A count the user typed, or a layered plan they approved with the count in it, is stated. A count you
worked out yourself is not, and neither is one you could get by counting the stack.

`N` changes only when the user states or changes the count. Then every title in the stack is edited
in one aliased mutation (see [Batching](./review-responses.md#batching)). Submitting, adding a layer
and merging change nothing.

Picking this up in a later session: a real number in the existing titles means the count was stated,
so keep it. A literal `N` stays literal. A merged stack keeps `[2/N]` forever
(why: a real number would claim a plan the user never made).

## Running `gh pr create`

- Body via `--body-file`, so quoting never eats backticks or `$`, and the file stays editable for the next update.
- `--attach <file>` uploads a picture or video into the body. Repeatable, also on `gh pr edit` and `gh pr comment`. Use it; a version number is not a preflight.
  When to attach: [Visuals](./pr-body.md#visuals). How the upload works: [`attach.md`](./attach.md).
- `--assignee @me`, so PRs land in the user's assigned queue.
- `--draft` by default unless told otherwise; lets the user inspect first.
- `--base <branch>` for any PR above the bottom of a stack. The stack relationship lives in `--base`; without it the PR targets `<trunk>` and the stack collapses.

## After `gh pr create` (in order, no waiting)

The number and URL come from the create command's output; carry them forward.

1. **Slack-ready line**, in a fenced block for copy-paste (drop the parenthesized ticket suffix when there's no ticket):
   ```
   [#<PR_Number>](<PR_URL>): <PR_Title> - ([<TICKET>](<TICKET_URL>))
   ```
2. **Clickable PR link**, separate from the Slack line:
   ```
   [<PR_Title>](<PR_URL>)
   ```

## After `gh stack submit`

`gh stack submit --auto` pushes every branch, opens a draft PR for each one that lacks one, and
generates their titles and bodies. It prints the PRs, and `gh stack view --json` (already run as the
path probe) has their numbers, so nothing needs re-fetching.

Finish all of them in one aliased mutation (see [Batching](./review-responses.md#batching)), setting
per PR:

- **title**: per [Title](#title), marker included.
- **body**: the [skeleton](./pr-body.md#skeleton), written straight over the generated one. That body
  is the commit message from seconds ago, so there is nothing in it to preserve and no read to do first.

Ask the mutation for `pullRequest { updatedAt }` and keep what it returns; that is the value
[Updating an open PR](#updating-an-open-pr) compares against.

Drafts, like `gh pr create`. `--open` marks new *and existing* PRs ready for review, so it flips
drafts you meant to keep.

## Updating an open PR

**New commits during review:** address feedback with new commits, not amends or history-rewriting force-pushes; reviewers read incremental changes more easily. The scoping rule from
[`commits.md`](./commits.md) still applies. A restack force-pushes the layers above by design; this rule is about the layer you edited.

**`gh pr edit --body` is destructive:** the flag replaces the whole body, so anything missing from your payload (Human Note, AI footer, receipts, links, collapsibles) is erased. Always:

1. Read the current body: `gh pr view <num> --json body --jq .body`. Skip this read when `updatedAt` still matches what your last edit returned; nothing has changed since. A mismatch means re-read,
   not that the body itself changed (comments, labels and pushes move it too).
2. Apply your edit to the local body file.
3. Pass it back with `gh pr edit --body-file`, then keep the new `updatedAt`.
