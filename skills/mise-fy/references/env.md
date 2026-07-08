# Env & Vars

Guidance on managing project environment and variables via Mise `[env]`.

**Where the block goes in `mise.toml`**: top-level section order (`min_version` -> tools -> env -> vars -> tasks -> hooks -> settings) is in [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#configuration-sorting).

## Rules and Best Practices:

1. Define project env in `[env]` and let mise load it (on `cd` with `mise activate`, and for `mise run`/`mise exec`). Don't re-export by hand.
2. Load dotenv with `_.file`, prepend PATH with `_.path`, source scripts with `_.source`. Use the table form (`{ path = ..., redact/tools = ... }`) only when you need an option.
3. Scope env to one task with `[tasks.x] env.FOO = "..."` instead of global `[env]` when only that task needs it. (why: smaller blast radius; note these are **not** passed to `depends` tasks.)
4. Share values between tasks with `[vars]` + `{{vars.x}}`, not `[env]`, when the value is only for task config and shouldn't leak into the process environment. (why: vars DRY task config without polluting env.)
   - **Naming convention:** Prefer `[env]` keys to be `UPPER_SNAKE_CASE` and `[vars]` keys are `lower_snake_case`.
5. Keep real secrets in sops/age-encrypted `_.file`, never plaintext-committed. Mark sensitive values `redact = true` (or top-level `redactions = ["*_TOKEN"]`).
6. Mark must-be-set vars with `{ required = true }` so a missing value fails loud, not silent; `{ required = "how to set it" }` prints that hint in the error. For optional vars, give a soft fallback with `{ default = "..." }`: it keeps any value already set (shell or earlier config) and applies only when the var is unset **or empty**.
7. Multiple directives of the same kind: use array-of-tables `[[env]]` to avoid duplicate keys.
8. Inspect what loads with `mise env`, knowing secrets print in plaintext there: redaction scrubs **task output only**. `mise env --redacted` does NOT hide values; it *filters to* the redacted vars and prints their plaintext (its purpose is feeding CI masking, e.g. `::add-mask::`). Don't paste either into logs.
9. If a value depends on an installed tool, defer it with `tools = true` (lazy eval). (why: `[env]` resolves _before_ tools by default, so `{{tools.node.version}}` is empty otherwise.)
10. mise supports shell expansion in env values (e.g. "prefix/${VAR:-default}/suffix"); the bare `$VAR` form works too.

## Notes & Gotchas:

- **Env resolves before tools.** To use a tool's output in a value, switch to the map form with `tools = true`: `MY = { value = "{{tools.node.version}}", tools = true }`. Same flag works on `_.path`/`_.file`/`_.source`.
- **Tera templating is always on:** `{{env.X}}`, `{{config_root}}`, `{{cwd}}`, `{{tools.<t>.version}}`.
- **`_.path` relatives resolve against `config_root`**, not cwd.
- **Redaction is line-based.** `redact`/`redactions` scrub task output line-by-line; tasks with `raw = true` bypass it entirely and will leak secrets.
- **`_.file` vs the `env_file` setting.** `_.file` paths resolve against the config that declares them; the global `[settings] env_file` (or `MISE_ENV_FILE`) is **deprecated (removal 2027.4.0)**. use `_.file`.
- **Vars are not env.** `[vars]`/`{{vars.x}}` are shared across tasks but never exported to the process; use them for task config, `[env]` for the actual environment. `[vars]` entries accept `required`/`redact` too, but redaction of `{{vars.x}}` substitution only takes effect on mise 2026.7.0+ (older versions parse it and print plaintext).
- **`default` empty == unset.** `{ default = ... }` applies when the var is unset *or* an empty string, and only accepts a string/integer. Combining it with `value`, `required`, or `age` is a parse-time error. `default` also works in `[vars]`, but there it reads the **process env only**, not `[env]` values.
- **`default` needs mise `2026.6.10`.** On an older client it errors. Preferred path: have the user upgrade and bump `min_version = "2026.6.10"` so the feature is guaranteed. If you can't require that version, fall back to the self-referencing `${VAR:-default}` shell form (rule 10) instead.

## Syntax

```toml
[vars]                                   # shared across tasks, NOT exported
e2e_args = "--headless"

[env]
NODE_ENV = "production"
DROP_THIS = false                        # unset a variable
DATABASE_URL = { required = true }       # error if unset
EDITOR = { default = "vim" }             # fallback if unset/empty (keeps existing); string|int
SECRET = { value = "...", redact = true }            # hide in output
NODE_V = { value = "{{tools.node.version}}", tools = true }  # lazy: after tools

_.file = ".env"                          # load dotenv/json/yaml/toml
_.path = ["./bin", "{{config_root}}/node_modules/.bin"]      # prepend PATH
_.source = "./script.sh"                 # source bash, capture exports
redactions = ["*_TOKEN", "PASSWORD"]     # bulk redact by glob

[tasks.test]
env.TEST_ENV_VAR = "ABC"                 # env for THIS task only (not depends)
vars = { e2e_args = "--headed" }         # override a var for this task
run = "./scripts/test-e2e.sh {{vars.e2e_args}}"
```

## Config environments (`MISE_ENV`)

Mise has a `-E` flag that can control the different mise.toml files that get loaded (like dotenv). mise.{MISE_ENV}.local.toml > mise.local.toml > mise.{MISE_ENV}.toml > mise.toml
Platform config environments (`mise.macos-arm64.toml` etc.) exist behind `auto_env` — off by default until 2027.6.0, and only enabled via `MISE_AUTO_ENV=1` or a `.miserc.toml` with `auto_env = true` (a `[settings]` entry has no effect).
Read more at [environments](https://mise.jdx.dev/configuration/environments.html)

## Shell Aliases

mise can also manage **directory-scoped shell aliases** via `[shell_alias]` (e.g. `ll = "ls -la"`), set on enter / unset on leave like `[env]`; needs `mise activate`.
Read more at [shell_aliases](https://mise.jdx.dev/shell-aliases.html)

## Docs:

- [environments](https://mise.jdx.dev/environments/)
- [task vars](https://mise.jdx.dev/tasks/task-configuration.html#vars)
- [settings](https://mise.jdx.dev/configuration/settings.html)
