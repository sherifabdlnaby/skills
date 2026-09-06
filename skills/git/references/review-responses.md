# Responding to Review Comments

Answering review comments on your own PR. (Reviewing someone else's PR is [`reviewing.md`](./reviewing.md).)
Apply [SKILL.md](../SKILL.md) voice rules to every reply.

Classify who left each comment first, because it sets how much you defer. Then run the same response flow.

## Who Left It

1. **Automated review (bot / AI tool).** Copilot, CodeQL, Sonar, Snyk, a review bot. Detected by
   author: GitHub `user.type == Bot`, or a review-tool login. `pr-watch.py` tags these `BOTREVIEW`.
2. **AI-disclosed (an agent behind a human account).** A comment from a person's account whose body
   carries AI authorship: a 🤖 emoji, or an explicit line like "on behalf of @...", "created with
   assistance from", "generated with/by". Agents post under their operator's GitHub identity (the
   same footer convention this skill appends), so `user.type` reads `User` while the content is
   machine-written. Detect it by reading the body, not the author.
3. **Human.** A person, no AI disclosure in the body.

When you can't tell 2 from 3, treat it as human; a real person is accountable for it either way.

## Respond (all three)

1. Read every comment first; assess each on its own before acting. One query gets them all, see [Batching](#batching).
2. Per comment, decide fix / push back / escalate:
   - **Fix** when clearly correct: typos, missing error handling on a critical path, wrong API usage.
   - **Push back**, specific and concise, when the suggestion adds complexity for a near-impossible
     edge case, solves a problem that doesn't exist here, or is factually wrong.
   - **Escalate** to the user when the tradeoff is genuinely ambiguous, or it's a design decision you
     lack context for.
3. Weigh correctness and proportionality on the merits; agreement is a conclusion, not a courtesy.
4. Fixes from the same review round go together, as one coherent commit per [`commits.md`](./commits.md).
5. Reply to every comment, including ones you disagree with, briefly and directly. **Replies go into
   the thread** (`addPullRequestReviewThreadReply`). `gh pr comment` posts to the PR-level
   conversation, which leaves the thread looking unanswered.
6. Resolve a thread only after its fix is pushed and the reply is posted; leave threads you pushed
   back on unresolved, the reviewer closes those. Skip resolving when it's more trouble than it's
   worth, an unresolved-but-answered thread is fine.
7. After a round is fully addressed (fix pushed, replies posted), re-request review so it lands
   back in the reviewer's queue: `gh pr edit <num> --add-reviewer <login>`.
   Skip for bots; they re-review on push.
8. End every reply with the AI footer ([SKILL.md AI Disclosure](../SKILL.md#ai-disclosure)),
   picked per reply and not per round, since one round routinely mixes all three: **🤖 Agent
   Decided** when you fixed or pushed back on your own (so the reviewer knows nobody has vetted it),
   **🧍‍♂️👍 Human Approved** when the user had the fix or the drafted reply in front of them and said yes, **🤝
   Human Guided** when the position you're posting is the user's. A reply sent from a watch loop is
   Agent Decided by definition.

## Batching

A review round is one query in and one mutation out. `gh pr view --json` has no `reviewThreads`
field, so the query is GraphQL; it returns the thread ids, the resolved state and every body at once,
which is also what step 1 needs to judge the round before replying to any of it.

```graphql
query { repository(owner: "<owner>", name: "<repo>") {
  pullRequest(number: <num>) {
    reviewThreads(first: 50) { nodes {
      id isResolved
      comments(first: 20) { nodes { author { login } body path } } } } } } }
```

Replies and resolves then ride one request, aliased one per thread:

```graphql
mutation {
  r1: addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: "<id1>", body: "<reply>"}) { comment { id } }
  x1: resolveReviewThread(input: {threadId: "<id1>"}) { thread { isResolved } }
  r2: addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: "<id2>", body: "<reply>"}) { comment { id } }
}
```

Pass either through a file, `gh api graphql -F query=@round.graphql`, for the same reason PR bodies
go in files.

**A batch is not atomic.** Each alias resolves on its own: the response carries `data` with a null
per failed alias and one `errors` entry per failure, each naming its alias in `path`. Read those,
not the exit code, to know what landed.

The same shape sets stacked-PR titles, aliasing `updatePullRequest` one per PR.

## Where the PR stands

One call, when you need the state of the round rather than its content:

```bash
gh pr view <num> --json number,title,state,isDraft,updatedAt,reviewDecision,statusCheckRollup,comments \
  --jq '"pr       #\(.number) \(.state)\(if .isDraft then " DRAFT" else "" end)
title    \(.title)
updated  \(.updatedAt)
review   \(.reviewDecision // "none")
comments \(.comments|length)
checks   \([.statusCheckRollup[]?|.conclusion//.state]|group_by(.)|map("\(.[0]//"PENDING")=\(length)")|join(" "))"'
```

The rollup collapses to `checks SUCCESS=12 SKIPPED=6` rather than listing every check.
(verified on gh 2.x.) For watching rather than looking, `pr-watch.py poll` self-baselines and belongs
to [`watch.md`](./watch.md).

## How much to defer

- **Bot / AI tool and AI-disclosed comments:** judge on merit, never on authority. Machine reviews
  tend to be right on mechanics (null checks, error paths, API misuse) and wrong on context (they
  flag impossible edge cases, miss why the code is shaped this way). Push back freely when they're
  wrong; you don't owe a bot deference.
- **Human:** same merit test, but give more room on design and taste calls, and escalate a real
  tradeoff to the user rather than overruling it. A terse dismissal of a person reads badly.
