# review

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-325%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 325 tokens" />
  <img src="https://img.shields.io/badge/Total-325%20tokens-2ea44f?style=flat-square" alt="Total: 325 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    325 |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/review` to require a local review panel before work is considered complete. By default, one reviewer sees the full session context and one starts fresh with only the task and branch diff. Larger
panels add independent reviewers with distinct concerns, and strong cross-model review may be used when available.

Reviews run in parallel. Valid findings are fixed, unsupported findings are rejected with reasons, and disputed points are raised to you. Fixes receive one focused re-review before the gate opens.

Invoke `/review` for the default two reviewers, or pass a count such as `/review 3`. More reviewers provide broader scrutiny but cost more time and model usage; fresh reviewers also lack conversation
context by design.
