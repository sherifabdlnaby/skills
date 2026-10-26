# AGENTS.md

## Toolchain (mise)

This project uses [**mise**](https://mise.jdx.dev) to pin tools, expose tasks, run the local services, and wire git hooks. `mise.toml` is the source of truth. Don't install tools by hand or add
ad-hoc scripts; add a mise tool or task instead.

**Setup** (once, and per new worktree): `mise trust && mise run setup`.

**Run via mise.** Run `mise run check` before you call work done. A few examples, not the full list:

```sh
mise run check          # all linters/formatters/validators (alias: lint); add --fix to auto-fix
mise run test           # fast tests, no services
mise run dev            # start the local services in the background (safe to run again)
mise tasks              # discover every task
mise run <task> --help  # a task's flags
```

Prefer `mise run <task>` over calling the tool directly, so local, hooks, and CI stay in sync.

## Local services (mise daemons)

- **`mise run dev`** starts the local stack in the background and prints its status and ports. It is safe to run again, and it is the repair command for a crashed or `errored` service. In a new
  worktree, `mise trust && mise run dev` brings up that checkout's own stack.
- **Connect through env**, never hard-coded ports: `DATABASE_URL`, `PG*`, `REDIS_URL`, and `<NAME>_PORT` come from mise (the shell, tasks, `mise x`). Every checkout has its own ports and data.
- **The services outlive your shell.** See them with `mise run dev:status`, read `mise run dev:logs <name> -n 50`, and stop them with `mise run dev:down`.
- **Schema changes** are a new migration file. The API applies pending migrations before every start, and saving the file restarts it.
- **Adding a service** is one `[daemons.<name>]` block in `mise.toml`: a preset when mise has one, else the plain process (`exec`, its port in the command, `watch`, `proxy = false`); the next free
  port in the project's block with `stride = 10`; a ready and a health check; `retry = 3`. The `dev:*` tasks and their completion pick it up with no change.

## Git hooks (hk)

Commits run [hk](https://hk.jdx.dev) commit gates on staged files, and a push runs the push gates; CI runs both as `mise run check`. Fix failures with `mise run check --fix`. Don't disable steps to
push a commit through; `git commit --no-verify` skips hooks for a WIP commit.

## Extending the setup

Changing tools, tasks, env, mise hooks, or pre-commit hooks? This is where things live:

- **`mise.toml`**: the source of truth for `[tools]`, `[tasks]`, `[daemons]`, `[env]`/`[vars]`, `[settings]`, and `[hooks]`.
- **`mise.lock`**: resolved versions plus checksums, the services' binaries included. Commit it; regenerate with `mise lock` after a `[tools]` or service version change.
- **`.config/mise/`**: project-local state, like the gitignored setup stamp the `setup`/`enter` hooks read. File tasks can live in `.config/mise/tasks/`.
- **`.config/hk.pkl`**: the pre-commit and `check` pipeline (linters and formatters, in Pkl). Add or edit a lint step here; linter configs live beside it in `.config/`.
