# Reference Setup — Canonical Layout

Refer to [mise.toml][../assets/mise.toml]

# Bare Root mise.toml

Include all the [mise.toml][../assets/mise.toml] main top-level fields, alongside comment decorators.
To not blindly copy the content under each top-level field, for that apply what is relevant. Respect Sorting.

## Configuration Sorting

The order of settings and options

### Top Level Settings

1. mise `min_version`
2. Tools
3. env
4. vars
5. tasks
6. hooks
7. settings

### In Tools

1. Runtime
2. <<anything>>
3. Linters and Formatters
4. hk

# Standard Tasks

Each project should start with: `setup` `check (alias lint)` `test` `build`(when applicable), and `dev`(when applicable).
These are root tasks. We can include sub-tasks under their namespace if needed. The root task is expected to run the most common.
For example, we can have 4 different kinds of tests (test:x, test:y:, test:z, and test:e2e), we group test (x/y/z) under just `test` expecting it to be fast.

Below are guidance on each command.

## Setup

Setup is expected to include all the (one time) setups, including mise own `mise install`, as well as things like installing runtime dependencies, etc.
Pre-commit (hk) hooks are **not** installed by an explicit step in setup — they self-install canonically via `[hooks] postinstall = "hk install --mise"`, which fires on the `mise install` that setup runs (and on any future `mise install`). See [`hk.md`](hk.md).
It's okay for setup to consist of other mise tasks (rely on depends and depends_post to use parallelism). Setup should be:

1. Idempotent.
2. Fast.
3. Do not do work unnecessarily (do not download a file that already exists, etc) (hint, use Mise tasks source and output)

### Setup Check & Versioning

Setup should include a `setup:check` and `setup:stamp` internal hidden commands that we use to check if the user ran the latest version of a setup or not. It's expected to run as a mise enter hook.
This allows us to version the setup, so we can notify users to re-run `mise run setup` again if expected version IS not equal to saved version.

The stamp is written to `.mise/setup`. Add a committed `.mise/` folder to the project so the directory exists for the stamp to write into. Inside it, commit a `.gitignore` (see [.mise/.gitignore][../assets/.mise/.gitignore]) that ignores just the generated `setup` file.

Check the reference [mise.toml][../assets/mise.toml]

## Check (Lint)

A command that runs all Linters, Formatters, and Static Validators. This is every check we expect to run pre-commit and in CI — NOT unit/integration tests.
It must be the **same command CI runs** and that the pre-commit hook runs, so behaviour can't drift between local, hook, and CI. Alias it `lint`.
The canonical CI wiring for this task lives at [.github/workflows/check.yml][../assets/.github/workflows/check.yml] (see [`ci.md`](ci.md)).

If using hk for pre-commit linters then delegate the actual steps to **hk** (one source of truth; see [`hk.md`](hk.md)) and have the task just forward flags. See the `check` task in the reference [mise.toml][../assets/mise.toml]. Key points:

- **`hk check` and `hk fix` are the same command**; the subcommand only sets the default mode, and `--fix`/`--check` override it. So a single `hk check` + an opt-in `--fix` flag covers both reporting and fixing — no need to branch on the subcommand.
- **Default scope is staged files**; expose `--all` (everything) and `--pr` (only files changed vs the default branch — what CI uses). hk makes `--all`/`--pr` mutually exclusive.
- **Forward variadic `--step`/`--skip-step`** to target or skip steps, and wire `complete "step"` off `hk check --plan --json` so completion lists real step names.

## Test

Your typical local tests. If the project doesn't, add a no-op.

## Build

For applicable projects, build the projects. Should use `sources` and `outputs` when possible.

## Dev

Whatever runs the dev environment.
