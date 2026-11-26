# what-happened

[All skills](../)

[Canonical skill instructions](SKILL.md)

Use `/what-happened` when you come back to a chat that kept working without you: agents ran, CI finished, PRs moved. You get a short, plain-words catch-up of what changed since your last
message, then every decision that waits on you, each with the agent's pick, the evidence, and the risk, so you can decide from the reply alone.

The turn is read-only: it reports and asks, and changes nothing. Pictures (screenshots, small diagrams) come first when the work produced them. The tradeoff is length: the reply grows with the number
of open decisions, because it never collapses them into a count or a link.

Forked from `ketchup` in [cursor/plugins](https://github.com/cursor/plugins), without its dependencies on other skills.
