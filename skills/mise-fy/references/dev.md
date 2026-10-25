# Dev Stack (local services)

How to run a project's local services (a database, a cache, the project's own servers and workers) as mise `[daemons]`, so one command starts a checkout's whole stack and many checkouts run side by
side.

`[daemons]` is experimental: set `experimental = true` in the project's `[settings]`. mise runs them under [pitchfork](https://pitchfork.jdx.dev), which it installs and starts on its own, so there is
no global mise or pitchfork config to write. Verified on mise 2026.10.18 and pitchfork 2.32.

## Safety

- **One pitchfork supervisor serves every project of the user.** Restarting it (`pitchfork supervisor stop`, `supervisor start --force`, a proxy setting change) stops the daemons of every project.
  Start and stop daemons through `mise daemons …` or the `dev:*` tasks, which act on one project.
- **Data lives outside the checkout**, in mise's state dir (`data_dir` in `mise daemons ls --json`), so `git clean` never touches it. Deleting it is `dev:reset`'s job.
- **Daemons outlive the shell and the checkout.** Nothing stops them when the terminal closes. Run `mise run dev:down` in a worktree before removing it; `mise daemons prune` cleans up the state of
  checkouts that are already gone.

## Rules and Best Practices:

1. **Pick the simplest kind of daemon.** A preset first (`preset = "postgres"`, `"redis"`, etc.): mise installs the binary, keeps the data, and exports the connection env. Else a custom daemon
   (`run = …`) on a mise-managed tool. A service with neither runs from a compose file, the one Docker exception (see [Compose](#compose)).
2. **One port block per project.** Each daemon gets `port = { auto = true, base = <B+k>, stride = 10 }`, with `k` from 0 to 9 and one `B` per project: a free multiple of 100 in 10000–27000, named in a
   comment. The main checkout uses `B+k`; a linked worktree adds 10 × its slot (1–511, derived from its path). `stride` has no project-wide setting, so repeat it on every daemon. (why: the default
   stride of 1 makes two daemons whose bases differ by less than 512 collide in some worktree, and presets on their default ports clash between projects.)
3. **Apps read connection settings from env, never hard-coded ports.** Presets export `DATABASE_URL`, `PG*`, `REDIS_URL`, etc.; a daemon with a port exports `<NAME>_PORT` (its name upper-cased,
   punctuation to `_`). They follow the worktree offset and reach the activated shell, tasks, `mise x`, and every daemon.
4. **Pass a daemon its own port in the command:** `run = "exec node src/server.js --port $API_PORT"`. An app that can't take it there gets it from the daemon's own
   `env = { HTTP_PORT = "{{ daemons.api.port }}" }`, which reaches only that process. `[env]` holds what the shell, tasks and tests need; a daemon's `env` holds settings for that process only.
5. **`proxy = false` on custom daemons.** Otherwise mise exports `<NAME>_URL` with a `https://<name>.<project>.localhost` hostname that only the machine-wide pitchfork proxy serves. (why: hostnames
   need global pitchfork config, a supervisor restart and certificate trust, none of which a project can set up.)
6. **Run the plain server process, and let pitchfork reload it.** `exec` the server itself and list its sources in `watch = ["src/**", …]`, not a dev server that runs its own watcher (`node --watch`,
   nodemon, etc.). The app must not exit 0 on SIGTERM. (why: pitchfork never retries a clean exit, and a watcher survives the crash and exits 0 when stopped, so the daemon never heals.)
7. **Readiness, health, and a bounded retry** on every custom daemon:
   - `ready_cmd`: `start`, and every daemon or task that waits on this one, blocks until it passes. A `port` alone only waits a fixed 3s.
   - `health_cmd`: probes for the daemon's whole life (every 10s; 3 failures kill it).
   - `retry = 3`: restarts it after a crash or a health kill; each `mise run dev` resets the count. Presets ship their own ready check; give them `retry = 3` too.
   - A timeout in each probe (`curl -sf -m 2 http://127.0.0.1:$API_PORT/health`) makes a hung process fail fast.
   - `ready_cmd` and `health_cmd` run through `mise x`, so `$API_PORT` works there. Fields pitchfork renders itself (`ready_http`, a daemon's `env`) know `{{ daemons.<name>.port }}`, not
     `{{ env.* }}`.
8. **Never `retry = true`.** A daemon that fails before it is ready is then retried forever, with a doubling delay. `start` (and `mise run dev`) waits with only a spinner, and Ctrl+C leaves the
   supervisor retrying until `mise daemons stop`.
9. **Migrations run in `init`.** `init` runs before every start and restart, and readiness waits for it, so the command must skip applied migrations. With the migrations dir in `watch`, saving a new
   migration applies it.
10. **Order with daemon `depends`.** `mise daemons start api` starts `api`'s `depends` first and waits until each is ready. A task reaches the stack with `depends = ["dev"]`, not a task-level
    `daemons = [...]`. (why: `daemons = [...]` starts the daemons before the task's own `depends`, so in a fresh worktree an app daemon starts before `deps` installed its packages.)
11. **Groups only for optional services.** Without `[daemon_groups]`, `dev` starts every daemon. Declare `default = [...]` only when a service shouldn't start every day; `mise run dev <name>` and
    `mise run dev --all` reach the rest.

## The `dev:*` tasks

Every project with daemons exposes the same set. Copy it from [`assets/mise.toml`](../assets/mise.toml).

| Task                            | Does                                                                                                                                                          |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dev [names…]` (alias `dev:up`) | Start every daemon (or the named ones and their `depends`) in the background, then print the port table. Safe to run again, so it is also the repair command. |
| `dev:status`                    | The port table (`mise daemons urls`), without starting anything.                                                                                              |
| `dev:logs [names…]`             | Follow the logs (history first; `-n 50` skips old lines). Ctrl+C closes the view only.                                                                        |
| `dev:down [names…]`             | Stop; the data is kept.                                                                                                                                       |
| `dev:reset <name>`              | Stop one daemon and delete its data, behind `confirm`.                                                                                                        |

- **Thin wrappers.** Each task `run`s `mise daemons <cmd>`. A `usage` arg (`var=#true double_dash="automatic"`) takes names and flags, `{{usage.daemons | join(sep=' ')}}` puts them in `run`
  (with a spec, args no longer append on their own), and `complete` lists the daemon names from `mise daemons ls --json` (`mise daemons` itself doesn't complete them). The `join` splits an arg that
  holds spaces (`--grep "a b"`); call `mise daemons logs` directly for that.
- **Adding a service** is one `[daemons.<name>]` block. The tasks and their completion need no change. The `dev:` verbs are reserved: no daemon takes one as its name.
- **`dev` depends on `deps`**, the one allowed fast-path crossing (see the [lane map](reference-setup-and-patterns.md#fast-path-vs-slow-path)). Everything else it needs, pitchfork and the preset
  binaries, mise installs on the first run; `setup`'s `mise install` and `mise lock` cover them too. A new worktree needs only `mise trust && mise run dev`.
- **Tests:** bare `test` stays fast and starts nothing. A test task that needs services (`test:integration`, `test:e2e`, etc.) uses `depends = ["dev"]`.
- **Foreground debugging:** `mise run dev:down api`, then `mise x -- node src/server.js --port $API_PORT` (same env), then `mise run dev` to put it back.

## Compose

For a service with no preset and no mise tool:

- **Docker is a prerequisite:** declare it as a `[doctor.checks]` probe (see [prerequisite checks](reference-setup-and-patterns.md#prerequisite-checks)).
- **`dev` runs `docker compose up -d --wait` before `mise daemons start`** (`--wait` blocks on the compose healthchecks); `dev:down` also runs `docker compose down`, and `docker compose logs -f` shows
  the logs.
- **Compose ports don't follow the worktree offset**, so only one checkout runs them at a time unless the compose file maps its ports from env. The compose file's content is the project's.
- **Don't run `docker compose up` as a daemon.** pitchfork's default 5s stop timeout kills the client while the containers keep running.

## Notes & Gotchas:

- **`mise daemons logs`/`status` fail with "No version is set for shim: pitchfork".** The mise shims are on PATH and the project doesn't pin pitchfork. Fix: `pitchfork = "2"` in `[tools]`.
- **`mise run dev` spins on "waiting for delay (3s)…" and never returns.** A daemon fails before it is ready under `retry = true`; `mise daemons logs <name>` shows it exiting again and again. Fix:
  `retry = 3` (rule 8).
- **A crashed daemon stays down, and its status is `stopped`, not `errored`.** It exited 0 (a watcher, or a SIGTERM handler that exits 0), and a clean exit is never retried. Fix: rule 6.
- **`start` reports started, then the first requests get "connection refused".** No ready check: a `port` alone waits a fixed 3s. Fix: `ready_cmd`.
- **"Variable `env` is not defined", and the daemon never starts.** `{{ env.X }}` in a field pitchfork renders (a daemon's `env`, `ready_http`). Fix: `{{ daemons.<name>.port }}` there, or `$VAR` in
  `run`/`ready_cmd`/`health_cmd`. `{{config_root}}` in `run` fails the same way; paths in `run` resolve from the project root.
- **Every daemon sees the same `PORT`.** `[env] PORT = …` overrides the per-daemon `PORT` that pitchfork sets. Fix: never set `PORT` in `[env]`; alias another name
  (`HTTP_PORT = "{{ env.API_PORT }}"`).
- **After `dev:reset` of a database, the app runs against an empty one.** Its `init` (the migrations) runs only when it starts, and `dev` leaves a running daemon alone. Fix:
  `mise run dev:down api && mise run dev`.
- **"port N is already in use".** Another checkout, project, or app holds a port of the block (two worktrees on one slot, overlapping blocks, macOS AirPlay on 5000/7000, etc.). Fix: move that daemon
  in `mise.local.toml`, as mise's hint says. It is rare and loud, so no code guards against it.
- **"exceeds 65535 for this worktree".** `B` is too high for a high slot. Fix: keep `B + 5119 ≤ 65535`.
- **A preset's `ports.<name>` override collides across worktrees.** It doesn't follow the offset. Fix: leave it unset.
- **The pitchfork CLI warns "CLI version … differs from supervisor version".** Another project started the shared supervisor with its own pin. Harmless: after a reboot the first project to start sets
  the version. Restarting the supervisor to match stops every project's daemons (see Safety).
- **`mise daemons urls` lists `project: https://<project>.localhost`** with the proxy off. Only the proxy serves it; ignore it.
- **`mise daemons prune` leaves an empty state dir and the project's namespace entry behind.** Harmless.
- **The Redis preset has no Windows build.**

## Checklist

- [ ] `experimental = true`; `pitchfork` and `jq` pinned in `[tools]`
- [ ] Each service is a preset, else a custom daemon; compose only for the rest, behind a Docker doctor check
- [ ] One port block: `base = B+k` and `stride = 10` on every daemon, the block named in a comment
- [ ] Custom daemons: the plain process with `exec` and its port in the command, `watch`, `proxy = false`, `ready_cmd` and `health_cmd` with a timeout, `depends`
- [ ] `retry = 3` on every daemon, never `true`
- [ ] Migrations in `init`, safe to repeat
- [ ] The `dev:*` tasks from the asset; tests that need services use `depends = ["dev"]`
- [ ] App code reads connection env, not hard-coded ports
- [ ] `mise run dev` works from a fresh clone and in a second worktree at the same time, and a second run changes nothing
- [ ] README and AGENTS.md document the stack (see [`docs.md`](docs.md))

## Docs:

- [daemons](https://mise.jdx.dev/daemons.html), [presets](https://mise.jdx.dev/daemons/presets.html), [worktrees and ports](https://mise.jdx.dev/daemons/worktrees.html)
- pitchfork: [ready checks](https://pitchfork.jdx.dev/guides/ready-checks.html), [health checks](https://pitchfork.jdx.dev/guides/health-checks),
  [auto-restart](https://pitchfork.jdx.dev/guides/auto-restart), [lifecycle hooks](https://pitchfork.jdx.dev/guides/lifecycle-hooks.html)
