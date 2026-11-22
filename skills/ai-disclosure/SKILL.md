---
name: ai-disclosure
description: >
  Load before you post to GitHub as the user: open a PR, edit a PR body, comment, reply to a review
  thread, file or edit an issue. Also load when the ai-disclosure hook blocks a post. Adds the AI
  disclosure line on top of your PR workflow, not instead of it.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# ai-disclosure

Every post on the user's behalf (PR body, issue, comment, review, review comment, thread reply)
carries an **AI disclosure line**: how much human judgment stands behind it. Commit messages carry
none.

**Versions.** Checked against gh 2.105.0 on 2026-11-21.

## The line

Copy it, fill it, never write it from memory:

```markdown
_<sub>🤖 Agent Decided: <TOOL> · <MODEL> (<EFFORT>)</sub>_
_<sub>📋 Human Planned: <TOOL> · <MODEL> (<EFFORT>)</sub>_
_<sub>🤝 Human Guided: <TOOL> · <MODEL> (<EFFORT>)</sub>_
```

- `<TOOL>`: your harness, e.g. Claude Code, Codex, Cursor.
- `<MODEL>`: your model's friendly name, e.g. `Opus 5.5`.
- `<EFFORT>`: the reasoning effort, when the harness exposes it (Claude Code: `$CLAUDE_EFFORT`).
  Unknown: drop ` (<EFFORT>)`.

An optional ` · <what the user decided>` may follow, e.g. `· approach picked in review`.

## Tier

Judge the decisions the post carries, not the request behind it.

- **🤖 Agent Decided.** You chose the change, the position, or the wording.
- **📋 Human Planned.** The user worked through the plan with you (a grill session, a plan of many
  decisions); the details are yours.
- **🤝 Human Guided.** The user settled a decision this post carries: picked an option, answered the
  deciding question, or named what to do.

**Understate.** Torn between two tiers, take the lower. Claimed judgment that never happened is the
failure that matters.

**Still 🤖:** a task, however specific; a standing rule (a skill, `AGENTS.md`, memory); delegation
or a bare sign-off; someone else's direction (a reviewer, another agent); an unattended run.

**Direction reaches only what the user saw.** A part they never saw, or a change that departs from
their plan, is 🤖. One tier per post.

## Edits and opt-out

- **A body edit replaces the whole body**, line included. The edit takes the tier of the new change.
- **Opt out only with a reason:** the user waived the line, or the repo forbids it (e.g. a strict
  PR body limit). Leave the line out of that one post and run it as `AI_DISCLOSURE=off <command>`.
  A block is not a reason: fix the body.

## GitHub

- **PR body, issue, top-level comment, review summary:** a chip in the top-right corner, first.
  Keep the blank lines inside the cell, or GitHub prints the `_`.

  ```markdown
  <table align="right"><tr><td>

  _<sub>🤖 Agent Decided: <TOOL> · <MODEL> (<EFFORT>)</sub>_

  </td></tr></table>

  The post starts here.
  ```

- **Review comment, thread reply:** a footer right under the last line. After a list or a code
  block, leave one blank line first.

  ```markdown
  Fixed in a1b2c3d.
  <sub>&emsp;╰</sub> _<sub>🤖 Agent Decided: <TOOL> · <MODEL> (<EFFORT>)</sub>_
  ```

### The hook

Where installed, it blocks a shell command that posts to GitHub (a `gh` command or `gh api` write
with a body) when a body has no line. It checks that the line is there, not its tier or place.
Every reply in a GraphQL batch needs its own line.

When it cannot read the body, pass the body one of these ways. It runs before the whole command
line, so write a body file in an earlier command.

```sh
gh pr create --title "<title>" --body-file /tmp/pr-body.md
gh pr comment <n> --body-file - <<'EOF'
<body>
EOF
gh api repos/<owner>/<repo>/issues/<n>/comments -F body=@/tmp/reply.md
gh api graphql -F query=@/tmp/round.graphql
```

## Compatibility

Assume everything below is present; do not probe for it.

Needs: `gh`; `python3` 3.9 or newer for the hook.
Hosts: Claude Code, Codex, Cursor on macOS and Linux: yes, with the hook. Other agents that post
through a shell: the skill works, nothing enforces it. Windows: no hook.

When a block says the hook needs python3 or its guard failed: tell the user to install python3 3.9
or newer (macOS `xcode-select --install`, Linux the distro's `python3` package).
