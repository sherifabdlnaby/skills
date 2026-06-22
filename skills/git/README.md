# Git

[![skills.sh](https://skills.sh/b/sherifabdlnaby/skills)](https://skills.sh/sherifabdlnaby/skills)

## Install

```bash
npx skills add sherifabdlnaby/skills --skill git
```

My git conventions, and utilities. Mostly opinionated stuff.
It also includes a `watch` script that let Agent baby-sit PRs, fix CI with minimum token overhead.

Read the Skill's [.MD](./SKILL.md) file, and the reference for whatever you're doing in [./references](references), to see exactly what the skill encodes.

> [!NOTE]
> Tuned for models around the coherence of `Opus 4.8` or `GPT 5.5`.

The skill **doesn't teach you git.** It assumes the agent knows git and `gh` cold, and only steps in where *my* taste differs from the default. World knowledge does the rest.

## What is covered

Each action routes to one reference holding the actual rules. Read the matching one before planning, not after.

- [`references/watch.md`](references/watch.md). Babysitting a PR's CI and reviews, via [`scripts/pr-watch.py`](scripts/pr-watch.py).
- [`references/commits.md`](references/commits.md). Staging and writing commits.
- [`references/branches.md`](references/branches.md). Branching, naming, and stacked PRs.
- [`references/pull-requests.md`](references/pull-requests.md). Opening and updating PRs.
- [`references/review-responses.md`](references/review-responses.md). Replying to reviews on your own PR.
- [`references/rebase.md`](references/rebase.md). Rewriting history safely.
- [`references/reviewing.md`](references/reviewing.md). Reviewing someone else's PR.
