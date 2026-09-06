---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the
whole frontier in one round, then wait for the user's answers before the next round.

**A round is a call to the harness's ask-the-user tool, never prose.** Whatever this harness names it: `AskUserQuestion` in Claude Code, `AskQuestion` (`cursor/ask_question`) in Cursor, `question` in
opencode. Each frontier question becomes one question in the call, its candidate answers become the options, and the recommended option goes first, labelled `(Recommended)`. A frontier wider than
the tool's question cap goes out as back-to-back calls, still one round.

**Every question stays answerable off-list.** Claude Code and opencode already offer free text beside the options, and Claude Code rejects an explicit "Other", so add nothing there. Cursor accepts
only the options it is handed, so give it one that invites a custom answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question
whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything
you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the
frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared
understanding.
