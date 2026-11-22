# ai-disclosure

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C182%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,182 tokens" />
  <img src="https://img.shields.io/badge/Total-1%2C182%20tokens-2ea44f?style=flat-square" alt="Total: 1,182 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   |  Tokens |
| ---------------------- | ------: |
| [`SKILL.md`](SKILL.md) | `1,182` |

<!-- token-estimates:end -->

Disclosing AI is etiquette. Sure, "You're absolutely right!" and three em dashes per sentence already gave it away.
What readers can't tell is whether you were behind it, or just said "go handle this for me." Saying how involved you
were is the least you owe the people who spend their time on it. Start with yourself.

Adds one line to every PR, issue, comment, and review reply an agent posts as you: its tier, the
model, and the thinking effort.

```markdown
Fixed in a1b2c3d.
<sub>&emsp;╰</sub> _<sub>🤝 Human Guided: Claude Code · Opus 5.5 (high)</sub>_
```

[The skill itself.](SKILL.md)

## Tiers

- **🤖 Agent Decided.** The agent made the calls. You named the task, at most.
- **📋 Human Planned.** You worked out the plan together; the agent carried it out.
- **🤝 Human Guided.** You settled a decision, and this post carries it.

When in doubt, the agent picks the lower tier, so the line never claims more of you than there was.

## Hook

The hook checks every `gh` post before it runs and blocks the ones without a line, telling the agent why and where the
skill is. No `python3`, no posts: it fails closed. To post without a line, tell the agent; it runs that one command as
`AI_DISCLOSURE=off gh ...`, so the opt-out shows in the command.

## Install

`ai-disclosure@sherif-plugins` on its own, or the `skills` plugin, which already has it. Claude Code, Codex, Cursor, on
macOS and Linux, with `python3` 3.9+. `npx skills` gets you the skill without the hook.
