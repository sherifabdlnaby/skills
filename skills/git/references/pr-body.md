# PR body

Covers: voice, blocks in body order, visuals, receipts and the structure hook, skeleton, linking, AI footers.

Apply [SKILL.md](../SKILL.md) voice to every block. The body has two readers: the reviewer today,
and whoever resumes the work later, a person or an agent. Decisions, Not covered and Follow-ups are
for the second one; the diff does not carry them.

## Voice

- **Summary and Changes are for a product person.** They know the product. They do not read code.
  Use Simplified Technical English, short sentences, and the product's own terms
  (`CONTEXT.md` when the repo has one; `CONTEXT-MAP.md` points to the right one). The other
  blocks are for engineers.
- **Name the few things that matter. The diff has the rest.** A changelog says what a person
  notices. A review guide says where to look.
- **Emphasis.** Bold the words a skimmer must catch: one phrase per block at most, never a whole
  sentence. Italic for a label the reader looks for on screen (a button, a menu, a page). A GitHub
  alert (`> [!NOTE]`, `> [!WARNING]` and the rest) for what the reviewer must not miss. Style
  nothing else.

## Blocks

In body order. Write each block, or drop it with a reason ([Receipts](#receipts)).

- **Human Note.** The user's own words, verbatim, in the `[!NOTE]` callout at the very top. Wait
  for the user to open it: they hand you a note, or they ask for one. Offer it as one more option
  only in a question you already ask. No paraphrase, no typo fixes, no punctuation changes.
- **Summary.** One paragraph, two to four sentences, in this order: the ticket link, one sentence
  that places the reader when the title does not (the feature or flow, in product terms), what
  used to happen, what changed. The prior behavior is a fact: read it from the diff. A motive
  needs a source (the ticket, a bug report, a failing test, the user). Without a source, write no
  motive. Say what changed, and leave the how to the review guide. A one-change PR is described
  here and drops Changes.
- **Visuals.** The one picture or diagram that carries the whole change, open. The rest collapsed
  under it. Rules in [Visuals](#visuals).
- **Changes.** The changelog, for the product reader. Each bullet leads with what a person
  notices. The mechanism follows in parentheses when it helps. Internal work reads
  `No user-visible change: <what moved>`. Flat up to about six bullets. Past that, group under
  bold product-area names (e.g. Search, Billing), never code layers.
- **Breaking.** A `> [!WARNING]` that names what breaks and what the reader must do about it.
- **Review guide.** Numbered, one line per stop: a file or area, then what to look at there.
  Order: the core change, then what changes because of it, then mechanical work (renames,
  generated code, CI) marked safe to skim. A diagram goes under its stop only when prose cannot
  carry the shape.
- **Decisions.** Top level. One bullet per real choice: `Chose X over Y: Z`. A constraint from
  the user is a Z. Write it as a fact about the system, never as who asked. A dead end appears
  only as the Y that lost. Drop the block when no alternative was weighed.
- **How to test locally** (collapsible). Setup the reader would not guess (e.g. a flag, seed data,
  an exact input). Written for the reader, not a record of what you did.
- **Verification** (collapsible). Three lines; each may say `none`. `Automated:` what the tests
  prove, never a count. `Manual:` the scenario, then what you observed; write `per How to test`
  when the steps are above. `Not covered:` what the reviewer must not assume was checked. Report
  only runs that happened.
- **Examples** (collapsible). Only when an example makes the diff clearer.
- **Follow-ups / out of scope** (collapsible). Seen and left for later on purpose, so the
  reviewer does not ask for it here.
- **Relevant Links.** Parent ticket or epic, docs used, related PRs. Forms in [Linking](#linking).
- **AI footer.** Last, after a `---`. Templates in [AI footers](#ai-footers).

## Visuals

- **A visual sits next to the shortest text it supports.** The whole change: the Visuals block.
  One changelog bullet: under that bullet. One review guide stop: under that stop. Two or more in
  one slot: the first open, the rest in a collapsible.
- **A picture earns its place when prose cannot carry the outcome:** UI before and after, an
  error state, rendered output, or a flow where the order is the point. When a code fence or a
  diagram says it better, use that.
- **Take shots from a dev env that already runs, or after the user asks.** An ask holds for the
  rest of the session: start what you need. Never start a server, an app or a browser on your own
  for a picture. A file already on disk is free (e.g. your own debugging shot, a recording the
  user gave).
- **A Before | After pair goes under a bullet when its words alone do not make the change clear**,
  and shots are available. A layout change passes; a label change does not. A PR where most
  bullets pass is a *guided diff*.
- **Diagrams.** Mermaid first, for a sequence or a flow. A fenced `diff` of a tree (component,
  file, call) when the point is what changed in the structure. A plain tree or pseudocode for a
  new area. The `show-me` skill carries these forms. An HTML artifact does not render on GitHub.
- **Upload, alt text and framing:** [`attach.md`](./attach.md).

## Receipts

- **Every block leaves a receipt.** A written block keeps its hidden `<!-- pr:x -->` marker where
  the skeleton puts it. A dropped block is named, with its reason, in one hidden line:
  `<!-- pr:dropped visuals: no UI | decisions: none weighed -->`. Both are invisible on GitHub.
  Human Note has none; it is the user's to open. (why: without a reason, a dropped block and a
  forgotten one look the same.)
- **The structure hook denies a post that misses a receipt**, where it is installed beside this
  skill, the same way the disclosure hook denies a missing footer. The message names the blocks.
  Add the marker or the dropped entry, then retry.
- **Repo template** (`<!-- pr:skeleton-off: <reason> -->`): when the repo ships a
  `PULL_REQUEST_TEMPLATE`, or its own instructions say how a body reads, theirs is the shape and
  ours is the content. Keep every heading and checkbox of theirs, in their order. Fold our blocks
  into the sections they fit: summary into their description, changes and review guide under the
  nearest heading, our collapsibles and links after their last section, the AI footer last.
  `gh pr create --body-file` does not apply the template for you: read the file and merge by hand.
  This marker, with its reason, replaces the receipts and silences the hook. Use the same marker
  for a body you did not shape (another author's PR).
- **Markdown inside `<details>` needs a blank line after `</summary>`**, as in the skeleton. Without
  it a fenced code block renders as literal backticks.

## Skeleton

Replace every `<...>` placeholder and instruction comment, or remove it with its block. Only the
`<!-- pr:x -->` markers and the `pr:dropped` line survive into the body.

```markdown
> [!NOTE]
>
> ### 🧍🏻 Human Note
>
> xxxx yyy zz <!-- verbatim, only if user gave one -->

### Summary

<!-- pr:summary -->

[TICKET-123](link) | <one sentence placing the reader, when the title does not>. <What used to happen.> <What changed.> <!-- no ticket, no prefix -->

**Visuals** <!-- pr:visuals -->

<the one picture or diagram that carries the change>

<details><summary>More</summary>

<the rest>

</details>

**Changes** <!-- pr:changes -->

- <What a person notices> (<mechanism, when it helps>).
- No user-visible change: <what moved>.

<!-- pr:breaking -->
> [!WARNING]
> **Breaking:** <what breaks, and what the reader must do about it>.

**Review guide** <!-- pr:review-guide -->

1. `<core file or area>`: <the real change>.
2. `<what changes because of it>`: <what to look at>.
3. Everything else is <renames, generated code, CI>, safe to skim.

**Decisions** <!-- pr:decisions -->

- Chose <X> over <Y>: <Z>.

---

<details><summary>How to test locally</summary> <!-- pr:how-to-test -->

<setup the reader would not guess>

</details>

<details><summary>Verification</summary> <!-- pr:verification -->

**Automated:** <what the tests prove>.
**Manual:** <the scenario, then what you observed>.
**Not covered:** <what the reviewer must not assume was checked>.

</details>

<details><summary>Examples</summary> <!-- pr:examples -->

<an example that makes the diff clearer>

</details>

<details><summary>Follow-ups / out of scope</summary> <!-- pr:follow-ups -->

<seen and left for later on purpose>

</details>

### Relevant Links

<!-- pr:links -->

<parent ticket or epic, docs, related PRs, prev/next PR (manual stacks only; gh-stack renders the stack)>

<!-- pr:dropped <block>: <reason> | <block>: <reason> -->

---

_<sub>🤖 Agent Decided PR: Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
<!-- footer emoji by how much human judgment is behind the PR: 🤖 Agent Decided, 📋 Human Planned, 🤝 Human Guided; see AI footers -->
```

## Linking

- The ticket prefixes the summary; parent ticket or epic go in `### Relevant Links`.
- Ticket URL: from the user, a repo config, or an earlier PR in the repo. None known means plain `TICKET-123` with no link, never a guessed base URL.
- Related PR, same repo: `#<num>` (GitHub auto-links). Another repo: `org/repo#<num>`.
- Docs (Notion, Confluence, RFC, README): clickable Markdown links, never raw URLs.
- Stacked PRs, manual path only: previous and next PR in `### Relevant Links`; return to edit once the next PR's URL exists. Under gh-stack, GitHub renders the stack itself.

## AI footers

These are the PR-**body** footers, one per tier. Which tier to pick, the placeholders, and the
comment and reply footers all live in [SKILL.md AI Disclosure](../SKILL.md#ai-disclosure). Append at
the very end, after a `---` separator. Where the disclosure hook that ships beside this skill is
installed, a post is denied when the footer is missing, so it goes in before the first `gh pr create`.

```markdown
_<sub>🤖 Agent Decided PR: Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

```markdown
_<sub>📋 Human Planned PR: Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

```markdown
_<sub>🤝 Human Guided PR: Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```
