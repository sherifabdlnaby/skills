---
name: coding
description: >
  The user's coding and docs conventions and taste. Load FIRST, at the start of any task that touches code or docs.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.1.1"
---

# Coding

## Making Changes

**Note:** These rules are defaults; deviate only when you can state what following the rule would cost here.

- **DRY**: a string, a threshold, a supported-values list has one authoritative home, easy to change/update/extend.
- **Do not overfit**: Avoid overfitting solutions to problems in this chat. Think bigger.
- **Separation of Concerns & Extendable Components**: Insist on separation of concerns.
- **Duplication over the wrong abstraction governs structure**: tolerate two similar blocks until the shared concept is obvious (rule of three); a helper/component that needs a `mode` flag to serve both callers is the wrong abstraction.
- **Extend along the promised axis**: at three cases the axis is promised (rule of three); shape code to make the fourth easy to add, without overfitting to just today's use-cases.
- **Don't name a general structure after its first occupant**: once something is a shared slot or grouping, name it for the axis it opens — not for today's only member. Specificity belongs on the leaves.
- **Tidy/Refactor separate from feature work**: an opportunistic refactor is in its own commit. Each stays reviewable.

## Code Comments

Guiding Principles:

1. **Write for the stranger who understands the purpose of the project**: a comment must hold
   for a reader with only the file (and its project); with no access to this conversation, no
   contextual awareness of how the project evolved, no memory of the task that produced it. A
   comment that echoes this session's instructions fails (e.g. `// Doing X (no Y)` where Y is
   something only this conversation knows).
2. Write to a reader who isn't aware of our chats, and does not include explanations or justifications based on our current conversation, or from our chat.
2. STOP Making code comments that make sense only in the context of the chat that overfit to our current conversation.
3. DO Not add comments about delta that are not with main. A comment to explain evolution of something between two commit of the same branch is redundant and won't make sense once commits are squashed.
2. **Describe the steady state, not the delta**: `// reads users_v2`, not `// migrated from
   users_v1`. Git records the transition, and delta comments become lies the moment it
   completes. A transition that must live in the code is a TODO with an end condition, never
   loose prose. Same for deletions and moves: git history is the record; leave no `moved to X`
   breadcrumb behind.
3. **WHY only as protection**: explain how we got here only when it stops the stranger from a wrong move, like "fixing" a deliberate choice, removing a needed workaround, or mistaking a cut corner for naivety. The next three principles are its instances.
4. **Mention a rejected alternative only as a warning**: keep `// not cached: results are user-specific` because it stops a stranger from "fixing" it; drop `// using native Map (no lodash)` because that avoidance only answers this session's instruction.
5. **Workarounds cite their cause**: `// workaround: SDK drops keepalive on h2, see github.com/x/y#456`. The link is the stranger's only way to check it's still needed.
6. **A cut corner names its ceiling**: `// good enough: O(n²) scan; revisit past
   ~1k rules` states the limit and the upgrade trigger, so the stranger can tell
   deliberate simplicity from naivety. Only for real corners with a known ceiling;
   trivial simplifications need no plaque.
7. **A TODO names what ends it**: a ticket, date, or event, as in `// TODO(PROJ-123): drop fallback after v2 ships`. Same for any "temporary"/"for now" claim; without an end condition it's permanent. Bare `// TODO: clean up` is a wish that sediments.
8. **Avoid enumeration; name the set, not its members**: `// sanitize PII
   fields`, not `// sanitize email, phone, SSN, address`. The criterion stays true
   as the set grows; the list reads as complete and rots. When examples aid
   clarity, mark them illustrative: `(e.g. email, SSN)`.

## Docs

Docs follow the Code Comments principles; the stranger is the reader. Especially: name the set, not its members; and don't hard-code today's specifics (counts, versions, file lists) that rot as the project moves.
