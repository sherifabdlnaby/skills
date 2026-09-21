# skill-fy

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-2%2C901%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 2,901 tokens" />
  <img src="https://img.shields.io/badge/Total-6%2C389%20tokens-2ea44f?style=flat-square" alt="Total: 6,389 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                                                           |  Tokens |
| -------------------------------------------------------------- | ------: |
| [`SKILL.md`](SKILL.md)                                         | `2,901` |
| [`assets/SKILL-skeleton.md`](assets/SKILL-skeleton.md)         |   `369` |
| [`assets/reference-skeleton.md`](assets/reference-skeleton.md) |   `433` |
| [`references/scaffold.md`](references/scaffold.md)             | `1,440` |
| [`references/skill-fy.md`](references/skill-fy.md)             | `1,246` |

<!-- token-estimates:end -->

`skill-fy` helps create a skill, or audit and reshape an existing one, so that it is concise, triggers correctly, runs on the fast path, and loads only the guidance a task needs.
It is useful when a skill has become a tool manual, checks its prerequisites on every run, has unclear activation rules, or has grown reference pages nobody reaches.

[Read the canonical skill instructions.](SKILL.md)

## What it provides

**Two modes.** Scaffolding writes the first version of a new skill with its owner: what it encodes, who fires it, how many tasks it covers, and what it needs from the environment.
Skill-fy audits an existing skill against the same doctrine, reports findings (with any disagreements stated), and transforms the skill only after the owner picks which findings to apply.

**The doctrine** covers the delta a skill should carry instead of a manual, when an example earns its place, the fast path (no pre-checks; setup and diagnosis live behind a failure), commands as a
cache of `--help` rather than documentation, one wide read saved to a file instead of many round trips, and a compatibility section for skills that need more than the model and the filesystem.

**The trace** walks the skill the way a stranger agent would, once per task the description names, and gives a verdict per hop.
It shows whether the progressive disclosure is real: pages that always load together, one task that loads most of the skill, or a router that every task walks in full.

The files under `assets/` are the skeletons for a new SKILL.md and a reference page. They carry the shapes the doctrine describes (the cache line, the compatibility section, the fenced command, the
inventory block, the on-failure block) so a copied file matches the rules without retyping.

The outcome of either mode is a draft, not a finished skill. It is handed back with a note on what to cut first.

## Boundaries and tradeoffs

- Skills capture practices, failure modes, and conventions that model knowledge does not reliably supply. Repeating a product manual adds cost and becomes stale.
- The fast path assumes tools, logins, and services are present. A skill that verifies them on every run pays its setup cost daily; the failure itself is the check.
- Command examples are a cache, declared as such once. Without the declaration an agent reads the skill as the tool's whole surface and spins on variants instead of reading `--help`.
- Progressive disclosure helps when tasks have distinct guidance. Speculative reference pages make discovery harder, and a split every task walks in full is theater.
- Reference pages work on their own even when that requires a small amount of duplication.
- Claims learned only from external documentation are verified before they become durable rules.
- The audit reads files only. It does not run the skill, and it edits nothing until the owner approves.

## Example requests

- "Scaffold a skill for reviewing database migrations."
- "Skill-fy this skill."
- "Audit this skill and show me the trace."
- "Split this large skill into a router and focused reference pages."
- "Rewrite this skill description so it activates only for configuration changes."
- "Add a reusable workflow template as an asset to this skill."
