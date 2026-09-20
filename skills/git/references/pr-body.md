# PR body

Covers: voice, blocks in body order, visuals, receipts and the structure hook, skeleton, linking, AI footers.

Apply [SKILL.md](../SKILL.md) voice to every block. A body is read twice: by a reviewer now, and by
whoever picks the work up later, human or agent. Decisions, Not covered and Follow-ups are what the
second reader cannot get from the diff.

## Voice

- **Summary and Changes read for a product person** who knows the product, not the code: Simplified
  Technical English, short sentences, the product's own terms (`CONTEXT.md` when the repo has one;
  `CONTEXT-MAP.md` routes to the right one). The rest of the body is for engineers.
- **Name the few things that matter; the diff has the rest.** A changelog says what a person
  notices, a review guide says where to look. Short sentences, few of them.
- **Emphasis.** Bold the words a skimmer must catch: at most one phrase per block, never a sentence.
  Italic for a label the reader looks for on screen (a button, a menu, a page). A callout
  (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) for what the reviewer must not
  miss. Nothing else is styled.

## Blocks

In body order. Each block is written, or dropped with a reason ([Receipts](#receipts)); none is
left out by oversight.

- **Human Note.** The user's own words, verbatim, in the `[!NOTE]` callout at the very top. Opt-in
  and theirs to open: they hand you a note or ask for one. Drafting never waits on it; offering it
  as one more option in a question you are already asking is fine. No paraphrase, no typo fixes, no
  punctuation changes.
- **Summary.** One paragraph, two to four sentences: the ticket link; one sentence placing the
  reader when the title does not (the feature or flow, in product terms); what used to happen; what
  changed. Prior behavior is a fact you read from the diff. A motive needs a source (the ticket, a
  bug report, a failing test, the user); without one, no motive. The solution names what changed,
  not how. A one-change PR is described here and drops Changes.
- **Visuals.** The one picture or diagram that carries the whole change, open; the rest collapsed
  under it. When and where in [Visuals](#visuals).
- **Changes.** The changelog, for the product reader. Each bullet leads with what a person notices;
  the mechanism follows in parentheses when it helps. Internal work reads
  `No user-visible change: <what moved>`. Flat to about six bullets, then grouped under bold
  product-area names (e.g. Search, Billing), never code layers.
- **Breaking.** A `> [!WARNING]` naming what breaks and what the reader must do about it.
- **Review guide.** Numbered, one line per stop: a file or area, then what to look at there. Order:
  the core change, then what changes because of it, then mechanical work (renames, generated code,
  CI) marked safe to skim. A diagram sits under its stop only when prose cannot carry the shape.
- **Decisions.** Top level. One bullet per real choice, `Chose X over Y: Z`. A constraint the user
  set is a Z, written as a fact about the system, not as who asked. A dead end appears only as the
  Y that lost. None weighed, drop the block.
- **How to test locally** (collapsible). Setup the reader would not guess: a flag, seed data, an
  env var, an exact input. Written for them, not a record of what you did.
- **Verification** (collapsible). Three lines, each may say `none`. `Automated:` what the tests
  prove, never a count. `Manual:` the scenario, then what was observed; `per How to test` when the
  steps are above. `Not covered:` what the reviewer should not assume was checked. Never a plan,
  never a run that did not happen.
- **Examples** (collapsible). Only when an example clarifies the diff.
- **Follow-ups / out of scope** (collapsible). Seen and deliberately left for later, so the reviewer
  does not ask for it here.
- **Relevant Links.** Parent ticket or epic, docs used, related PRs. Forms in [Linking](#linking).
- **AI footer.** Last, after a `---`. Templates in [AI footers](#ai-footers).

## Visuals

- **A visual sits by the shortest text it supports.** The whole change: the Visuals block. One
  changelog bullet: under that bullet. One review guide stop: under that stop. Two or more in one
  slot: the first open, the rest in a collapsible.
- **A picture earns its place when prose cannot carry the outcome.** UI before and after, an error
  state, rendered output, a flow whose order is the point. A code fence or a diagram that says it
  better wins.
- **Shots are taken only when cheap.** A dev env already running, or the user asked (then start
  what you need; the ask holds for the session). A server, an app or a browser is never started for
  a picture. A file already on disk is free: your own debugging shot, a recording the user gave, a
  build's output.
- **A Before | After pair goes under a bullet whose words alone would not make the change clear**,
  when shots are cheap. A layout change passes, a label change does not. A PR where most bullets
  pass is a *guided diff*.
- **Diagrams.** Mermaid first, for a sequence or a flow. A fenced `diff` of a tree (component, file,
  call) when the point is what changed in the structure. A plain tree or pseudocode for a new area.
  The `show-me` skill carries these forms; an HTML artifact does not render on GitHub.
- **Upload, alt text and framing** are [`attach.md`](./attach.md).

## Receipts

- **Every block carries a receipt.** A written block keeps its hidden `<!-- pr:x -->` marker where
  the skeleton puts it. A dropped block is named, with its reason, in one hidden line:
  `<!-- pr:dropped visuals: no UI | decisions: none weighed -->`. Both are invisible on GitHub.
  Human Note is the exception, it is the user's to open. (why: a skip is a decision, and the reason
  is its proof.)
- **The structure hook denies a post missing a receipt**, where it is installed beside this skill,
  the way the disclosure hook denies a missing footer. Its message names the blocks: add the marker
  or the dropped entry, then retry.
- **Repo template** (`<!-- pr:skeleton-off: <reason> -->`): when the repo ships a
  `PULL_REQUEST_TEMPLATE` or its own instructions say how a body reads, theirs is the shape and
  ours is the content. Keep every heading and checkbox of theirs, in their order, and fold our
  blocks into the sections they fit: summary into their description, changes and review guide
  under the nearest heading, our collapsibles and links after their last section, the AI footer
  last. `gh pr create --body-file` does not apply the template for you: read the file and merge by
  hand. This marker, with its reason, stands in for the receipts and silences the hook. Same marker
  for a body you did not shape (another author's PR).
- **Markdown inside `<details>` needs a blank line after `</summary>`**, as in the skeleton. Without
  it a fenced code block renders as literal backticks (verified against GitHub's own renderer).

## Skeleton

Replace every `<...>` placeholder and instruction comment, or remove it with its block. The
`<!-- pr:x -->` markers and the `pr:dropped` line are the only comments that survive into the body.

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
**Manual:** <the scenario, then what was observed>.
**Not covered:** <what the reviewer should not assume was checked>.

</details>

<details><summary>Examples</summary> <!-- pr:examples -->

<an example that clarifies the diff>

</details>

<details><summary>Follow-ups / out of scope</summary> <!-- pr:follow-ups -->

<seen and deliberately left for later>

</details>

### Relevant Links

<!-- pr:links -->

<parent ticket or epic, docs, related PRs, prev/next PR (manual stacks only; gh-stack renders the stack)>

<!-- pr:dropped <block>: <reason> | <block>: <reason> -->

---

_<sub>🤖 Agent Decided PR: Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
<!-- footer emoji by how much human judgment is behind the PR: 🤖 Agent Decided, 🧍‍♂️👍 Human Approved, 🤝 Human Guided; see AI footers -->
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
installed, a post is denied when the footer is missing, and when a human tier is missing its
degree word, so it goes in before the first `gh pr create`.

```markdown
_<sub>🤖 Agent Decided PR: Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

```markdown
_<sub>🧍‍♂️👍 Human Approved PR (<glanced|read|tested>): Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

```markdown
_<sub>🤝 Human Guided PR (<nudged|steered|dictated>): Created with <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```
