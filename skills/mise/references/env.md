# Env & Vars

Guidance on managing project environment and variables via Mise `[env]`.

## Rules and Best Practices:

1. Define project env in `[env]` and let mise load it (on `cd` with `mise activate`, and for `mise run`/`mise exec`). Don't re-export by hand.
2. Load dotenv with `_.file`, prepend PATH with `_.path`, source scripts with `_.source`. Use the table form (`{ path = ..., redact/tools = ... }`) only when you need an option.
3. Scope env to one task with `[tasks.x] env.FOO = "..."` instead of global `[env]` when only that task needs it. (why: smaller blast radius; note these are **not** passed to `depends` tasks.)
4. Share values between tasks with `[vars]` + `{{vars.x}}`, not `[env]`, when the value is only for task config and shouldn't leak into the process environment. (why: vars DRY task config without polluting env.)
5. Keep real secrets in sops/age-encrypted `_.file`, never plaintext-committed. Mark sensitive values `redact = true` (or top-level `redactions = ["*_TOKEN"]`).
6. Mark must-be-set vars with `{ required = true }` so a missing value fails loud, not silent.
7. Multiple directives of the same kind: use array-of-tables `[[env]]` to avoid duplicate keys.
8. Always inspect with `mise env --redacted` (never bare `mise env`) to confirm what loads and that secrets stay hidden.
9. If a value depends on an installed tool, defer it with `tools = true` (lazy eval). (why: `[env]` resolves *before* tools by default, so `{{tools.node.version}}` is empty otherwise.)
10. Mise support shell expansion in env (e.g "something/${VAR:-default}/something and support $VAR format too )

## Notes & Gotchas:

- **Env resolves before tools.** To use a tool's output in a value, switch to the map form with `tools = true`: `MY = { value = "{{tools.node.version}}", tools = true }`. Same flag works on `_.path`/`_.file`/`_.source`.
- **Tera templating is always on:** `{{env.X}}`, `{{config_root}}`, `{{cwd}}`, `{{tools.<t>.version}}`.
- **`_.path` relatives resolve against `config_root`**, not cwd. .
- **Redaction is line-based.** `redact`/`redactions` scrub task output line-by-line; tasks with `raw = true` bypass it entirely and will leak secrets.
- **`_.file` vs the `env_file` setting.** `_.file` paths resolve against the config that declares them; the global `[settings] env_file = ".env"` (or `MISE_ENV_FILE`) auto-loads dotenv from the current + parent dirs regardless of config. Prefer `_.file` for project-committed config.
- **Vars are not env.** `[vars]`/`{{vars.x}}` are shared across tasks but never exported to the process; use them for task config, `[env]` for the actual environment.

## Syntax

```toml
[vars]                                   # shared across tasks, NOT exported
e2e_args = "--headless"

[env]
NODE_ENV = "production"
DROP_THIS = false                        # unset a variable
DATABASE_URL = { required = true }       # error if unset
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

## Examples

WIP

## Docs:
- [environments](https://mise.jdx.dev/environments/)
- [task vars](https://mise.jdx.dev/tasks/task-configuration.html#vars)
- [settings](https://mise.jdx.dev/configuration/settings.html)
