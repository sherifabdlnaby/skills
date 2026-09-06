# Show Me

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-775%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 775 tokens" />
  <img src="https://img.shields.io/badge/Total-775%20tokens-2ea44f?style=flat-square" alt="Total: 775 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    775 |

<!-- token-estimates:end -->

[Read the canonical skill instructions.](SKILL.md)

When prose hides the important shape of a system, Show Me turns the current discussion into a focused visual explanation. The outcome can be a small inline diagram or a standalone HTML artifact, depending on what makes the point clear with the least extra detail.

It selects a format that matches the question: pseudocode for logic, call trees for runtime flow, component or file trees for ownership, Mermaid for interactions, and diffs for a proposed change. Dense UI or layout comparisons can become a responsive HTML page that uses the product's visual language and real labels.

This skill explains the topic already under discussion. It is not a full codebase audit, a polished product mockup, or a replacement for the source code. The visual intentionally omits calls, files, states, and boundaries that do not help answer the current question.

```text
/show-me How does a submitted command move from the UI to the daemon?
```

Vendored from [HumanLayer's skills repository](https://github.com/humanlayer/skills).
