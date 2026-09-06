# domain-modeling

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-766%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 766 tokens" />
  <img src="https://img.shields.io/badge/Total-1%2C939%20tokens-2ea44f?style=flat-square" alt="Total: 1,939 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                       | Tokens |
| ------------------------------------------ | -----: |
| [`ADR-FORMAT.md`](ADR-FORMAT.md)           |    618 |
| [`CONTEXT-FORMAT.md`](CONTEXT-FORMAT.md)   |    533 |
| [`SKILL.md`](SKILL.md)                     |    766 |
| [`agents/openai.yaml`](agents/openai.yaml) |     22 |

<!-- token-estimates:end -->

`domain-modeling` helps a team make the language and boundaries of a software domain precise while design work is in progress. See [`SKILL.md`](SKILL.md) for the canonical agent instructions.

## Use

Ask to sharpen domain terminology, create or update a `CONTEXT.md`, test a model against concrete scenarios and code, or record an architectural decision. The skill can also activate when a discussion
is changing the project's domain model.

## Workflow

The process challenges conflicting or overloaded terms, tests relationships with edge cases, and checks stated behavior against the code. Resolved vocabulary is written immediately to the relevant
`CONTEXT.md`. Repositories with several bounded contexts can use a root `CONTEXT-MAP.md` to locate each glossary and describe their relationships.

`CONTEXT.md` stays a concise glossary of domain-specific language, not an implementation guide or specification. Architecture decision records are offered only for consequential, hard-to-reverse
choices that involve a real tradeoff and would otherwise surprise a future reader. Both glossaries and ADR directories are created only when there is useful content to record.

## Source

Vendored from **Matt Pocock**'s [`domain-modeling`](https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling) skill in
[`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT).
