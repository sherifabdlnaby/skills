---
name: mise-fy
description: >
  Use when working with mise (mise-en-place) or planning to update mise.toml.
  If the project use mise consult it even for one-line edits to mise.toml/hk.pkl, hooks, or CI tool setup, as it has the practices and security defaults you'd otherwise skip.
  Trigger on the intent even when the user never says "mise" (e.g. "update/pin the node version", "set up pre-commit") as long as project already use mise.
  Don't load for routine mise *use* (run/install/trust) that isn't changing config. Optionally use the skill to transform local development into using mise, aka (mise-fy).
license: MIT
argument-hint: "Mise-fy this project | Audit this project | Add x tool via Mise"
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# mise-fy

[//]: # (If you're an agent, focus on # How to use the SKill, and the progressive disclosure rules!)

# Introduction to Humans

Best-practices, tips, and gotchas to maximize the use of [mise](https://mise.jdx.dev) (along-side [hk](http://hk.jdx.dev/)) distilled from experience building dev (& CI) setups that ✨just works ✨ for diverse teams at different levels that you and your agents would love to use!

**The skill has two modes to trigger for:**
1. Provide tips & gotchas to agents when working with Mise. (duhh!)
2. **_Mise-fy_** 🪄 an existing project and transform it to a recommended structure.

Read each topic's reference in [./references](references) to learn more about what the skill encodes.

> [!TIP]
> The skill is written and optimized to be used by models with coherence level similar to `Opus 4.8` or `GPT 5.5`, especially when mise-fying.

The skill **does not enumerate** all of Mise's features. It relies on Agents world knowledge, and ability to read docs (and it ask agents to!) but **guide the agent to best practices**. I may cover more use-cases later!

## Is this a `Mise` skill ? or a good local dev setup skill ?

Kinda both; `Mise` is THE tool to use to have a great UX in your dev setups, so there is a lot of overlap. However, the skill is primarily focused on Mise itself, and only encode tips/gotchas **when Mise is involved.** It'll be a good skill to pair with "local-setup" Skill that is runtime specific (maybe soon!).

## So What does the skill encode exactly ?

The skill encodes what needs for dev setup to just work, stay discoverable, and guide you to be set up correctly.

**It just works.** Clone the repo, run `mise trust && mise run setup`, and you're done. Tools install pinned and locked, so your versions match everyone else's and CI's. Setup is idempotent and cached, so re-running it is cheap (and for worktrees too!), and the git hooks install themselves on `mise install`, and will nag you if you didn't (so u trust every one and their agent get all local linters/tests/validations)!

**It's discoverable.** Tasks follow the same names in every repo

---

# How to use the Skill

The skill uses progressive disclosure: each area routes to a `references/` file holding the actual rules and best practices.
Read the matching one **before** planning or acting, not after. SKILL.md alone is not enough. Plan ahead, and read all references you'll need!

## When to read references

Always read at-least 1 reference from the router below. Depending on your goal you might want to read more than 1 reference.
Be eager to load local .md references. Do not load online links/references unless you really need to, default to trust your knowledge. Only load online reference when you need to learn more.

## Router

**Install mise** (machine setup, not project setup) -> [`references/install.md`](references/install.md)
Install via package manager, activate the shell, shims for non-interactive shells, completions.

**Dev tools / runtimes** (install, pin, update, backends, lockfile, lazy/uncommon tools) -> [`references/tools.md`](references/tools.md)
Installing a tool or runtime; lazy-installing **uncommon** tools (task-scoped tools & committed `./bin/` **tool stubs**) instead of `[tools]` for everyone.

**Runtime integration** (per-runtime: package managers, dep install) -> [`references/runtimes/`](references/runtimes/).

- Node -> [`runtimes/node.md`](references/runtimes/node.md)

**Env & vars** (project env, dotenv, secrets) -> [`references/env.md`](references/env.md)
`[env]`, `_.file`/`_.path`/`_.source`, templating, required vars, default fallbacks, redaction, updating PATH, loading .env files, config environments (`MISE_ENV`), shell aliases.

**Tasks** (run scripts, build pipelines, watch) -> [`references/tasks.md`](references/tasks.md)
TOML vs file tasks, `depends`/`wait_for`, `sources`/`outputs` caching, running and parallelism, `mise watch` (re-run on change).

**hk** (pre-commit / git hooks) -> [`references/hk.md`](references/hk.md)
`hk.pkl` (Pkl), `check` vs `fix`, builtins, mise integration, install, extending with custom steps.

**CI** (running mise tasks/tools in CI: shims, caching, pinning, tokens) -> [`references/ci.md`](references/ci.md)
General platform-agnostic CI rules; platform specifics under [`references/ci/`](references/ci/):

- GitHub Actions -> [`ci/github.md`](references/ci/github.md)

**mise-fy an existing project** (migrate + audit) -> [`references/mise-fy.md`](references/mise-fy.md)
Step-by-step conversion from custom/asdf/Makefile, plus a full audit checklist. References every other doc.

**Project docs** (README + AGENTS.md onboarding) -> [`references/docs.md`](references/docs.md)
What to put in README.md and AGENTS.md/CLAUDE.md so a human and an agent can install mise, set up, run tasks, and extend the setup. Part of every mise-fy/audit.

**Reference setup** (canonical example layout) -> [`references/reference-setup-and-patterns.md`](references/reference-setup-and-patterns.md)
Annotated example file tree + `mise.toml` to copy from.

## Always applies (regardless of task)

These hold no matter which reference you loaded; check them even when fixated on one task. Unlike the opinionated best practices (scope those to your goal; see top), these are the safety/correctness floor: apply them even on a one-tool change, not polish you'd defer.

1. **Untrusted config errors out.** A `mise.toml` containing `[env]`, hooks, templates, or task logic hard-errors as a *whole file* until `mise trust` (interactive shells prompt to trust; non-interactive ones error). Only a bare `min_version` + plain-string `[tools]`/`[tasks]` file loads untrusted (since 2026.6.6). A fresh clone needs `mise trust` (or a `trusted_config_paths` entry).
2. **Some features need `experimental = true`** and may change between releases. If a documented flag errors, check whether it's gated.
3. **Set `min_version`** (root level, not under `[settings]`) when you rely on a newer feature, so old clients are guided to update. It also floors users past known-vulnerable releases, e.g. `>=2026.6.5`.
4. **Avoid GitHub rate limits** on tool installs (local *and* CI): set `github.gh_cli_tokens` and `github.use_git_credentials` under `[settings]`. mise tries the gh CLI token first, falls back to git credentials, fails open. In CI a `GITHUB_TOKEN` env var works too (see [`ci.md`](references/ci.md)).
5. **Mise moves fast.** When you hit a wall, check the recent changelog alongside the docs.
6. **Shims don't expose every `mise activate` feature** (e.g. some env-on-`cd`); local-vs-CI mismatches often trace here. See [`install.md`](references/install.md) / [`ci.md`](references/ci.md).
