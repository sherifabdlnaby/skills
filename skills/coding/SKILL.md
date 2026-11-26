---
name: coding
description: >
  The user's coding and docs conventions and taste. Load FIRST, at the start of any task that touches code or docs.
license: MIT
metadata:
  author: sherifabdlnaby
  version: "0.3.0"
---

# Coding

## Making Changes

**Note:** These rules are defaults; deviate only when you can state what following the rule would cost here.

- **Simple and idiomatic**: fit the existing system and take the idiomatic way first. Keep sane system defaults; override one only when the gain is worth the extra code.
- **Subtract before you add**: the smallest diff that solves the problem. Remove what the change makes dead before you build. No guards, validators, or parsers beyond what the spec demands.
- **Speculative edge cases need buy-in**: before adding code for an unlikely race or security case, tell the user the concrete failure, how likely it is, and what the code costs. Widen scope only on
  their go-ahead.
- **Minimize reader load**: inline wrappers with one caller and layers that only forward. Returns over mutation, locals over fields over globals; derive state instead of syncing it.
- **DRY**: a string, a threshold, a supported-values list has one authoritative home, easy to change/update/extend.
- **Do not overfit**: Avoid overfitting solutions to problems in this chat. Think bigger.
- **Separation of Concerns & Extendable Components**: Insist on separation of concerns.
- **Duplication over the wrong abstraction governs structure**: tolerate two similar blocks until the shared concept is obvious (rule of three); a helper/component that needs a `mode` flag to serve
  both callers is the wrong abstraction.
- **Extend along the promised axis**: at three cases the axis is promised (rule of three); shape code to make the fourth easy to add, without overfitting to just today's use-cases.
- **Don't name a general structure after its first occupant**: once something is a shared slot or grouping, name it for the axis it opens — not for today's only member. Specificity belongs on the
  leaves.
- **Tidy/Refactor separate from feature work**: an opportunistic refactor is in its own commit. Each stays reviewable.
- **Guard at the boundary, trust inside**: validate and parse raw data into domain types where it enters (CLI args, config, network, external APIs); inside, no re-validation and no redundant nil
  checks.
- **Migrate callers, then delete the old API**: in the same change, when no external user depends on it. No compatibility shim kept "just in case".
- **Converge, don't replay**: a state-changing operation reads the current state and applies only the difference, so it is safe to run twice or after a crash at any point. Leftovers (locks, temp
  files, claimed jobs) are recognizable as stale; write to a temp path and rename into place.
- **Separate before you serialize**: concurrent writers get their own file, key, or branch, merged where read. A lock or single writer only when one shared target is a real invariant.
- **Encode a repeated correction**: a rule that needed saying twice becomes a type, lint, or check whose error names the fix. Prose is for judgment calls only.

## Debugging and Verifying

- **Fix the root cause**: the first place the system did something wrong. Ask whether the triggering state is legitimate: if yes, handle it where it broke; if not, a guard there hides the bug, so fix
  what produced it. Fix every instance of the pattern.
- **Attack the premise**: when two fixes that share one assumption fail the same check, write the assumption down and test it before a third fix.
- **Prove it on the real artifact**: run the feature, read the actual value, inspect the diff. "It compiles", a self-report, or cached output is not proof. When a check passes too easily, suspect the
  check.
- **Explain the number**: before you trust a measured number, name what limits it and rule out that it measured errors, cached or skipped work, or noise. Report it with run count and spread.

## Tests

- **Test behavior, not implementation**: a test fails when the behavior breaks and passes when only the internals change. Drive it through the public interface and derive the expected value from the
  requirement, never from the code under test. A tautological test is a checksum: correct and broken code pass it alike.

## Code Comments

Code is the best documentation. Comment only what the code cannot say: why it is this way, or a detail it does not show. A tautological comment is harmful.

**Reshape before you comment**: a surprise in our own code is a smell. Rename, extract, or type it until the behavior is obvious. A comment stays for what the code cannot carry: a vendor, platform, or
protocol quirk, a public API contract, a link to an external constraint, or a coupling nothing else connects (`# change TIMEOUT in worker.py if you change this`) when one source of truth is not
possible.

1. **Write for the stranger who understands the purpose of the project**: a comment must hold
   for a reader with only the file (and its project); with no access to this conversation, no
   contextual awareness of how the project evolved, no memory of the task that produced it. A
   comment that echoes this session's instructions fails (e.g. `// Doing X (no Y)` where Y is
   something only this conversation knows).
2. **Describe the steady state, not the delta**: `// reads users_v2`, not `// migrated from
   users_v1`. Git records the transition, and delta comments become lies the moment it
   completes. This includes changes between commits of the same branch: they vanish on squash.
   A transition that must live in the code is a TODO with an end condition, never
   loose prose. Same for deletions and moves: git history is the record; leave no `moved to X`
   breadcrumb behind.
3. **WHY only as protection**: explain how we got here only when it stops the stranger from a wrong move, like "fixing" a deliberate choice, removing a needed workaround, or mistaking a cut corner for
   naivety. The next three principles are its instances.
4. **Mention a rejected alternative only as a warning**: keep `// not HTTP/2: the proxy drops long-lived streams` because it stops a stranger from "fixing" it; drop `// using native Map (no lodash)`
   because that avoidance only answers this session's instruction.
5. **Workarounds cite their cause**: `// workaround: SDK drops keepalive on h2, see github.com/x/y#456`. The link is the stranger's only way to check it's still needed.
6. **A cut corner names its ceiling**: `// good enough: O(n²) scan; revisit past
   ~1k rules` states the limit and the upgrade trigger, so the stranger can tell
   deliberate simplicity from naivety. Only for real corners with a known ceiling;
   trivial simplifications need no plaque.
7. **A TODO names what ends it**: a ticket, date, or event, as in `// TODO(PROJ-123): drop fallback after v2 ships`. Same for any "temporary"/"for now" claim; without an end condition it's permanent.
   Bare `// TODO: clean up` is a wish that sediments.
8. **Avoid enumeration; name the set, not its members**: `// sanitize PII
   fields`, not `// sanitize email, phone, SSN, address`. The criterion stays true
   as the set grows; the list reads as complete and rots. When examples aid
   clarity, mark them illustrative: `(e.g. email, SSN)`.
9. **Suppressions are suspect**: a lint or type suppression (e.g. `eslint-disable`, `@ts-ignore`, `# noqa`) for a rule that guards correctness or safety gets fixed, not silenced. Keep one only for a
   faulty or style-only rule, with its reason.
10. **Verify "do not remove"**: an `IMPORTANT` or `do not remove` comment is a claim. Check it in the code and its history. True: encode it as a type, test, or lint, then delete the comment. False:
    delete it.
11. **Explain a detail where it lives**: when a function gets a new behavior, say so in the function, not at its call sites. The reader who opens the code to look finds it there.

## Docs and UI strings

Docs and UI strings follow the Code Comments principles; the stranger is the reader. Also:

- **Each layer shows what its reader needs**: a UI, an API, a doc each hide the rest behind the abstraction. Before adding a line, ask whether its reader needs it or can find it in the code.
- **How it works now**: history belongs in the commit message. Give today's change only the space it takes in the whole system; touch outer-layer text only where what its reader sees changed.
- **One doc, one mode** (Diátaxis): tutorial, how-to, reference, or explanation. Split a doc that mixes them, and link the parts.
- **Real names**: write the real symbol, file, flag, or command, not a synonym or a description of it.
- **Match the voice** the doc already has.
- **Nothing that rots**: name the set, not its members; no hard-coded counts, versions, or file lists. A count or tree the doc needs ships with the command that regenerates it.
