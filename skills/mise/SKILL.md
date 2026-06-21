---
name: mise
description: >
  Use whenever a task touches a project's mise setup: adding or pinning a tool/runtime, editing tasks/env/vars/settings in mise.toml, wiring `hk` (pre-commit) or CI, or transforming (mise-fy)/auditing a project to use mise (incl. that its README/AGENTS.md document the setup).
  Trigger even when the user doesn't say "mise", e.g. "pin the node version", "add a lint task", "set up pre-commit", "speed up CI tool installs".
  Carries mise/hk conventions and current docs so you get the best out of the tool.
  Don't load for routine mise *use* (mise x/run/install/trust) that isn't changing config.
---

# mise

An opinionated conventions and best-practices guide for [mise](https://mise.jdx.dev).
The skill uses progressive disclosure: each area routes to a `references/` file holding the actual rules and best practices.
Read the matching one **before** planning or acting, not after. SKILL.md alone is not enough. Doing several things? Open several references.

Use this skill when adding a mise tool/task/env, or when the user asks you to audit the whole project and "mise-fy" it. Scope your effort to the request:

- **Narrow change** (one tool/task/env): apply only the best practices that touch that change, plus the "Always applies" floor below. Surface at most one or two adjacent improvements as suggestions; don't refactor the rest.
- **Explicit "mise-fy" / audit**: apply and recommend everything.

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

## When to read references.

Always read at-least 1 reference from the router below. Depending on your goal you might want to read more than 1 reference.
Be eager to load local .md references. Do not load online links/references unless you really need to, default to trust your knowledge. Only load online reference when you need to learn more.

## Router

**Install mise** (machine setup, not project setup) -> [`references/install.md`](references/install.md)
Install via package manager, activate the shell, shims for non-interactive shells, completions.

**Dev tools / runtimes** (install, pin, update, backends, lockfile) -> [`references/tools.md`](references/tools.md)
Installing a tool, or runtime.

**Runtime integration** (per-runtime: package managers, dep install) -> [`references/runtimes/`](references/runtimes/).

- Node -> [`runtimes/node.md`](references/runtimes/node.md)

**Env & vars** (project env, dotenv, secrets) -> [`references/env.md`](references/env.md)
`[env]`, `_.file`/`_.path`/`_.source`, templating, required vars, default fallbacks, redaction, updating PATH, loading .env files.

**Tasks** (run scripts, build pipelines) -> [`references/tasks.md`](references/tasks.md)
TOML vs file tasks, `depends`/`wait_for`, `sources`/`outputs` caching, running and parallelism.

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

## Notes

### Config environments (`MISE_ENV`)

Mise has a `-E` flag that can control the different mise.toml files that get loaded (like dotenv). mise.{MISE_ENV}.local.toml > mise.local.toml > mise.{MISE_ENV}.toml > mise.toml
Read more at [environment](https://mise.jdx.dev/configuration/environments.html)

### Shell Alias

mise can also manage **directory-scoped shell aliases** via `[shell_alias]` (e.g. `ll = "ls -la"`), set on enter / unset on leave like `[env]`; needs `mise activate`.
Read more at [shell_aliases](https://mise.jdx.dev/shell-aliases.html)

### Always applies (regardless of task)

These hold no matter which reference you loaded; check them even when fixated on one task. Unlike the opinionated best practices (scope those to your goal; see top), these are the safety/correctness floor: apply them even on a one-tool change, not polish you'd defer.

1. **Untrusted config doesn't load.** Before `mise trust`, `[env]`/tasks/hooks are silently skipped (interactive shells prompt; non-interactive ones error or skip). A fresh clone needs `mise trust` (or a `trusted_config_paths` entry) before *anything* in `mise.toml` takes effect.
2. **Some features need `experimental = true`** and may change between releases. If a documented flag errors, check whether it's gated.
3. **Set `min_version`** (root level, not under `[settings]`) when you rely on a newer feature, so old clients are guided to update. It also floors users past known-vulnerable releases, e.g. `>=2026.6.4` for the CVE-2026-35533 config-trust bypass fix (GHSA-436v-8fw5-4mj8).
4. **Avoid GitHub rate limits** on tool installs (local *and* CI): set `github.gh_cli_tokens` and `github.use_git_credentials` under `[settings]`. mise tries the gh CLI token first, falls back to git credentials, fails open. In CI a `GITHUB_TOKEN` env var works too (see [`ci.md`](references/ci.md)).
5. **Mise moves fast.** When you hit a wall, check the recent changelog alongside the docs.
6. **Shims don't expose every `mise activate` feature** (e.g. some env-on-`cd`); local-vs-CI mismatches often trace here. See [`install.md`](references/install.md) / [`ci.md`](references/ci.md).
