# grilling

## Credit

Forked from **Matt Pocock**'s [`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) and its
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) entry point ([`mattpocock/skills`](https://github.com/mattpocock/skills), MIT).

## What I changed

Three paragraphs in the middle of `SKILL.md`, the ones about how a round of questions reaches the user. Upstream writes the round out as a numbered markdown list. The fork asks through the harness's
ask-the-user tool instead, keeps every question answerable off the list of options, and falls back to writing the round out when the harness has no such tool. An agent then has nothing to override
and nothing to forget.

Everything else in the file is Matt's text as it stands upstream: the design tree, the frontier and its rounds, sub-agents for facts, and the empty frontier that ends the session.

## Usage

```
/grill-me [what to stress-test]
```

Or any 'grill' phrase; this skill triggers on its own.
