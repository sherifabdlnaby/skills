# Review Someone Else's PR

Reviewing a PR the user points you at ("Review `<PR name or link>`").

The other direction, responding to review comments on your _own_ PR, is [`review-responses.md`](./review-responses.md).

## Procedure

1. Read the PR description and any existing comments or code review.
2. Read context the user gave in this conversation.
3. Read relevant previous PRs or links surfaced in the description or comments.
4. Check out the PR locally if possible.
5. Trace the change until you can say, per file, what it does and why it belongs in this PR. A file you cannot place is a finding, not a gap to skip.
6. Give the user a summary and a review guide: where to start, what carries risk, what to check by hand.

Post to GitHub only when the user asks. Each comment carries the AI footer per
[SKILL.md AI Disclosure](../SKILL.md#ai-disclosure), and replies go into the thread per
[`review-responses.md`](./review-responses.md#batching).
