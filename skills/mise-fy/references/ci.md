# CI

Guidance on running Mise-managed tools and tasks in CI. These rules are platform-agnostic: they hold on GitHub, GitLab, or anywhere else.

Platform-specific setup lives under [`ci/`](ci/):

- **GitHub Actions** -> [`ci/github.md`](ci/github.md)

## Rules and Best Practices:

1. **Drive work through `mise run <task>` or `mise x` for consistent results**,
   even when the tools are already on `PATH` via shims. It guarantees the
   pinned versions and mise's `[env]`, which bare-command shims don't fully
   carry, and avoids the prompt-hook activation that's spotty in CI (see
   [Getting tools on PATH](#getting-tools-on-path)).
2. **Run the same tasks as locally** (`mise run check`, `mise run test`), don't re-encode commands in YAML (see [`tasks.md`](tasks.md)). When local, the pre-commit hook, and CI all call one task,
   behavior can't drift.
3. Pin tool versions, commit `mise.lock`, and set `MISE_LOCKED=1` for the whole job, so no install drifts off the lockfile or rewrites it (see [`tools.md`](tools.md)). `--locked` on the install
   step alone misses lazy and task tools, which `mise run` installs later without it.
4. Set a CI token (e.g. `GITHUB_TOKEN`) so tool installs don't hit provider API rate limits. Locally the same is achieved via `[settings] github.gh_cli_tokens`/`github.use_git_credentials` (see
   SKILL.md "Always applies").

## Notes & Gotchas:

- **Color is off in CI by default.** Set `CLICOLOR_FORCE: "1"` / `FORCE_COLOR: "1"` to keep linter output readable in the logs.
- **No mise in the image?** Prefer the official integration (e.g. GitHub Action); otherwise commit an install script (`mise generate install-script`). See
  [Installing mise in CI](#installing-mise-in-ci).
- **`mise.lock` is per-platform.** Installs keep the platforms the file already
  lists and never add one, so a runner on an unlisted platform (e.g. a lockfile
  scoped with `lockfile_platforms`, then a new arm64 runner) fails `--locked` with
  `No lockfile URL found for <tool>@<ver> on platform linux-arm64`, even though it
  works on your Mac. Add the platform with `mise lock --platform <os-arch>,…` (or
  extend `lockfile_platforms`), commit the lockfile, and re-run `mise lock`
  whenever you add or bump a tool.

## Installing mise in CI

**Prefer the platform's official integration** (e.g. `jdx/mise-action` on GitHub). It installs mise, pins the version, caches, and puts tools on `PATH` for you, so the steps below are already handled.
Pin the action to a commit SHA **and** pin its mise `version:` input (why: [`ci/github.md`](ci/github.md)).

**No integration / custom image: commit an install script**, don't hand-roll curl + verify:

```bash
mise generate install-script -V <version> -w ./bin/mise   # commit the result
```

CI (and contributors without mise) then call `./bin/mise install --locked`, `./bin/mise run check`, … — the script downloads the pinned version on first use, verifies it, and executes it.

The script embeds per-platform SHA256s for the pinned version and verifies the download against them. Bump by regenerating with the new `-V`.

Then add the shims dir to `PATH` as the fallback net (see [Getting tools on PATH](#getting-tools-on-path)).

**Last resort**: `curl https://mise.run | sh` with `MISE_VERSION` pinned — install.sh pins the binary SHA for the version it fetches; never "latest". Provenance on top:
`gh attestation verify <tarball> --repo jdx/mise`, or the GPG-signed `install.sh.sig` (release key `24853EC9F655CE80B48E6C3A8B81C9D17413A06D` on keys.openpgp.org).

## Getting tools on PATH

The mise binary on `PATH` only gives you the `mise` command; the *managed* tools (node, linters) still need one of:

- **`mise x` / `mise run` is the correct path.** Resolve tools at call time; no shims or activation, nothing to break, and you get pinned versions + mise's `[env]`.
- **Shims on `PATH` are a fallback safety net, not the primary mechanism.** Add
  `~/.local/share/mise/shims` (`echo "$HOME/.local/share/mise/shims" >>
  "$GITHUB_PATH"`, or `eval "$(mise activate bash --shims)"`) so that **any
  step or sub-script that forgot (or hasn't yet been updated) to use `mise x`/a
  task still finds the right tool version** instead of failing or silently
  grabbing a system one. It's belt-and-suspenders: keep driving real work
  through `mise run`, and let shims catch the bare `node`/`npm` calls you
  missed. Caveat: shims expose tools but **not** mise's `[env]` vars to them,
  and the `cd`/`enter`/`watch_files` hooks don't fire, which is exactly why
  shims are the backstop and `mise run` is the rule.
- **`mise activate` (avoid in CI).** Prompt-hook activation (`eval "$(mise activate bash)"`) rebuilds `PATH`/env before each prompt; CI steps are fresh non-interactive shells with no prompt loop, so
  it fires unreliably.

## Verifying the mise install

Two independent layers

**1. The mise binary** — covered by [Installing mise in CI](#installing-mise-in-ci)
(install script: embedded checksums; `mise-action`: the release's signed
packslip, see [`ci/github.md`](ci/github.md)). Only a hand-rolled install
verifies manually: against the release's `SHASUMS256.txt` (GPG `.asc` /
minisign `.minisig`) or `gh attestation verify <tarball> --repo jdx/mise`;
hashes are per-platform — grep the asset for *this* runner's os/arch.

**2. The tools mise installs** are handled by the lockfile, not the steps above.
With `lockfile = true` + `mise install --locked`, mise re-verifies each tool's
checksum **and** provenance (cosign, SLSA, minisign, GitHub attestations; all on
by default, each with a `MISE_AQUA_*` toggle) on every install, aborting
on mismatch. A tool already installed is not re-checked, which is what decides
[what to cache](#caching). This is the main reason to commit `mise.lock` and pass `--locked`
(see [`tools.md`](tools.md)). Pre-populate every CI platform with `mise lock
--platform linux-x64,…` (see the per-platform gotcha above).

## Caching

Cache mise's **downloads**, not its installed tools. mise keeps every download in
`$MISE_CACHE_DIR/downloads-cas` (default `~/.cache/mise/downloads-cas`), stored by content hash.
With `--locked`, a cached download is used only when its hash matches `mise.lock`, so a poisoned
cache is downloaded again. A cached data dir (`$MISE_DATA_DIR`) holds installed tools, and those run as-is.

- **`jdx/mise-action`**: its `cache: true` caches the data dir. Set `cache: false` and cache `downloads-cas` in a step before it; see [`ci/github.md`](ci/github.md).
- **Generic CI**: key on the lockfile so a tool bump writes a new entry.

  ```yaml
  # path: ~/.cache/mise/downloads-cas
  # key:  mise-cas-${{ hashFiles('mise.lock') }}
  ```

  GitLab example (set `MISE_CACHE_DIR` inside the project so it's cacheable):

  ```yaml
  variables:
    MISE_CACHE_DIR: $CI_PROJECT_DIR/.mise-cache
  cache:
    key:
      files: [mise.lock]
      prefix: mise-cas-
    paths: [.mise-cache/downloads-cas]
  ```

## Docs:

- [continuous-integration](https://mise.jdx.dev/continuous-integration.html)
