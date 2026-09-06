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

### Adapting the assets

- **`check.yml`/`check.autofix.yml`'s mise `version:` input** is pinned to whatever was current when this template was last touched; when copying either workflow, replace it with the mise version
  current at setup time instead of keeping the template's pin.

## Standard Tasks

Each project should start with: `setup` `check (alias lint)` `test` `build`(when applicable), and `dev`(when applicable).
These are root tasks. We can include sub-tasks under their namespace if needed. The root task is expected to run the most common.
For example, we can have 4 different kinds of tests (test:x, test:y:, test:z, and test:e2e), we group test (x/y/z) under just `test` expecting it to be fast.

### Fast path vs slow path

Every task belongs to a lane; the lane sets its budget:

- **Fast path** — `check`, `test`, `dev`, `build`, the `enter` hook, pre-commit. Runs many
  times a day: cheap, offline-safe, non-interactive, and never `depends` on a slow-path
  task. Staleness is *reported* here (the `setup:check` nag), never repaired.
- **Slow path** — `setup` and its `setup:*` sub-tasks. Run deliberately (onboarding, after
  the nag): may be slow, online, interactive. Nothing on the fast path waits on it.
- **The one crossing: `deps`.** Fast-path tasks may depend on `deps` because its
  `sources`/`outputs` cache makes it a no-op when fresh; when stale it self-heals (needs
  network). The experimental `[deps]` auto engine is this same stance built in. `setup`
  itself is never a dependency of anything.

Below are guidance on each command.

### Setup

Setup is expected to include all the (one time) setups, including mise own `mise install`. Runtime/project dependencies are **not** inlined here; they live in their own [`deps`](#deps) task that setup
runs after `mise install` (see below). Pre-commit (hk) hooks are **not** installed by an explicit step in setup; they self-install canonically via `[hooks] postinstall = "hk install --mise"`, which
fires on the `mise install` that setup runs (and on any future `mise install`). See [`hk.md`](hk.md). It's okay for setup to consist of other mise tasks (rely on depends and depends_post to use
parallelism). Setup should be:

1. Idempotent.
2. [Slow-path](#fast-path-vs-slow-path): the first run may be slow, online, or interactive — nothing waits on it.
3. Cheap to re-run: skip work already done (hint, use Mise tasks source and output).

#### Preflight

When the project needs prerequisites mise can't install (Docker present, VPN reachable, supported
OS), add a hidden `setup:preflight` that setup `depends` on first. **Check-and-instruct only** —
anything a script can fix is a regular setup step; preflight fails fast with exact instructions
before setup burns minutes on a machine that can't finish.

#### Setup Check & Versioning

Setup should include a `setup:check` and `setup:stamp` internal hidden commands that we use to check if the user ran the latest version of a setup or not. It's expected to run as a mise enter hook.
This allows us to version the setup, so we can notify (AND NAG!) users to re-run `mise run setup` again if expected version is not equal to saved version.

The stamp is a **human-bumped counter**. Bump it only for a change nothing reconciles on its own: a new manual step, a changed preflight, a one-time migration. A missing tool installs itself
on the next `mise run`, and `deps` self-heals from its cache, so adding or bumping a tool or a dependency leaves the stamp alone.

The stamp is written to `.config/mise/setup`. Add a committed `.config/mise/` folder to the project so the directory exists for the stamp to write into. Inside it, commit a `.gitignore` (see
[.config/mise/.gitignore](../assets/.config/mise/.gitignore)) that ignores just the generated `setup` file.

Wrap this enter hook in `MISE_OFFLINE=1` (`enter = "MISE_OFFLINE=1 mise run setup:check"`) so it never resolves tools online and can't hang the shell offline — see [`hooks.md`](hooks.md).

Check the reference [mise.toml](../assets/mise.toml)

### Deps

Runtime/project dependencies (`node_modules`, a Python `.venv`, `vendor/`, …) belong in their **own `deps` task**,
never inlined into `setup`. This keeps them runnable on their own after a lockfile change (`mise run deps`) and lets
each side cache independently.

Make it a no-op when nothing changed with `sources` + `outputs` (explicit `outputs` so the cache tracks the install dir itself; see [`tasks.md`](tasks.md)):

- `sources` = the manifest + lockfile(s), e.g. `package.json` + `package-lock.json`/`pnpm-lock.yaml`, `requirements.txt`/`uv.lock`, `go.mod` + `go.sum`.
- `outputs` = the install dir, e.g. `node_modules`, `.venv`, `vendor`.

**Pre-deps steps** (e.g. npm auth against a private registry) get their own hidden idempotent task that
`deps` `depends` on (`deps:auth`, not `setup:*`) so `mise run deps` works standalone. Add one only when the
project needs it; on the experimental `[deps]` engine a custom provider is the equivalent slot.

#### Native engine: `[deps]` providers (experimental)

mise's [`[deps]` providers](https://mise.jdx.dev/dev-tools/deps.html) do the same job natively; it has built-in providers
per package manager (npm/pnpm/yarn/bun/uv/poetry/pip/go/bundler/composer/…) plus custom ones, with blake3
content-hash. With `auto = true`, stale deps install automatically before **every** `mise run`/`mise x`.

Offer it when the team accepts `experimental = true`; keep classic as the default until the feature graduates.

- Prefer `auto = true` when adopting
- **No lockfile init; provider counts as *fresh*** and silently does nothing. The lockfile must exist (commit it)
  before the provider ever runs.
- **Custom providers are the extension point** the classic task has no equivalent for — project-specific steps
  with their own staleness engine, and `depends` between providers:

### Check (Lint)

A command that runs all Linters, Formatters, and Static Validators. This is every check we expect to run pre-commit and in CI, NOT unit/integration tests. It is the **one command CI runs**, every gate
at once; the git hooks run subsets of it by cost (commit gates on commit, push gates on push, see [`hk.md`](hk.md)), so a step outside `check` is invisible to CI. Alias it `lint`. The canonical CI
wiring for this task lives at [.github/workflows/check.yml](../assets/.github/workflows/check.yml) (see [`ci.md`](ci.md)).

If using hk for pre-commit linters then delegate the actual steps to **hk** (one source of truth; see [`hk.md`](hk.md)) and have the task just forward flags. See the `check` task in the reference
[mise.toml](../assets/mise.toml). Key points:

- **Stay on `hk check` and forward flags**: `hk check`/`hk fix` command semantics and
  the scope flags (staged default, `--all`, `--pr`, mutually exclusive) are in
  [`hk.md`](hk.md); the task exposes an opt-in `--fix` plus `--all`/`--pr`, with no
  branching on the subcommand.
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
