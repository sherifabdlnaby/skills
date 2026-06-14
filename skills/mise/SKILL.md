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

Conventions and best-practices guide for [mise](https://mise.jdx.dev) alongside opinionated best practices.
The skill implements progressive disclosure;  Each area routes to a `references/` file holding the actual rules and best practices.
Read the matching one **before** planning or acting, not after. SKILL.md alone is not enough. Doing several things? Open several references.

The skill encodes best practices. You can use this skill when adding a Mise tool/task/env, or when user ask you audit the whole project and "mise-fy" it.
Since the skill encode opinionated best practices, pushing for all of them **when only asked to add a simple task/tool** would be too much.
Try to apply best-practices that applies **just to your goal**, and suggest/surface tangential improvements to user sparingly.
When `mise-fy`-ing and improving codebase then you can suggest all improvements and recommendation. 

## When to read references.

Always read at-least 1 reference from the router below. Depending on your goal you might want to read more than 1 reference.
Be eager to load local .md references. Do not load online links/references unless you really need to, default to trust your knowledge. Only load online reference when you need to learn more.

## Router

**Dev tools / runtimes** (install, pin, update, backends, lockfile) -> [`references/tools.md`](references/tools.md)
Installing a tool, or runtime. 

**Runtime integration** (per-runtime: package managers, virtualenvs, dep install) -> [`references/runtimes/`](references/runtimes/). 
- Node -> [`runtimes/node.md`](references/runtimes/node.md) (WIP)
- Python -> [`runtimes/python.md`](references/runtimes/python.md) (WIP)

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

**Reference setup** (canonical example layout) -> [`references/reference-setup.md`](references/reference-setup-and-patterns.md)
Annotated example file tree + `mise.toml` to copy from.

### Templating (Tera)

mise renders most `mise.toml` values (and `.tool-versions`) with [Tera](https://mise.jdx.dev/templates.html), a Jinja2-like engine; 
it applies across `[env]`, `[tasks]`, tool versions, and aliases. The file must stay valid TOML. 
Distinct from shell expansion (`${VAR}`, opt-in via `env_shell_expand`, see [`references/env.md`](references/env.md)).

Only use Tera templating when you really need it.

### Config environments (`MISE_ENV`)

Mise has a `-E` flag that can control the different mise.toml files that get loaded (like dotenv). mise.{MISE_ENV}.local.toml  > mise.local.toml > mise.{MISE_ENV}.toml > mise.toml
Read more at [environment](https://mise.jdx.dev/configuration/environments.html)

## Shell Alias

mise can also manage **directory-scoped shell aliases** via `[shell_alias]` (e.g. `ll = "ls -la"`), set on enter / unset on leave like `[env]`; needs `mise activate`.
Read more at [shell_aliases](https://mise.jdx.dev/shell-aliases.html)

## Miscellaneous Notes & Gotchas

1. Mise updates very often. When you hit a wall, consider reading the recent changelog as well as docs.
2. **Idiomatic version files are OFF by default.** `.nvmrc`/`.python-version`/`.ruby-version` are ignored until enabled per-tool (`idiomatic_version_file_enable_tools`). If a version "isn't being picked up," this is usually why.
3. **Lockfile is opt-in.** No `mise.lock` is written until `[settings] lockfile = true`. Don't assume reproducibility you didn't enable.
4. **Untrusted config silently does nothing.** Before `mise trust`, `[env]`/tasks/hooks don't load, no error, just absent. A fresh clone needs `mise trust` (or a `trusted_config_paths` entry).
5. **Some features need `experimental = true`** and may change between releases. If a documented flag errors, check whether it's gated.
6. **CI without a GitHub token hits rate limits.** Tool installs call provider APIs; set `github_token`/`MISE_GITHUB_TOKEN`. See [`ci.md`](ci.md).
7. **Shims don't support every feature** of `mise activate` (e.g. some env-on-`cd` behavior). Mismatched local-vs-CI results often trace back to this.
8. Recommended to set `min_version` (at root toml, not under settings) to set minimum mise version. This will help provide good user experience when you rely on new mise feature. If use have old version this will guide them to update. 
9. Always set `github.gh_cli_tokens` and `github.use_git_credentials` under settings to bypass Github Rate Limits. Setting both use GH first, fallback to GCM. And fails-open with no problems.

