# Mise-fy 👨🏻‍🍳

[![skills.sh](https://skills.sh/b/sherifabdlnaby/skills)](https://skills.sh/sherifabdlnaby/skills)

## Install

```bash
npx skills add sherifabdlnaby/skills --skill mise-fy
```

Best-practices, tips, and gotchas to maximize the use of [mise](https://mise.jdx.dev) (along-side [hk](http://hk.jdx.dev/)) distilled from experience building dev (& CI) setups that ✨just works ✨ for diverse teams at different levels that you and your agents would love to use!

**The skill has two modes to trigger for:**
1. Provide tips & gotchas to agents when working with Mise. (duhh!)
2. **_Mise-fy_** 🪄 an existing project and transform it to a recommended structure.

Read the Skill's [.MD](./SKILL.md) file, as well as each topic's reference in [./references](references) to learn more about what the skill encodes.

> [!TIP]
> The skill is written and optimized to be used by models with coherence level similar to `Opus 4.8` or `GPT 5.5`, especially when mise-fying.

The skill **does not enumerate** all of Mise's features. It relies on Agents world knowledge, and ability to read docs (and it ask agents to!) but **guide the agent to best practices**. I may cover more use-cases later!

## Is this a `Mise` skill ? or a good local dev setup skill ?

Kinda both; `Mise` is THE tool to use to have a great UX in your dev setups, so there is a lot of overlap. However, the skill is primarily focused on Mise itself, and only encode tips/gotchas **when Mise is involved.** It'll be a good skill to pair with "local-setup" Skill that is runtime specific (maybe soon!).

## So What does the skill encode exactly ?

The skill encodes what needs for dev setup to just work, stay discoverable, and guide you to be set up correctly.

**It just works.** Clone the repo, run `mise trust && mise run setup`, and you're done. Tools install pinned and locked, so your versions match everyone else's and CI's. Setup is idempotent and cached, so re-running it is cheap (and for worktrees too!), and the git hooks install themselves on `mise install`, and will nag you if you didn't (so u trust every one and their agent get all local linters/tests/validations)!

**It's discoverable.** Tasks follow the same names in every repo (`setup`, `check`, `test`, `build`, etc), tasks have good descriptions, flags, and auto-completion. The README and AGENTS.md teach that same discovery path, and Agents can explore and extend the setup too!.

**It's friendly.** The setup nudges instead of failing silently. Try to handle all annoying stuff declaratively (e.g Handle GH Rate limits). And try to fail in obvious way with explanation on how to update things (adding a `min_version`). Security comes along for the ride: a verified, locked supply chain and security linters on every commit.

## Shout out!

Shout out to [@jdx](https://github.com/jdx) for building such tasteful tools such as `mise` and `hk` !

## Reference index

- [`references/install.md`](references/install.md). Machine setup: install via package manager, shell activation, shims for non-interactive shells, completions.
- [`references/tools.md`](references/tools.md). Dev tools / runtimes: installing, pinning, updating, backends, lockfile.
    - [`references/runtimes/node.md`](references/runtimes/node.md). Node runtime integration: package managers, dep install, idioms.
- [`references/env.md`](references/env.md). Env & vars: `[env]`, dotenv, secrets, templating, required vars, defaults, redaction, PATH.
- [`references/tasks.md`](references/tasks.md). Tasks: TOML vs file tasks, `depends`/`wait_for`, `sources`/`outputs` caching, parallelism.
- [`references/hk.md`](references/hk.md). hk pre-commit / git hooks: `hk.pkl` (Pkl), `check` vs `fix`, builtins, mise integration, custom steps.
- [`references/ci.md`](references/ci.md). CI: platform-agnostic rules for shims, caching, pinning, tokens.
    - [`references/ci/github.md`](references/ci/github.md). GitHub Actions specifics for running mise tasks/tools.
- [`references/mise-fy.md`](references/mise-fy.md). Migrate an existing project to mise + full audit checklist; references every other doc.
- [`references/docs.md`](references/docs.md). README + AGENTS.md/CLAUDE.md onboarding so a human and an agent can set up and extend mise.
- [`references/reference-setup-and-patterns.md`](references/reference-setup-and-patterns.md). Canonical example file tree + `mise.toml` to copy from.
