# Tasks

How to build or improve mise Tasks.

## Rules and Best Practices:

1. **Tasks are the single source of truth** for lint/test/build. The same names drive local dev, hk pre-commit, and CI. Expose the consistent contract every repo shares: `setup`, `check` (alias
   `lint`), `test`, `build`, `dev`.
2. **Namespace with colons** (`test:unit`, `gen:docs`). The bare group name runs the common case (`test` = fast tests); a **quoted** glob runs the group (`mise run 'test:*'`; quote it or the shell
   expands it).
3. **`depends` for ordering; `sources`/`outputs` for caching**. `sources` alone already
   skips-if-unchanged (mise auto-tracks an internal marker); add explicit `outputs` when the
   artifact's existence is itself a correctness condition (a deleted output must re-run).
   `--force` bypasses for a clean run.
4. **Identify a task's lane**: fast path (e.g. `check`, the `enter` hook, pre-commit)
   runs many times a day: cheap, offline-safe, non-interactive, and never `depends` on
   slow path (`setup`, `setup:*`). Membership: [lane map](reference-setup-and-patterns.md#fast-path-vs-slow-path).
5. **TOML for <= 5-line tasks; longer logic use an executable file task** with a shebang + `set -euo pipefail` (unless the repo already has a scripts dir).
6. **File tasks must be executable** in a discovered dir. Prefer to use `.config/mise/tasks` over `.mise` to keep repo root directories few.
7. **Scope `env`/`tools` to the task** (`[tasks.x] env.FOO` / `tools = [...]`) instead of global when only it needs them.
8. **Invoke `mise run <task>` (alias `mise r`)**, never bare `mise <task>` (avoids command/tool conflicts).
9. **Take input via the `usage` spec**; never the deprecated `{{arg()}}/{{option()}}/{{flag()}}` (deprecated since 2026.5.0; scheduled for removal in 2027.5.0). Built-in; `help=` + `choices` make
   `--help` and completion free. See Task Arguments below.
10. **Give every task a `description`**;
11. add `choices`/simple `complete` when useful and it's a short one-liner command. Avoid hardcoding/enumerating lists that are expected to extend in the future.
12. Handwritten completion scripts only on request by user; keep them under **`.config/mise/completion/`** (Convention only;
    mise does **not** auto-load that dir; it's just where we standardize these scripts.).
13. **Gate destructive tasks with `confirm = "…"`** and `hide = true` on internal
    helpers. In CI pass `-y`/`--yes` **before** the task name (`mise run -y deploy
    prod`); after it, a task with a `usage` spec parses it as a task arg and errors
    (`unexpected word: -y`). Otherwise the prompt aborts the task (`ERROR aborted by
    user`). Beware: `depends` run **before** the prompt, so keep side effects out of
    a gated task's deps.
14. **Prefer config to runtime flags**. Put reused settings in `mise.toml`, not ad-hoc `--flags`.
15. **Share static values via `[vars]`, not `[env]`** (vars stay template-only; they don't leak into the process environment).
16. **Building a standard task** (`setup`/`check`(=lint)/`test`/`build`/`dev`)? Unless project already have a pattern, then refer to
    [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#standard-tasks). If user ask for a `check`/`lint`, check if **hk** is set up and use it (refer to -> [`hk.md`](hk.md)).

## Notes & Gotchas:

- **Don't wire `setup` into the fast path "so it always works".** `test depends =
  ["setup"]` puts slow, online (possibly interactive) work into a loop that runs dozens
  of times a day, and breaks offline.
- **Tasks run from the config root, not your cwd.** Override per-task with `dir` (default `"{{config_root}}"`; set `dir = "{{cwd}}"` to follow the caller). Only reach for `{{config_root}}` when the
  task sets a non-default `dir`.
- **`run` as an array = serial commands, each its own shell**; `cd` and unexported vars
  don't carry between entries. Use one multi-line `run` (or a file task) for stateful
  sequences. Stops on first failure (`set -e`); `mise run -c`/`--continue-on-error` keeps going.
- **Freshness is mtime-based, per-clone**: `touch` alone re-runs;
  state lives in `~/.local/state/mise/`, so fresh clones/worktrees start stale.
- Explicit `outputs` compare make-style: outputs older than sources re-run the task
  every invocation until the outputs are refreshed.
- **Auto outputs are blind to your real artifacts** — the marker only tracks
  _inputs_; mise never stat's the files your task wrote. `rm -rf dist/` and mise
  still says `skipping` — it won't regenerate a deleted output. Declare **explicit
  `outputs`** whenever "the artifact must exist" is a correctness condition: a
  missing/deleted explicit output resolves to no mtime -> task re-runs. Rule of
  thumb: `sources` alone for "re-run when inputs change"; explicit `outputs` for
  artifact tasks.
- **`depends` run in parallel** (default 4 jobs; `--jobs`/`MISE_JOBS`); `depends_post` run after. `wait_for` only waits _if_ that task is already in the run. A task's `env` is **not** seen by its
  `depends`.
- **No-spec args go to the _last_ `run` entry only** (with a `usage` spec they're parsed instead; see Task Arguments).
- **Output is line-buffered + label-prefixed.** Change with `--output
  interleave|keep-order|quiet|silent` (or `MISE_TASK_OUTPUT`). `raw = true` / `--raw`
  reads-writes the terminal directly (forces `--jobs=1`) and **bypasses secret
  redaction**; never in env-bearing tasks (see [`env.md`](env.md)). When a task just
  needs stdio, prefer `interactive = true` (targeted stdio lock, no global side
  effects).
- **`run` entries can be task refs**, not just shell scripts composed inline in list
  order: `run = ["echo start", { task = "build", args = ["--release"] }, {
  tasks = ["lint", "test"] }]`. `{ task = }` runs one (accepts `args`/`env`
  overrides); `{ tasks = [...] }` runs them in parallel. Unlike `depends`, these run
  _as_ steps, in position.
- Mise has Tera function "task_source_files" read at [`additional mise functions`](https://mise.jdx.dev/templates.html#additional-mise-functions)

Still stuck? Check the docs below.

## Syntax Hints

TOML task:

```toml
[tasks.build]
description = "Build the CLI"
depends = ["lint"]                        # run first, in parallel
sources = ["src/**/*.rs", "Cargo.toml"]   # freshness inputs
outputs = ["target/debug/mycli"]          # explicit output -> also re-runs if deleted (omit to auto-track)
env = { RUST_BACKTRACE = "1" }            # task-scoped env (NOT seen by depends)
tools = { rust = "1.82" }                 # task-scoped tool
run = "cargo build"
```

(Args/flags via `usage` are covered in Task Arguments below; gate destructive ones with `confirm = "…"`.)

File task (`.config/mise/tasks/build`, must be executable):

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

Take input via the [`usage`](https://usage.jdx.dev) spec: `usage = '''…'''` (TOML) or `#USAGE` lines (file task). The parser is built-in; don't add `usage` to `[tools]`. Values arrive as
`$usage_<name>` env vars (dashes to underscores), and inside a TOML `run` also as Tera `{{usage.<name>}}` (variadics are arrays). Precedence: CLI > `env="VAR"` > `default`. The spec grammar
(args, flags, `choices`, `complete`, defaults) is the usage docs; the `check` task in [`assets/mise.toml`](../assets/mise.toml) is a worked example, and `mise run <task> --help` is generated
from the spec.

Gotchas:

- **`{{usage.X}}` in `description`** (or any other config-load-time field) throws `Variable 'usage.X' not found` and **breaks the whole config**; every task fails, not just that one. It works
  in `run`, `confirm`, and `depends`/`wait_for` args.
- **File-task bodies are not Tera-rendered.** `{{usage.X}}` prints literally there; read `$usage_X`. Every line of a multi-line `{ choices … }` block needs its own `#USAGE`.
- **No spec means passthrough.** Extra CLI args append to the last `run` entry (`$@` in a file task). With a spec they are parsed instead, so an explicit passthrough is
  `arg "[a]" var=#true double_dash="automatic"`.
- A required `<arg>` is satisfied by its `env="VAR"` with no CLI value; `hide=#true` drops an item from help and completion.

## Watch

`mise watch <task>` (alias `mise w`) re-runs a task when its **`sources`** change. It shells out to **watchexec**, so that binary must be present (add it to tools).

```bash
mise watch test                # run + re-run on source change
mise watch -r serve            # -r/--restart: kill & restart the process (dev servers)
```

Flags pass through to watchexec (`mise watch --help`); `-r/--restart` is the one dev servers need, and `--poll` is for filesystems whose native events don't fire.

Worth wiring watch for: tight edit -> rebuild/retest loops, dev servers, doc/asset rebuilds.

**`mise watch` is a command you run, not a task**; it's a long-lived foreground process
(Ctrl-C to stop) that takes a task as its argument; mise never starts it on its own. Wrap
it in a task so it has a standard name and `mise run <task>` starts the watcher:

```toml
[tasks.dev]
description = "Watch sources & re-run tests on change"
run = "mise watch test"        # `mise run dev` starts the watcher; someone still has to invoke it
```

**Notes & Gotchas:**

- **watchexec is a real dependency**, not bundled. pin it in `[tools]` if the team relies on `mise watch`.
- **Need it truly unattended** (daemon, auto-restart, scheduled)? That's outside watch -> use a dedicated process manager or system service.

## Checklist

Before considering a task done:

- [ ] `description` set; standard names used where they fit (`setup`/`check`(=lint)/`test`/`build`/`dev`); colon-namespaced if part of a group.
- [ ] Right form: TOML for <=5 lines, executable file task for longer logic; file task lives in a discovered dir (`.config/mise/tasks`).
- [ ] Ordering via `depends`; skip-if-unchanged via `sources` (explicit `outputs` on artifact tasks).
- [ ] `env`/`tools` scoped to the task, not global, when only it needs them.
- [ ] Args via `usage` spec (not deprecated `{{arg()}}` etc.); `{{usage.X}}` only inside a TOML `run`, `$usage_X` everywhere else.
- [ ] Completion added where useful: `{ choices … }` for static sets that aren't expected to grow, `complete "name" run="…"` for dynamic (if command is oneliner); handwritten scripts under
      `.config/mise/completion/` only on request.
- [ ] Destructive tasks gated with `confirm`; internal helpers `hide = true`; CI passes `-y`.
- [ ] Reused settings in config (`mise.toml`/`MISE_*`), static values in `[vars]` not `[env]`.
- [ ] Runs green via `mise run <task>`; if it's `check`/`lint`, wired to hk when the repo uses it.

## Docs:

- [tasks](https://mise.jdx.dev/tasks/)
- [toml-tasks](https://mise.jdx.dev/tasks/toml-tasks.html)
- [file-tasks](https://mise.jdx.dev/tasks/file-tasks.html)
- [running-tasks](https://mise.jdx.dev/tasks/running-tasks.html)
- [watch](https://mise.jdx.dev/cli/watch.html)
