---
name: scaffold-skill
description: >
  Load when creating a new skill, scaffolding a SKILL.md, adding a reference page to a skill, writing or tuning a skill's description, or restyling/auditing an existing skill.
  Carries the authoring patterns (progressive disclosure, router, voice, triggering) a skill is shaped with.
license: MIT
argument-hint: "[scaffold <name> | restyle <skill> | description <skill>]"
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# scaffold-skill

A skill encodes ideas and patterns, not specific prescriptions.
Everything below is a default with an intent behind it; deviate when you can state what following it would cost the skill at hand.
Don't copy an example's shape verbatim into a skill it doesn't fit just to follow.

## Scaffolding

This skill scaffolds and writes the first version of a skill. It does not ship the final one.
Build it talking with the user: the calls that shape the skill (what it encodes, who fires it, how it splits) are theirs, ask instead of assuming.
And expect and ask the user to come back and trim. A skill gets good when its owner cuts it down to what they actually mean, so hand off the draft with a note on what you'd cut first.

## Doctrine

### Encode the delta, not the manual

Rely on the model's world knowledge. A skill carries the practices, gotchas, and conventions the model wouldn't apply on its own, usually from user's experience and observed gotchas.
Enumerating a tool's features duplicates pretraining and rots as the tool moves.

### Examples, and overfitting

A lot of skill guidance, especially early ones focused too much on mentioning examples.

Model world knowledge is usually underestimated:
an example of something in pretraining (how to commit, how to open a PR) teaches nothing,
and anchors the agent to one instance; the skill overfits to today's case and rots. It's a delicate balance. An example is good when:

- **Output must be consistent across runs.** The skill exists to make every run produce the same
  shape: a PR-body skeleton, a scaffolded CI workflow, a config template. Show the exact template
  (or ship it as an asset) and instruct to use it as verbatim as possible if it's something expected to be consistent.

- **The model demonstrably errs.** A syntax it reliably flips, a flag it invents. Show the wrong and the right form; one verified case is enough.

Otherwise state the rule and skip the example; the model knows the how.

### Progressive disclosure

A small skill is one SKILL.md. When distinct tasks need distinct rules, SKILL.md becomes a router:
cross-cutting, easily-missed doctrine stays in SKILL.md; each clear task's rules move to a `references/` page.

Inline what every path needs; push down what only one path reads.
Don't scaffold `references/` speculatively. Don't over do it ... too many references means we rely more on the Agent deciding the perfect references.

A router entry names the task the agent is about to do (not the topic), then gives a keyword-dense line of the page's contents so the agent picks without opening, e.g.:

```markdown
**Committing** -> [`references/commits.md`](references/commits.md)
Pre-staging walk, message style, hook-failure handling, scoping, empty commits.
```

The router isn't the only path between pages: references link sideways to each other wherever their rules touch, so an agent landing on one page still finds the rest. Mechanics in [`scaffold.md`](references/scaffold.md#reference-pages).

### Teach the reader how to read

A routed skill tells its agent, in SKILL.md, how to consume it:

- **Read the matching reference before planning or acting, not after.** Rules shape the plan; reading them late means redoing it. SKILL.md alone is not enough.
- **At least one reference per task**; several tasks, several references, this force model to think what to pick.
- **Local references eager, online links lazy.** Default to trusting model knowledge; go online only to learn more, or double check.
- **Link the authoritative docs as the escape hatch**: when the tool moves fast or reality disagrees with the skill, check the current docs and changelog instead.

### Voice

Skill prose is direct doctrine written for a stranger agent mid-task, with no access to the conversation that authored it.

- **No bullshit**, no performative wording. Just concise/dense and direct instructions.
- **Concise against your instincts.** A generated draft runs verbose and over-enumerated by default;
  a skill is the opposite artifact: a distillate of few rules, each earning its context cost.
  When coverage and concision fight, concision wins; world knowledge fills the gaps.
- **Strip pass** after every draft: remove audience narration ("engineers often..."), authoring-session residue ("as discussed"), and rhetorical flourish. State the model and the instruction; keep a why only as mechanism, not story.
- **Bold lead-ins.** `**Rule.** mechanics.` One rule per bullet; pages stay scannable.
- **Why as protection.** Attach `(why: ...)` where the reason stops a wrong move — "fixing" a deliberate choice, removing a needed workaround. Obvious whys are noise.
- **Leading words.** Prefer one strong pretrained concept over a restated triad ("a *tight* loop" over "fast, deterministic, low-overhead").
- **Rot-resistant.** Name the set, not its members (mark examples `e.g.`). Skip counts, versions, and file lists that rot; version-stamp only claims actually verified ("verified on X 1.2").

### Descriptions

Written last, once the tasks are real. A model-invoked skill pays for its description in context every turn.
A manual-only skill (`disable-model-invocation: true`) costs nothing, the user is its index; keep its description one neutral line without trigger phrasing.
(why: some harnesses ignore the invocation-off flag, and a trigger-rich description auto-fires the skill anyway.)

For model-invoked:

- **Short, made of words attention snags on.** Concrete action verbs first: "Load when about to commit, branch, push..."
- **Focus on Triggering**: Only target on what makes an Agent/User know to use the skill, don't enumerate what the skill does inside in the description, only what get someone who merely knows some keywords get to trigger the skill.
- **Say when not to load, only for common misfires.** A tool touched constantly earns its anti-trigger
  ("don't load for routine use that isn't changing config"); a rare misfire doesn't earn the words.
  (e.g don't load mise skill just to run mise install, only when modifying mise.toml)

## Router

**Scaffold or restructure a skill** -> [`references/scaffold.md`](references/scaffold.md)
Intake, invocation decision, layout, assets and the starter skeleton, frontmatter, build order (description last), reference-page patterns, variants, optional shapes skills sometimes take.
