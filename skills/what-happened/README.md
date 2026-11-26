# what-happened

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-976%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 976 tokens" />
  <img src="https://img.shields.io/badge/Total-976%20tokens-2ea44f?style=flat-square" alt="Total: 976 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |  `976` |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/what-happened` when you come back to a chat that kept working without you: agents ran, CI finished, PRs moved. You get a short, plain-words catch-up of what changed since your last
message, then every decision that waits on you, each with the agent's pick, the evidence, and the risk, so you can decide from the reply alone.

The turn is read-only: it reports and asks, and changes nothing. Pictures (screenshots, small diagrams) come first when the work produced them. The tradeoff is length: the reply grows with the number
of open decisions, because it never collapses them into a count or a link.

Forked from `ketchup` in [cursor/plugins](https://github.com/cursor/plugins), without its dependencies on other skills.
