# Show Me

[Read the canonical skill instructions.](../../../skills/vendor/show-me/SKILL.md)

When prose hides the important shape of a system, Show Me turns the current discussion into a focused visual explanation. The outcome can be a small inline diagram or a standalone HTML artifact, depending on what makes the point clear with the least extra detail.

It selects a format that matches the question: pseudocode for logic, call trees for runtime flow, component or file trees for ownership, Mermaid for interactions, and diffs for a proposed change. Dense UI or layout comparisons can become a responsive HTML page that uses the product's visual language and real labels.

This skill explains the topic already under discussion. It is not a full codebase audit, a polished product mockup, or a replacement for the source code. The visual intentionally omits calls, files, states, and boundaries that do not help answer the current question.

```text
/show-me How does a submitted command move from the UI to the daemon?
```

Vendored from [HumanLayer's skills repository](https://github.com/humanlayer/skills).
