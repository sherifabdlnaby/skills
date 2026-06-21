# Dev Tools / Runtimes

Guidance on Installing Tools and Runtimes via Mise.

## Rules and Best Practices:

1. **Default to pure mise**: add tools to `mise.toml` `[tools]` via `mise use` (core/aqua). Don't author `.tool-versions`, idiomatic files (`.nvmrc`/`.python-version`), or asdf/vfox plugins; those are last-resort and should only be used if pre-existing and you're not already moving away from them.
2. **Pin by version policy**, never floating:
   - Tool is **`>=1.0`** → pin at **major** (e.g. `node = "24"`); tracks patches/minors within that major.
   - Tool is **`<1.0`** (0.x) → pin at **minor** (e.g. `ruff = "0.15"`); 0.x ships breaking changes on minor bumps, so a bare major (`"0"`) is meaningless.
3. **Never use `latest`** until the user explicitly asks for it (even with a lockfile present). The lockfile is a safety net, not a license to float.
4. When adding/updating/removing tools, use `mise use` and `mise unuse`, then re-read the mise.toml to confirm it look as expected, and re-order the added part by the command to match file structure (e.g group relevant tools on top of each other)
5. To pin per rule 2: `mise use <tool>@$(mise latest <tool> | cut -d. -f1) --fuzzy` for a `>=1.0` tool (writes the bare major); for a `0.x` tool use `cut -d. -f1,2` to write `0.<minor>`.
6. Use mise's core backends. If you're choosing backends, pick the one with checksums + timestamp support as much as possible.
7. Group relevant tools categories close to each other in the toml when you have >6 tools. Use a code comment as a title for group.
8. If a tool existence in a list is not obvious, add a 3~4 words sentence to give a hint in a code comment on the same line.
9. If the repo doesn't contain `minimum_release_age` always suggest to add it.
10. If a tool/runtime needed **just for a single task** define it just for the task.
11. Use and enable Lockfile whenever possible, unless the user told you not to.

## Notes & Gotchas:

- **Lockfile only updates when enabled.** `mise use`/`install` write `mise.lock` only after `[settings] lockfile = true`. Without it, fuzzy versions resolve fresh each install.
- **`mise use` edits the closest config**. It may not be the one you expect in a nested/monorepo tree.
- **`prefix:`/fuzzy/`latest` need version listing**. They work on backends that enumerate versions (core, aqua, github/gitlab, cargo, go, npm, pipx) but not on fixed-artifact specifiers (direct URLs, git `ref:`).
- **Per-tool options exist** (`os`, `depends`, `install_env`, `postinstall` via the `name = { ... }` table form) reach for them only when you actually need them; plain `name = "version"` is the norm.
- **`~/.tool-versions` is not global** (unlike asdf): global config is `~/.config/mise/config.toml`.
- **Idiomatic version files are OFF by default.** `.nvmrc`/`.python-version`/`.ruby-version` are ignored until enabled per-tool (`idiomatic_version_file_enable_tools`). If a version "isn't being picked up," this is usually why.
- **Lockfile is opt-in.** No `mise.lock` is written until `[settings] lockfile = true`. Don't assume reproducibility you didn't enable. For *using* the lockfile in CI (`mise install --locked`) and the per-platform gotcha, see [`ci.md`](ci.md).

## Backends

Backends differ in how much they verify a download. **Not all are safe**; prefer the most-verified one that has the tool.
Verifications are: checksums, attestation, and release timestamp (to support min-release-age)

Safety, high -> low:

- **`core`**; runtimes built into mise (node/python/go/ruby/...). Use for these. `node = "22"`.
- **`aqua`**; preferred for everything else: checksums + cosign + SLSA + attestations, no plugin code. `aqua:BurntSushi/ripgrep`.
- **`github`/`gitlab`**; release binaries with provenance when not in aqua. (`ubi` is deprecated, use `github`.)
- **`cargo`/`npm`/`pipx`/`go`/`gem`**; language ecosystems. ⚠️ **No checksums/provenance** and need the runtime installed. Use only when the tool ships nowhere else.
- **`vfox`**; plugin system (Lua, cross-platform via mise's built-in interpreter). ⚠️ Still runs plugin code, and gives **no automatic checksums** like aqua. mise *can* verify attestations (GitHub/cosign/SLSA) **only when a tool plugin opts in** (verified at install, recorded to the lockfile); backend plugins get none. Above asdf (maintained, optional attestation), below aqua. Use when a tool ships only as a plugin.
- **`asdf`**; ⚠️ legacy plugins: arbitrary code, no checksums, often broken on Windows. Last resort.

## Blocked Backends

It's recommended Block unsafe/legacy backends globally with `disable_backends` so a tool is never _silently_ installed through one.
A blocked backend errors instead of falling back, forcing an explicit, verified choice.

```toml
[settings]
disable_backends = ["asdf", "vfox"]   # resolve only via verified backends; drop "vfox" if you need a vfox-only tool
```

## Runtime Integration

Runtimes have extra integration features (package managers, virtualenvs, idiomatic files, dep install). When adding/configuring one of these, **read its file first**; the general rules above still apply:

- **Node** (corepack vs pinned PM, `npm_shim`, deps task) -> [`runtimes/node.md`](runtimes/node.md)

Key shared fact: **mise installs the runtime and can create/activate a venv, but it does not install project deps** (`npm install`/`uv sync`). Use a `setup` task or a hook; see the runtime file.

## Syntax Reminder

```toml
[tools]
# --- runtimes (core backend) -----------------------------------------------
node = "22"                              # >=1.0 → pin major; tracks patches within it
python = "3.12"                          # prefix-pin at minor
ruff = "0.15"                            # <1.0 (0.x) → pin minor (0.x breaks on minor)

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
minimum_release_age = "7d"               # skip releases newer than 7 days (rule 9)
```

## Docs:

- [dev-tools](https://mise.jdx.dev/dev-tools/)
- [lockfile](https://mise.jdx.dev/dev-tools/mise-lock.html)
- [tool options](https://mise.jdx.dev/dev-tools/#tool-options)
- [settings](https://mise.jdx.dev/configuration/settings.html)
