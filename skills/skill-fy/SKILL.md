---
name: skill-fy
description: >
  Load when creating a new skill, scaffolding a SKILL.md, adding a reference page to a skill, writing or tuning a skill (or their description)
  or restyling/auditing an existing skill. Carries the authoring patterns (progressive disclosure, router, voice, triggering logic) a skill is shaped with.
  Optionally use the skill to audit and transform an existing skill to the recommended shape.
license: MIT
argument-hint: "Skill-fy this skill | Audit this skill | Scaffold a skill <name>"
metadata:
  author: sherifabdlnaby
  version: "0.2.0"
---

# skill-fy

A skill encodes ideas and patterns, sometimes prescriptions if the user explicitly asked for this.

Everything below is a default with an intent behind; You're allowed to deviate only after stating why it would be better than the default.
Don't copy an example's shape verbatim into a skill it doesn't fit just to follow.

**Two modes:**

1. **Scaffold** and write the first version of a new skill.
2. **Skill-fy** an existing skill: audit it against the doctrine below, trace how an agent reads it, transform it on approval.

Both hand off a draft unless asked otherwise. Build it talking with the user, expect the user to hand edit parts, A skill gets good when its owner cuts it down to what they actually mean.

# How to use THIS Skill

The skill uses progressive disclosure: each mode routes to a `references/` file holding the procedure.
Read the matching one **before** planning or acting, not after. SKILL.md alone is not enough.

Load the **writing-for-agents** skill tool first when it is installed. It carries the theory this skill relies on.

## Router

**Scaffold a new skill, or add a reference page to one** -> [`references/scaffold.md`](references/scaffold.md)
Intake, invocation decision, layout, the skeletons, frontmatter, build order (description last), reference-page shapes (commands, inventory, on-failure), the trace before handoff.

**Skill-fy an existing skill** (audit + transform) -> [`references/skill-fy.md`](references/skill-fy.md)
Inventory, the trace (one walk per task, a verdict per hop), findings with disagreements, convert on approval, the checklist. References every doctrine section below.

**Tune a description** -> [Descriptions](#descriptions) below. No reference page.

## Doctrine

### Encode the delta, not the whole manual

Rely on the model's world knowledge. A skill carries the practices, gotchas, and conventions the model wouldn't apply on its own, usually from user's experience and observed gotchas.
Enumerating a tool's features duplicates pretraining and rots as the tool moves.

### Examples, and overfitting

Model world knowledge is usually underestimated:
an example of something in pretraining (how to commit, how to open a PR) teaches the model nothing,
and overfit the agent to one style; the skill overfits to today's case and rots. An example is good when:

- **Output must be consistent across runs.** The skill exists to make every run produce the same
  shape: a PR-body skeleton, a scaffolded CI workflow, a config template. Show the exact template
  (or ship it as an asset) and instruct to use it as verbatim as possible.

- **The model demonstrably errors.** A syntax it reliably miss, a flag it invents or not use correctly, a check it runs unasked. Show the wrong and the right form; one verified case is usually enough.

Otherwise state the rule and skip the example; the model knows the how.

### Fast path

A skill runs many times a day; its setup and prerequisite checks runs once. Setup and prerequisite checks need to run outside of the fast happy path.

- **Assume, then act.** The tool is installed, the login is valid, the service is up. The first real command *is* the check; its failure routes to the slow path.
- **Pre-checks the fast path never carries.** Each is a habit the model has, so the skill names it:
  - tool present or version. Wrong: `which gh`, `gh --version`, then `gh pr create`. Right: `gh pr create`.
  - login state. Wrong: `gh auth status`, then the call. Right: the call; its auth error names the fix.
  - `--help` or the docs before a command the skill already shows. Wrong: read, then run. Right: run the cached call; read on a cache miss.
- **The slow path lives behind a failure.** A reference page ends with an `On failure` block: symptom, quick fix, then a link into `setup.md` (one-time: install, auth, config) or `troubleshooting.md`
  (diagnose), by scenario. Most importantly outside the main/commong/fast workflow. Example Shape in [`scaffold.md`](references/scaffold.md#reference-pages).
- **Cadence rules dependencies.** A fast-path step never waits on a slow-path one; it nags instead. (why: a skill that re-verifies its setup on every run pays the setup cost daily.)

### Commands as a cache

A command in a skill is a cached lookup, not documentation. It saves the agent a `--help` on the usual call; it does not replace one.

- **Show the fast path only.** A synopsis with the flags that matter, then examples of the usual calls, in one fenced block. Do not do a walkthrough of the tool. (why: an enumerated surface duplicates
  pretraining and rots as the tool moves.)
- **Declare the cache once.** SKILL.md carries one line: commands shown are the usual call, not the full surface; `--help` and current docs are authoritative. Not per block.
  (why: doc voice reads as "the only way that exists"; the agent then tries variants of the cached call instead of reading `--help`.)
- **A cache miss goes to the source.** A flag the block lacks, an error it did not predict, a version that behaves differently: read `--help` or the docs, then act. One read beats three guessed
  variants.
- **Synopsis over prose.** `gh pr create [--fill] [--base <branch>] [--draft]` teaches the shape in one line. The same in prose costs more and anchors to one call.
- **One wide read beats many narrow ones.** When the task consumes a lot of state anyway (a PR's reviews, checks, and files; a project's tool versions), cache one piped command that gathers all of it
  in a single call. Multi-line is fine; it must paste and run as one unit.
- **Save the wide read, query it locally.** Write the output to a temp file once and `jq` it as questions come up. (why: each re-run is a round trip and a chance to drift; a file answers every
  follow-up for free.)
- **A wide read is not a pre-check.** It runs because the task needs the data, not to confirm the tool exists. The fast-path rule still holds.

### Environment

A skill runs on more than one host/environment. Think along the following axes, declare the result, and do not probe for it.

- **Axes.**
  - Network and sandbox (no network, no installs, read-only tree).
  - System tools and services (a CLI, Docker, VPN, a running local service).
- **Declare only when there is something to declare.** A skill that needs anything beyond the model and the filesystem ends SKILL.md with a `## Compatibility` section: a `Needs:` line, and a `Hosts:`
  line with a verdict and reason per host. A skill with no needs has no section. Shape in the [skeleton](assets/SKILL-skeleton.md).
- **Assume present** bail early on failure on a listed unsupported host. The goal is for the skill to fail gracefully and not get the agents into loops until they figure out they're in a sandbox.

### Interactive vs autonomous

A skill need to differentiate and be aware of when the skill is triggered via autonomous unattended system (Cron, Trigger, etc), or by a Human (Interactive).
A skill workflow need to declare both so we can easily add conditions (if interactive do that), (unless autonomous, confirm with user ) and so on. Build this in the doctrine of the skill you build.

### Progressive disclosure

A small skill is one SKILL.md. When distinct tasks need distinct rules, SKILL.md becomes a router:
cross-cutting, easily-missed doctrine stays in SKILL.md; each clear task's rules move to a `references/` page.

Inline what every path needs; push down what only one path reads.
Don't scaffold `references/` speculatively. Too many references means relying on the agent to pick the perfect one every time.

A router entry names the task the agent is about to do (not the topic), then gives a keyword-dense line of the page's contents so the agent picks without opening, e.g.:

```markdown
**Committing** -> [`references/commits.md`](references/commits.md)
Pre-staging walk, message style, hook-failure handling, scoping, empty commits.
```

The router isn't the only path between pages: references link sideways to each other wherever their rules touch, so an agent landing on one page still finds the rest. Mechanics in
[`scaffold.md`](references/scaffold.md#reference-pages).

The split is right when the trace says so: each task loads its own few pages, no page is loaded by every task, none is loaded by no task. The trace lives in
[`skill-fy.md`](references/skill-fy.md#2-trace).

### Teach the reader how to read

A routed skill tells its agent, in SKILL.md, how to consume it:

- **Read the matching reference before planning or acting, not after.** Rules shape the plan; reading them late means redoing it. SKILL.md alone is not enough.
- **At least one reference per task**; several tasks, several references, this forces the model to think what to pick.
- **Local references eager, online links lazy.** Default to trusting model knowledge; go online only to learn more, or double check.
- **Link the authoritative docs as the escape hatch**: when the tool moves fast or reality disagrees with the skill, check the current docs and changelog instead.

### Voice

Skill prose is direct doctrine written for a stranger agent mid-task, with no access to the conversation that authored it.

- **No bullshit**, no performative wording. Just concise/dense and direct instructions.
- **Concise against your instincts.** A generated draft runs verbose and over-enumerated by default;
  a skill is the opposite artifact: a distillate of few rules, each earning its context cost.
  When coverage and concision fight, concision wins; world knowledge fills the gaps.
- **Strip pass** after every draft: remove audience narration ("engineers often..."), authoring-session residue ("as discussed"), and rhetorical flourish. State the model and the instruction; keep a
  why only as mechanism, not story.
- **Bold lead-ins.** `**Rule.** mechanics.` One rule per bullet; pages stay scannable.
- **Why as protection.** Attach `(why: ...)` where the reason stops a wrong move: "fixing" a deliberate choice, removing a needed workaround. Obvious whys are noise.
- **Leading words.** Prefer one strong pretrained concept over a restated triad ("a *tight* loop" over "fast, deterministic, low-overhead").
- **Rot-resistant.** Name the set, not its members (mark examples `e.g.`). Skip counts, versions, and file lists that rot; version-stamp only claims actually verified ("verified on X 1.2").

### Descriptions

Written last, once the tasks are real. A model-invoked skill pays for its description in context every turn.
A manual-only skill (`disable-model-invocation: true`) costs nothing, the user is its index; keep its description one neutral line without trigger phrasing.
(why: some harnesses ignore the invocation-off flag, and a trigger-rich description auto-fires the skill anyway.)

For model-invoked:

- **Short, made of words attention snags on.** Concrete action verbs first: "Load when about to commit, branch, push..."
- **Focus on triggering.** Only what makes an agent or user know to use the skill; don't enumerate what the skill does inside. Someone who merely knows some keywords should land on it.
- **Say when not to load, only for common misfires.** A tool touched constantly earns its anti-trigger
  ("don't load for routine use that isn't changing config"); a rare misfire doesn't earn the words.

## Always applies

Process floor for both modes; hold to it even when fixated on one task.

1. **The owner decides.** Put every shaping call to the user; the audit argues, it does not overrule.
2. **Trace before handoff.** Every draft and every audit walks the graph once ([`skill-fy.md`](references/skill-fy.md#2-trace)); an orphan page or a performative split never ships.
3. **Strip pass, then description.** Voice strip over everything, then the description, last.
4. **Copy shapes from the skeletons**, never retype them from prose. A copied file doesn't drift.
5. **Hand off as a draft** with a note on what you'd cut first.
