# Pull Requests

Operational mechanics for opening and updating PRs.
Covers: pre-flight, title format (including stacked PRs), description style, Human Note, footers, post-create flow, responding to review, destructive edits, Jira.

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

## Body: Human Note (always ask)

Before drafting the body, ask the user with the Ask User tool, default `No`, and an option for the user to entier their note verbatim.

> Want to add a Human Note?

Ask on the first PR of the conversation, when user ask you, and when you think it's necessary:

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

## Body and Description:

- **One-line summary of the change**: ALWAYS include.
- **User-facing Changelog style bullet points**: Include when we change more than one possibly unrelated things.
- **Why / big picture**: ONLY if User gave you a reason. NEVER invent a WHY.
- **Per-change narration**: NEVER. Let the code diff speak for itself.
- **Test plan**: ONLY if User explicitly asked. NEVER invent. NEVER assume how to test.
- **Clickable links** (Jira ticket, parent ticket, related PRs, docs used): ALWAYS when they exist.
- **Collapsible: rationale**: ALWAYS (when applicable) Include a section for what didn't work, and why we reached the current solution.
- **Collapsible: rationale**: ONLY for non-obvious design choices.
- **Collapsible: validation done**: ALWAYS when meaningful manual or automated validation actually happened.
- **Collapsible: examples**: when examples genuinely clarify the diff.

PR Body and Description needs to be concise, but not miss a spot. Focus on what behavior changed, what breaking changes introduced but do not narrate the diff yourself.

## Body: linking

- Jira ticket: clickable Markdown link only if you know the full URL. Never guess the Jira instance URL.
- Parent ticket (epic or umbrella): same format, labeled "Parent" or "Epic".
- Related PR, same repo: `#<num>` (GitHub auto-links). Another repo: `org/repo#<num>`.
- Docs (Notion, Confluence, RFC, README): clickable Markdown links, avoid raw URLs.
- Stacked PRs: link the previous and next PRs in the body footer; return to edit once the next PR's URL exists.

## AI footers

Resolve the GitHub username once per session and cache it as `<GITHUB_USERNAME>`:

```bash
gh api user --jq '.login'
```

Substitute the tool you're running as: `Claude`, `Cursor`, or `OpenCode`.

Append AI Disclosure footer at the very end, after a `---` separator:

```markdown
---

_<sub>This PR Code was created with assistance from <Claude|Cursor|OpenCode> on behalf of @<GITHUB_USERNAME></sub>_
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

## Responding to review comments:

1. Read all comments first; assess each independently before acting.
2. For each, decide fix / push back / escalate:
   - **Fix** when clearly correct (typos, missing error handling on a critical path, wrong API usage).
   - **Push back**, specific and concise, when the suggestion adds complexity for a near-impossible edge case, solves a problem that doesn't exist in this context, or is factually wrong.
   - **Escalate** when the tradeoff is genuinely ambiguous, or it's a design decision you lack context for.
3. Don't blindly agree; evaluate correctness and proportionality.
4. Batch fixes addressing the same review round into one commit.
5. Reply to every comment, including ones you disagree with, briefly and directly.
6. Append the AI posts footer to replies made on the user's behalf.
