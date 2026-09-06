# afk-soon

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-166%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 166 tokens" />
  <img src="https://img.shields.io/badge/Total-166%20tokens-2ea44f?style=flat-square" alt="Total: 166 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    166 |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/afk-soon` when you will leave shortly but can still answer questions now. It first reads the task and batches the highest-value clarifying questions. When you say you are leaving or stop
answering, it switches to the [`/afk`](../../afk/README.md) contract and continues autonomously.

You can combine it with `/afk-careful` or `/afk-yolo` to choose a more conservative or more autonomous posture after departure. The initial question phase costs a little time, but reduces avoidable
assumptions during unattended work.
