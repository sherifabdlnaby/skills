# handoff

`handoff` compacts the current conversation into a focused document that a fresh session can use to continue the work. See [`SKILL.md`](../../../skills/vendor/handoff/SKILL.md) for the canonical agent instructions.

## Use

Invoke the skill when changing sessions or agents:

```text
/handoff [what the next session will focus on]
```

The optional focus tailors the handoff to the next task. The document captures the live context, points to relevant workspace artifacts and URLs instead of repeating them, and names useful skills for
the next session.

The handoff is written to the operating system's temporary directory rather than the project. It is a transfer aid, not a replacement for plans, decisions, commits, or other durable project records.
Sensitive values and personal information are removed.

## Source

Vendored from **Matt Pocock**'s [`handoff`](https://github.com/mattpocock/skills/tree/main/skills/productivity/handoff) skill in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT).
