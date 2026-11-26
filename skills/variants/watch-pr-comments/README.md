# watch-pr-comments

[All skills](../../)

[Canonical skill instructions](SKILL.md)

Use `/watch-pr-comments` to answer a pull request's reviews and comments as they land, while CI is
someone else's concern. It narrows the [`/watch-pr`](../watch-pr/README.md) contract to reviews:
automated reviews are addressed, human comments are answered per the git skill's rules, and a red
check does not wake it. Only a merge, a close, or the time budget ends the watch.
