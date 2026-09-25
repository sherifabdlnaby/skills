# Dev Tools / Runtimes

Guidance on Installing Tools and Runtimes via Mise.

## Rules and Best Practices:

1. **Default to pure mise**: add tools to `mise.toml` `[tools]` via `mise use`
   (core/aqua). Don't author `.tool-versions`, idiomatic files
   (`.nvmrc`/`.python-version`), or asdf/vfox plugins; those are last-resort and
   should only be used if pre-existing and you're not already moving away from
   them.
2. **Pin by version policy**, never floating:
   - Tool is **`>=1.0`** → pin at **major** (e.g. `node = "24"`); tracks patches/minors within that major.
   - Tool is **`<1.0`** (0.x) → pin at **minor** (e.g. `ruff = "0.15"`); 0.x ships breaking changes on minor bumps, so a bare major (`"0"`) is meaningless.
   - Exceptions the mechanism forces: a runtime whose minor releases break (e.g. python) pins at **minor**; hk pins the full patch (its Pkl URLs need the exact tag, see
     [`hk.md`](hk.md)); a Node package manager follows `packageManager` (see [`runtimes/node.md`](runtimes/node.md)).
3. **Never use `latest`** until the user explicitly asks for it (even with a lockfile present). The lockfile is a safety net, not a license to float.
4. When adding/updating/removing tools, use `mise use` and `mise unuse`, then re-read the mise.toml to confirm it looks as expected, and re-order the added part by the command to match file structure
   (e.g group relevant tools on top of each other)
5. To pin per the version policy: `mise use <tool>@$(mise latest <tool> | cut -d. -f1) --fuzzy` for a `>=1.0` tool (writes the bare major); for a `0.x` tool use `cut -d. -f1,2` to write `0.<minor>`.
6. Use mise's core backends. If you're choosing backends, pick the one with checksums + timestamp support as much as possible.
7. Group relevant tools categories close to each other in the toml when you have >6 tools. Use a code comment as a title for group.
8. If a tool existence in a list is not obvious, add a 3~4 words sentence to give a hint in a code comment on the same line.
9. If the repo doesn't contain `minimum_release_age` always suggest to add it (e.g. `"7d"`, above mise's `24h` default; months are `6mo`, not `6m` — `6m` is minutes and filters nothing; exempt
   fast-moving tools via `minimum_release_age_excludes` if needed). An exact pin already in `mise.lock` installs regardless of the cutoff.
10. If a tool/runtime needed **just for a single task** define it just for the task.
11. Use and enable Lockfile whenever possible, unless the user told you not to. Commit everything `mise lock` writes beside `mise.lock` (e.g. a `locks/` dir of per-tool dependency lockfiles), not
    just the file itself.

## Notes & Gotchas:

- **Lockfile only updates when enabled.** `mise use`/`install` write `mise.lock` only after `[settings] lockfile = true`. Without it, fuzzy versions resolve fresh each install.
- **Lockfile format is versioned.** A `mise.lock` written by a newer mise can be unreadable to an older one (it warns and ignores the lock), so keep `min_version` and CI's pinned mise at or above
  the version that wrote it.
- **Locked tools keep their locked backend.** When the registry moves a short name to a new backend, a tool already in `mise.lock` stays on the old one and mise warns; `mise backends switch` moves it.
- **`mise use` edits the closest config**. It may not be the one you expect in a nested/monorepo tree.
- **A backend spec goes in the KEY, never the value.** `ripgrep = "aqua:BurntSushi/ripgrep"` is a parse error (`invalid tool: invalid prefix: aqua`) that breaks the whole config; write
  `"aqua:BurntSushi/ripgrep" = "15"` (see Syntax Reminder).
- **`prefix:`/fuzzy/`latest` need version listing**. They work on backends that enumerate versions (core, aqua, github/gitlab, cargo, go, npm, pypi) but not on fixed-artifact specifiers (direct URLs,
  git `ref:`).
- **Per-tool options exist** (`os`, `depends`, `install_env`, `postinstall` via the `name = { ... }` table form) reach for them only when you actually need them; plain `name = "version"` is the norm.
- **`.tool-versions` is read hierarchically** like any config (a `~/.tool-versions` applies to everything under `$HOME`); mise's canonical global config is `~/.config/mise/config.toml`.
- **Idiomatic version files are OFF by default.** `.nvmrc`/`.python-version`/`.ruby-version` are ignored until enabled per-tool (`idiomatic_version_file_enable_tools`). If a version "isn't being
  picked up," this is usually why.
- **`mise install` is the eager step.** To keep a *specific* tool out of everyone's install, see [Lazy-install for uncommon tools](#lazy-install-for-uncommon-tools).

## Backends

Backends differ in how much they verify a download. **Not all are safe**; prefer the most-verified one that has the tool.
Verifications are: checksums, attestation, and release timestamp (to support min-release-age)

Safety, high -> low:

- **`packslip`**; the vendor's own release workflow signs a manifest of every artifact (Sigstore, transparency log), and mise pins that signer on first install. Few tools publish one; the registry
  short name picks it when they do, so write the short name, not `packslip:`.
- **`core`**; runtimes built into mise (node/python/go/ruby/...). Use for these. `node = "22"`.
- **`aqua`**; preferred for everything else: checksums + cosign + SLSA + attestations, no plugin code. `aqua:BurntSushi/ripgrep`.
- **`github`/`gitlab`**; release binaries with provenance when not in aqua. (`ubi` is deprecated, use `github`.)
- **`http`**; a direct URL plus a checksum you record yourself (what tool stubs use). Only as safe as the checksum you pin.
- **`cargo`/`npm`/`pypi`/`go`/`gem`**; language ecosystems (`pypi:` is the current name; `pipx:` still works but is a separate tool identity). ⚠️ **No checksums/provenance** and need the runtime
  installed. Use only when the tool ships nowhere else.
- **`vfox`**; plugin system (Lua, cross-platform via mise's built-in interpreter).
  ⚠️ Still runs plugin code, and gives **no automatic checksums** like aqua. mise
  *can* verify attestations (GitHub/cosign/SLSA) **only when a tool plugin opts
  in** (verified at install, recorded to the lockfile); backend plugins get none.
  Above asdf (maintained, optional attestation), below aqua. Use when a tool ships
  only as a plugin.
- **`asdf`**; ⚠️ legacy plugins: arbitrary code, no checksums, often broken on Windows. Last resort.

## Blocked Backends

It's recommended Block unsafe/legacy backends globally with `disable_backends` so a tool is never _silently_ installed through one.
A blocked backend errors instead of falling back, forcing an explicit, verified choice.

```toml
[settings]
disable_backends = ["asdf", "vfox"]   # resolve only via verified backends; drop "vfox" if you need a vfox-only tool
```

## Runtime Integration

Runtimes have extra integration features (package managers, virtualenvs, idiomatic files, dep install). When adding/configuring one of these, **read its file first**; the general rules above still
apply:

- **Node** (corepack vs pinned PM, deps task) -> [`runtimes/node.md`](runtimes/node.md)

Key shared fact: **mise installs the runtime and can create/activate a venv, but it does not install project deps out of the box** (`npm ci`/`uv sync`). That's the cached `deps` task or the
experimental `[deps]` providers, which can auto-install before every `mise run`. Both engines: [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#deps).

## External Services & Daemons (Docker, DBs, clusters)

mise owns **user-space client binaries**, not **system daemons/services**. The line:

- **Client binaries → mise.** Static CLIs install + pin cleanly via a verified
  backend: `docker compose` (`aqua:docker/compose`), `buildx`, `kubectl`,
  `helm`, `psql`, plus Docker-adjacent lint/inspect tools (`hadolint`, `dive`,
  `lazydocker`). These go in `[tools]` per the version policy.
- **Daemons/services/engines → NOT mise.** The Docker **engine** (`dockerd`, needs
  root + a VM on macOS), a running Postgres server, a k8s cluster — these need
  privilege, a system service, or kernel features. mise can't pin or verify them,
  and they're machine/infra-level, not per-project. Leave them out of `[tools]`.
- **The bundled CLI is a gray zone.** The bare `docker` CLI ships with whatever
  engine you installed (Desktop/Colima/OrbStack); a mise-installed one can shadow
  it and drift from the daemon's API. Let the engine provide `docker`; let mise
  own only the *plugins* (`compose`, `buildx`).

**If the project depends on an out-of-scope service, the docs must declare it as
a prerequisite** (see [`docs.md`](docs.md)) — README/AGENTS, not `[tools]`.
Declare it as a `[doctor.checks.<name>]` probe too, so setup fails fast with the fix when the service is
unreachable (see [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#prerequisite-checks)).

## Syntax Reminder

```toml
[tools]
# --- runtimes (core backend) -----------------------------------------------
node = "22"                              # >=1.0 → pin major; tracks patches within it
python = "3.12"                          # exception: minor releases break, pin minor
ruff = "0.15"                            # <1.0 (0.x) → pin minor (0.x breaks on minor)

# --- everything else (aqua preferred) --------------------------------------
ripgrep = "15"                           # registry shorthand (resolves via aqua)
"aqua:sharkdp/fd" = "10"                 # explicit backend as KEY, version as value
"github:koalaman/shellcheck" = "0.11"    # provenance when not in aqua

# --- table form: per-tool options ------------------------------------------
deno = { version = "2" }                                   # plain pin, table form
rust = { version = "1", os = ["linux", "macos"] }          # restrict OS
my-cli = { version = "1", depends = ["node"] }             # install after node
some-tool = { version = "3", install_env = { CC = "clang" } }  # env at install
patched = { version = "1", postinstall = "./fix.sh" }       # run after install


# --- lazy: skipped by `mise install`, installed on first use, still locked ---
terraform = { version = "1", lazy = true }

# --- scope a tool to ONE task: lazy-installed, not seen by `depends` ---
[tasks.build]
tools.rust = "1"
run = "cargo build"


[settings]
lockfile = true                          # write mise.lock (records exact versions + checksums)
minimum_release_age = "7d"               # skip releases newer than 7 days
```

## Lazy-install for uncommon tools

Not every tool belongs in everyone's `mise install` (e.g. devs on a weak connection). A tool only _some_ workflows touch should install **lazily**, on first use. All three mechanisms below stay
pinned and land in `mise.lock`; pick in this order:

1. **Lazy tool: _prefer this_.** `foo = { version = "1", lazy = true }` in `[tools]`. A bare `mise install` skips it; the first call to its command (shell, `mise x`, a task) installs it from
   the lockfile, then runs it. It is on `PATH` like any other tool. Non-registry backends name their commands with `lazy_bins = ["foo"]`.
2. **Task-scoped tool: when exactly one task needs it** and it shouldn't be on anyone's `PATH`. `[tasks.x] tools.foo = "…"`: installed when that task runs, not seen by `depends`.
   - **Don't use it when several tasks need the same tool**; the pin repeats per task and drifts. That's option 1.
3. **Tool stub: an off-registry binary, or a tool run by path outside mise.** A committed `./bin/x` that installs-and-runs **one** pinned tool on first run.
   - Append ./bin/ to PATH using [env] _.path = ["./bin"] (ref: [env.md](env.md))

A tool everyone is expected to use (e.g. every pre-commit linter) is none of these; it's a plain `[tools]` entry.

**Stubs work with any backend, not just http.** The format takes a `tool` field — `tool = "github:cli/cli"`, `"aqua:…"`, `"cargo:…"`, or a core tool like `"python"`, same notation as `[tools]`.

### Notes & Gotchas

- **First use needs the network.** The deferred download lands in a fast-path moment (the first commit, the first task run); keep anything a hook or a routine task calls out of the lazy set.
- **Install everything now** (a laptop before going offline, a CI image, a devcontainer): `mise install --include-lazy --include-task-tools`. Naming a tool (`mise install foo`) also installs it.
- **Stubs lock into the project's `mise.lock`.** `mise generate tool-stub <path> --lock` needs a project config above the stub, records it under `tool-stubs`, and leaves the stub file unpinned
  beyond its `version`; `--locked` installs then verify it like any other tool.

**Stub mechanics:**

- **Generate, don't hand-author http stubs.** Without `--skip-download` mise fetches once to record checksum/size/bin.
- **A bare-`url` stub's only guarantee is the checksum it pins**.
- **Re-running appends platforms**, never overwrites; an existing platform's URL is replaced only if you re-specify that platform.
- **The stub is just a file you run by path** (`./bin/x`), `chmod +x` and committed. It is not on `PATH` by default; add `./bin` via `_.path` (above) or run it by path. ~4ms overhead once cached
  (cache busts when the file changes).

## Docs:

- [dev-tools](https://mise.jdx.dev/dev-tools/)
- [tool-stubs](https://mise.jdx.dev/dev-tools/tool-stubs.html)
- [lockfile](https://mise.jdx.dev/dev-tools/mise-lock.html)
- [tool options](https://mise.jdx.dev/dev-tools/#tool-options)
- [settings](https://mise.jdx.dev/configuration/settings.html)
