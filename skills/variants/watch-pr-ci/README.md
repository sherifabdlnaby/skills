# watch-pr-ci

[All skills](../../)

[Canonical skill instructions](SKILL.md)

Use `/watch-pr-ci` to babysit a pull request's CI and nothing else. It narrows the
[`/watch-pr`](../watch-pr/README.md) contract to checks: a red check is debugged from its link,
fixed, and pushed; reviews and comments do not wake it; the watch ends when every check is green.
