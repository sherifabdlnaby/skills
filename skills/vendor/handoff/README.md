# handoff

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-182%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 182 tokens" />
  <img src="https://img.shields.io/badge/Total-216%20tokens-2ea44f?style=flat-square" alt="Total: 216 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                       | Tokens |
| ------------------------------------------ | -----: |
| [`SKILL.md`](SKILL.md)                     |    182 |
| [`agents/openai.yaml`](agents/openai.yaml) |     34 |

<!-- token-estimates:end -->

`handoff` compacts the current conversation into a focused document that a fresh session can use to continue the work. See [`SKILL.md`](SKILL.md) for the canonical agent instructions.

## Use

Invoke the skill when changing sessions or agents:

```text
/handoff [what the next session will focus on]
```

The optional focus tailors the handoff to the next task. The document captures the live context, points to relevant workspace artifacts and URLs instead of repeating them, and names useful skills for
the next session.

The handoff is written to the operating system's temporary directory rather than the project. It is a transfer aid, not a replacement for plans, decisions, commits, or other durable project records.
Sensitive values and personal information are removed.

## Source

Vendored from **Matt Pocock**'s [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff) skill in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT).
