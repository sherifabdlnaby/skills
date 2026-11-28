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

**Write no text between tool calls.** Text after a tool result and before another tool call can come back as thinking, reworded, and the user sees a summary or nothing (verified on Claude Opus 5.5,
2026-11). Two places reliably reach the user: the tool call, and the last text of the turn.

- **Short context goes in the call.** The question text carries what the last answer changed and the name of the thing it asks about; the option descriptions carry the tradeoffs. Some harnesses hide
  previews.
- **A long explanation ends the turn.** A concept, a plan, or test results: write it as the turn's last text and ask in the next turn. Do not pack it into the call.
- **A show-text tool sends it mid-turn.** When the harness has one (e.g. `send_to_user` in T3 Code), send the explanation with it, then ask in the same turn.

**Look facts up yourself.** Ask the user only for decisions: what the code, tools, or docs can answer is your job.
