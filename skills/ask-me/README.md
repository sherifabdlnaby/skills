# ask-me

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-336%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 336 tokens" />
  <img src="https://img.shields.io/badge/Total-336%20tokens-2ea44f?style=flat-square" alt="Total: 336 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |  `336` |

<!-- token-estimates:end -->

`ask-me` sets how an agent asks you questions in any task, not only when it plans. See [`SKILL.md`](SKILL.md) for the canonical agent instructions.

## How It Works

The agent asks in rounds: every question it can ask now goes out together, and a question that depends on an open answer waits for the next round. Each question goes through the harness's question
tool, with a recommended answer first, and you can always answer in your own words. The agent looks up facts itself and asks you only for decisions.

Everything you need to answer sits inside the question call. Newer models sometimes write their reply to your last answer into their thinking instead of the chat, and you then see only a summary of
it, or nothing. The question text and option descriptions always reach you, so the context and the reaction to your last answer go there.

## Use

The agent loads it on its own before it asks you something. You can also call it:

```text
/ask-me
```

For a full interview that stress-tests a plan, use [`grilling`](../grilling/).
