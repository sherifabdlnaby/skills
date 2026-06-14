# Dev Tools / Runtimes

Guidance on Installing Tools and Runtimes via Mise.

## Rules and Best Practices:

1. **Default to pure mise**: add tools to `mise.toml` `[tools]` via `mise use` (core/aqua). Don't author `.tool-versions`, idiomatic files (`.nvmrc`/`.python-version`), or asdf/vfox plugins, those are legacy should only be used if pre-existing and we're not in the process of moving away from them.
2. Favor pinning at major version. Then prefix pin at minor.
3. Never Pin `latest`, if you're making an exception make sure lockfile exist.
4. When adding/updating/removing tools, use `mise use` and `mise unuse`, then re-read the mise.toml to confirm it look as expected, and re-order the added part by the command to match file structure (e.g group relevant tools on top of each other)
5. To pin the latest major: `mise use <tool>@$(mise latest <tool> | cut -d. -f1) --fuzzy` (auto-installs, writes the bare major, tracks patches within it).
6. Use mise's core backends. If you're choosing backends, pick the one with checksums + timestamp support as much as possible.
7. Group relevant tools categories close to each other in the toml when you have >6 tools. Use a code comment as a title for group.
8. If a tool existence in a list is not obvious, add a 3~4 words sentence to give a hint in a code comment on the same line.
9. If the repo doesn't contain `minimum-release-age` always suggest to add it. 
10. If a tool/runtime needed **just for a single task** define it just for the task.

## Notes & Gotchas:

- **Lockfile only updates when enabled.** `mise use`/`install` write `mise.lock` only after `[settings] lockfile = true`. Without it, fuzzy versions resolve fresh each install.
- **`mise use` edits the closest config**, which may not be the one you expect in a nested/monorepo tree.
- **`prefix:`/fuzzy/`latest` need version listing**, they work on backends that enumerate versions (core, aqua, github/gitlab, cargo, go, npm, pipx) but not on fixed-artifact specifiers (direct URLs, git `ref:`/`branch:`/`rev:`).
- **Per-tool options exist** (`os`, `depends`, `install_env`, `postinstall` via the `name = { ... }` table form) reach for them only when you actually need them; plain `name = "version"` is the norm.

If still can't fix your problems, check [gotchas](gotchas.md), and check the docs references below.

## Backends

Backends differ in how much they verify a download. **Not all are safe**, prefer the most-verified one that has the tool.
Verifications are: checksums, attestation, and release timestamp (to support min-release-age)

Safety, high → low:
- **`core`** — runtimes built into mise (node/python/go/ruby/...). Use for these. `node = "22"`.
- **`aqua`** — preferred for everything else: checksums + cosign + SLSA + attestations, no plugin code. `aqua:BurntSushi/ripgrep`.
- **`github`/`gitlab`** — release binaries with provenance when not in aqua. (`ubi` is deprecated, use `github`.)
- **`cargo`/`npm`/`pipx`/`go`/`gem`** — language ecosystems. ⚠️ **No checksums/provenance** and need the runtime installed. Use only when the tool ships nowhere else.
- **`asdf`/`vfox`** — ⚠️ legacy plugins: arbitrary code, no checksums, often broken on Windows. Last resort (vfox over asdf).

## Syntax Reminder

```toml
[tools]
# --- runtimes (core backend) -----------------------------------------------
node = "22"                              # pin major; tracks patches within it
python = "3.12"                          # prefix-pin at minor
go = "latest"                            # only OK with lockfile present

# --- everything else (aqua preferred) --------------------------------------
ripgrep = "aqua:BurntSushi/ripgrep"      # explicit backend + version "latest"
"aqua:sharkdp/fd" = "10"                 # backend as key, version as value
shellcheck = "github:koalaman/shellcheck"  # provenance when not in aqua

# --- fuzzy / prefix pins ----------------------------------------------------
terraform = "prefix:1.9"                 # newest 1.9.x
deno = { version = "2" }                 # table form, plain pin

# --- table form: per-tool options ------------------------------------------
rust = { version = "1.80", os = ["linux", "macos"] }       # restrict OS
my-cli = { version = "1.2", depends = ["node"] }            # install after node
some-tool = { version = "3", install_env = { CC = "clang" } }  # env at install
patched = { version = "1", postinstall = "./fix.sh" }       # run after install


# --- scope a tool to ONE task (rule 10): lazy-installed, not seen by `depends` ---
[tasks.build]
tools.rust = "1.80"
run = "cargo build"


[settings]
lockfile = true                          # write mise.lock (required for pinning)
min_release_age = "7d"                   # skip releases newer than 7 days (rule 9)
```

## Docs:
- [dev-tools](https://mise.jdx.dev/dev-tools/)
- [lockfile](https://mise.jdx.dev/dev-tools/mise-lock.html)
- [tool options](https://mise.jdx.dev/dev-tools/#tool-options)
- [settings](https://mise.jdx.dev/configuration/settings.html)
    