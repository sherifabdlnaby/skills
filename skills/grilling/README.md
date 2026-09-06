# grilling

## Credit

Forked from **Matt Pocock**'s [`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) and its
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) entry point ([`mattpocock/skills`](https://github.com/mattpocock/skills), MIT).

## What I changed

A round of questions goes through the harness's ask-the-user tool. Upstream writes the round out as a numbered markdown list, and the fork asks with the tool instead, so an agent has nothing to
override and nothing to forget. A harness without such a tool still gets the written list. Where a harness accepts only the options it is handed, the skill adds one that invites a custom answer.

## Usage

```
/grill-me [what to stress-test]
```

Or any 'grill' phrase; this skill triggers on its own.
