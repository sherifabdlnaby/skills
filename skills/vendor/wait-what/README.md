# Wait What

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-100%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 100 tokens" />
  <img src="https://img.shields.io/badge/Total-139%20tokens-2ea44f?style=flat-square" alt="Total: 139 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                       | Tokens |
| ------------------------------------------ | -----: |
| [`SKILL.md`](SKILL.md)                     |    100 |
| [`agents/openai.yaml`](agents/openai.yaml) |     39 |

<!-- token-estimates:end -->

[Read the canonical skill instructions.](SKILL.md)

Wait What is a reset button for an explanation that did not land. It asks for the previous point again with enough missing context to follow it, simpler technical English, and the domain terms already defined by the project.

Use it immediately after a confusing answer. The new explanation stays on the same topic but changes the pitch instead of merely shortening the original wording.

This skill does not research a new topic or provide a full course. Its value depends on the preceding conversation and, where available, the project's `CONTEXT.md` or `CONTEXT-MAP.md` files.

```text
/wait-what
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
