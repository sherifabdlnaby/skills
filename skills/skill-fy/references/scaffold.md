# Scaffold a New Skill

Covers: intake, invocation decision, layout, assets and the starter skeletons, frontmatter, build order, reference-page patterns, hand-off.

Build it talking with the user: the calls that shape the skill (what it encodes, who fires it, how it splits) are theirs, ask instead of assuming.

## Intake

Settle before touching files:

1. **What the skill encodes.** Conventions already stated, a workflow to freeze, or gotchas to catalog. A claim known only from docs is a lead: reproduce it before encoding it, and stamp the
   verified version ([SKILL.md, *Verified, not read*](../SKILL.md#verified-not-read)).
2. **Who fires it.** The agent on its own, or only the user typing its name. A model-invoked skill pays for its description every turn; a manual-only one costs nothing and gets a neutral
   one-line description ([`triggering.md`](triggering.md#levers)).
3. **How many distinct tasks.** One task fits a single SKILL.md; several want a router. Don't plan pages for tasks that aren't real yet.

## Layout

One shape this commonly takes (keep only what the skill needs):

```
<name>/
  SKILL.md
  references/   # per-task rule pages; nest a dir when an axis has variants, e.g. references/ci/github.md
  assets/       # known-good files the skill copies out, instead of retyping them from prose
  scripts/      # executables the skill runs (long scripts live here, not inline in prose)
```

**Assets** are for anything the skill installs or starts from: a CI workflow, a config template, a PR-body skeleton. Copy the asset then adjust; an agent retyping a file from prose drifts, a
copied file doesn't. A landed asset carries no header that addresses the agent or points back at the skill (why: the skill won't be there for the file's future readers).
This skill eats its own cooking: [`../assets/SKILL-skeleton.md`](../assets/SKILL-skeleton.md) is the starting file for a new skill.

## Frontmatter

The skeleton carries the minimum. Common extras, host conventions vary:

```yaml
license: MIT
argument-hint: "[<arg> | <arg>]"   # shown when the user types /<name>; only when arguments make sense
metadata:
  author: <handle>
  version: "0.1.0"
```

`name` matches the folder.

## Build order

1. **Copy [`../assets/SKILL-skeleton.md`](../assets/SKILL-skeleton.md)** in as SKILL.md; fill the cross-cutting doctrine, then the router with planned entries.
2. **Reference pages one at a time**, each starting from [`../assets/reference-skeleton.md`](../assets/reference-skeleton.md); keep each router entry's contents line current as its page
   lands, and link pages sideways as their rules touch.
3. **Strip pass** over everything (SKILL.md, *Voice*).
4. **Description last**, once the tasks are real; the levers are in [`triggering.md`](triggering.md#levers).
5. **Verify** as a skill-fy pass would: links and anchors resolve, every page reachable, the cold read holds ([`skill-fy.md`](skill-fy.md#5-verify)).
6. **Hand off as a draft.** Tell the user what you'd cut first; the distilling is theirs to do.

## Reference pages

Start a page from [`../assets/reference-skeleton.md`](../assets/reference-skeleton.md). Patterns that serve it well:

- **Standalone over DRY.** A page is loaded alone; a short trap restated with a link to the authoritative page beats forcing a hop. Dedupe only long-form or drifted duplication.
- **Pages link sideways.** References cite other references wherever a rule leans on another page's mechanics: in place, anchored to the exact `#section`, with a read cue ("restack
  mechanics live in `branches.md#restacking`, read that too"). A hub page (a `-fy`/audit flow) references every other doc; a topic page links down into its variant pages
  (`ci.md` -> `ci/github.md`). This web is what lets an agent land on one page and still find the rest of the skill.
- **Fix discovery gaps in place.** When one route never finds a rule living on another page, add a small conditional cross-link at every entry point, anchored to the exact `#section`,
  not a restructure.
- **Covers line.** Open with `Covers: ...` naming the page's sections; it doubles as the router's contents line.
- **Safety first.** Rules that prevent damage lead the page, before workflow.
- **Steps end on a bound.** A procedure step names what done looks like, checkable and exhaustive, so the agent doesn't end it early.
- **Gotcha catalogs.** Symptom -> mechanism -> discriminator -> fix. The discriminator (how to tell this case from its lookalike) is the valuable part.
