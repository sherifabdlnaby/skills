# skill-fy

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C801%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,801 tokens" />
  <img src="https://img.shields.io/badge/Total-6%2C081%20tokens-2ea44f?style=flat-square" alt="Total: 6,081 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| File                                                           |  Tokens |
| -------------------------------------------------------------- | ------: |
| [`SKILL.md`](SKILL.md)                                         | `1,801` |
| [`assets/SKILL-skeleton.md`](assets/SKILL-skeleton.md)         |   `187` |
| [`assets/reference-skeleton.md`](assets/reference-skeleton.md) |   `189` |
| [`references/scaffold.md`](references/scaffold.md)             | `1,138` |
| [`references/skill-fy.md`](references/skill-fy.md)             | `1,850` |
| [`references/triggering.md`](references/triggering.md)         |   `916` |

<!-- token-estimates:end -->

`skill-fy` is how I want skills written, and the pass that brings an existing skill to that shape. A skill that reads like a product manual, triggers on the wrong prompts, or
buries its one important rule on a page nobody opens is a skill that quietly does nothing. This one finds that and fixes it.

[Read the canonical skill instructions.](SKILL.md)

## What it provides

The skill has two modes:

- **Authoring mode** shapes a new skill, or an edit to one, around the taste: encode what the model would not do on its own, keep the entry file to the rules an agent would break mid-task,
  route the rest to focused pages that link sideways, write in a direct voice, and write the description last so it triggers on the words its owner actually types.
- **Skill-fy mode** audits an existing skill. It reads every shipped file, names each smell with its cause and fix (manual text, overfit examples, narrative, rot, unverified claims, thin-index
  or sprawling entry files, orphan pages, discovery gaps, weak descriptions, steps with no end condition), plans the cuts with the owner, converts, and verifies that every page is reachable
  and every anchor resolves.

Descriptions get their own page, because their effect only shows in a measurement: the levers that were found to move trigger rate, and how to measure a description change on the real
installed skill rather than a synthetic harness.

The files under `assets/` are small skeletons for a new skill and a reference page: starting structures, not mandatory sections.

## Boundaries and tradeoffs

- The skill encodes taste, so every rule is a default with an intent. The owner's stated preference wins over any rule, and a "smell" kept on purpose is not a defect.
- It relies on strong models' world knowledge instead of examples; a skill written this way is thin on hand-holding by design.
- The output of either mode is a draft. The distilling that makes a skill good is the owner's, so the hand-off names what to cut first.
- Trigger measurement is described for Claude Code. Other harnesses need their own runner; the metric and the levers carry over.
- Mechanisms this taste leans on (leading words, negation, pruning, information hierarchy) are explained by the vendored writing-for-agents skill and pointed at, not restated.

## Example requests

- "Scaffold a skill for reviewing database migrations."
- "Skill-fy the deploy skill: it has grown into a manual."
- "Audit this skill for stale examples, excess prose, and pages nobody reaches."
- "Rewrite this description so it fires on config changes and not on routine runs, and measure it."
- "Split this skill into a router and focused reference pages."
