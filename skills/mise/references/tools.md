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
- **Tools are lazy by default; `mise install` is the eager step.** To make a *specific* tool lazy and not in everyone's install, scope it to its task or use a tool stub see [Lazy-install for uncommon tools](#lazy-install-for-uncommon-tools).

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

## External Services & Daemons (Docker, DBs, clusters)

mise owns **user-space client binaries**, not **system daemons/services**. The line:

- **Client binaries → mise.** Static CLIs install + pin cleanly via a verified backend: `docker compose` (`aqua:docker/compose`), `buildx`, `kubectl`, `helm`, `psql`, plus Docker-adjacent lint/inspect tools (`hadolint`, `dive`, `lazydocker`). These go in `[tools]` per the version policy.
- **Daemons/services/engines → NOT mise.** The Docker **engine** (`dockerd`, needs root + a VM on macOS), a running Postgres server, a k8s cluster — these need privilege, a system service, or kernel features. mise can't pin or verify them, and they're machine/infra-level, not per-project. Leave them out of `[tools]`.
- **The bundled CLI is a gray zone.** The bare `docker` CLI ships with whatever engine you installed (Desktop/Colima/OrbStack); a mise-installed one can shadow it and drift from the daemon's API. Let the engine provide `docker`; let mise own only the *plugins* (`compose`, `buildx`).

**If the project depends on an out-of-scope service, the docs must declare it as a prerequisite** (see [`docs.md`](docs.md)) — README/AGENTS, not `[tools]`. Optionally add a task that fails fast with a helpful message when the service is unreachable (e.g. `docker info` before `docker compose up`).

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

## Lazy-install for uncommon tools

Not every tool belongs in the shared `[tools]` block that installs it for **everyone** on `mise install` (e.g devs with weak internet connection).
A tool only _some_ workflows touch should be installed **lazily** (only when first used) and **not** for everyone. Two mechanisms; pick in this order:

1. **Task-scoped tool: _prefer this_ when a single task needs the tool.** `[tasks.x] tools.foo = "…"` (rule 10). Installed only when that task runs, never on `mise install`, and not seen by `depends`. The tool stays declared in `mise.toml`, version-pinned like any other.
   - **Don't use it when several tasks need the same tool** as you'd repeat the pin per task and they drift. That's the case for option 2.
2. **Tool stub: use when (1) doesn't fit:** the tool is shared across multiple tasks/`./bin/` scripts or run by path (not from a task), but still shouldn't be in everyone's `mise install`; or it's an off-registry binary with no good `[tools]` home. A committed `./bin/x` that installs-and-runs **one** pinned tool on first run.
   - Append ./bin/ to PATH using [env] _.path = ["./bin"] (ref: [env.md](env.md))

(If the tool _is_ part of the shared toolchain everyone installs and is expected to use then it's neither of these it's a plain `[tools]` entry.

**Stubs work with any backend, not just http.** The format takes a `tool` field — `tool = "github:cli/cli"`, `"aqua:…"`, `"cargo:…"`, or a core tool like `"python"`, same notation as `[tools]`.

### Notes & Gotchas

**Lockfile / reproducibility:**

- **Task-scoped tools are NOT written to `mise.lock`** (as of v2026.6.11) even after the task runs. They're pinned by their `mise.toml` version string but get **no locked exact-version/checksum**. If a lazy tool must be lockfile-reproducible, that's a reason to lift it to top-level `[tools]` (and accept it's then in `mise install`) or make it a `--lock`'d stub instead.
- **Tool stubs don't participate in `mise.lock` at all.** Each stub carries its **own** embedded lock via `mise generate tool-stub … --lock` (exact version + per-platform URLs/checksums baked into the file). So "the repo is locked" via `mise.lock` says nothing about stubs.

**Stub mechanics:**

- **Generate, don't hand-author http stubs.** Without `--skip-download` mise fetches once to record checksum/size/bin.
- **A bare-`url` stub's only guarantee is the checksum it pins**.
- **Re-running appends platforms**, never overwrites; an existing platform's URL is replaced only if you re-specify that platform.
- **The stub is just a file you run by path** (`./bin/x`), `chmod +x` and committed. It is **not** added to `PATH` like `[tools]`. ~4ms overhead once cached (cache busts when the file changes).
-
## Docs:

- [dev-tools](https://mise.jdx.dev/dev-tools/)
- [tool-stubs](https://mise.jdx.dev/dev-tools/tool-stubs.html)
- [lockfile](https://mise.jdx.dev/dev-tools/mise-lock.html)
- [tool options](https://mise.jdx.dev/dev-tools/#tool-options)
- [settings](https://mise.jdx.dev/configuration/settings.html)
