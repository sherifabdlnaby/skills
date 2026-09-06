# Pull Requests

Operational mechanics for opening and updating PRs.

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
  instructions. Either one changes the body shape: see the **Repo template** rule under [Notes](#notes).

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

## Body: Human Note

A **Human Note** is the user's own words at the top of the PR body, in their voice instead of yours. It is opt-in, and the user is the one who opens it: they either hand you a note or ask for the PR
to carry one. You never open a question about it, so drafting the body never waits on an answer. If you are already asking the user something else, offering the note as one more option is fine.

Their words go in the skeleton's `[!NOTE]` callout at the very top of the body, exactly as written: no paraphrasing, typo fixes, punctuation changes, or voice normalization.

## Body and Description

The skeleton below is the shape; these are the rules for filling each block.

- **One-line summary of the change**: ALWAYS include.
- **Why / big picture / Problem we are solving**: ONLY if User gave you this in the context. NEVER assume or invent a WHY.
- **User-facing Changelog style bullet points**: Include when we change more than one possibly unrelated things.
- **Breaking changes**: a `> [!WARNING]` callout naming what breaks and what the reader must do about it.
- **Per-change narration**: NEVER. Let the code diff speak for itself.
- **Review guide**: where to start and what deserves a close look; a diff that reads linearly says so instead.
- **Collapsible: How to test locally**: how the reader runs this themselves. Written for them, not a record of what you did.
- **Collapsible: rationale**: the back and forth with the user that shaped the PR, when there was one.
- **Collapsible: things that didn't work**: when dead ends shaped the solution, what was tried and why it failed.
- **Collapsible: Tests & Validation**: what you actually ran, and what it showed. ALWAYS when meaningful manual or automated validation happened. Never a plan, never something you did not run.
- **Collapsible: examples**: when examples genuinely clarify the diff.
- **Collapsible: Follow-ups / out of scope**: what was seen and deliberately left for later, so the reviewer does not ask for it here.
- **Clickable links** (parent ticket or epic, related PRs, docs used): ALWAYS when they exist. The ticket itself prefixes the summary line.

### Notes

- Use GitHub alerts/callouts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`) to surface information the reviewer must not miss.
- The `<!-- pr:x -->` markers are structure receipts, invisible on GitHub; every PR body keeps all of
  them, hook or no hook (the hook that nudges about missing ones ships beside this skill, may not be
  installed, and only prints an informational note). A marked block that does not apply keeps its
  marker and says `Not applicable: <reason>.` in its place, the reason four or five words long. An
  unmarked block (Human Note, the Breaking warning, every collapsible) is dropped when it does not apply.
- **Markdown inside `<details>` needs a blank line after `</summary>`**, as in the skeleton. Without
  it a fenced code block renders as literal backticks (verified against GitHub's own renderer).
- **Repo template** (`<!-- pr:skeleton-off: <reason> -->`): when the repo ships a
  `PULL_REQUEST_TEMPLATE` or its own instructions say how a PR body reads, theirs is the shape
  and ours is the content. Keep every heading and checkbox of theirs, in their order, and fold
  our blocks into the sections they fit: summary and why into their description, changes and
  review guide under the nearest matching heading, our collapsibles and Relevant Links after
  their last section, the AI footer last. `gh pr create --body-file` does not apply the template
  for you: read the file and merge by hand. Drop this one hidden marker anywhere in the body
  with a reason (e.g. `merged with the repo PR template`); it silences the missing-marker
  nudge where that hook runs, since `pr:x` markers may not survive the merge. Without a
  template or repo instruction, the skeleton is the shape. Invisible on GitHub, like the
  other markers.

Skeleton. The `<!-- pr:x -->` comments are the only ones that survive into the body; replace every
other comment and `<...>` placeholder, or remove it with its block:

```markdown
> [!NOTE]
>
> ### 🧍🏻 Human Note
>
> xxxx yyy zz <!-- verbatim, only if user gave one -->

### Summary

<!-- pr:summary -->

[TICKET-123](link) | xxxx yyy zz. <!-- short summary, always; no ticket, no prefix -->

**Why** <!-- pr:why -->

<the problem being solved, as the user gave it, or `Not applicable: user gave no why.`>

**Changes** <!-- pr:changes -->

<user-facing changelog bullets, or `Not applicable: this PR contains one focused change.`>

> [!WARNING]
> **Breaking:** what breaks, and what the reader must do about it.

**Review guide** <!-- pr:review-guide -->

<where to start, or `Not applicable: the diff is small and can be reviewed linearly.`>

---

<details><summary>How to test locally</summary>

<!-- commands and steps for the reader, when there are any -->

</details>

<details><summary>Rationale</summary>

<!-- the back and forth that shaped the PR, when there was one -->

</details>

<details><summary>Things that didn't work</summary>

tried xxxx, didn't work because yyy.

</details>

<details><summary>Tests & Validation</summary>

<!-- what you ran, and what it showed -->

</details>

<details><summary>Examples</summary>

<!-- only when an example clarifies the diff -->

</details>

<details><summary>Follow-ups / out of scope</summary>

<!-- seen and deliberately left for later -->

</details>

### Relevant Links

<!-- pr:links -->

<parent ticket or epic, docs, related PRs, prev/next PR (manual stacks only; gh-stack renders the stack); otherwise `Not applicable: no relevant external links.`>

---

_<sub>🤖 Agent Decided PR: Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
<!-- footer emoji by how much human judgment is behind the PR: 🤖 Agent Decided, 🧍‍♂️👍 Human Approved, 🤝 Human Guided; see AI footers -->
```

### Body: linking

- The ticket prefixes the summary line; parent ticket or epic go in the `### Relevant Links` block.
- Ticket URL: from the user, a repo config, or an earlier PR in the repo. None known means plain `TICKET-123` with no link, never a guessed base URL.
- Related PR, same repo: `#<num>` (GitHub auto-links). Another repo: `org/repo#<num>`.
- Docs (Notion, Confluence, RFC, README): clickable Markdown links, avoid raw URLs.
- Stacked PRs, manual path only: previous and next PR in `### Relevant Links`; return to edit once the next PR's URL exists. Under gh-stack, GitHub renders the stack itself.

### AI footers

These are the PR-**body** footers, one per tier. Which tier to pick, the placeholders, and the
comment and reply footers all live in [SKILL.md AI Disclosure](../SKILL.md#ai-disclosure). Append at
the very end, after a `---` separator. Where the disclosure hook that ships beside this skill is
installed, a post without a footer is denied, so it goes in before the first `gh pr create`.

```markdown
_<sub>🤖 Agent Decided PR: Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

```markdown
_<sub>🧍‍♂️👍 Human Approved PR (<glanced|read|tested>): Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

```markdown
_<sub>🤝 Human Guided PR (<nudged|steered|dictated>): Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

## Running `gh pr create`

- Body via `--body-file`, so quoting never eats backticks or `$`, and the file stays editable for the next update.
- `--assignee @me`, so PRs land in the user's assigned queue.
- `--draft` by default unless told otherwise; prevents premature reviewer pings and lets the user inspect first.
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
- **body**: the skeleton, written straight over the generated one. That body is the commit message
  from seconds ago, so there is nothing in it to preserve and no read to do first.

Ask the mutation for `pullRequest { updatedAt }` and keep what it returns; that is the value
[Updating an open PR](#updating-an-open-pr) compares against.

Drafts, like `gh pr create`. `--open` marks new *and existing* PRs ready for review, so it flips
drafts you meant to keep.

## Updating an open PR

**New commits during review:** address feedback with new commits, not amends or history-rewriting force-pushes; reviewers read incremental changes more easily. The scoping rule from
[`commits.md`](./commits.md) still applies. A restack force-pushes the layers above by design; this rule is about the layer you edited.

**`gh pr edit --body` is destructive:** the flag replaces the whole body, so anything missing from your payload (Human Note, AI footer, links, collapsibles) is erased. Always:

1. Read the current body: `gh pr view <num> --json body --jq .body`. Skip this read when `updatedAt` still matches what your last edit returned; nothing has changed since. A mismatch means re-read,
   not that the body itself changed (comments, labels and pushes move it too).
2. Apply your edit to the local body file.
3. Pass it back with `gh pr edit --body-file`, then keep the new `updatedAt`.
