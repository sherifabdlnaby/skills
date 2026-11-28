# review

[All skills](../)

[Canonical skill instructions](SKILL.md)

One review skill for 3 jobs, picked from what you point it at:

- **Your own work** (`/review`): before handoff, the agent that wrote the code reviews it and fixes what it finds.
- **Someone else's PR** (`/review #123`): a suggested verdict first, then failing CI and what to check by hand, a tour of the change, and the findings drafted as Conventional Comments, posted as one
  review.
- **Comments on your PR**: it decides per comment whether to fix it or push back, then the `git` skill posts the replies. `watch-pr` uses it too.

The rules are not here. They live in [`coding`](../coding/README.md), so a rule you add there applies to every review the same day. This skill only sets how strict to be:

- **`loose`, `balanced`, `strict`** (`/review loose #123`). Every rule applies at every level; the level sets how much a breach must cost before it is raised. A rename an agent can sweep later is
  cheap. Persisted state, migrations, and anything released that others depend on are costly.
- **Defaults:** `strict` on your own work, `balanced` on others' PRs and on comments left on yours.
- An opinion that no rule covers is marked as one, raised only at `strict`, and never blocks.

It also runs [`no-comments`](../no-comments/README.md) and [`no-docs`](../no-docs/README.md) when they have not run yet. It starts no reviewer subagents of its own, so a review costs one pass in the
current session.

Needs: `coding`, `no-comments`, `no-docs`, and `git` for the PR jobs. Other skills can call it, because it is model-invocable.
