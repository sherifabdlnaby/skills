# grilling

## Credit

Forked from **Matt Pocock**'s [`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) and its
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) entry point ([`mattpocock/skills`](https://github.com/mattpocock/skills), MIT).

## What I changed

A round is a call to the harness's ask-the-user tool. Upstream prints the round as a numbered markdown list and the fork drops that template, so there is nothing left to override and nothing to
forget. Where a harness offers no free-text answer of its own, the skill adds an option that invites one.

## Usage

```
/grill-me [what to stress-test]
```

Or any 'grill' phrase — this skill triggers on its own.
