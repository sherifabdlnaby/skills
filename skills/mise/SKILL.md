---
name: mise-fy
description: >
  Use when asked to update mise's settings, tasks, variables, tools, or add a new tool/runtime in a project managed by mise.
  Do not load just because you are using mise (e.g mise x, run, install, trust).
  Include mise conventions, guidance, and updated docs to make you make the best of the tool. 
  Use to transform (mise-fy) an existing project to use mise.
  Also applies to `hk` (pre-commit) tool.
---

# mise

Conventions and best-practices guide for [mise](https://mise.jdx.dev).

Each area routes to a `references/` file holding the actual rules and best practices. Read the matching one **before** planning or acting, not after.
SKILL.md alone is not enough. Doing several things? Open several references.

Shortcuts:
- **You know what you need** -> jump straight to the matching router entry.
- **Exploring / Looking for best practices** -> read [`references/mise-fy.md`](references/mise-fy.md) for the full audit + rewrite checklist, which pulls in every other reference.

## Rules and Best Practices:

These apply across everything mise.

- **Prefer `mise use` over hand-editing** `[tools]`. (why: keeps `mise.toml` and the lockfile in sync and auto-trusts the file.)
- **Trust is a security boundary.** mise refuses to load `[env]`, tasks, and scripts from untrusted config until `mise trust`. Don't blanket-trust `/`. (why: config files can run arbitrary code on `cd`.)
- **Commit the lockfile, pin in config.** Use fuzzy versions (`node = "24"`) in `mise.toml` and commit `mise.lock` for reproducible exact versions. Lockfile is **opt-in** but push for it. (`[settings] lockfile = true`).
- **`activate` for humans, shims for machines.** Interactive shells use `mise activate`; CI/IDEs/scripts use shims. (why: shims work without a shell hook but don't support every feature.)

> TODO(you): encode your house rules here. e.g. canonical config filename (`mise.toml` vs `.mise.toml`), whether lockfile is mandatory, default backends (aqua/ubi preference), redaction policy. Keep additions terse with a `why:`.

Hit something surprising? Cross-cutting traps live in [`references/gotchas.md`](references/gotchas.md). Area-specific ones live under each reference's `Notes & Gotchas`.

## Router

**Dev tools / runtimes** (install, pin, update, backends, lockfile) -> [`references/tools.md`](references/tools.md)

**Env & vars** (project env, dotenv, secrets) -> [`references/env.md`](references/env.md)
`[env]`, `_.file`/`_.path`/`_.source`, templating, required vars, redaction, sops/age secrets.

**Tasks** (run scripts, build pipelines) -> [`references/tasks.md`](references/tasks.md)
TOML vs file tasks, `depends`/`wait_for`, `sources`/`outputs` caching, running and parallelism.

**hk** (pre-commit / git hooks) -> [`references/hk.md`](references/hk.md)
`hk.pkl` (Pkl), `check` vs `fix`, builtins, mise integration, install, extending with custom steps.

**CI** (GitHub Actions, GitLab, caching) -> [`references/ci.md`](references/ci.md)
`jdx/mise-action`, caching, running tasks in CI, shims, pinning, rate-limit tokens.

**mise-fy an existing project** (migrate + audit) -> [`references/mise-fy.md`](references/mise-fy.md)
Step-by-step conversion from asdf/nvm/direnv/Makefile, plus a full audit checklist. References every other doc.

**Reference setup** (canonical example layout) -> [`references/example-setup.md`](references/example-setup.md)
Annotated example file tree + `mise.toml` to copy from.

**Staying current** (verify against live docs, self-update) -> [`references/staying-current.md`](references/staying-current.md)
How to confirm facts against current mise docs and update this skill when mise changes.

**Gotchas** (cross-cutting traps) -> [`references/gotchas.md`](references/gotchas.md)
Non-obvious behaviors that bite across tools/env/tasks/CI.

## Templating (Tera)

mise renders most `mise.toml` values (and `.tool-versions`) with [Tera](https://mise.jdx.dev/templates.html), a Jinja2-like engine — applies across `[env]`, `[tasks]`, tool versions, and aliases. The file must stay valid TOML. Always on; distinct from shell expansion (`${VAR}`, opt-in via `env_shell_expand`, see [`references/env.md`](references/env.md)).

- **Syntax:** `{{ value }}` (expr), `{% if %}…{% endif %}` (logic), `{# #}` (comment). Wrap literals in `{% raw %}…{% endraw %}`.
- **Vars:** `{{env.X}}`, `{{config_root}}`, `{{cwd}}`, `{{tools.node.version}}`, `{{xdg_config_home}}`, `{{mise_bin}}`.
- **Functions/filters:** `exec(command='…')`, `os()`/`arch()`/`os_family()`, `read_file(path)`, path (`basename`/`dirname`/`canonicalize`), string (`kebabcase`/`hash`).
- **why it matters:** prefer Tera over shelling out for portable, OS-aware config (`{{exec(command='…')}}` beats embedding a subshell). But it runs at config-load — keep it cheap; heavy `exec` slows every `cd`/`mise` invocation.

## Config environments (`MISE_ENV`)

Built-in "profiles": pick an active env and mise layers extra named config files over the base `mise.toml`. Same project, different tools/env/tasks per environment — no `.env` juggling. See [config environments](https://mise.jdx.dev/configuration/environments.html).

Activate (most→least local): `mise -E prod …` / `--env`, `MISE_ENV=prod`, or sticky `env = ["dev"]` in `.miserc.toml`. Stack with `MISE_ENV=ci,test` (last wins).

Load order, **top wins** (`.local.` = gitignored, rest committed):
```
mise.{MISE_ENV}.local.toml  >  mise.local.toml  >  mise.{MISE_ENV}.toml  >  mise.toml
```
- **why:** it's the same recurse-upward, closest-wins merge mise already does — `MISE_ENV` just splices two named layers in. Anything not overridden falls through to base.
- Platform auto-envs (`mise.{os}.toml`, `auto_env`) exist but are **off by default** until `2027.6.0`.

## Cross-references

Concerns that span multiple areas. Note them when touching any single area.

- **Config precedence & merge.** Files recurse upward; closest dir wins. `[tools]`/`[env]` merge additively, `[tasks]` replace per-task. Local overrides go in `mise.local.toml` (git-ignore it). Details in [`references/tools.md`](references/tools.md).
- **Trust** affects env, tasks, and hk equally (all can execute code). See Rules and Best Practices above.
- **Lockfile** governs both tools and CI reproducibility. Decided in [`references/tools.md`](references/tools.md), consumed in [`references/ci.md`](references/ci.md).
- **Tasks ↔ hk ↔ CI** share commands: lint/test/build are defined once as tasks, then invoked by hk hooks and CI. (why: single source of truth, no drift.) See [`references/tasks.md`](references/tasks.md), [`references/hk.md`](references/hk.md), [`references/ci.md`](references/ci.md).
- **Env in tasks/CI.** mise loads the full tool + env context automatically for `mise run` and `mise exec`. Don't re-export by hand.

> TODO(you): add any other cross-cutting conventions (naming, where secrets live, monorepo layout).
