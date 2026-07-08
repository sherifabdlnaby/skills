# Responding to Review Comments

Answering review comments on your own PR. (Reviewing someone else's PR is [`reviewing.md`](./reviewing.md).)
Use `gh` first, GitHub MCP as fallback. Apply [SKILL.md](../SKILL.md) voice rules to every reply.

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

1. Read every comment first; assess each on its own before acting.
2. Per comment, decide fix / push back / escalate:
   - **Fix** when clearly correct: typos, missing error handling on a critical path, wrong API usage.
   - **Push back**, specific and concise, when the suggestion adds complexity for a near-impossible
     edge case, solves a problem that doesn't exist here, or is factually wrong.
   - **Escalate** to the user when the tradeoff is genuinely ambiguous, or it's a design decision you
     lack context for.
3. Don't blindly agree; weigh correctness and proportionality.
4. Batch fixes from the same review round into one commit.
5. Reply to every comment, including ones you disagree with, briefly and directly.
6. Resolve a thread only after its fix is pushed and the reply is posted; leave threads you pushed
   back on unresolved, the reviewer closes those. Resolving is a GraphQL mutation:

   ```bash
   gh api graphql -f query='mutation { resolveReviewThread(input: {threadId: "<id>"}) { thread { isResolved } } }'
   ```

   (Thread ids come from the `reviewThreads` connection on the PR; skip resolving when it's more
   trouble than it's worth, an unresolved-but-answered thread is fine.)

7. After a round is fully addressed (fix pushed, replies posted), re-request review so it lands
   back in the reviewer's queue: `gh api repos/<owner>/<repo>/pulls/<num>/requested_reviewers -f "reviewers[]=<login>"`.
   Skip for bots; they re-review on push.

8. End every reply with the AI posts footer ([SKILL.md AI Disclosure](../SKILL.md#ai-disclosure)),
   picking the variant by **provenance**: the **autonomous** footer when you fixed or pushed back
   without the user's input (so the reviewer knows no human has vetted it yet), the **user-directed**
   footer when the user gave input or approved. You drafted and the user only tweaked? Still
   user-directed. A reply posted from a watch loop is autonomous by definition.

## How much to defer

- **Bot / AI tool and AI-disclosed comments:** judge on merit, never on authority. Machine reviews
  tend to be right on mechanics (null checks, error paths, API misuse) and wrong on context (they
  flag impossible edge cases, miss why the code is shaped this way). Push back freely when they're
  wrong; you don't owe a bot deference.
- **Human:** same merit test, but give more room on design and taste calls, and escalate a real
  tradeoff to the user rather than overruling it. A terse dismissal of a person reads badly.
