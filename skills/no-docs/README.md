# no-docs

[All skills](../)

[Canonical skill instructions](SKILL.md)

Use `/no-docs` to cut changed docs and UI strings down to what their reader needs. The rules are not here: they live in [`coding`](../coding/README.md), under Docs and UI strings, so there is one copy
to edit. This skill loads `coding` and enforces those rules on the diff.

It reads each changed line as that layer's reader would. It cuts what the reader takes for granted, what belongs to another layer, and history. It rewrites stale text instead of adding to it. It
reports what is left for a human to decide.

Needs: `coding`. Other skills can call it, because it is model-invocable.
