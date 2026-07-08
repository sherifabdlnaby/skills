# Pull Requests

Operational mechanics for opening and updating PRs.
Covers: pre-flight, tickets, title format (including stacked PRs), description style, Human Note, footers, post-create flow, responding to review, destructive edits.

Use `gh` first, GitHub MCP only as a fallback. Apply [SKILL.md](../SKILL.md) voice rules to every title, body, and comment.

## Opening a PR: pre-flight

1. `git status`: clean tree (or only intended changes).
2. `git branch --show-current`: correct branch.
3. Branch pushed? `git push -u origin <branch>` if needed.
4. `git log <base>..HEAD`: intended commits are present.
5. Base branch: `main` for a normal PR, the branch directly below for a stacked one.

## Title

- **With ticket:** `<TICKET>: <Title>`, e.g. `XYZ-1234: Add autoscale zone 1`
- **Without ticket:** `<Title>`, e.g. `Add autoscale zone 1`

One line, first letter capitalized, no trailing period.
Join multiple changes with `+`: `XYZ-1234: Add autoscale + clean up dead config`.

### Stacked PR position marker

Add `[n/N]` to mark position: `n` is this PR's 1-indexed position, `N` is the stack total (the real number when known, the literal letter `N` when not).
Place it after the ticket and before the colon; with no ticket, prefix the title.

- **Ticket, total known:** `XYZ-1234 [1/3]: Add autoscale zone 1`
- **Ticket, total unknown:** `XYZ-1234 [1/N]: Add autoscale zone 1`
- **No ticket, total known:** `[1/3] Add autoscale zone 1`
- **No ticket, total unknown:** `[1/N] Add autoscale zone 1`

When the total becomes known, edit prior titles (`gh pr edit --title`) to replace the literal `N`. Title-only edit, so the `--body` warning below doesn't apply.

## Body: Human Note

Ask on the first PR of the conversation, when the user requests one, or when you judge the PR needs a human voice. Ask before drafting the body, with the Ask User tool, default `No`, and an option for the user to enter their note verbatim:

> Want to add a Human Note?

When given:

1. Place it at the very top of the body, before the summary line.
2. Use GitHub's `[!NOTE]` callout.
3. Take it verbatim: no paraphrasing, typo fixes, punctuation changes, or voice normalization.

```markdown
> [!NOTE]
>
> ### 🧍🏻Human Note
>
> <User's text, verbatim>

<rest of the body…>
```

## Body and Description

PR Body anatomy.

- **One-line summary of the change**: ALWAYS include.
- **User-facing Changelog style bullet points**: Include when we change more than one possibly unrelated things.
- **Why / big picture**: ONLY if User gave you a reason. NEVER invent a WHY.
- **Per-change narration**: NEVER. Let the code diff speak for itself.
- **Test plan**: ONLY if User explicitly asked. NEVER invent. NEVER assume how to test.
- **Clickable links** (Jira ticket, parent ticket, related PRs, docs used): ALWAYS when they exist.
- **Collapsible: rationale**: More details on the back and forth between the user on what shaped the PR.
- **Collapsible: things that didn't work**: when dead ends shaped the solution, what was tried and why it failed.
- **Collapsible: validation done**: ALWAYS when meaningful manual or automated validation actually happened.
- **Collapsible: examples**: when examples genuinely clarify the diff.

### Notes

- PR Body and Description needs to be concise, but not miss a spot. Focus on what behavior changed, what breaking changes introduced but do not narrate the diff yourself.
- Use Emojis to help scanning/glancing, but not as decorations.
- Use GitHub alerts/callouts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`) to surface information the reviewer must not miss.
- The skeleton's hidden `<!-- pr:x -->` markers are structure receipts, invisible on GitHub: keep each with its block, drop it with its block. A post-create hook nudges about missing ones; the nudge is informational.

Skeleton (drop any block that doesn't apply):

```markdown
> [!NOTE]
>
> ### 🧍🏻 Human Note
>
> xxxx yyy zz <!-- verbatim, only if user gave one -->

### Summary

<!-- pr:summary -->

[TICKET-123](link) | xxxx yyy zz. <!-- short summary, always -->

**Changes** <!-- pr:changes -->

- **Breaking**: xxxx yyy
- **New Functionality**: xxxx yyy
- **Backward Compatible**: xxxx yyy
- **Fixed**: xxxx yyy
- ... and so on.

> [!WARNING]
> **Breaking:** xxxx yyy. <!-- important to know, understand, validate, test -->

**Review guide** <!-- pr:review-guide -->
start in `xxxx`; then read `yyy`, then the rest is mechanical fallout.

<!-- The rest is what you believe should include in the PR Description  -->

---

<details><summary>Things that didn't work</summary> tried xxxx, didn't work because yyy. </details>

<details><summary>Tests & Validation</summary>  <!-- things you validated & tested.  -->  </details>

### Relevant Links

<!-- pr:links -->

< relevant links (epic, issues, docs, sources, other stacked PRs)

---

_<sub>🤝 Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>, with their input and approval.</sub>_
<!-- footer emoji by provenance: 🤖 autonomous, 🤝 user-directed; see AI footers -->
```

## Body: linking

- Tickets and parent/epic: see [`## Tickets`](#tickets).
- Related PR, same repo: `#<num>` (GitHub auto-links). Another repo: `org/repo#<num>`.
- Docs (Notion, Confluence, RFC, README): clickable Markdown links, avoid raw URLs.
- Stacked PRs: link the previous and next PRs in the body footer; return to edit once the next PR's URL exists.

## AI footers

This is the PR-**body** footer. Comment and reply footers, chosen by provenance (autonomous vs user-directed), live in [SKILL.md AI Disclosure](../SKILL.md#ai-disclosure).

Resolve the GitHub username once per session and cache it as `<GITHUB_USERNAME>`:

```bash
gh api user --jq '.login'
```

Substitute two values:

- `<Claude|Cursor|OpenCode>`: the tool you're running as.
- `<MODEL>`: the friendly name of the model you're running, e.g. `Opus 4.8`.

Append the footer at the very end, after a `---` separator, picking the variant by **provenance**
(same rule as [SKILL.md AI Disclosure](../SKILL.md#ai-disclosure): 🤖 autonomous, 🤝 user-directed).

**Autonomous** (🤖), you opened the PR without the user's input on its content:

```markdown
---

_<sub>🤖 Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>, fully autonomous, they have not reviewed this.</sub>_
```

**User-directed** (🤝), the user gave input on or approved the PR:

```markdown
---

_<sub>🤝 Created with <Claude|Cursor|OpenCode> (<MODEL>) on behalf of @<GITHUB_USERNAME>, with their input/approval.</sub>_
```

For a back-and-forth with the user on how to comment, offer a verbatim Human Note (Ask User tool).

## Running `gh pr create`

- Body via HEREDOC so formatting and code blocks survive shell quoting.
- `--assignee @me`, so PRs land in the user's assigned queue.
- `--draft` by default unless told otherwise; prevents premature reviewer pings and lets the user inspect first.
- `--base <branch>` for any PR above the bottom of a stack. The stack relationship lives in `--base`; without it the PR targets `main` and the stack collapses.

## After `gh pr create` (in order, no waiting)

Output the PR link first, then:

1. **Slack-ready line**, in a fenced block for copy-paste (drop the parenthesized ticket suffix when there's no ticket):
   ```
   [#<PR_Number>](<PR_URL>): <PR_Title> - ([<TICKET>](<TICKET_URL>))
   ```
2. **Clickable PR link**, separate from the Slack line:
   ```
   [<PR_Title>](<PR_URL>)
   ```

## Updating an open PR

**New commits during review:** address feedback with new commits, not amends or history-rewriting force-pushes; reviewers read incremental changes more easily. The scoping rule from [`references/commits.md`](./commits.md) still applies.

**`gh pr edit --body` is destructive:** the flag replaces the whole body, so anything missing from your payload (Human Note, AI footer, links, collapsibles) is erased. Always:

1. Read the current body: `gh pr view <num> --json body --jq .body`.
2. Apply your edit locally.
3. Pass the full updated body via `gh pr edit --body` (HEREDOC).

## Responding to review comments

Full flow lives in [`review-responses.md`](./review-responses.md): classify the reviewer (automated bot/AI tool, an AI-disclosed agent behind a human account, or a human), then fix / push back / escalate, replying to every comment with the AI footer.
