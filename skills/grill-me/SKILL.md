---
name: grill-me
description: A relentless interview to sharpen a plan or design.
disable-model-invocation: true
---

Call the Skill tool with "grilling".

**Every round goes through the harness's ask-the-user tool, overriding the markdown template `grilling` shows.** Whatever this harness names it: `AskUserQuestion` in Claude Code, `AskQuestion`
(`cursor/ask_question`) in Cursor, `question` in opencode. Each frontier question becomes one question in the call, its candidate answers become the options, and the recommended option goes first,
labelled `(Recommended)`. A frontier wider than the tool's question cap goes out as back-to-back calls, still one round. The user picks; nothing is put to them as prose.

**Every question stays answerable off-list.** Claude Code and opencode already offer free text beside the options, and Claude Code rejects an explicit "Other", so add nothing there. Cursor accepts
only the options it is handed, so give it one that invites a custom answer.
