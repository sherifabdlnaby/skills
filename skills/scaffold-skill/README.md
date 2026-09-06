# scaffold-skill

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C532%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,532 tokens" />
  <img src="https://img.shields.io/badge/Total-2%2C890%20tokens-2ea44f?style=flat-square" alt="Total: 2,890 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                                           | Tokens |
| -------------------------------------------------------------- | -----: |
| [`SKILL.md`](SKILL.md)                                         |  1,532 |
| [`assets/SKILL-skeleton.md`](assets/SKILL-skeleton.md)         |    187 |
| [`assets/reference-skeleton.md`](assets/reference-skeleton.md) |    189 |
| [`references/scaffold.md`](references/scaffold.md)             |    982 |

<!-- token-estimates:end -->

`scaffold-skill` helps create or restructure an AI skill that is concise, easy to trigger correctly, and organized so only relevant guidance is loaded for a task. It is useful when a skill has become
a tool manual, has unclear activation rules, or needs references and reusable templates.

[Read the canonical skill instructions.](SKILL.md)

## What it provides

The process first establishes what uncommon knowledge or workflow the skill should preserve, whether it is invoked automatically or only by name, and how many distinct tasks it covers. A small skill
stays in one `SKILL.md`; a larger one uses a compact router and focused reference pages with links between related rules.

The outcome is a first draft, not a finished skill. It is shaped with its owner, checked for unnecessary explanation and fragile examples, and handed back with clear opportunities to trim. The
activation description is written last, after the actual task boundaries are known.

The files under `assets/` are intentionally small skeletons for a new skill and a reference page. Assets are appropriate for output that should stay consistent across uses, such as configuration or
document templates. They are starting structures, not mandatory sections and not substitutes for deciding what the skill needs.

## Boundaries and tradeoffs

- Skills should capture practices, failure modes, and conventions that general model knowledge does not reliably supply. Repeating a product manual adds cost and becomes stale.
- Progressive disclosure helps when tasks have distinct guidance, but speculative reference pages make discovery harder and increase context use.
- Exact examples are valuable when output must be stable or a known error must be prevented. Otherwise they can overfit the skill to one case.
- Reference pages should work on their own even when that requires a small amount of duplication.
- Claims learned only from external documentation should be verified before they become durable skill rules.
- Automatic invocation needs a short, concrete trigger description. Manual-only skills should avoid trigger-rich descriptions that could cause accidental activation.

## Example requests

- "Scaffold a skill for reviewing database migrations."
- "Split this large skill into a router and focused reference pages."
- "Rewrite this skill description so it activates only for configuration changes."
- "Add a reusable workflow template as an asset to this skill."
- "Audit this skill for stale examples, excess prose, and discovery gaps."
