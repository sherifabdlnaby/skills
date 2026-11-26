---
name: ask-me
description: Load before you ask the user a question or give them choices.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# ask-me

**Ask in rounds.** Each round asks every question you can ask now. A question that needs an answer you do not have yet waits for the next round.

**Ask through the harness's question tool**, e.g. `AskUserQuestion` in Claude Code, `AskQuestion` in Cursor, `question` in opencode. One question per decision, the likely answers as options, and your
pick first, marked `(Recommended)`. More questions than the tool takes: send calls back to back, still one round. The user can always answer in their own words; Cursor takes only the options you give,
so add one for that. With no such tool, number the questions in your reply, put your pick under each, and end your turn.

**Put everything inside the call.** The user reliably sees only the call. Text you write between tool calls can land in your thinking, which the user sees only as a summary, if at all. So the question
text carries the context, what the last answer changed, and the name of the thing it asks about; the option descriptions carry the tradeoffs. Some harnesses hide previews. When the context is too long
for the call, end your turn on it and ask in the next turn.

**Look facts up yourself.** Ask the user only for decisions: what the code, tools, or docs can answer is your job.
