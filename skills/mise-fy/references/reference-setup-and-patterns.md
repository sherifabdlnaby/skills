# Reference Setup Canonical Layout

This is notes and comments on the canonical layout under [../assets](../assets)

## Bare Root mise.toml

Include all the [mise.toml](../assets/mise.toml) main top-level fields, alongside comment decorators.
Don't blindly copy the content under each top-level field. apply only what's relevant, and respect the sorting.

### Configuration Sorting

The order of settings and options

#### Top Level Settings

1. mise `min_version`
2. Tools
3. env
4. vars
5. tasks
6. hooks
7. settings

#### In Tools

1. Runtime
2. <<anything>>
3. Linters and Formatters
4. hk

## Standard Tasks

Each project should start with: `setup` `check (alias lint)` `test` `build`(when applicable), and `dev`(when applicable).
These are root tasks. We can include sub-tasks under their namespace if needed. The root task is expected to run the most common.
For example, we can have 4 different kinds of tests (test:x, test:y:, test:z, and test:e2e), we group test (x/y/z) under just `test` expecting it to be fast.

Below are guidance on each command.

### Setup

Setup is expected to include all the (one time) setups, including mise own `mise install`. Runtime/project dependencies are **not** inlined here; they live in their own [`deps`](#deps) task that setup runs after `mise install` (see below).
Pre-commit (hk) hooks are **not** installed by an explicit step in setup; they self-install canonically via `[hooks] postinstall = "hk install --mise"`, which fires on the `mise install` that setup runs (and on any future `mise install`). See [`hk.md`](hk.md).
It's okay for setup to consist of other mise tasks (rely on depends and depends_post to use parallelism). Setup should be:

1. Idempotent.
2. Fast.
3. Do not do work unnecessarily (do not download a file that already exists, etc) (hint, use Mise tasks source and output)

#### Setup Check & Versioning

Setup should include a `setup:check` and `setup:stamp` internal hidden commands that we use to check if the user ran the latest version of a setup or not. It's expected to run as a mise enter hook.
This allows us to version the setup, so we can notify users to re-run `mise run setup` again if expected version is not equal to saved version.

The stamp is written to `.mise/setup`. Add a committed `.mise/` folder to the project so the directory exists for the stamp to write into. Inside it, commit a `.gitignore` (see [.mise/.gitignore](../assets/.mise/.gitignore)) that ignores just the generated `setup` file.

Wrap this enter hook in `MISE_OFFLINE=1` (`enter = "MISE_OFFLINE=1 mise run setup:check"`) so it never resolves tools online and can't hang the shell offline — see [`hooks.md`](hooks.md).

Check the reference [mise.toml](../assets/mise.toml)

### Deps

Runtime/project dependencies (`node_modules`, a Python `.venv`, `vendor/`, …) belong in their **own `deps` task**, never inlined into `setup`. This keeps them runnable on their own after a lockfile change (`mise run deps`) and lets each side cache independently. Setup wires `deps` to run **after** `mise install` (the runtime must exist before its package manager runs) via `depends_post`; gate the `setup:stamp` on it with `wait_for = ["deps"]` so a successful stamp implies deps were installed.

Make it a no-op when nothing changed with `sources` + `outputs` (explicit `outputs` so the cache tracks the install dir itself; see [`tasks.md`](tasks.md)):

- `sources` = the manifest + lockfile(s), e.g. `package.json` + `package-lock.json`/`pnpm-lock.yaml`, `requirements.txt`/`uv.lock`, `go.mod` + `go.sum`.
- `outputs` = the install dir, e.g. `node_modules`, `.venv`, `vendor`.

`deps` stays runtime-agnostic in shape (one task, cached the same way); only the install command differs per runtime (`npm ci`, `pnpm install --frozen-lockfile`, `uv sync`, `go mod download`, …). For the Node-specific package-manager **version** pinning (Corepack vs mise), see [`runtimes/node.md`](runtimes/node.md). That is orthogonal to *who runs* the install.

### Check (Lint)

A command that runs all Linters, Formatters, and Static Validators. This is every check we expect to run pre-commit and in CI, NOT unit/integration tests.
It must be the **same command CI runs** and that the pre-commit hook runs, so behaviour can't drift between local, hook, and CI. Alias it `lint`.
The canonical CI wiring for this task lives at [.github/workflows/check.yml](../assets/.github/workflows/check.yml) (see [`ci.md`](ci.md)).

If using hk for pre-commit linters then delegate the actual steps to **hk** (one source of truth; see [`hk.md`](hk.md)) and have the task just forward flags. See the `check` task in the reference [mise.toml](../assets/mise.toml). Key points:

- **Stay on `hk check` and forward flags**: `hk check`/`hk fix` command semantics and the scope flags (staged default, `--all`, `--pr`, mutually exclusive) are in [`hk.md`](hk.md); the task exposes an opt-in `--fix` plus `--all`/`--pr`, with no branching on the subcommand.
- **Forward variadic `--step`/`--skip-step`** to target or skip steps, and wire `complete "step"` off `hk check --plan --json` so completion lists real step names.

### Test

Your typical local tests. If the project doesn't, add a no-op.

### Build

For applicable projects, build the projects. Should use `sources` and `outputs` when possible.

### Dev

Whatever runs the dev environment.

## Docs:

- [configuration](https://mise.jdx.dev/configuration.html)
- [tasks](https://mise.jdx.dev/tasks/)
