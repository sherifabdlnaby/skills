# Responding to Review Comments

The mechanics of a review round on your own PR: fetch, fix, reply, resolve. What each reply says (fix, push back, or escalate) is the **review** skill's call; load it first.
Apply [SKILL.md](../SKILL.md) voice rules to every reply.

## A round

1. Read every comment of the round before acting on any; one query gets them all, see [Batching](#batching).
2. Fixes from the same round go together, as one coherent commit per [`commits.md`](./commits.md).
3. Reply to every comment, including ones you push back on. **Replies go into the thread** (`addPullRequestReviewThreadReply`). `gh pr comment` posts to the PR-level conversation, which leaves
   the thread looking unanswered.
4. Resolve a thread only after its fix is pushed and the reply is posted. **Leave threads you pushed back on unresolved**; the reviewer closes those.
5. After the round is fully addressed, re-request review from each person so it returns to their queue: `gh pr edit <num> --add-reviewer <login>`. Skip bots; they re-review on push.
6. Every reply carries the AI disclosure, per [SKILL.md AI Disclosure](../SKILL.md#ai-disclosure).

**A thread reply carries no media.** `--attach` works on `gh pr comment` and `gh pr edit`, and the reply mutation takes no file. So a picture goes on the PR-level comment or in the body, and the
thread reply links to it. When to attach at all is [Visuals](./pr-body.md#visuals). How `--attach` uploads is [`attach.md`](./attach.md).

## Batching

A round is one GraphQL query in (`reviewThreads` with ids, `isResolved`, and every comment body) and one aliased mutation out, one alias per reply and per resolve. Pass it through a file
(`gh api graphql -F query=@round.graphql`). **A batch is not atomic**: read the `errors` entries, each naming its alias in `path`, not the exit code, to know what landed.

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
