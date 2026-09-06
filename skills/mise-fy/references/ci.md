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
3. Pin tool versions and commit `mise.lock`; install with `--locked` so CI can't silently drift off the lockfile (see [`tools.md`](tools.md)).
4. Set a CI token (e.g. `GITHUB_TOKEN`) so tool installs don't hit provider API rate limits. Locally the same is achieved via `[settings] github.gh_cli_tokens`/`github.use_git_credentials` (see
   SKILL.md "Always applies").

## Notes & Gotchas:

- **Color is off in CI by default.** Set `CLICOLOR_FORCE: "1"` / `FORCE_COLOR: "1"` to keep linter output readable in the logs.
- **No mise in the image?** Prefer the official integration (e.g. GitHub Action); otherwise commit a bootstrap script (`mise generate bootstrap`). See [Installing mise in CI](#installing-mise-in-ci).
- **`mise.lock` is per-platform.** `mise install` records only the platform it
  ran on, so a lockfile grown that way plus `--locked` fails CI on `linux-x64`
  with `No lockfile URL found for <tool>@<ver> on platform linux-x64`, even
  though it works on your Mac. Run `mise lock` (resolves all 7 default platforms
  without installing; scope with `--platform linux-x64,macos-arm64`, or persist
  the set via the `lockfile_platforms` setting), commit the lockfile, and
  re-run it whenever you add or bump a tool.

## Installing mise in CI

**Prefer the platform's official integration** (e.g. `jdx/mise-action` on GitHub). It installs mise, pins the version, caches, and puts tools on `PATH` for you, so the steps below are already handled.
Pin the action to a commit SHA **and** pin its mise `version:` input (why: [`ci/github.md`](ci/github.md)).

**No integration / custom image: commit a bootstrap script**, don't hand-roll curl + verify:

```bash
mise generate bootstrap -V <version> -w ./bin/mise   # commit the result
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
(bootstrap script: embedded checksums; `mise-action`: minisign-verified release
checksums, see [`ci/github.md`](ci/github.md)). Only a hand-rolled install
verifies manually: against the release's `SHASUMS256.txt` (GPG `.asc` /
minisign `.minisig`) or `gh attestation verify <tarball> --repo jdx/mise`;
hashes are per-platform — grep the asset for *this* runner's os/arch.

**2. The tools mise installs** are handled by the lockfile, not the steps above.
With `lockfile = true` + `mise install --locked`, mise re-verifies each tool's
checksum **and** provenance (cosign, SLSA, minisign, GitHub attestations; all on
by default, each with a `MISE_AQUA_*` toggle) on every CI run, aborting
on mismatch. This is the main reason to commit `mise.lock` and pass `--locked`
(see [`tools.md`](tools.md)). Pre-populate every CI platform with `mise lock
--platform linux-x64,…` (see the per-platform gotcha above).

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
