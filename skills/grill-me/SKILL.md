---
name: grill-me
description: A relentless interview to sharpen a plan or design.
disable-model-invocation: true
---

Call the Skill tool with "grilling".

**Every round goes through the `AskUserQuestion` tool, overriding the markdown template `grilling` shows.** Each frontier question becomes one question in the call, its candidate answers become the
options, and the recommended option goes first, labelled `(Recommended)`. The user picks; nothing is put to them as prose. A frontier wider than the tool's four-question cap goes out as back-to-back
calls, still one round.
