# ask-me

[All skills](../)

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
