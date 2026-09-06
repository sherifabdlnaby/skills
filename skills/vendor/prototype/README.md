# Prototype

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-642%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 642 tokens" />
  <img src="https://img.shields.io/badge/Total-3%2C567%20tokens-2ea44f?style=flat-square" alt="Total: 3,567 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                       | Tokens |
| ------------------------------------------ | -----: |
| [`LOGIC.md`](LOGIC.md)                     |  1,329 |
| [`SKILL.md`](SKILL.md)                     |    642 |
| [`UI.md`](UI.md)                           |  1,575 |
| [`agents/openai.yaml`](agents/openai.yaml) |     21 |

<!-- token-estimates:end -->

[Read the canonical skill instructions.](SKILL.md)

Some design questions are easier to answer by trying a small working model than by discussing them. Prototype creates disposable code that makes one uncertain choice concrete enough to test.

For business logic, state transitions, or data-shape questions, it builds one self-contained HTML demo. The demo exposes the full relevant state, free-play controls, and guided edge-case scenarios in domain language. For visual design questions, it builds several structurally different UI variants on one route, preferably inside the existing application context, with a URL-based switcher for comparison.

The result is deliberately not production code. It omits persistence, broad error handling, abstractions, and tests. A validated decision is rewritten into the real system; the full prototype is kept
off the main branch as a record of what was tested. This keeps fast experimental choices from becoming accidental production constraints.

```text
/prototype Show three different information hierarchies for the existing settings page.
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
