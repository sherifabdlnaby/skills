# grill-me

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-61%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 61 tokens" />
  <img src="https://img.shields.io/badge/Total-61%20tokens-2ea44f?style=flat-square" alt="Total: 61 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |   `61` |

<!-- token-estimates:end -->

`grill-me` is the manual entry point for a structured interview that stress-tests a plan, design, decision, or idea. Its canonical instructions are in [`SKILL.md`](SKILL.md); the interview itself
lives in [`grilling`](../grilling/).

## Use

```text
/grill-me [what to stress-test]
```

The command delegates to `grilling`, which asks successive rounds of questions until the important decisions and dependencies are explicit. This entry point does not implement a separate interview or
start work on the resulting plan.

## Fork

Forked from **Matt Pocock**'s [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT). It keeps
upstream's thin dispatcher and routes to this repository's fork of `grilling`, where the interaction behavior differs.
