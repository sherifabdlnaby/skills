# ask-me

[All skills](../)

`ask-me` sets how an agent asks you questions in any task, not only when it plans. See [`SKILL.md`](SKILL.md) for the canonical agent instructions.

## How It Works

The agent asks in rounds: every question it can ask now goes out together, and a question that depends on an open answer waits for the next round. Each question goes through the harness's question
tool, with a recommended answer first, and you can always answer in your own words. The agent looks up facts itself and asks you only for decisions.

Newer models sometimes write text that sits between two tool calls into their thinking instead of the chat, and you then see only a summary of it, or nothing. The question call and the last text of
a turn always reach you. So short context goes in the question text and option descriptions, and a longer explanation ends the turn, with the question in the next turn. The agent does not pack a
whole plan into the question. Where the harness has a tool that shows text mid-turn, the agent explains and asks in one turn.

## Use

The agent loads it on its own before it asks you something. You can also call it:

```text
/ask-me
```

For a full interview that stress-tests a plan, use [`grilling`](../grilling/).
