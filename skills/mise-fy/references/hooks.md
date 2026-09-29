# Hooks (directory & lifecycle)

Guidance on mise's directory & lifecycle hooks (`enter`/`cd`/`leave`, `watch_files`, `preinstall`/`postinstall`, others...). For git/pre-commit hooks specifically, see [`hk.md`](hk.md).

## Rules and Best Practices:

1. **Keep `enter`/`cd` hooks offline-safe.** They fire on **every** directory change, so a hook that reaches the network taxes each `cd` and hangs the shell when offline.
2. **Write `enter`/`cd` hooks as plain shell, not `mise run`.** `mise run` installs every missing tool before the task starts, even tools the task never uses: a fresh clone or a new pin downloads
   on `cd`, and `MISE_OFFLINE=1` only turns that download into an error on each `cd`. The hook string is templated like a task (`{{vars.*}}`, `{{config_root}}`), so a staleness check or nudge needs
   no task. It runs in the shell's current directory, which can be a subfolder: reach project files through `{{config_root}}`.
3. **Keep hook commands fast and idempotent.** They run on routine events; slow or side-effecting work belongs in a task you invoke explicitly.

## Notes & Gotchas:

- **Adding any hook makes the whole `mise.toml` untrusted** until `mise trust` (see SKILL.md "Always applies"). Fresh clones and CI need the trust step or a `trusted_config_paths` entry.
- **`MISE_OFFLINE` does not suppress `[deps]` auto-providers.** If the project uses the experimental `[deps]` engine with `auto = true`, any `mise run` inside a hook installs stale deps first — on
  every `cd` for `enter`. When a hook must call `mise run`, add `--no-deps`; the flag is the only kill switch (no env var). See
  [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#deps).
- **Hooks are no longer experimental**: You don't need to enable experiments for hooks.

## Docs:

- [hooks](https://mise.jdx.dev/hooks.html)
