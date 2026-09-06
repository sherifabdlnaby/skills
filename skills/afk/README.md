# afk

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-228%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 228 tokens" />
  <img src="https://img.shields.io/badge/Total-228%20tokens-2ea44f?style=flat-square" alt="Total: 228 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    228 |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/afk` when you need to leave but want the current task to continue. The skill favors momentum without silently making hard-to-reverse choices: sensible reversible defaults move the work forward,
while genuinely undecidable or blocked work is parked.

On return, you get a structured handoff covering completed work, judgment calls and rejected alternatives, parked decisions with recommendations, what to inspect first, and how to try the result when
applicable. The tradeoff is that work continues without live clarification, so reversible defaults may differ from what you would have chosen.
