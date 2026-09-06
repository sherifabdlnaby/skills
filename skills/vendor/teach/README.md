# Teach

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C946%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,946 tokens" />
  <img src="https://img.shields.io/badge/Total-3%2C837%20tokens-2ea44f?style=flat-square" alt="Total: 3,837 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                                     | Tokens |
| -------------------------------------------------------- | -----: |
| [`GLOSSARY-FORMAT.md`](GLOSSARY-FORMAT.md)               |    484 |
| [`LEARNING-RECORD-FORMAT.md`](LEARNING-RECORD-FORMAT.md) |    588 |
| [`MISSION-FORMAT.md`](MISSION-FORMAT.md)                 |    349 |
| [`RESOURCES-FORMAT.md`](RESOURCES-FORMAT.md)             |    437 |
| [`SKILL.md`](SKILL.md)                                   |  1,946 |
| [`agents/openai.yaml`](agents/openai.yaml)               |     33 |

<!-- token-estimates:end -->

[Read the canonical skill instructions.](SKILL.md)

Teach turns a directory into a long-lived learning workspace rather than giving a one-off explanation. It keeps the learner's goal, trusted sources, progress, terminology, and lesson material available across sessions so each lesson can build on demonstrated understanding.

The workspace begins with a concrete mission and success criteria. Trusted resources ground the material, while short self-contained HTML lessons provide one practical win at a time. Exercises use retrieval, spacing, and immediate feedback to build durable knowledge. Learning records capture proven understanding and corrected misconceptions; printable references and a shared glossary compress material that will be useful again.

This approach has more setup and file maintenance than a quick answer. It works best for an ongoing goal with one mission per workspace and depends on access to reliable sources. Progress records evidence of learning, not simple lesson completion. Community practice can add real-world feedback, but it remains optional when the learner does not want it.

```text
/teach Help me learn enough Rust to ship a command-line tool for my team.
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
