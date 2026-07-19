# Scaffold or Restructure a Skill

Covers: intake, invocation decision, layout, assets, frontmatter, build order, reference-page patterns and cross-linking, variants, optional shapes.

## Intake

Settle before touching files, with the user (ask, don't assume):

1. **What the skill encodes.** Conventions already stated, a workflow to freeze, or gotchas to
   catalog. A behavioral claim known only from docs or a changelog is a lead, not evidence:
   reproduce it (yourself, or delegate to a cheaper agent) before encoding it, and stamp the
   verified version.
2. **Who fires it.** The agent on its own, or only the user typing its name. Decision rules in [SKILL.md#descriptions](../SKILL.md#descriptions).
3. **How many distinct tasks.** One task fits a single SKILL.md; several want a router.

## Layout

One shape this commonly takes (keep only what the skill needs):

```
<name>/
  SKILL.md
  references/   # per-task rule pages; nest a dir when an axis has variants, e.g. references/ci/github.md
  assets/       # known-good files the skill copies out, instead of retyping them from prose
  scripts/      # executables the skill runs (long scripts live here, not inline in prose)
```

**Assets** are for anything the skill installs or starts from: a CI workflow a cicd skill drops into
`.github/workflows/`, the `mise.toml` + `AGENTS.md` a setup skill seeds a project with, a config
template, a PR-body skeleton. Copy the asset then adjust; an agent retyping a file from prose
drifts, a copied file doesn't. This skill eats its own cooking:
[`../assets/SKILL-skeleton.md`](../assets/SKILL-skeleton.md) is the starting file for a new skill.

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
2. **Reference pages one at a time**, each starting from [`../assets/reference-skeleton.md`](../assets/reference-skeleton.md); keep each router entry's contents line current as its page lands, and link pages sideways as their rules touch.
3. **Voice strip pass** over everything (the Voice doctrine in SKILL.md).
4. **Description last**, once the tasks are real. (why: written first, it bakes in branches the body ends up not having.)
5. **Hand off as a draft.** Tell the user what you'd cut first; the distilling is theirs to do.

## Reference pages

Start a page from [`../assets/reference-skeleton.md`](../assets/reference-skeleton.md). Patterns that serve it well:

- **Standalone over DRY.** A page is loaded alone; a short trap restated with a link to the authoritative page beats forcing a hop. Dedupe only long-form or drifted duplication.
- **Pages link sideways.** References cite other references wherever a rule leans on another page's
  mechanics: in place, anchored to the exact `#section`, with a read cue ("restack mechanics live
  in `branches.md#restacking`, read that too"). A hub page (a `-fy`/audit flow) references every
  other doc; a topic page links down into its variant pages (`ci.md` -> `ci/github.md`). This web
  is what lets an agent land on one page and still find the rest of the skill.
- **Fix discovery gaps in place.** When one route never finds a rule living on another page, add a small conditional cross-link at every entry point, anchored to the exact `#section` — not a restructure.
- **Covers line.** Open with `Covers: ...` naming the page's sections; it doubles as the router's contents line.
- **Safety first.** Rules that prevent damage lead the page, before workflow.
- **Gotcha catalogs.** Symptom -> mechanism -> discriminator -> fix. The discriminator (how to tell this case from its lookalike) is the valuable part.
