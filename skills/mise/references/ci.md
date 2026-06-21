# CI

Guidance on running Mise-managed tools and tasks in CI. These rules are platform-agnostic: they hold on GitHub, GitLab, or anywhere else.

Platform-specific setup lives under [`ci/`](ci/):

- **GitHub Actions** -> [`ci/github.md`](ci/github.md)

## Rules and Best Practices:

1. **Drive work through `mise run <task>` or `mise x` for consistent results**, even when the tools are already on `PATH` via shims. It guarantees the pinned versions and mise's `[env]`, which bare-command shims don't fully carry, and avoids the prompt-hook activation that's spotty in CI (see [Getting tools on PATH](#getting-tools-on-path)).
2. **Run the same tasks as locally** (`mise run check`, `mise run test`), don't re-encode commands in YAML (see [`tasks.md`](tasks.md)). When local, the pre-commit hook, and CI all call one task, behavior can't drift.
3. Pin tool versions and commit `mise.lock`; install with `--locked` so CI can't silently drift off the lockfile (see [`tools.md`](tools.md)).
4. Set a CI token (e.g. `GITHUB_TOKEN`) so tool installs don't hit provider API rate limits. Locally the same is achieved via `[settings] github.gh_cli_tokens`/`github.use_git_credentials` (see SKILL.md "Always applies").

## Notes & Gotchas:

- **Color is off in CI by default.** Set `CLICOLOR_FORCE: "1"` / `FORCE_COLOR: "1"` to keep linter output readable in the logs.
- **No mise in the image?** Prefer the official integration (e.g. GitHub Action); otherwise install the binary, pin the version, and verify it. See [Installing mise in CI](#installing-mise-in-ci).
- **`mise.lock` is per-platform, and `mise lock` only locks the platform you run it on.** With `--locked`, CI on `linux-x64` then fails at the mise setup step with `No lockfile URL found for <tool>@<ver> on platform linux-x64`, even though it works on your Mac. Pre-populate every platform CI uses: `mise lock --platform linux-x64,macos-arm64` (add `windows-x64` if relevant), then commit the lockfile. Re-run it whenever you add or bump a tool.

## Installing mise in CI

**Prefer the platform's official integration** (e.g. `jdx/mise-action` on GitHub). It installs mise, pins the version, caches, and puts tools on `PATH` for you, so the steps below are already handled. Pin the *action itself* to a commit SHA.

**No integration / custom image:** install the single static binary yourself, then add the shims dir to `PATH` as a fallback so anything not routed through `mise x`/a task still resolves (see [Getting tools on PATH](#getting-tools-on-path)). When you install manually:

1. **Verify the download** using **GitHub attestation and/or GPG**, whichever is easier in the image you have (attestation needs the `gh` CLI; GPG needs `gpg`). See [Verifying the mise install](#verifying-the-mise-install) for the exact commands.
2. **Pin the version** via `MISE_VERSION`; never install "latest". An unpinned `curl … | sh` makes the build non-reproducible.
3. **Pinning the binary SHA256 is optional, so ask the user.** It's the strongest guarantee (you trust an exact byte-for-byte build, not just the version tag + signature), but you must bump the hash on every mise upgrade, so it adds maintenance. Default to version-pin + verify; add the SHA pin only when the user wants maximum supply-chain assurance.

## Getting tools on PATH

The mise binary on `PATH` only gives you the `mise` command; the *managed* tools (node, linters) still need one of:

- **`mise x` / `mise run` is the correct path.** Resolve tools at call time; no shims or activation, nothing to break, and you get pinned versions + mise's `[env]`. See rule 1.
- **Shims on `PATH` are a fallback safety net, not the primary mechanism.** Add `~/.local/share/mise/shims` (`echo "$HOME/.local/share/mise/shims" >> "$GITHUB_PATH"`, or `eval "$(mise activate bash --shims)"`) so that **any step or sub-script that forgot (or hasn't yet been updated) to use `mise x`/a task still finds the right tool version** instead of failing or silently grabbing a system one. It's belt-and-suspenders: keep driving real work through `mise run`, and let shims catch the bare `node`/`npm` calls you missed. Caveat: shims expose tools but **not** mise's `[env]` vars to them, and the `cd`/`enter`/`watch_files` hooks don't fire, which is exactly why shims are the backstop and `mise run` is the rule.
- **`mise activate` (avoid in CI).** Prompt-hook activation (`eval "$(mise activate bash)"`) rebuilds `PATH`/env before each prompt; CI steps are fresh non-interactive shells with no prompt loop, so it fires unreliably.

## Verifying the mise install

Two independent layers

**1. The mise binary itself** is only your concern when CI installs mise *manually* (no `mise-action`/package image). Each release publishes per-platform checksums and signatures: `SHASUMS256.txt` (+ GPG-signed `SHASUMS256.asc`, minisign `.minisig`) and `install.sh.sig`/`.minisig`. Pick the level you need:

Use the following script as reference, and pick what you want from it. (you don't have to copy all steps)
```bash
# Mise version, if you update this you must update sha's below.
ver=v2026.6.11

# Resolve the right asset for THIS runner — ARM and x86 CI need different binaries.
# uname -m → x64|arm64;  uname -s → linux|macos. (mise also ships *-musl variants.)
case "$(uname -m)" in
  x86_64|amd64)   arch=x64   ;;
  aarch64|arm64)  arch=arm64 ;;
  *) echo "unsupported arch: $(uname -m)" >&2; exit 1 ;;
esac
os=$(uname -s | tr '[:upper:]' '[:lower:]'); [ "$os" = darwin ] && os=macos
asset="mise-$ver-$os-$arch.tar.gz"
base="https://github.com/jdx/mise/releases/download/$ver"

# (a) checksum. install.sh already pins the binary's SHA256 for the version it fetches,
#     so the floor is just to pin the version (don't pipe "latest"). To verify a tarball
#     against mise's published sums (SHASUMS256.txt covers every platform — grep yours):
curl -fsSLO "$base/$asset"
curl -fsSL "$base/SHASUMS256.txt" | grep " $asset\$" | sha256sum -c -
#     Strongest (the optional SHA pin — ask the user): hardcode the expected hash so you
#     trust an exact build, not whatever the published sums say. The hash is PER-ARCH, so
#     pin one per runner arch and bump them on every upgrade:
case "$arch" in
  x64)   sha="<known-sha256-linux-x64>"   ;;
  arm64) sha="<known-sha256-linux-arm64>" ;;
esac
echo "$sha  $asset" | sha256sum -c -

# (b) GPG signature of the install script (mise release key on keys.openpgp.org).
#     install.sh auto-detects the runner's arch, so this path needs no arch handling.
gpg --keyserver hkps://keys.openpgp.org --recv-keys 24853EC9F655CE80B48E6C3A8B81C9D17413A06D
curl -fsSL https://mise.jdx.dev/install.sh.sig | gpg --decrypt > install.sh   # aborts if not signed by the key
sh ./install.sh   # honors MISE_VERSION for a pinned, reproducible install

# (c) GitHub artifact attestation — verify build provenance (SLSA) of the downloaded binary
gh attestation verify "$asset" --repo jdx/mise
```

**2. The tools mise installs** are handled by the lockfile, not the steps above. With `lockfile = true` + `mise install --locked`, mise re-verifies each tool's checksum **and** provenance (cosign / SLSA / minisign / GitHub attestations, all on by default; toggle via `MISE_AQUA_COSIGN`, `MISE_AQUA_SLSA`, `MISE_AQUA_GITHUB_ATTESTATIONS`, `MISE_AQUA_MINISIGN`) on every CI run, aborting on mismatch. This is the main reason to commit `mise.lock` and pass `--locked` (see [`tools.md`](tools.md)). Pre-populate every CI platform with `mise lock --platform linux-x64,…` (see the per-platform gotcha above).

## Caching

Always cache mise's tool installs so CI doesn't re-download every run.

- **`jdx/mise-action`**: caching is on by default (`cache: true`); it keys on a hash of `mise.toml` + `mise.lock`. Nothing to wire up; see [`ci/github.md`](ci/github.md).
- **Generic CI** (no action): cache the data dir where tools land, keyed on the config + lockfile so a tool bump busts the cache:

  ```yaml
  # paths:  ~/.local/share/mise   ($MISE_DATA_DIR — installed tools live here)
  #         ~/.cache/mise         ($MISE_CACHE_DIR — downloads; optional, smaller win)
  # key:    mise-${{ hashFiles('mise.toml', 'mise.lock') }}
  ```

  GitLab example (set `MISE_DATA_DIR` inside the project so it's cacheable):

  ```yaml
  variables:
    MISE_DATA_DIR: $CI_PROJECT_DIR/.mise-data
  cache:
    key:
      files: [mise.toml, mise.lock]
      prefix: mise-
    paths: [.mise-data]
  ```

## Docs:

- [continuous-integration](https://mise.jdx.dev/continuous-integration.html)
