# wait-what

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-232%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 232 tokens" />
  <img src="https://img.shields.io/badge/Total-232%20tokens-2ea44f?style=flat-square" alt="Total: 232 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |  `232` |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/wait-what` when the agent's last message did not land: too much jargon, labels it made up, or no context for where it got to. The agent says the same thing again, point first, in plain
words and the project's own terms, shorter than before. It does no new work.

It covers one message. To catch up on everything that happened since your last message, use [`/what-happened`](../what-happened/README.md).

Started from `wait-what` in [mattpocock/skills](https://github.com/mattpocock/skills) and `bro` in [cursor/plugins](https://github.com/cursor/plugins).
