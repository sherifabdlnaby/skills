# Project

> One-line description of what this project is.

## Getting started

This project uses [**mise**](https://mise.jdx.dev) to pin its tools (languages, CLIs), expose common tasks, and wire up git hooks — so everyone works with the same versions and commands. You only deal with mise once; after that it's a couple of `mise run` commands.

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

That's everything — you're ready to work.

## Everyday commands

| Command                                  | What it does                                                          |
| ---------------------------------------- | --------------------------------------------------------------------- |
| `mise run check` (alias `mise run lint`) | Run all linters, formatters, and validators. Add `--fix` to auto-fix. |
| `mise run test`                          | Run the test suite.                                                   |
| `mise tasks`                             | List every available task.                                            |

Run `mise run <task> --help` to see a task's options.

## Git hooks

`mise run setup` runs `mise install`, which self-installs git hooks (via [hk](https://hk.jdx.dev)) through a postinstall step. On **commit**, your staged files are formatted and linted automatically — the same `check` that runs in CI, so problems surface before you push.

Need to skip them for a work-in-progress commit? `git commit --no-verify`.
