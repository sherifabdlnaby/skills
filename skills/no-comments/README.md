# no-comments

[All skills](../)

[Canonical skill instructions](SKILL.md)

Use `/no-comments` to clean the comments out of a diff. The rules are not here: they live in [`coding`](../coding/README.md), under Code Comments, so there is one copy to edit. This skill loads
`coding` and enforces those rules on the diff.

It runs the vendored [`comment-sicko`](../../agents/vendor/comment-sicko.md) subagent, which reads only the diff and deletes by default. Then it checks the deletions against our keep list, which is
wider than comment-sicko's (for example, it keeps couplings and concurrency rules). It deletes what fails, and it reshapes code that needed a comment to be understood. Without the subagent (it ships
only in this plugin, for Claude Code and Cursor), the agent does the pass itself.

Needs: `coding`. Other skills can call it, because it is model-invocable.
