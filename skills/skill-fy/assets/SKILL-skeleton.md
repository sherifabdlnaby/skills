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

Commands and synopses in this skill are the usual call, cached for speed, not the tool's surface.
For anything they do not cover, read `--help` or the current docs, then act.

## How to read

<!-- Single-file skill? Delete this section and the router; put the rules above. -->

Read the matching reference **before** planning or acting, not after; SKILL.md alone is not enough.
Read at least one; a task that spans several reads several.

## Router

**<Task the agent is about to do>** -> `references/<file>.md`
<Keyword-dense line of the page's contents, so the agent picks without opening.>

## Compatibility

<!-- Delete this section when the skill needs nothing beyond the model and the filesystem. -->

Assume everything below is present; do not probe for it. Stop early only on a host listed as unsupported.

Needs: <e.g. `gh` (authenticated), a Docker runtime, network>.
Hosts: <e.g. Claude Code CLI yes. claude.ai web no (no Docker). Sandbox no (no network). Autonomous runs no (asks the user)>.
