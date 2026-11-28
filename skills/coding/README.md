# Coding

[All skills](../)

This skill keeps code and documentation maintainable after the immediate task is forgotten. It prevents chat-specific solutions, premature abstractions, and comments that become misleading as the
project changes.

[Read the canonical skill instructions.](SKILL.md)

## How It Works

Changes follow a small set of defaults: take the simple, idiomatic path and the smallest diff, ask before adding code for unlikely edge cases, keep one source of truth, separate concerns, tolerate
limited duplication until the shared concept is clear, and make established extension points easy to extend. Opportunistic cleanup stays separate from feature work so each change remains reviewable.
State changes converge safely on rerun, validation sits at system boundaries, and a repeated correction becomes a check rather than more prose.

Debugging fixes the first place the system went wrong, not where the symptom surfaced, and work counts as done only when the real artifact shows it. Tests check what callers can observe, so they fail
when behavior breaks and survive a refactor.

Comments and documentation describe the steady state for a reader who knows the project but not the conversation that produced the change. Explanations are reserved for facts the code cannot show,
such as a workaround's cause, a deliberate limit and its threshold, or the event that ends a TODO. Lists that can drift are replaced by the rule that defines the set.

## Use

The skill is intended to load for any task that changes code or documentation. It can also be requested explicitly when reviewing a proposed implementation, refactor, comment, or document against
these conventions.

The comment keep list and the principles draw on [pstack](https://github.com/cursor/plugins/tree/main/pstack) by [poteto](https://github.com/poteto) (Lauren Tan), and on the comment and docs rules in
[t3code](https://github.com/pingdotgg/t3code).

Works with: [`no-comments`](../no-comments/README.md) and [`no-docs`](../no-docs/README.md), which enforce these rules on a diff.
