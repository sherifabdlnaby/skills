---
name: git
description: >
  Load when planning or about to git commit, branch, push, rebase, resolve a merge conflict, open PR, stack PRs (also when gh-stack drives the stack), or write/update the description of a Pull Request (PR / stacked diff), respond to review comments, review a PR, watch/babysit a PR's CI or reviews, or get a review bot (Copilot, Bugbot) to run on a draft PR.
  Carries the user's git conventions and style you are expected to match. Load as early as possible, the moment git or GitHub work is anywhere in the chat's future.
license: MIT
argument-hint: "[commit|branch|pr|rebase|review|watch]"
metadata:
  author: sherifabdlnaby
  version: "0.3.0"
---

# Git

Route first: each action's actual rules live in a `references/` file. Open the matching one before planning or acting; rules like commit grouping and branch naming shape the plan, so reading them late
means redoing it. Several actions, several references.

## Router

**Branches** (create, name, stack) -> [`references/branches.md`](references/branches.md) Switching branches, naming rules, ticket references, switching with a dirty tree, stacked PRs (conventions
here, mechanics via the gh-stack skill), the gh-stack/manual path probe, cascade conflicts and verification, manual restacking fallback (after merge, chain of 3+, mid-stack push), force-pushing.

**Committing** -> [`references/commits.md`](references/commits.md)
Pre-staging walk, file confirmation, message style, hook-failure handling, scoping, editor-free squash, empty commits.

**Pull Requests** (open, update) -> [`references/pull-requests.md`](references/pull-requests.md) Pre-flight survey, title format (including the stacked `[n/N]` marker), body skeleton and how to write
descriptions, AI footers, post-create flow, finishing PRs after `gh stack submit`, linking PRs, updating a body without clobbering it.

**Responding to review comments** (on your own/target PR) -> [`references/review-responses.md`](references/review-responses.md) Classify the reviewer (automated bot/AI tool, an AI-disclosed agent
behind a human account, or a human), then fix / push back / escalate; in-thread replies, thread resolution, re-requesting review, batching a round into one GraphQL query and one aliased mutation,
where a PR stands.

**Rebasing, resolving conflicts** -> [`references/rebase.md`](references/rebase.md)
Conflict-time snapshot (`ORIG_HEAD`), force-with-lease, unconditional range-diff verification.
Stacked-PR restack mechanics and `--onto` (drop intermediate commits) live in [`references/branches.md`](references/branches.md), read that too.

**Reviewing someone else's PR** -> [`references/reviewing.md`](references/reviewing.md)
Procedure: gather context, check out locally, trace the change, deliver a summary and review guide.

**Watch a PR's CI and reviews** -> [`references/watch.md`](references/watch.md) The four verdicts, the three modes (green CI / green and quiet / reviews only), the cheap
sub-agent that runs the loop, the stale nudge. Uses `scripts/pr-watch.py`, never a sleep loop; its flags are in `references/watch-flags.md`.

**Draft PR that review bots ignore** -> [`references/watch.md`, Draft PRs and review bots](references/watch.md#draft-prs-and-review-bots)
`pr-watch.py flick`: a mechanical toggle to ready and back so Copilot, Bugbot, and their kind review a draft; chasing beyond it only on the user's word that a bot exists, with `--wip` on the title.

**Stuck CI check with no manual retry** -> [`references/commits.md`, Empty commits](references/commits.md#empty-commits)
The last-resort empty commit: when it beats retrying the check, and the zero-file-change guards that keep approvals alive.

## Always

**Disclose AI.** Anything posted on GitHub on the user's behalf (PR body, comment, issue, ticket update) carries an **AI footer**.
The PR-body template lives in [`references/pull-requests.md`](references/pull-requests.md);
the post templates, one per tier of human judgment behind the post (Agent Decided, Human Approved,
Human Guided), live in [AI Disclosure](#ai-disclosure) below.
Use them as verbatim as possible, do not write from memory.

**Reach for `gh` first.** Every GitHub action goes through the `gh` CLI; the GitHub MCP server is
the fallback for what `gh` cannot do.

**Parallelize read-only calls.** Batch independent read-only `git`/`gh` calls
(`status`, `diff`, `log`, `gh pr view/diff/checks`) into a single tool call; each
sequential read is a roundtrip for nothing. Mutating commands (`commit`, `push`,
`rebase`, `gh pr create/edit/merge`) stay sequential.

**Fewer round-trips, smaller payloads.** Batching is the first lever; these are the next four,
your call when a one-off is cheaper:

- **One wide fetch, many narrow reads.** Anything you'll consult more than once in a task (PR JSON, `gh stack view --json`, a review-thread query) goes to a temp file once, and each step reads its
  slice with `jq`. Re-fetch after anything you did that changes it (push, edit, reply, resolve); or if time passed and you've been idle, a snapshot is not a live view.
- **Ask for an answer, not a payload.** A count or a single field leaves as `--jq '.x'`; a yes/no leaves as an exit code (`git diff --quiet`, `git merge-base --is-ancestor`). JSON you read with your
  own eyes is a payload.
- **Same-shape mutations ride one request.** GraphQL aliases: every reply, resolve, or title edit of a round in one `gh api graphql`. Aliases fail independently, so read the per-alias `errors[].path`,
  not the exit code.
- **Bodies travel by file.** PR body or GraphQL query to a file, then `--body-file` / `-F query=@file`. (why: shell quoting eats backticks and `$`, and a file stays editable for the next update.) The
  disclosure guard refuses a body it cannot read from a file.

**Resolve once per session, reuse everywhere.** One line for all three:

```bash
gh repo view --json nameWithOwner,defaultBranchRef --jq '"repo  \(.nameWithOwner)\ntrunk \(.defaultBranchRef.name)"'; gh api user --jq '"user  \(.login)"'
```

Carry `<OWNER/REPO>`, `<trunk>` and `<GITHUB_USERNAME>` through the session from that.

**Voice** for everything public (commit messages, PR titles and bodies, comments, issues):

- Omit needless words. Concise sentences, no padding paragraphs.
- Emojis sparingly, only where one helps the reader catch something while glancing.
- NO em dashes in any public-facing text. Use commas, parentheses, or periods. (why: em dashes are a classic AI tell and repel readers.)
- No vague reaffirmations like "for accountability", "for performance", "for resiliency" unless that reason is already in the conversation. (why: invented justification misrepresents the change.)
- Dry, low-key humor.
- Don't overdo formatting. Keep it balanced. (why: visual noise crowds out the content.)
- A user-supplied Human Note is exempt: it goes in the PR body verbatim.

## AI Disclosure

Every post on the user's behalf (comment, reply, issue) ends with an AI footer: a `---`, then one
line copied verbatim from the templates below. The PR-**body** variants live in
[`references/pull-requests.md`](references/pull-requests.md) and follow the same rule.

Placeholders, the same in every footer:

- `<TOOL>`: the tool you're running as, e.g. Claude, Cursor.
- `<MODEL>`: the friendly name of the model you're running, e.g. `Opus 4.8`.
- `<GITHUB_USERNAME>`: resolve once per session with `gh api user --jq '.login'`.

### Picking the variant

The footer answers one question for whoever reads the post: how much human judgment stands behind
it? Judge the decisions the post carries, not the request that produced them. The two human tiers
carry a word grading the degree; picking it is your call.

**🤖 Agent Decided.** You chose the change, position, or wording. Nobody has vetted it.

```markdown
_<sub>🤖 Agent Decided: Posted by <TOOL> (<MODEL>) autonomously on behalf of @<GITHUB_USERNAME>.</sub>_
```

**🧍‍♂️👍 Human Approved (glanced | read | tested).** The user had the real thing in front of them and
said yes. The word grades how closely they looked: `glanced` is a fast yes, `tested` means they ran
it themselves. A yes on something they would have had to go open is 🤖.

```markdown
_<sub>🧍‍♂️👍 Human Approved (<glanced|read|tested>): Posted by <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

**🤝 Human Guided (nudged | steered | dictated).** A back and forth on a technical decision happened,
and its outcome is in this post. The word grades how much came from them: `nudged` is one remark that
changed your direction, `dictated` is them naming exactly what to do.

```markdown
_<sub>🤝 Human Guided (<nudged|steered|dictated>): Posted by <TOOL> (<MODEL>) on behalf of @<GITHUB_USERNAME>.</sub>_
```

Still 🤖, however it feels:

- A task, however specific. "Fix the flaky test", "file an issue about X": naming what to work on is not deciding what it says.
- A rule the user wrote earlier, in a skill, in CLAUDE.md, in memory. Their instruction set is not a call on this post.
- Delegation. "Do whatever you think is best" is the opposite of direction.
- Approval from anyone but the user. The post goes out under their name, so the tier reports what they did.
- A Human Note. It is context in the body, not a decision about the change.
- A reply posted from a watch loop. The user was not in it.

Already 🤝, even though every word is yours:

- They approved a written plan and the post carries out what it named.
- They picked one of the options you laid out, or answered the question that settled the design.

**Late approval** upgrades a PR body, piggybacked on the next body edit rather than a round-trip of
its own; a posted comment or reply keeps the footer it went out with. The user's own GitHub approval
of the PR counts as approval.

**Direction does not reach what they never saw.** On a long run, a post about a part the user was
never in is 🤖, and a push after approval drops back to 🤖 once it changes what they endorsed.

**Understate, never overstate.** Torn between two tiers, or two words, take the lower one. A footer
claiming human judgment that never happened is the failure that matters.
