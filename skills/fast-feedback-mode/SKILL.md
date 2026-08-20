---
name: fast-feedback-mode
description: Act fast, keep me in the zone.
license: MIT
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# /fast-feedback-mode

Optimize the feedback loop between you and the human, keeping the human in the loop.
Do only the work necessary for the human to see, use or try the change they requested, keeping them engaged as much as possible.
While deferring all work that finalizes the change until they say so.

For example:

1. a user asked for a UI Change, do the code changes that let them see it, and defer writing tests, running lints, tests, committing, updating PRs, etc.
2. a change require a lot of background work but can be mocked now to show the user the experience.

Keep track of deferred items in a TODO List tool if it's available to you. And in conversation if not.
While in this mode you also try to talk as little as possible. If user ask you to move a button, do it and say done.
Unless you have a question, want to explain a gotcha, or took a tricky decision. Do not state what changed everytime.

## While On

State that the mode is on. Tell the user to say "finalize" or similar word to end a turn, then wait for the first request from them.

- Change only the code to satisfy the user's requests and only their request.
- Skip writing tests, running tests, linters, formatters, and other checks, or update docs.
- After each change: say what changed minimally, then wait for another request, finalize, or turning off the mode.
- If user switched to a completely unrelated different feature, consider reminding them to finalize the previous work.
- Do not commit changes unless you finalize.
- Do not assume that finalize means commit.
