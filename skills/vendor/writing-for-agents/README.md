# Writing for Agents

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-2%2C349%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 2,349 tokens" />
  <img src="https://img.shields.io/badge/Total-2%2C937%20tokens-2ea44f?style=flat-square" alt="Total: 2,937 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                       | Tokens |
| ------------------------------------------ | -----: |
| [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md) |    567 |
| [`SKILL.md`](SKILL.md)                     |  2,349 |
| [`agents/openai.yaml`](agents/openai.yaml) |     21 |

<!-- token-estimates:end -->

[Read the canonical skill instructions.](SKILL.md)

Agent-facing documents can fail even when every sentence is correct: key material may load too late, weak pointers may not trigger, long reference sections may hide the next action, or vague completion criteria may let work stop early. Writing for Agents provides a vocabulary for designing these documents around predictable use.

It treats descriptions and links as context pointers, separates always-loaded context cost from the human cost of finding material, and places steps and reference material in a clear information hierarchy. It also helps define checkable completion criteria, split documents only where a real branch or sequence earns the split, and remove duplicated or stale guidance. A companion page covers skill frontmatter, model versus user invocation, and router skills.

The method does not offer one universal template. Moving material out of the main document can reduce context load but make it harder to discover, while adding model discovery creates a permanent context cost. The right balance depends on how the document is invoked and should be checked against real agent behavior.

```text
Use writing-for-agents to review AGENTS.md for weak context pointers and hidden completion criteria.
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
