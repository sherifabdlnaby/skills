# Skill-fy an Existing Skill

Covers: rules, inventory, trace, findings, convert, verify, checklist.

Audit a skill against the doctrine in [`SKILL.md`](../SKILL.md), show the findings, transform on approval. The owner decides; the audit argues.

## Rules

- **Findings before edits.** No file changes until the user picks which findings to apply. (why: the owner is the eval; an audit that edits as it reads mixes its judgment with theirs.)
- **Disagree in the open.** Where the skill's choice contradicts the doctrine on purpose, report it as a disagreement, not a defect, and let the owner decide.
- **Files are the evidence.** Read the skill's files. The audit does not run the skill and does not collect transcripts.
- **Copied assets stay silent about this skill.** A skeleton copied into a skill never mentions skill-fy; the skill must read standalone.

## Procedure

### 1. Inventory

Read every file of the skill: SKILL.md, each `references/` page, `assets/`, `scripts/`. Note per file: the task that reads it, what it links to, what it needs from the environment.
Mark each line that fails a doctrine section with that section's anchor.

### 2. Trace

Walk the skill as a stranger agent would, once per task the description names. A walk starts at the description, enters SKILL.md, follows the router entry, then each sideways link on the page.
At every hop ask: with only the text read so far, would I open this page for this task?

Verdict per hop:

- **reached**: the pointer names what this task needs.
- **weak**: the pointer names a topic; the agent would assume it already knows and skip.
- **dead**: the link's target or anchor does not exist.

After all walks, list **orphans**: pages no walk reached.

```
Task: commit
  description -> SKILL.md              reached
  SKILL.md -> references/commits.md    reached
  commits.md -> branches.md#restack    weak: says "see branches", not what is there
  load: 2 pages

Orphans: references/env.md
```

Findings the trace raises:

- **Merge.** Two pages every walk loads together are one page split in two.
- **Overwhelm.** One task loads most of the skill: the split is by topic, not by task. Re-cut by what each task reads.
- **Performative disclosure.** Every task loads nearly every page: the router costs hops and saves nothing. Collapse toward one file.
- **Weak hop.** Reword the pointer to name what the page holds for this task. A restructure is the last resort.
- **Dead link, orphan.** Fix the link, or reach the page from the task that needs it. An orphan no task needs is deleted.

### 3. Findings

One list, ordered by damage: correctness first (pre-checks in the fast path, a missing Compatibility section, a slow-path step inside a workflow), then load (trace findings, sprawl, duplicated
meaning), then voice. Each finding names the file, the line, the doctrine anchor, and the proposed change. Disagreements are marked as such. Put the list to the user and ask which to apply.

### 4. Convert

Apply the approved findings per the doctrine section each one cites. Structural moves (merge, split, inline) before wording. Copy shapes from the skeletons rather than retyping them.
Re-run the trace after a structural move.

### 5. Verify

Every box below is accounted for: done, or the owner's stated disagreement.

## Checklist

- [ ] Description: concrete verbs first, trigger branches only, anti-trigger only for a common misfire; one neutral line if manual-only ([descriptions](../SKILL.md#descriptions))
- [ ] Invocation matches who fires it: model-invoked only when the agent or another skill must reach it
- [ ] Delta, not manual: no feature enumeration the model already knows ([delta](../SKILL.md#encode-the-delta-not-the-whole-manual))
- [ ] Examples only where output must be consistent or the model demonstrably errs ([examples](../SKILL.md#examples-and-overfitting))
- [ ] No pre-checks; the first real command is the check ([fast path](../SKILL.md#fast-path))
- [ ] Slow path behind `On failure`, routed into `setup.md` / `troubleshooting.md` by scenario; no fast-path step waits on a slow-path one
- [ ] Cache line present once in SKILL.md; commands are synopsis + usual call in a fenced block ([cache](../SKILL.md#commands-as-a-cache))
- [ ] Wide reads cached where a task consumes much state; saved to a file, queried locally
- [ ] Compatibility section present exactly when the skill needs more than the model and the filesystem; assume-present and bail rule stated ([environment](../SKILL.md#environment))
- [ ] Router entries name the task, then a keyword-dense contents line; no speculative pages ([disclosure](../SKILL.md#progressive-disclosure))
- [ ] How-to-read lines present in a routed skill ([how to read](../SKILL.md#teach-the-reader-how-to-read))
- [ ] Trace clean: no orphan, no dead link, no merge / overwhelm / performative finding left unaddressed
- [ ] Voice: bold lead-ins, one rule per bullet, why only as protection, no narration or session residue ([voice](../SKILL.md#voice))
- [ ] Rot-resistant: sets not members, no counts / versions / file lists, stamps only on verified claims
- [ ] Assets carry what must be consistent across runs; nothing retyped from prose
- [ ] Handed off as a draft with a note on what to cut first
