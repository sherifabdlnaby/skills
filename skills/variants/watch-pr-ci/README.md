# watch-pr-ci

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-228%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 228 tokens" />
  <img src="https://img.shields.io/badge/Total-228%20tokens-2ea44f?style=flat-square" alt="Total: 228 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |  `228` |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/watch-pr-ci` to babysit a pull request's CI and nothing else. It narrows the
[`/watch-pr`](../watch-pr/README.md) contract to checks: a red check is debugged from its link,
fixed, and pushed; reviews and comments do not wake it; the watch ends when every check is green.
