---
name: my-skill
description: >
  Load when <concrete action verbs: the tasks that should fire this skill>.
  <One identity sentence: what the skill carries, so the agent knows what it's loading.>
  Load as early as possible, the moment <the topic> is anywhere in the chat's future.
# disable-model-invocation: true   # manual-only skills; then keep the description to one neutral line
metadata:
  version: "0.1.0"
---

# my-skill

<Cross-cutting doctrine: the rules an agent would violate mid-task without thinking to open a reference.>

## Router

<!-- Single-file skill? Delete this section and put the rules above. -->

**<Task the agent is about to do>** -> `references/<file>.md`
<Keyword-dense line of the page's contents, so the agent picks without opening.>
