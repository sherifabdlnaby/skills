# Coding

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C048%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,048 tokens" />
  <img src="https://img.shields.io/badge/Total-1%2C048%20tokens-2ea44f?style=flat-square" alt="Total: 1,048 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |  1,048 |

<!-- token-estimates:end -->

This skill keeps code and documentation maintainable after the immediate task is forgotten. It prevents chat-specific solutions, premature abstractions, and comments that become misleading as the
project changes.

[Read the canonical skill instructions.](SKILL.md)

## How It Works

Changes follow a small set of defaults: keep one source of truth, separate concerns, tolerate limited duplication until the shared concept is clear, and make established extension points easy to
extend. Opportunistic cleanup stays separate from feature work so each change remains reviewable.

Comments and documentation describe the steady state for a reader who knows the project but not the conversation that produced the change. Explanations are reserved for facts the code cannot show,
such as a workaround's cause, a deliberate limit and its threshold, or the event that ends a TODO. Lists that can drift are replaced by the rule that defines the set.

## Use

The skill is intended to load for any task that changes code or documentation. It can also be requested explicitly when reviewing a proposed implementation, refactor, comment, or document against
these conventions.
