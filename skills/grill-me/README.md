# grill-me

[All skills](../)

`grill-me` is the manual entry point for a structured interview that stress-tests a plan, design, decision, or idea. Its canonical instructions are in [`SKILL.md`](SKILL.md); the interview itself
lives in [`grilling`](../grilling/).

## Use

```text
/grill-me [what to stress-test]
```

The command delegates to `grilling`, which asks successive rounds of questions until the important decisions and dependencies are explicit. This entry point does not implement a separate interview or
start work on the resulting plan.

## Fork

Forked from **Matt Pocock**'s [`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT). It keeps
upstream's thin dispatcher and routes to this repository's fork of `grilling`, where the interaction behavior differs.
