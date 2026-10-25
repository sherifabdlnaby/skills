# Project

> One-line description of what this project is.

## Getting started

This project uses [**mise**](https://mise.jdx.dev) to pin its tools (languages, CLIs), expose common tasks, run the local services, and wire up git hooks, so everyone works with the same versions and
commands. You only deal with mise once; after that it's a couple of `mise run` commands.

### 1. Install mise (first time on this machine)

<details>
<summary><b>macOS / Linux</b></summary>

```sh
brew install mise          # macOS / Linux (Homebrew)
# or: apt install mise · dnf install mise · pacman -S mise · …
```

No package manager? See the [installation docs](https://mise.jdx.dev/installing-mise.html) for other install methods.

</details>

<details>
<summary><b>Windows</b></summary>

```sh
winget install jdx.mise
```

See [installation docs](https://mise.jdx.dev/installing-mise.html) for Scoop/Chocolatey and WSL.

</details>

### 2. Activate mise in your shell

<details>
<summary><b>zsh / bash</b></summary>

```sh
echo 'eval "$(mise activate zsh)"'  >> ~/.zshrc   # zsh
echo 'eval "$(mise activate bash)"' >> ~/.bashrc  # bash
```

Restart your shell afterwards. Other shells: [activation docs](https://mise.jdx.dev/getting-started.html).

</details>

Confirm your install is healthy:

```sh
mise doctor
```

### 3. Set up the project

From the repo root:

```sh
mise trust      # allow this repo's mise config to load
mise run setup  # install the pinned tools (git hooks self-install via mise)
```

That's everything. You're ready to work.

## Run it locally

```sh
mise run dev    # alias: mise run dev:up
```

This starts the local services (Postgres, Redis, and the API) in the background, then prints their ports. No Docker is needed: mise downloads the services like any other project tool.
`mise run dev` is safe to run again: it starts what is down and leaves the rest alone, so it is also the repair command. The services keep running after you close the terminal.

| Command                     | What it does                                                        |
| --------------------------- | ------------------------------------------------------------------- |
| `mise run dev [name…]`      | Start everything, or one service and what it needs                  |
| `mise run dev:status`       | Show each service's port and status                                 |
| `mise run dev:logs [name…]` | Follow the logs (add `-n 50` to skip old lines); Ctrl+C closes them |
| `mise run dev:down [name…]` | Stop everything, or one service; the data is kept                   |
| `mise run dev:reset <name>` | Delete a service's data, e.g. a broken local database               |

Connection settings come from mise, not from a `.env` file: `DATABASE_URL`, `PGHOST`/`PGPORT`/…, `REDIS_URL`, and `API_PORT`. In your shell (with mise activated), `psql` connects with no flags and
`redis-cli -u $REDIS_URL` reaches Redis.

The API restarts when you save a file under `src/` or `migrations/`, and it applies new migrations before it starts. If it crashes or stops answering its health check, it restarts a few times on its
own; after that it shows as `errored` (`mise run dev:status`) until you fix it and run `mise run dev`.

### Many checkouts at once

Each git worktree runs its own stack, with its own data and ports. This project owns ports 14100–14109, and each worktree shifts that block by a multiple of 10. In a new worktree:

```sh
mise trust && mise run dev
```

Before you delete a worktree, run `mise run dev:down` in it.

### Debug a service in the foreground

```sh
mise run dev:down api                           # the other services keep running
mise x -- node src/server.js --port $API_PORT   # same env as the background service
mise run dev                                    # put it back in the background when you're done
```

## Everyday commands

| Command                                  | What it does                                                          |
| ---------------------------------------- | --------------------------------------------------------------------- |
| `mise run check` (alias `mise run lint`) | Run all linters, formatters, and validators. Add `--fix` to auto-fix. |
| `mise run test`                          | Run the fast test suite (no services).                                |
| `mise run test:integration`              | Run the integration tests; starts the local services when needed.     |
| `mise tasks`                             | List every available task.                                            |

Run `mise run <task> --help` to see a task's options.

## Git hooks

`mise run setup` runs `mise install`, which self-installs git hooks (via [hk](https://hk.jdx.dev))
through a postinstall step. On **commit**, your staged files are formatted and linted; a **push** runs the slower gates. CI
runs both as `mise run check`, so problems surface before review.

Need to skip them for a work-in-progress commit? `git commit --no-verify`.
