# PR body

Covers: voice, blocks in body order, visuals, receipts and the structure hook, skeleton, linking.

Apply [SKILL.md](../SKILL.md) voice to every block. The body has two readers. The first decides
whether to merge, often without reading the diff. The open blocks are theirs: what changed, the
proof, where to look, what is not proven, what they must decide. The second resumes the work
later, a person or an agent. The collapsibles are their record; the diff does not carry them.

## Voice

- **Summary and the top-level Changes bullets are for a product person.** They know the product.
  They do not read code. Use Simplified Technical English, short sentences, and the product's own
  terms (`CONTEXT.md` when the repo has one; `CONTEXT-MAP.md` points to the right one). The other
  blocks are for engineers.
- **Name the few things that matter. The diff has the rest.** A changelog says what a person
  notices. A review guide says where to look.
- **A change carries its check.** A check says what was run, then what was seen, in plain words
  (e.g. `Imported a 2 GB file: done in 40 s.`, `A new test fails without the fix.`). Report only
  runs that happened. `CI is green` says neither: name what the tests prove. A change with no
  check is named in Not checked.
- **Emphasis.** Bold the words a skimmer must catch: one phrase per block at most, never a whole
  sentence. Italic for a label the reader looks for on screen (a button, a menu, a page). A GitHub
  alert (`> [!NOTE]`, `> [!WARNING]` and the rest) for what the reviewer must not miss. Style
  nothing else.

## Blocks

In body order. Write each block, or drop it with a reason ([Receipts](#receipts)). Not checked
and Your call are always written: `None.` is an answer.

- **AI disclosure.** What it says and where it goes: [SKILL.md AI Disclosure](../SKILL.md#ai-disclosure).
- **Human Note.** The user's own words, verbatim, in the `[!NOTE]` callout at the top of the body. Wait
  for the user to open it: they hand you a note, or they ask for one. Offer it as one more option
  only in a question you already ask. No paraphrase, no typo fixes, no punctuation changes.
- **Summary.** One paragraph, two to four sentences, in this order: the ticket link, one sentence
  that places the reader when the title does not (the feature or flow, in product terms), the
  problem (what happens today), the solution (what this PR changes), the improvement (what a
  person now sees or can measure; left out when there is none to name). The problem is a fact:
  read it from the diff. A motive needs a source (the ticket, a bug report, a failing test, the user).
  Without a source, write no motive. Say what changed, and leave the how to Why it works. A
  one-change PR is described here and drops Changes; its check goes in Proof.
- **Proof.** The one picture, recording or pasted output that shows the result, open. A fix shows
  before and after. The rest collapsed under it. Rules in [Visuals](#visuals).
- **Changes.** The changelog. Each top-level bullet leads with what a person notices, and reads
  complete alone. Sub-bullets, one level deep, carry the mechanism when it helps, and the check.
  Internal work reads `No user-visible change: <what moved>`. Three bullets or fewer stay flat.
  More are grouped under bold product-area names (e.g. Search, Billing), never code layers.
- **Breaking.** A `> [!WARNING]` that names what breaks and what the reader must do about it.
- **Review guide.** Small: five stops at most, numbered, the most important first. A stop is a
  file where the logic changed, linked to its diff in the PR ([Linking](#linking)), then what to
  look at there. Mechanical work (renames, generated code, version bumps, etc.) gets no stop: one
  closing line names it as safe to skim. A diagram goes under its stop only when prose cannot
  carry the shape.
- **Not checked.** What the reader must not assume was checked: a change with no check, an
  environment not tried, a case skipped. `None.` only when every change carries a check.
- **Your call.** What only the reader can decide before the merge: a tradeoff taken for them,
  work beyond the ask, a gap left open (e.g. `Merge without a run on staging?`). Three at most,
  each with the fact behind it. A file to read belongs in the review guide.
- **Why it works** (collapsible). The mechanism as behavior, with no file paths. A fix: the root
  cause, then why the change removes it. A feature: how the parts work together. A diagram goes
  here when the order or the shape is the point. Drop it when Changes already says it.
- **Decisions** (collapsible). One bullet per real choice: `Chose X over Y: Z`. A constraint from
  the user is a Z. Write it as a fact about the system, never as who asked. A dead end appears
  only as the Y that lost. What got worse reads `Cost: <what, and how much>`. A choice the reader
  must approve goes in Your call. Drop the block when no alternative was weighed.
- **How to test locally** (collapsible). Setup the reader would not guess (e.g. a flag, seed data,
  an exact input). Written for the reader, not a record of what you did.
- **Examples** (collapsible). Only when an example makes the diff clearer.
- **Follow-ups / out of scope** (collapsible). Seen and left for later on purpose, so the
  reviewer does not ask for it here.
- **Relevant Links.** Parent ticket or epic, docs used, related PRs. Forms in [Linking](#linking).

## Visuals

- **A visual sits next to the shortest text it supports.** The whole change: the Proof block.
  One changelog bullet: under that bullet. One review guide stop: under that stop. Two or more in
  one slot: the first open, the rest in a collapsible.
- **A picture earns its place when prose cannot carry the outcome:** UI before and after, an
  error state, rendered output, or a flow where the order is the point. When a code fence or a
  diagram says it better, use that.
- **Start the app for a picture only when it starts smoothly.** A dev env that already runs and
  a file already on disk (e.g. your own debugging shot, a recording the user gave) are free.
  Otherwise use the run command the repo documents, once. A failed start ends the attempt: name
  the missing picture under Not checked and move on. Stop what you started.
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
  `<!-- pr:dropped proof: nothing to observe | decisions: none weighed -->`. Both are invisible on GitHub.
  Human Note has none; it is the user's to open. (why: without a reason, a dropped block and a
  forgotten one look the same.)
- **The structure hook denies a post that misses a receipt**, where it is installed beside this
  skill. The message names the blocks.
  Add the marker or the dropped entry, then retry.
- **Repo template** (`<!-- pr:skeleton-off: <reason> -->`): when the repo ships a
  `PULL_REQUEST_TEMPLATE`, or its own instructions say how a body reads, theirs is the shape and
  ours is the content. Keep every heading and checkbox of theirs, in their order. Fold our blocks
  into the sections they fit: summary into their description, changes and review guide under the
  nearest heading, our collapsibles and links after their last section.
  `gh pr create --body-file` does not apply the template for you: read the file and merge by hand.
  The AI disclosure still opens the body, before their template; the template governs
  everything after that. This marker, with its reason, replaces the receipts and
  silences the hook. Use the same marker for a body you did not shape (another author's PR).
- **Markdown inside `<details>` needs a blank line after `</summary>`**, as in the skeleton. Without
  it a fenced code block renders as literal backticks.

## Skeleton

Replace every `<...>` placeholder and instruction comment, or remove it with its block. Only the
`<!-- pr:x -->` markers and the `pr:dropped` line survive into the body.

```markdown
<!-- AI disclosure: the ai-disclosure skill places it; without that skill, the fallback line from SKILL.md goes at the end -->

> [!NOTE]
>
> ### 🧍🏻 Human Note
>
> xxxx yyy zz <!-- verbatim, only if user gave one -->

### Summary

<!-- pr:summary -->

[TICKET-123](link) | <one sentence placing the reader, when the title does not>. <The problem: what happens today.> <The solution: what this PR changes.> <The improvement a person sees or can measure.> <!-- no ticket, no prefix -->

**Proof** <!-- pr:proof -->

<the one picture, recording or pasted output that shows the result>

<details><summary>More</summary>

<the rest>

</details>

**Changes** <!-- pr:changes -->

**<Product area>**

- <What a person notices>.
  - <The mechanism, when it helps>.
  - <What was run, then what was seen>.
- No user-visible change: <what moved>.

<!-- pr:breaking -->
> [!WARNING]
> **Breaking:** <what breaks, and what the reader must do about it>.

**Review guide** <!-- pr:review-guide -->

1. [`<file where the logic changed>`](<its diff in the PR>): <what to look at>.
2. [`<the next one>`](<its diff in the PR>): <what to look at>.

Everything else is <renames, generated code, version bumps>, safe to skim.

**Not checked** <!-- pr:not-checked -->

- <What the reader must not assume was checked>.

**Your call** <!-- pr:your-call -->

1. <A decision only the reader can make, with the fact behind it>.

---

<details><summary>Why it works</summary> <!-- pr:why-it-works -->

<the root cause and why the change removes it, or how the parts work together>

</details>

<details><summary>Decisions</summary> <!-- pr:decisions -->

- Chose <X> over <Y>: <Z>.
- Cost: <what got worse, and how much>.

</details>

<details><summary>How to test locally</summary> <!-- pr:how-to-test -->

<setup the reader would not guess>

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
```

## Linking

- The ticket prefixes the summary; parent ticket or epic go in `### Relevant Links`.
- Ticket URL: from the user, a repo config, or an earlier PR in the repo. None known means plain `TICKET-123` with no link, never a guessed base URL.
- Related PR, same repo: `#<num>` (GitHub auto-links). Another repo: `org/repo#<num>`.
- Docs (Notion, Confluence, RFC, README): clickable Markdown links, never raw URLs.
- Review guide stop: the file's diff in the PR, `<PR URL>/files#diff-<SHA-256 of the path>` (verified on github.com, 2026-11).
  The URL exists only after `gh pr create`: create with plain paths, then link them in one body edit.

  ```sh
  url=$(gh pr view --json url --jq .url)
  for f in <path>...; do
    printf '[`%s`](%s/files#diff-%s)\n' "$f" "$url" "$(printf %s "$f" | shasum -a 256 | cut -d' ' -f1)"
  done
  ```
- Stacked PRs, manual path only: previous and next PR in `### Relevant Links`; return to edit once the next PR's URL exists. Under gh-stack, GitHub renders the stack itself.
