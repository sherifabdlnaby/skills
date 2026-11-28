---
name: coding
description: >
  The user's coding and docs conventions and taste. Load FIRST, at the start of any task that touches code or docs.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.5.0"
---

# Coding

## Making Changes

**Note:** These rules are defaults; deviate only when you can state what following the rule would cost here.

- **Simple and idiomatic**: fit the existing system and take the idiomatic way first. Keep sane system defaults; override one only when the gain is worth the extra code.
- **Subtract before you add** (extending an existing feature): the smallest diff that solves the problem, where possible. Remove what the change makes dead before you build. No guards,
  validators, or parsers beyond what the spec demands.
- **Do not overfit** (adding a new system or functionality): design for the problem, not only the cases in this chat.
- **Speculative edge cases need buy-in**: before adding code for an unlikely race or security case, tell the user the concrete failure, how likely it is, and what the code costs. Widen scope only on
  their go-ahead.
- **Minimize reader load**: inline wrappers with one caller and layers that only forward. Returns over mutation, locals over fields over globals; derive state instead of syncing it. Early returns over
  nesting.
- **DRY**: a string, a threshold, a supported-values list has one authoritative home, easy to change/update/extend.
- **Separation of concerns**: split code where its parts change for different reasons. Add an extension point only when the axis is promised (below).
- **Duplication over the wrong abstraction governs structure**: tolerate two similar blocks until the shared concept is obvious (rule of three); a helper/component that needs a `mode` flag to serve
  both callers is the wrong abstraction.
- **Extend along the promised axis**: at three cases the axis is promised (rule of three); shape code to make the fourth easy to add, without overfitting to just today's use-cases.
- **Don't name a general structure after its first occupant**: once something is a shared slot or grouping, name it for the axis it opens — not for today's only member. Specificity belongs on the
  leaves.
- **Tidy/Refactor separate from feature work**: an opportunistic refactor is in its own commit. Each stays reviewable.
- **Fix the type, don't silence it**: no cast or ignore (`as any`, `# type: ignore`) only to make the checker pass.
- **Guard at the boundary, trust inside**: validate and parse raw data into domain types where it enters (CLI args, config, network, external APIs); inside, no re-validation and no redundant nil
  checks.
- **Migrate callers, then delete the old API**: in the same change, when no external user depends on it. No compatibility shim kept "just in case".
- **Converge, don't replay**: a state-changing operation reads the current state and applies only the difference, so it is safe to run twice or after a crash at any point. Leftovers (locks, temp
  files, claimed jobs) are recognizable as stale; write to a temp path and rename into place.
- **Separate before you serialize**: concurrent writers get their own file, key, or branch, merged where read. A lock or single writer only when one shared target is a real invariant.
- **Encode a repeated correction**: a rule that needed saying twice becomes a type, lint, or check whose error names the fix. Prose is for judgment calls only.

## Debugging and Verifying

- **Fix the root cause**: the first place the system did something wrong. Ask whether the triggering state is legitimate: if yes, handle it where it broke; if not, a guard there hides the bug, so fix
  what produced it. Look for other instances of the pattern, list them, and ask before you fix them.
- **Attack the premise**: when two fixes that share one assumption fail the same check, write the assumption down and test it before a third fix.
- **Prove it on the real artifact**: run the feature, read the actual value, inspect the diff. "It compiles", a self-report, or cached output is not proof. When a check passes too easily, suspect the
  check.
- **Clean the diff before handoff**: the handoff is the finalize step: the code is finished (code-ready), and you hand the PR or the change to the user or to review. It is not each commit or push. Run
  the **no-comments** and **no-docs** skills on the whole diff once, right before it, then the **review** skill on your own work, and say in the handoff that you did. A later small fix (a review
  round, a rebase) does not run them again; a large new diff does.
- **Explain the number**: before you trust a measured number, name what limits it and rule out that it measured errors, cached or skipped work, or noise. Report it with run count and spread.

## Tests

- **Test behavior, not implementation**: a test fails when the behavior breaks and passes when only the internals change. Drive it through the public interface and derive the expected value from the
  requirement, never from the code under test. A tautological test is a checksum: correct and broken code pass it alike.

## Code Comments

Default to no comment: the code is the documentation and git is the history. Write a comment only for an item on the keep list, in 1 to 4 lines. When you are not sure an item applies, delete
the comment.

To enforce these rules on a diff, use the **no-comments** skill.

**Keep list:**

- **Section banner**: a short banner that groups a long file into sections (`// ===== Retry =====`).
- **File header**: one or two lines at the top of a file on what it is for, when its name and place do not say it. Not a list of what it contains.
- **External cause**: a vendor, platform, or protocol behavior we cannot reshape, or the paper, spec, or RFC a formula or algorithm comes from, with a link:
  `// workaround: SDK drops keepalive on h2, see github.com/x/y#456`.
- **Published API contract**: a doc comment on the public API of a library or package that others import, when its name and types do not show the behavior. An exported function inside an app
  gets none.
- **Required doc comment**: one a language convention or a linter requires (e.g. Go's doc comment on an exported name). Keep it to the contract.
- **Coupling nothing else connects**, when one source of truth is not possible: `# change TIMEOUT in worker.py if you change this`.
- **Concurrency or ownership rule the types cannot express**: `// guarded by mu`, `// caller holds the lock`.
- **Warning against a "fix"** that names what breaks: `// not HTTP/2: the proxy drops long-lived streams`. When the cause is our own code, encode it as a test instead.
- **Regression guard**: a test that exists for a past bug links it: `// regression: github.com/x/y#456`.
- **TODO with what ends it**: a ticket, date, event, or measured limit: `// TODO(PROJ-123): drop fallback after v2 ships`, `// good enough: O(n²) scan; revisit past ~1k rules`.
- License headers, tool directives, and generated-code markers (`// Code generated by X; DO NOT EDIT.`).

A surprise in our own code is not on the list. Rename, extract, or type it until the behavior is obvious.

**Write a kept comment for the stranger**: the reader has only the file and the project, not this session or its history. Describe the code as it is now. Name the set, not its members
(`// sanitize PII fields`, not `// sanitize email, phone, SSN`).

**Verify "do not remove"**: an `IMPORTANT` or `do not remove` comment is a claim. Check it in the code and its history. True: encode it as a type, test, or lint, then delete the comment. False:
delete it.

**Explain a detail where it lives**: when a function gets a new behavior, say so in the function, not at its call sites.

**Checkable rules.** Each ID is stable, so a check can report it. A comment fails when it has:

- `C1` change narration: `Added`, `Updated`, `Changed`, `Now`, `previously`, `migrated from`, `moved to`, `for now`. Describe the code as it is, or delete.
- `C2` only the words of the name below it (`// get user` above `getUser()`).
- `C3` a step label (`// Step 1:`, `// Arrange`).
- `C4` more than 4 lines, except a license. Keep the constraint, drop the background.
- `C5` `TODO`, `FIXME`, `HACK`, or `XXX` with no ticket or link.
- `C6` a bare `#123` for our own PR or issue. Keep the reason; git keeps the number.
- `C7` commented-out code.
- `C8` a placeholder for code (`// ... rest of the code`, `// omitted for brevity`).
- `C9` words for a person: `you`, `Replace this with your`, `Note:`.
- `C10` a lint or type suppression with no reason. A rule that guards correctness or safety gets fixed, not suppressed.
- `C11` an empty `@param` or `@returns`, or a JSDoc `{type}` in typed code.
- `C12` an emoji.
- `C13` a figurative verb or stock AI word: `lands`, `ships` (outside a release), `surfaces`, `wires up`, `bakes in`, `plumbs`, `threads through`, `unblocks`, `additionally`, `crucial`,
  `delve`, `enhance`, `foster`, `pivotal`, `showcase`, `underscore`, `robust`, `seamless`. Use the literal word.

`C1` and `C9` match some real uses (`now()`, a `Note:` before an external quirk), so a check reports them as warnings.

## Docs and UI strings

Docs and UI strings are for the same stranger, and describe how things work now. To enforce these rules on changed docs, use the **no-docs** skill.

**Document at the reader's level of abstraction** (information hiding): every layer (a UI, a CLI, an API, a module, a README) has a reader who uses it through its contract. Write what that reader
needs to use it, and hide how it works below. This applies at every layer: the user guide does not explain the API, the API reference does not explain the database, and a module's doc does not
explain its callers.

- **Document the surprise, not the expected** (principle of least astonishment): leave out behavior the reader takes for granted or finds intuitive. Write what they would not predict: a limit, a side
  effect, an irreversible step, a default that differs from the norm. A customer doc says "deleted projects stay restorable for 30 days", not "click Delete to delete a project".
- **Write for what the reader lacks, not what you learned** (curse of knowledge): what you discovered while building it is not what the reader needs. Before adding a line, ask what its reader would
  get wrong without it. If nothing, or the code or UI already shows it, leave it out.
- **How it works now**: history belongs in the commit message. Give today's change only the space it takes in the whole system; touch outer-layer text only where what its reader sees changed.
- **Rewrite, don't append**: when a fact changes, rewrite or remove the text that states it. Do not add a second account next to the old one.
- **Link the source, don't copy it**: a doc points to the code, config, or command that holds a fact. A copy drifts.
- **One doc, one mode** (Diátaxis): tutorial, how-to, reference, or explanation. Split a doc that mixes them, and link the parts.
- **Plain words**: no `C13` words.
- **Real names**: write the real symbol, file, flag, or command, not a synonym or a description of it.
- **Match the voice** the doc already has.
- **Nothing that rots**: name the set, not its members; no hard-coded counts, versions, or file lists. A count or tree the doc needs ships with the command that regenerates it.
