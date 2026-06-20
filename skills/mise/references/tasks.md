# Tasks

How to build or improve mise Tasks.

## Rules and Best Practices:

1. **Tasks are the single source of truth** for lint/test/build. The same names drive local dev, hk pre-commit, and CI. Expose the consistent contract every repo shares: `setup`, `check` (alias `lint`), `test`, `build`, `dev`.
2. **Namespace with colons** (`test:unit`, `gen:docs`). The bare group name runs the common case (`test` = fast tests); a **quoted** glob runs the group (`mise run 'test:*'`; quote it or the shell expands it).
3. **`depends` for ordering; `sources` + `outputs` for caching**. Both are needed to skip-if-unchanged; `--force` bypasses for a clean run.
4. **TOML for <= 5-line tasks; longer logic use an executable file task** with a shebang + `set -euo pipefail` (unless the repo already has a scripts dir).
5. **File tasks must be executable** in a discovered dir. Prefer to use `.mise/tasks`. Subdirs become `colon:names` ( .mise/tasks/test/one `test:one` ).
6. **Scope `env`/`tools` to the task** (`[tasks.x] env.FOO` / `tools = [...]`) instead of global when only it needs them.
7. **Invoke `mise run <task>` (alias `mise r`)**, never bare `mise <task>` (avoids command/tool conflicts).
8. **Take input via the `usage` spec**; never the deprecated `{{arg()}}/{{option()}}/{{flag()}}` (deprecated since 2026.5.0; scheduled for removal in 2026.11.0). Built-in; don't add `usage` to `[tools]`. `help=` + `choices` make `--help` and completion free. See Task Arguments below.
9. **Give every task a `description`**; add `choices`/simple `complete` when cheap. Hand-written completion scripts only on request; keep them under **`.mise/completion/`** and reference by path from `complete … run="./.mise/completion/x.sh"`. (Convention only; mise does **not** auto-load that dir; it's just where we standardize these scripts.)
10. **Gate destructive tasks with `confirm = "…"`** and `hide = true` on internal helpers. In CI pass `-y`/`--yes` or `confirm` hangs forever.
11. **Prefer config over runtime flags**. Put reused settings in `mise.toml` (or `MISE_*`), not ad-hoc `--flags`.
12. **Share static values via `[vars]`, not `[env]`** (vars stay template-only; they don't leak into the process environment).
13. **Building a standard task** (`setup`/`check`(=lint)/`test`/`build`/`dev`)? Unless project already have a pattern, then refer to [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#standard-tasks).
    If user ask for a `check`/`lint`, check if **hk** is set up and use it (refer to -> [`hk.md`](hk.md)).

## Notes & Gotchas:

- **Tasks run from the config root, not your cwd.** Override per-task with `dir` (default `"{{config_root}}"`; set `dir = "{{cwd}}"` to follow the caller). Only reach for `{{config_root}}` when the task sets a non-default `dir`.
- **`run` as an array = serial commands, each its own shell**; `cd` and unexported vars don't carry between entries. Use one multi-line `run` (or a file task) for stateful sequences. Stops on first failure (`set -e`); `mise run -c`/`--continue-on-error` keeps going.
- **Skip-if-unchanged needs _both_ `sources` and `outputs`**. `sources` alone only feeds `mise watch`. `--force` ignores the cache.
- **`depends` run in parallel** (default 4 jobs; `--jobs`/`MISE_JOBS`); `depends_post` run after. `wait_for` only waits _if_ that task is already in the run. A task's `env` is **not** seen by its `depends`.
- **No-spec args go to the _last_ `run` entry only** (with a `usage` spec they're parsed instead; see Task Arguments).
- **Output is line-buffered + label-prefixed.** Change with `--output interleave|keep-order|quiet|silent` (or `MISE_TASK_OUTPUT`). `raw = true` / `--raw` reads-writes the terminal directly (forces `--jobs=1`) and **bypasses secret redaction**; never in env-bearing tasks (see [`env.md`](env.md)).

Still stuck? Check the docs below.

## Syntax Hints

TOML task:

```toml
[tasks.build]
description = "Build the CLI"
depends = ["lint"]                        # run first, in parallel
sources = ["src/**/*.rs", "Cargo.toml"]   # freshness inputs
outputs = ["target/debug/mycli"]          # skip if unchanged
env = { RUST_BACKTRACE = "1" }            # task-scoped env (NOT seen by depends)
tools = { rust = "1.82" }                 # task-scoped tool
run = "cargo build"
```

(Args/flags via `usage` are covered in Task Arguments below; gate destructive ones with `confirm = "…"`.)

File task (`.mise/tasks/build`, must be executable):

```bash
#!/usr/bin/env bash
#MISE description="Build the CLI"
#MISE depends=["lint"]
#MISE sources=["src/**/*.rs"]
#MISE outputs=["target/debug/mycli"]
#USAGE flag "-r --release" help="Release build"
set -euo pipefail
cargo build ${usage_release:+--release}
```

## Task Arguments

Take input via the [`usage`](https://usage.jdx.dev) spec: `usage = '''…'''` (TOML) or `#USAGE` lines (file task). Parser is **built-in**; don't add `usage` to `[tools]`.
Values arrive as **`$usage_<name>`** env vars (dashes->underscores: `--dry-run` -> `$usage_dry_run`), and **only inside a TOML `run`** as Tera **`{{usage.<name>}}`** (variadics are arrays). Precedence: **CLI > `env="VAR"` > `default`**.

```toml
[tasks.deploy]
description = "Deploy app"          # shows in `mise tasks`; --help is auto-generated from the spec
usage = '''
arg  "<env>"            help="Target environment" { choices "dev" "staging" "prod" }   # required
arg  "[tag]"            help="Release tag" default="latest"                            # optional + default
arg  "[files]" var=#true                                                               # variadic 0+ (1+ uses <files>)
flag "-p --profile <profile>" help="Build profile" env="BUILD_PROFILE" default="dev"   # flag WITH value
flag "-f --force"      help="Skip safety checks"                                        # boolean: present->"true"
flag "--color"         negate="--no-color" default=#true                                # explicit true/false
flag "-v --verbose"    count=#true                                                      # repeatable -vvv
complete "env" run="ls deploy/envs" descriptions=#true                                  # dynamic completion
'''
run = './deploy.sh "$usage_env" --tag "$usage_tag" ${usage_force:+--force} ${usage_verbose:+-v}'
```

Same spec as a **file task** (`.mise/tasks/deploy`, executable). Spec lives in `#USAGE`/`#MISE` comments; the body is a plain script, so read **only `$usage_X` env vars**. The body isn't Tera-rendered, so `{{usage.X}}` prints literally. Every line of a multi-line `{ choices … }` block needs its own `#USAGE`.

```bash
#!/usr/bin/env bash
#MISE description="Deploy app"
#USAGE arg "<env>" help="Target environment" {
#USAGE   choices "dev" "staging" "prod"
#USAGE }
#USAGE arg "[tag]" help="Release tag" default="latest"
#USAGE arg "[files]" var=#true
#USAGE flag "-p --profile <profile>" help="Build profile" env="BUILD_PROFILE" default="dev"
#USAGE flag "-f --force" help="Skip safety checks"
#USAGE flag "--color" negate="--no-color" default=#true
#USAGE flag "-v --verbose" count=#true
#USAGE complete "env" run="ls deploy/envs" descriptions=#true
set -euo pipefail
echo "deploying $usage_env (tag=$usage_tag, profile=$usage_profile)"
[ -n "${usage_force:-}" ] && echo "  --force"
[ "${usage_verbose:-0}" -gt 0 ] && echo "  verbosity=$usage_verbose"
./deploy.sh "$usage_env" --tag "$usage_tag" ${usage_force:+--force}
```

No `#USAGE` spec? Extra CLI args arrive as plain `$@`. Everything else (args, flags, choices, defaults, validation, `complete`, auto `--help`) works exactly like TOML. (verified on mise 2026.6.6.)

| Need                      | Spec                                                                                                               | Consume                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| Required / optional arg   | `arg "<x>"` / `arg "[x]"`                                                                                          | `${usage_x?}` / `${usage_x:-}`              |
| Variadic                  | `arg "<x>" var=#true` (1+), `[x]` (0+); `var_min`/`var_max`                                                        | `{{usage.x}}` (array)                       |
| Flag with value           | `flag "-p --profile <p>"`                                                                                          | `$usage_profile`                            |
| **Arbitrary passthrough** | **omit spec** -> extra CLI args append to the **last** `run` cmd; or `arg "[a]" var=#true double_dash="automatic"` | `mise run t -- --raw`                       |
| Binary true/false         | `flag "-f --force"` or `flag "--x" negate="--no-x" default=#true`                                                  | `${usage_force:-false}`, `{% if usage.x %}` |
| Defaults                  | `default="…"` (and/or `env="VAR"` as a fallback source)                                                            | (none)                                      |
| Help                      | `help="…"` per item, `long_help="…"`, `description=` on task                                                       | `mise <task> --help` (auto)                 |
| Completion                | static `{ choices "a" "b" }`; dynamic `complete "name" run="…" descriptions=#true`                                 | needs `mise completion <shell>` installed   |

Gotchas: required `<arg>` is satisfied by its `env="VAR"` (no CLI value needed) · `hide=#true` drops an item from help/completions · `complete` Tera vars: `words`, `CURRENT`, `PREV`.
**`{{usage.X}}` works ONLY inside a TOML `run`.** mise Tera-renders `description`/`confirm`/etc. at config-load, where `{{usage.X}}` has no context: it throws `Variable 'usage.X' not found` and **breaks the whole config**; every task fails, not just that one. Everywhere else, and in all file-task bodies, use plain `$usage_X`. (verified on mise 2026.6.6.)

## Docs:

- [tasks](https://mise.jdx.dev/tasks/)
- [toml-tasks](https://mise.jdx.dev/tasks/toml-tasks.html)
- [file-tasks](https://mise.jdx.dev/tasks/file-tasks.html)
- [running-tasks](https://mise.jdx.dev/tasks/running-tasks.html)
