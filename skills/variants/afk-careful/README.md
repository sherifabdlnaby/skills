# afk-careful

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-89%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 89 tokens" />
  <img src="https://img.shields.io/badge/Total-89%20tokens-2ea44f?style=flat-square" alt="Total: 89 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |   `89` |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/afk-careful` for a conservative, local-only version of [`/afk`](../../afk/README.md). Work continues only where there is one obvious right answer; every ambiguous choice is parked for your
return.

This reduces the risk of an unwanted decision while you are unavailable, but it can leave substantially more work unfinished than the base mode. It is best when caution matters more than maximum
progress.
