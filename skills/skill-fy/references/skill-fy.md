# Skill-fy an Existing Skill

Covers: rules, inventory, the smell catalog, planning the cuts with the owner, converting, verifying, checklist.

## Rules

1. **Know the target.** The doctrine in [SKILL.md](../SKILL.md) is the picture; the shapes it commonly takes are in [`scaffold.md`](scaffold.md) and the
   [skeletons](../assets/). Convert *toward* the picture, not toward a copy of another skill's exact layout.
2. **Inventory before editing.** Read every file the skill ships, not only SKILL.md; a smell on one page is often caused by another.
3. **Cheap fixes before structural.** Strip pass, rot, dead anchors, a nudge; then router recast, page split or merge, invocation change. Structural moves change how the skill is found and
   are the owner's call.
4. **A discovery gap gets a nudge, not a restructure.** A short conditional pointer at every entry point, anchored to the exact `#section`, keeps each page standalone and discovery in place.
5. **The owner trims.** Present the cuts; they decide. Every rule here is a default, and the owner's stated taste wins over it.
6. **Prose apart from structure.** Voice and rot edits in their own commit, separate from moves and splits, so each diff reads on its own.
7. **A description edit is measured.** Trigger rate moves in ways that don't show in a read; run the eval in [`triggering.md`](triggering.md#measuring) before and after.

## Procedure

### 1. Inventory

Read the whole skill, then record:

- **Frontmatter.** `name` matches the folder; invocation flag and whether the description matches it (neutral one-liner when manual-only, trigger-shaped when model-invoked).
- **Cost.** Tokens per file (`mise run tokens` in this repo, or any tokenizer). The description is paid every turn, SKILL.md on every load, a reference only when its route fires.
- **SKILL.md, passage by passage**: cross-cutting rule, router entry, how-to-read instruction, one-branch material, narrative, manual. The last three are findings.
- **Routes.** Which pages a router entry or a sideways link reaches, and which nothing reaches. Every anchor resolves.
- **Assets and scripts.** Referenced from a page, and free of headers that address the agent or the skill.
- **Claims.** Behavioral claims with a verification stamp, and the ones lifted from docs.

### 2. Audit: the smell catalog

Symptom -> mechanism -> fix. Cite the file and line for each finding.

- **Manual.** Enumerates the tool's features or flags the model already knows. Duplicates pretraining and rots with the tool. Fix: delete; keep the gotchas and conventions around it.
- **Overfit example.** An example of a pretrained thing, or a template mandated where output needn't be consistent. Anchors the agent to one instance. Fix: state the rule; keep an example only
  for consistent output or a demonstrated error (SKILL.md, *Examples*).
- **Narrative.** Audience narration, authoring-session residue, story-shaped whys. Fix: strip to the instruction; keep a why only where it stops a wrong move.
- **Rot.** Counts, versions, file lists, "new", "currently", an enumerated set. Fix: name the set, mark examples `e.g.`, stamp only verified claims.
- **Unverified claim.** A behavior stated as fact with no stamp, traceable to docs. Fix: reproduce it or downgrade it to a lead ("docs say X; check").
- **Thin index.** SKILL.md routes everything out, so the rules an agent would break mid-task sit on a page it never opens. Fix: lift the cross-cutting rules inline.
- **Sprawl.** SKILL.md carries material only one branch reads. Attention thins across it. Fix: push it down to the page that branch reads.
- **Speculative page.** A reference no route reaches, or one too thin to earn a hop. Fix: fold it into its neighbour, or delete it.
- **Discovery gap.** A rule on one page that another route to the same situation never reaches. Fix: a conditional nudge at each entry point, anchored (Rules, item 4).
- **Topic router.** An entry names a topic instead of the task the agent is about to do, or lacks the contents line. Fix: task verb first, then the keyword-dense line.
- **Dead anchor.** A link to a section that moved or was renamed. Fix: repoint, and add the anchor check to verification.
- **Description smells.** Abstract lead, internals enumerated, trigger phrasing on a manual-only skill, no anti-trigger on a constantly-touched tool. Fix: [`triggering.md`](triggering.md).
- **Ban.** A rule phrased as a prohibition with no positive target. Fix: state what to do; keep the ban only as a hard guardrail beside it.
- **Duplicate meaning.** The same long-form rule on two pages. A short standalone restatement with a link is fine; a drifted copy is the finding. Fix: one authoritative home, the other
  restates in a line and links.
- **No-op.** A sentence the model already obeys by default ("be careful", "think step by step"). Fix: delete the whole sentence, or replace the weak word with a stronger one.
- **Open-ended step.** A procedure step with no completion criterion, so the agent ends it early. Fix: a checkable, exhaustive bound ("every modified page accounted for").
- **Restated triad.** The same idea spelled out at several sites. Fix: one pretrained leading word, repeated as a token.
- **Skill-facing asset.** A copied-out file whose header says "see SKILL.md" or "adapt from references/". Fix: strip; the skill won't be there for future readers of the landed file.

### 3. Plan the cuts with the owner

The owner is the eval: there are no sample outputs to test against, so their picks are the spec. Run it as a design session:

1. **Rounds.** Group the findings (cheap, structural, needs the owner) and put them as questions through the ask-user tool, a recommended option first. Lead with what you'd cut first and the
   tokens it saves. The owner may keep a "smell" on purpose; that decision is the skill's taste, not a defect, and a rule of this page never overrides it.
2. **Audit.** Before converting, hand over an objective read of the whole plan, including where you'd decide differently from their picks, as one more round.
3. **Convert** only after that round.

### 4. Convert

Per finding, apply the matching doctrine or page. Strip pass over every passage touched. Descriptions last, once the pages settled, and measured.

### 5. Verify

- Frontmatter parses; `name` equals the folder name.
- Every link and anchor resolves (a link checker, or a grep for each `#anchor` against its target's headings).
- Every reference page is reached by a router entry or a sideways link; each router contents line matches its page's `Covers:` line.
- Token deltas explained: growth is fine when a rule earns it, and a cut that grew the skill is a finding.
- A changed description is re-measured ([`triggering.md`](triggering.md#measuring)).
- **Cold read.** Read SKILL.md alone as a stranger agent mid-task: it holds no rule you'd break without opening a reference, and no rule only one route needs.

## Checklist

The skill-fy isn't done until every box is accounted for:

- [ ] Every shipped file read and classified; cost per file recorded
- [ ] Frontmatter: `name` matches folder; description shape matches the invocation flag
- [ ] SKILL.md holds only cross-cutting doctrine, how-to-read, and the router; one-branch material pushed down
- [ ] No manual, no overfit example, no narrative left after the strip pass
- [ ] Rot removed: sets named, examples marked, only verified claims stamped
- [ ] Every page reachable; every anchor resolves; router contents lines match `Covers:` lines
- [ ] Discovery gaps closed with nudges at every entry point
- [ ] Steps end on a checkable completion criterion
- [ ] Assets carry no skill-facing headers
- [ ] Description rewritten last and measured before/after, or untouched
- [ ] Owner handed the list of what to cut next
