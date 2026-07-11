# Hooks (directory & lifecycle)

Guidance on mise's directory & lifecycle hooks (`enter`/`cd`/`leave`, `watch_files`, `preinstall`/`postinstall`, others...). For git/pre-commit hooks specifically, see [`hk.md`](hk.md).

**Where the block goes in `mise.toml`**: top-level section order (`min_version` -> tools -> env -> vars -> tasks -> hooks -> settings) is in [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#configuration-sorting).

## Rules and Best Practices:

1. **Keep `enter`/`cd` hooks offline-safe.** They fire on **every** directory change, so a hook that reaches the network taxes each `cd` and hangs the shell when offline.
2. When the command needs no network (staleness checks, nudges, stamps), wrap it: e.g `enter = "MISE_OFFLINE=1 mise run setup:check"`.
   - **Set env on the hook string, not task `env`.** `sh -c` reads `MISE_OFFLINE` before mise starts; a task's `env` is applied *after* resolution — too late to stop the fetch.
3. **Keep hook commands fast and idempotent.** They run on routine events; slow or side-effecting work belongs in a task you invoke explicitly.

## Notes & Gotchas:

- **Adding any hook makes the whole `mise.toml` untrusted** until `mise trust` (see SKILL.md "Always applies"). Fresh clones and CI need the trust step or a `trusted_config_paths` entry.
- **Hooks are no longer experimental**: You don't need to enable experiments for hooks.

## Docs:

- [hooks](https://mise.jdx.dev/hooks.html)
