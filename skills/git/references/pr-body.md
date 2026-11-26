# PR body

Covers: readers and size, skeleton, parts, visuals, markers and the structure hook, repo template, linking.

Apply [SKILL.md](../SKILL.md) voice. The body is a handoff: the session, compacted for two readers
who were not in it. One decides the merge. The other picks the work up later, a person or their
agent. Both arrive cold, and neither is an expert on the project.

- **Open what needs the reader. Fold what informs the reader.** Work nobody asked for, a gap in
  the checks or a thing left out is a *Decide* line when it waits on the reader's answer, and
  stays in its fold when it does not. The open part, everything outside a collapsible, fits one
  screen: about 300 words.
- **Every PR has the four marked parts**, a chore too. An optional part goes when it has nothing
  to say. Fill the [skeleton](#skeleton) and keep its titles.
- **Each part opens with its point**, in plain sentences with no "I".
- **Orient once.** The summary gives the context the reader skipped (what this part of the
  project does, where the change fits) and introduces each project term the reader needs, one
  time: a few plain words and a link (its code or doc on trunk, or its ticket). The link carries
  the detail.
- **Claim only what has a source.** The prior behavior is a fact: read it from the diff. A motive
  or a human decision needs a source (the session, the ticket, a bug report, a failing test).
  Without one, write no motive, and the decision is the agent's. Report only runs that happened.

## Skeleton

Replace every `<...>` placeholder and instruction comment, or remove it with its part. Only the
four `<!-- pr:x -->` markers survive into the body.

```markdown
<!-- AI disclosure: the ai-disclosure skill places it; without that skill, the fallback line from SKILL.md goes at the end -->

> [!NOTE]
>
> ### 🧍🏻 Human Note
>
> xxxx yyy zz <!-- verbatim, only if user gave one -->

### Summary

<!-- pr:summary -->

<What this part of the project does, each term linked, the ticket too.> <What used to happen.> <What changed>, so **<the result>**.

> [!WARNING]
> **Breaking:** <what breaks, and what the reader must do about it>. <!-- only when something breaks -->

<!-- pr:visuals -->

<One line that says what the visual shows:>

<one or two visuals, wide, not tall>

<details><summary>More visuals</summary>

<the rest, and anything tall>

</details>

---

### Changes

<!-- pr:changes -->

**<Product area, never a code layer>**

- <What a person notices>.
  - <The mechanism, when it helps.>

### Review guide <!-- optional -->

- **Decide:** <a question that waits on the reader's answer>
- **Read:** [`<path>`](https://github.com/<OWNER/REPO>/blob/<this branch>/<path>) (<what to look at>) | [`<path>`](<url>) (<what to look at>). The rest is <tests, renames, generated code>. <!-- only the few files that carry the real change; one line, split by | while it stays short -->

---

<details><summary>Decisions</summary> <!-- pr:decisions -->

**Decided by a human**

- **Asked for:** <the request, or "not on record">.
- <A choice a person said or picked>: <reason>.

**Decided by the agent**

- <X>, not <Y>: <reason>.

**Left out**

- <Not done, or left for later>: <reason> (<human or agent>).

</details>

<details><summary>Verification</summary> <!-- optional -->

- **Verified:** <the scenario, then what was observed>.
- **Not verified:** <what the reader must not assume was checked>.
- **Try it:** `<command>`, then <the result to expect>. <Setup the reader would not guess.>

</details>

### Links <!-- optional -->

- [<ticket, epic, doc or related PR>](<url>): <what it is, in a few words>
```

## Parts

- **Human Note.** The user's own words, verbatim. Wait for the user to open it: they hand you a
  note, or they ask for one. Offer it as one more option only in a question you already ask. No
  paraphrase, no typo fixes, no punctuation changes.
- **Decisions.** What is there on purpose, and who chose it.
  - **A human decision is one a person said, or picked from options.** A plain "ok" or "go"
    leaves the choice with the agent.
  - **Only what a reviewer could question or undo**, with its reason. About five lines per group.
    An empty group reads `None.`
  - **Each line is a fact about the work.** No names, no quotes, no instruction to the reader's
    agent, no link to the session.
- **Verification.** *Verified* says what a run proves, never a test count.

## Visuals

- **A visual that is not needed does not help.** Add one only when it makes a point clearer
  than prose. Behavior shown is behavior that ran. A small text-only change gets none: the marker
  becomes `<!-- pr:no-visuals: <reason> -->` (e.g. `text-only change`) and the part is dropped.
- **The smallest view that makes the point**, under the one line it supports: a screenshot or
  recording for UI, pasted output, a small table, pseudocode for logic, a call tree, a component
  tree, a shallow file tree, Mermaid for flow between parts, or a fenced `diff` shaped to the
  topic (the call tree, file tree or state that changed). Keep only the parts the point needs.
- **Wide, not tall.** Two visuals at most on the landing; a `Before | After` pair counts as one.
  More than about 10 lines of code, diff or table, a top-to-bottom diagram, or a full-page
  screenshot is too tall. Make a shorter one for the landing: cropped shots side by side, a
  left-to-right diagram, the two or three lines that show the result, one row per state. The tall
  one goes in *More visuals*, or is not made.
- **Start the app for a picture only when it starts smoothly.** When it does not, bail early and
  show the result another way.
- **Mermaid renders on GitHub.** An HTML artifact does not.
- **Upload, alt text and framing:** [`attach.md`](./attach.md).

## Markers

- **Four hidden markers stay where the skeleton puts them:** summary, visuals (or its opt-out),
  changes, decisions. The structure hook, where it is installed beside this skill, denies a body
  that misses one and names it. Write the part, then retry.
- **Repo template** (`<!-- pr:skeleton-off: <reason> -->`): when the repo ships a
  `PULL_REQUEST_TEMPLATE`, or its own instructions say how a body reads, theirs is the shape and
  ours is the content. Keep every heading and checkbox of theirs, in their order, and fold our
  parts into the sections they fit. `gh pr create --body-file` does not apply the template for
  you: read the file and merge by hand. The AI disclosure keeps its place. This marker, with
  its reason, replaces the four markers. Use it also for a body you did not shape (another
  author's PR).
- **Markdown inside `<details>` needs a blank line after `</summary>`**, as in the skeleton. Without
  it a fenced code block renders as literal backticks.
- **A `---` separator needs a blank line above it.** Under a line of text it turns that line into
  a heading.

## Linking

- **Ticket URL** from the user, a repo config, or an earlier PR in the repo. None known means
  plain `TICKET-123` with no link, never a guessed base URL.
- **Related PRs** as `#<num>`, or `org/repo#<num>` in another repo. Docs as Markdown links, never
  raw URLs.
- **Manual stacks only:** previous and next PR in Links; return to edit once the next PR's URL
  exists. Under gh-stack, GitHub renders the stack itself.
