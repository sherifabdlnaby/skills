# watch-pr-comments

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-256%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 256 tokens" />
  <img src="https://img.shields.io/badge/Total-256%20tokens-2ea44f?style=flat-square" alt="Total: 256 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |  `256` |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/watch-pr-comments` to answer a pull request's reviews and comments as they land, while CI is
someone else's concern. It narrows the [`/watch-pr`](../watch-pr/README.md) contract to reviews:
automated reviews are addressed, human comments are answered per the git skill's rules, and a red
check does not wake it. Only a merge, a close, or the time budget ends the watch.
