---
name: skill-fy
description: >
  Use when creating a new skill, scaffolding a SKILL.md, adding a reference page or asset to a skill,
  writing or tuning a skill's description, or auditing, trimming, or restyling an existing skill.
  Carries the authoring taste a skill is shaped with: encode the delta, progressive disclosure, voice, descriptions that trigger.
  Optionally use the skill to audit an existing skill and transform it to that shape, aka (skill-fy).
license: MIT
argument-hint: "Skill-fy this skill | Audit this skill | Scaffold a skill for <topic>"
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# skill-fy

A skill encodes ideas and patterns, not specific prescriptions. Everything below is a default with an intent behind it;
deviate when you can state what following it would cost the skill at hand. Don't copy an example's shape verbatim into a skill it doesn't fit just to follow.

**The skill has two modes:**

1. Authoring taste while creating or editing a skill: what to encode, how to split it, how it should read, how it triggers.
2. **Skill-fy** an existing skill: audit it against this doctrine, find what is wrong, and transform it.

Both hand back a draft. A skill gets good when its owner cuts it down to what they actually mean, so end with a note on what you'd cut first.

# How to use the skill

The skill uses progressive disclosure: each task routes to a `references/` file holding the actual rules.
Read the matching one **before** planning or acting, not after. SKILL.md alone is not enough.

## Router

**Scaffold a new skill** -> [`references/scaffold.md`](references/scaffold.md)
Intake, invocation decision, layout, assets and the starter skeletons, frontmatter, build order (description last), reference-page patterns, hand-off.

**Skill-fy an existing skill** (audit, trim, restructure, restyle) -> [`references/skill-fy.md`](references/skill-fy.md)
Inventory -> audit against the smell catalog -> plan the cuts with the owner -> convert -> verify, plus the checklist. References every other doc.

**Description & triggering** (write, tune, measure) -> [`references/triggering.md`](references/triggering.md)
The levers that move trigger rate, anti-triggers, manual-only descriptions, measuring on the real installed skill, prompts that never fire cold.

### Complementary skill

**Leading words, negation, pruning, information hierarchy, completion criteria** -> load the **writing-for-agents** skill if installed
([vendored beside this one](../vendor/writing-for-agents/SKILL.md)). This skill carries the taste; that one explains the mechanisms it leans on, and is not restated here.

## Doctrine

### Encode the delta, not the manual

Rely on the model's world knowledge. A skill carries the practices, gotchas, and conventions the model wouldn't apply on its own, usually from the owner's experience and observed gotchas.
Enumerating a tool's features duplicates pretraining and rots as the tool moves.

### Verified, not read

A behavioral claim known only from docs or a changelog is a lead, not evidence. Reproduce it (yourself, or delegate to a cheaper agent) before encoding it, and stamp the verified version
("verified on X 1.2"). Unstamped claims are the first thing a skill-fy pass questions.

### Examples, and overfitting

Model world knowledge is usually underestimated: an example of something in pretraining (how to commit, how to open a PR) teaches nothing,
and anchors the agent to one instance; the skill overfits to today's case and rots. An example is good when:

- **Output must be consistent across runs.** The skill exists to make every run produce the same shape: a PR-body skeleton, a scaffolded CI workflow, a config template.
  Show the exact template (or ship it as an asset) and instruct to use it as verbatim as possible.
- **The model demonstrably errs.** A syntax it reliably flips, a flag it invents. Show the wrong and the right form; one verified case is enough.

Otherwise state the rule and skip the example; the model knows the how.

### Progressive disclosure

A small skill is one SKILL.md. When distinct tasks need distinct rules, SKILL.md becomes a router:
cross-cutting, easily-missed doctrine stays in SKILL.md; each clear task's rules move to a `references/` page.

- **Inline what every path needs; push down what only one path reads.**
- **SKILL.md is not a thin index.** A rule an agent would violate mid-task without thinking to open a reference lives inline, however tidy routing it out would look.
- **Don't scaffold `references/` speculatively.** Too many pages means relying on the agent to pick the perfect one.
- **Router entries name the task**, not the topic, then a keyword-dense line of the page's contents so the agent picks without opening, e.g.:

  ```markdown
  **Committing** -> [`references/commits.md`](references/commits.md)
  Pre-staging walk, message style, hook-failure handling, scoping, empty commits.
  ```

- **Pages link sideways** wherever their rules touch, so an agent landing on one page still finds the rest. Mechanics in [`scaffold.md`](references/scaffold.md#reference-pages).

### Teach the reader how to read

A routed skill tells its agent, in SKILL.md, how to consume it:

- **Read the matching reference before planning or acting, not after.** Rules shape the plan; reading them late means redoing it.
- **At least one reference per task**; several tasks, several references. This forces the model to think about what to pick.
- **Local references eager, online links lazy.** Default to trusting model knowledge; go online only to learn more, or to double check.
- **Link the authoritative docs as the escape hatch**: when the tool moves fast or reality disagrees with the skill, check the current docs and changelog instead.

### Voice

Skill prose is direct doctrine written for a stranger agent mid-task, with no access to the conversation that authored it.

- **No bullshit**, no performative wording. Concise, dense, direct instructions.
- **Concise against your instincts.** A generated draft runs verbose and over-enumerated by default; a skill is the opposite artifact: a distillate of few rules, each earning its context cost.
  When coverage and concision fight, concision wins; world knowledge fills the gaps.
- **Strip pass** after every draft: remove audience narration ("engineers often..."), authoring-session residue ("as discussed"), and rhetorical flourish.
  State the model and the instruction; keep a why only as mechanism, not story.
- **Bold lead-ins.** `**Rule.** mechanics.` One rule per bullet; pages stay scannable.
- **Why as protection.** Attach `(why: ...)` where the reason stops a wrong move: "fixing" a deliberate choice, removing a needed workaround. Obvious whys are noise.
- **Say the target, not the ban.** A prohibition drags the banned behaviour into context; state what to do instead, and keep a ban only as a hard guardrail paired with its positive form.
- **Leading words.** Prefer one strong pretrained concept over a restated triad ("a *tight* loop" over "fast, deterministic, low-overhead").
- **Rot-resistant.** Name the set, not its members (mark examples `e.g.`). Skip counts, versions, and file lists that rot; version-stamp only claims actually verified.

### Descriptions

Written last, once the tasks are real. A model-invoked skill pays for its description in context every turn; it exists to trigger, not to summarize.
A manual-only skill (`disable-model-invocation: true`) costs nothing, the user is its index; keep its description one neutral line without trigger phrasing.
(why: some harnesses ignore the invocation-off flag, and a trigger-rich description auto-fires the skill anyway.)

For model-invoked: concrete action verbs first, the words a user actually types, an anti-trigger only for a common misfire.
The levers, and how to measure whether a change helped, are in [`triggering.md`](references/triggering.md).
