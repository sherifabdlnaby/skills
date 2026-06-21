# Installing mise

Use this as a guide on how to install mise.
Prefer a package manager. Always Latest instructions: [installing-mise](https://mise.jdx.dev/installing-mise.html).

## 1. Install

- macOS/Linux: `brew install mise`
- Windows: `winget install jdx.mise` (or `scoop install mise`)
- If no package manager, refer to installation steps from the docs above.

## 2. Activate (interactive shell)

Add to your interactive shell rc (`~/.zshrc` / `~/.bashrc`), swap `zsh`→`bash` as needed:

```sh
eval "$(mise activate zsh)"
```

## 3. Shims for non-interactive shells

Add `mise activate --shims` to the non-interactive shells (scripts, IDEs, CI-like) need the shims dir on `PATH`.
Run:

```sh
eval "$(mise activate zsh --shims)"
```

In ~/.zshenv (or what is similar in Bash).


## 4. Install Completions

Read [completion](https://mise.jdx.dev/cli/completion.html).


## 5. Confirm

Run `mise doctor` in new subshell to ensure config got reloaded. Validate the two activation methods. Validate completions are loaded and working.

## Docs:

- [installing mise](https://mise.jdx.dev/installing-mise.html)
- [activate](https://mise.jdx.dev/cli/activate.html)
- [shims](https://mise.jdx.dev/dev-tools/shims.html)
- [completions](https://mise.jdx.dev/cli/completion.html)
