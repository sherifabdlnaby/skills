# Node (runtime integration)

## Pinning the package manager (Corepack-proof setup)

**Goal:** the package manager (pnpm/yarn) runs at one fixed version for everyone, whether or not a contributor has Corepack enabled. Corepack's on/off state is **global to a Node version, not project-scoped**. A project can't force it either way, so the setup must be correct in *both* states. Pinning `node` in mise fixes the *runtime* but not the *PM*: Node bundles only `npm`, and Corepack (when on) shadows bundled yarn/pnpm with its own shims. Three moves, each covering one failure mode:

1. **Pin the PM in mise**: add `pnpm`/`yarn` to `[tools]`. Covers **Corepack off**: without it there is no pnpm/yarn on the machine at all (Node bundles only npm).
2. **Order it *above* `node`** in `[tools]`. Covers **Corepack on**: both mise's real binary and Node's Corepack shim sit on `PATH`, and the dir declared first wins. `mise use` writes tools in call order, so the PM must precede `node/bin` for mise's binary to shadow the shim (not the reverse).
3. **Set `packageManager` in package.json** to that same version. Covers every invocation that resolves through a Corepack shim instead of the mise shell: non-mise contributors, editors, CI steps that call Node directly, or a future tool misordering.

**Invariant: the two pins must name the same version.** If the mise pin and the `packageManager` field diverge, the mise shell runs one and any Corepack-shim path runs the other, re-introducing exactly the nondeterminism this setup removes. If `packageManager` is absent, add it; if it's already present, pin mise to match it (the field is the more portable source of truth, since non-mise users still read it). The lockfile pins *dependency* versions, never the PM. Only `packageManager` does.

## Notes & Gotchas:

### Corepack precedence: the reason `packageManager` is mandatory

Corepack ships **inside** Node (≤ 24; removed from the Node 25+ distribution). When a developer runs `corepack enable`, it installs shim binaries for **`yarn`/`pnpm`** **into the same directory as `corepack` itself**, which, under mise, is the pinned Node's own `bin/` (e.g. `~/.local/share/mise/installs/node/<ver>/bin/`). Those shims **replace the bundled `yarn`/`pnpm`**. (`npm` is *not* shimmed by default: *"the npm shims will not be installed unless explicitly requested"*; that needs `corepack enable npm`.) So once Corepack is enabled it intercepts every yarn/pnpm invocation *unconditionally*. This is not a PATH-ordering race against the bundled PM; the shim physically sits where mise points.

Each shim then decides **which version of the PM to run** by reading the `packageManager` field of the nearest package.json:

- **Field present** (`"pnpm@9.12.0"` / `"yarn@4.5.0"`) → Corepack runs *exactly* that version (downloading it once if needed), and **rejects a mismatched manager** with `This project is configured to use <x> because package.json has a "packageManager" field`. Deterministic.
- **Field absent** → Corepack falls back to its own **baked-in default** and fetches it over the network, *not* the PM bundled with the mise-pinned Node. Observed on Node 24.16.0: with no field, the Corepack `yarn` shim runs **1.22.22** regardless of what mise provides. (Same drift hits `npm` only if you ran `corepack enable npm`: the bundled npm 11.13.0 is replaced by the Corepack default, e.g. 11.17.0.) So the version that actually runs is dictated by Corepack, drifts from what mise provides, varies with the Corepack release, and silently differs between a contributor who has Corepack on and one who doesn't.

**Net:** pinning `node` in mise fixes the *runtime* but not the *package manager*. The `packageManager` field is what pins the PM. Set it so Corepack-on and Corepack-off contributors (and CI) all converge on one version. The lockfile (`package-lock.json` / `pnpm-lock.yaml`) pins *dependency* versions; it does **not** pin the PM. Only `packageManager` does.

### Other

- mise's `node` is a **core backend**. It provides `npm`/`npx`/`corepack` already; don't add `npm` as a separate `[tools]` entry.
- Add `node_modules/.bin` to `[env] _.path` so project bins (`vite`, `vitest`, `tsc`, `eslint`, `biome`) run without `npx`.
- The `[tasks.setup]` below is a sketch. Follow the standard `setup` contract (idempotent, fast, stamped re-run check) in [`reference-setup-and-patterns.md`](../reference-setup-and-patterns.md#setup).

## Syntax

```toml
[tools]
# pnpm/yarn ABOVE node when mise-managed (rule 2); for plain npm, just node.
pnpm = "9"
node = "24"

[env]
_.path = ["node_modules/.bin"]   # run vite/vitest/tsc/eslint without `npx`

# JS deps go in the `deps` task (cached, run after `mise install`) — see reference-setup-and-patterns.md
[tasks.deps]
description = "Install JS deps (cached)"
sources = ["package.json", "package-lock.json"]   # or pnpm-lock.yaml / yarn.lock
outputs = ["node_modules"]
run = "npm ci"                                    # or: pnpm install --frozen-lockfile
```

```jsonc
// package.json — ALWAYS set packageManager (rule 1). Match the pinned runtime.
{
  "packageManager": "npm@11.13.0"   // `mise exec -- npm -v` for the node-bundled npm
}
```

## Docs:

- [mise node](https://mise.jdx.dev/lang/node.html)
- [Corepack](https://nodejs.org/api/corepack.html)
