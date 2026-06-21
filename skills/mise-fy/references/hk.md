# hk (pre-commit / git hooks)

Guidance on managing git hooks with hk, the mise-native pre-commit tool.

Read [assets/mise.toml](../assets/mise.toml) and [assets/hk.pkl](../assets/hk.pkl)

## Rules and Best Practices:

1. All linters should be managed by mise.
2. Do not install `pkl`; hk bundles a Pkl evaluator (`pklr`), so no separate install is needed. Pin the hk version to your installed one via `hk init`; these conventions target hk >= 1.48.
3. **For custom linters/tests, delegate to a mise task.** Avoid putting logic in `hk.pkl` where possible.
4. Pin the `<VER>` in the `amends`/`import` URLs; regenerate with `hk init`, don't hardcode from memory.
5. Always use a linter hk builtin settings.

## Notes & Gotchas:

- **`hk check` and `hk fix` are the same command** the subcommand only sets the default mode; `-c/--check` and `-f/--fix` flip it (so `hk check --fix` mutates, `hk fix --check` is dry-run). `check_first = true` runs check before fix; `{{files}}` expands to matched files.
- **Scope flags**: default is **staged** files. `--all` (whole tree), `--pr` (only files changed vs the default branch, `= --from-ref DEFAULT_BRANCH --to-ref HEAD`;
- **Git 2.54+ uses config-based hooks**: install writes `hook.<name>.command` into git config and leaves `.git/hooks/` untouched, so hk coexists with other hook managers; older Git falls back to script shims (`--legacy` forces them). Don't hand-edit `.git/hooks`. Beware: a forced per-repo install on top of a global one (`--force-local`) fires hooks **twice** per event.
- **Drive one `check` task off this**, not two: stay on `hk check` and forward an opt-in `--fix`, with no branching on subcommand. That `check` task is the repo's standard lint contract (same command CI and the pre-commit hook run); see [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#check-lint).
- **`hk check`/`hk fix` need their own `check`/`fix` hooks**; they do _not_ fall back to `pre-commit` (`Hook 'check' not found`). DRY it: define `local linters: Mapping<String, Step>` once and assign `steps = linters` in both the `check` and `pre-commit` hooks (see `assets/hk.pkl`). Same builtins, both check and fix commands; the hook's `fix` flag picks the mode.
- **Manage ignores in one place**: define `local commonIgnores = List(...)` and assign top-level `exclude = commonIgnores`, which applies to every step (see `assets/hk.pkl`). hk already honors `.gitignore` (`walk_ignore = true`), so this list is only for _committed_ paths you don't want linted (vendored/generated/snapshots/minified). A step's own `exclude` **stacks** (unions) on top of the global one; it does _not_ replace it (despite the config docs saying "overrides"), so never re-list the common ones per step. Use `List(...)`, not a Pkl `Listing` (the field is typed `String | List`).
- **Introspect with `hk config dump|get|explain|sources`** (and `hk validate`) when a setting behaves unexpectedly; `explain` shows the winning source. Precedence: CLI > `HK_*` env > git config (local) > `.hkrc.pkl` (user) > git config (global) > `hk.pkl` > defaults; `exclude`/`skip_steps`/`skip_hooks` **union** across sources rather than overriding.
- **`hk check --plan --json`** prints the resolved plan without running it; feed it to tooling (e.g. completions: `… --json --no-progress | jq -r '.steps[].name'`).
- **CI "must be already formatted" gate**: `fail_on_fix = true` + `stage = false` makes a fixing hook fail (without staging) when it changes anything, so CI rejects unformatted code.
- **Pin hk to a full `MAJOR.MINOR.PATCH`** in `[tools]` _and_ match it in `hk.pkl`'s `amends`/`import` URLs. A partial pin like `hk = "1.48"` resolves to the git tag `v1.48`, which doesn't exist → `404 Not Found` on install. Use `1.48.0`.
- **The `actionlint` builtin needs `shellcheck` pinned.** actionlint shells out to shellcheck to lint workflow `run:` blocks; in not defined, or unpinned, it fails. Add both to `[tools]`.

## Setup & Templates.

Install via mise, setup via postinstall hook in reference mise.toml.
Check the hk.pkl to baseline scaffold.

## Linters

### Defining Linters

hk ships [builtins](https://hk.jdx.dev/builtins.html), ready-made configs for popular linters. Always prefer a builtin over hand-rolled config (they're maintained and pre-tuned), so check the builtins list first.
run `hk builtins` to list all linters builtins (or grep for the one you're looking for).

### Recommended Linters

Beyond Popular Runtime Linters (check that yourself, and take a look at builtins). The following Linters are highly recommended and you should always suggest to the user:

- mise: Lint mise file itself.
- newlines
- trailing_whitespace
- check_added_large_files (block large blobs; default >500KB)
- zizmor (GitHub Actions Security)
- pinact (GitHub Actions pin SHAs; needs a GitHub token, see note below)
- actionlint (GitHub Actions Linter)
- check_executables_have_shebangs
- check_case_conflict
- check_merge_conflict
- check_byte_order_marker
- mixed_line_ending (normalize CRLF/LF)
- check_symlinks (catch broken symlinks)
- detect_private_key (block committed private keys; cheap, complements betterleaks)
- yamllint (validate YAML structure syntax, duplicate keys, nesting; see note below)
- taplo (TOML lint + format; alt impl: `tombi`/`tombi_format`)
- betterleaks (see note below; confirm + scaffold an ignore file)
- typos ( must confirm with user, can generate a ton of false positives, see note below; confirm + scaffold an ignore file)
- lychee: Lint Broken Links. (Important for Agents.md files and to ensure progressive disclsure doesn't break)
- rumdl ( must confirm with user; full ruleset is noisy on prose/docs repos; ask whether they want table formatting, see note below; confirm + scaffold a config): Markdown lint + format (markdownlint-compatible, Rust).
- yamlfmt ( must confirm with user since it usually generate a lot of noise).

You can recommend to the user other linters based on the project. Use Builtins list of inspiration.

#### Specific Linters Notes

##### lychee (https://github.com/lycheeverse/lychee)

By default, make lychee check for local .md files, only check for online links after confirming with user.
Configure this in a `lychee.toml` at the repo root (auto-loaded): `offline = true` resolves local/relative links and skips http(s), which then show as `👻 Excluded` rather than checked. See this repo's `lychee.toml`.

- **`exclude_path` entries are regexes matched against the whole path**, not globs or literals. So `.mise` also matches `/mise`, and one bad entry can silently drop a whole subtree. When that happens lychee prints `No files found for this input source` and exits `0` with `✅ 0 OK`, a **green vacuous pass, not a real check**. Don't scope inputs with `exclude_path`; let hk pass the file list (it already honors `.gitignore` + `commonIgnores`). After wiring lychee up, confirm the run reports a non-zero `OK` count, otherwise it's checking nothing.

##### rumdl (https://github.com/rvben/rumdl)

Fast markdownlint-compatible Markdown linter **and formatter**. **Confirm with the user before enabling**: its default rule set turns on the whole markdownlint suite, which is noisy on prose/docs repos (`MD013` line-length alone flagged ~350 issues in this repo, pure noise). The builtin shells out to the `rumdl` CLI (add `rumdl` to `[tools]`) and auto-loads a `rumdl.toml` (or `.rumdl.toml`) at the repo root. `check` reports; the `pre-commit`/`--fix` path runs `rumdl check --fix` and rewrites files. When enabled, **scaffold a `rumdl.toml`** at the repo root so the user has an obvious place to tune rules. See this repo's `rumdl.toml`.

- **Ask the user whether they want table formatting** (and cell padding); it's a stylistic opt-in. That's `MD060` (`table-cell-alignment`, alias `table-format`), and it's **OFF by default**. Enabling it isn't enough; pick a style: `[MD060] style = "aligned"` pads every cell so columns line up visually (the cell-padding most people mean). Other values: `aligned-no-space` (no pad inside the delimiter row), `compact` (single-space, normalized), `tight` (no padding at all), `any` (don't enforce). The fixer respects `:--`/`--:` alignment markers.
- **Scope it on prose-heavy/docs repos.** If the user only wants table formatting, set `[global] enable = ["MD055", "MD056", "MD058", "MD060"]` (this **replaces** the default set, so only these run; use `extend-enable` to *add* to defaults instead).
- **Drop a stray cache dir** with `[global] cache = false`; otherwise rumdl writes a `.rumdl_cache/` next to the files (hk only lints staged files, so the cache buys little).

##### typos (https://github.com/crate-ci/typos)

Spell-checks source. It produces project-specific false positives (jargon, identifiers, example tokens), so **confirm with the user before enabling**. When enabled, **scaffold a `typos.toml`** at the repo root with commented `extend-exclude`, `extend-words`, `extend-identifiers`, and `extend-ignore-re` examples so the user has an obvious place to silence false positives. See this repo's `typos.toml`.

##### yamllint (https://github.com/adrienverge/yamllint)

Runs `yamllint --strict`. Its **error-level** rules are the structural ones you want: syntax errors, **duplicate keys**, bad indentation/nesting. Its **warning-level** defaults are cosmetic and noisy (`line-length`, `truthy`, `comments`, `document-start`). If the user only wants structure/spec validation (not style), scaffold a `.yamllint` that disables the cosmetic rules:

```yaml
extends: default
rules:
  line-length: disable
  truthy: disable
  comments: disable
  comments-indentation: disable
  document-start: disable
  # keep structural: key-duplicates, indentation, syntax, anchors
```

Note: none of the generic YAML builtins do **JSON-Schema** validation.

##### betterleaks (https://github.com/betterleaks/betterleaks)

Secret scanner (gitleaks-compatible). Real codebases hit false positives (example keys, test fixtures), so **confirm with the user before enabling**. When enabled, **scaffold a `.betterleaks.toml`** at the repo root with `[extend] useDefault = true` (keep the built-in rules) plus a commented `[allowlist]` (`paths`, `regexes`, `stopwords`). See this repo's `.betterleaks.toml`.

##### pinact (https://github.com/suzuki-shunsuke/pinact)

Pins GitHub Actions (and reusable workflows) to commit SHAs. It calls the GitHub API to resolve a tag to a SHA, so **without a token it hits the anonymous rate limit** and can't resolve. Pass a token, but don't commit one or set it in a shared `[env]`. pinact reads `PINACT_GITHUB_TOKEN` (its own var, higher priority) then `GITHUB_TOKEN`.

**Recommended**: prefer `$GITHUB_TOKEN` (CI injects it) and fall back to the dev's `gh` login locally. hk `env` values are static strings (no command substitution), so the token can't come from an `env` entry; instead **prepend it to the builtin's own command** so it stays in sync with the builtin (no restating flags):

```pkl
["pinact"] = (Builtins.pinact) {
  check_diff = "PINACT_GITHUB_TOKEN=\"${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || true)}\" " + Builtins.pinact.check_diff
  fix        = "PINACT_GITHUB_TOKEN=\"${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || true)}\" " + Builtins.pinact.fix
}
```

`gh` missing or not logged in yields an empty token, so pinact runs unauthenticated (rate-limited) rather than failing the commit; `${GITHUB_TOKEN:-…}` means `gh` is never called in CI. Needs `gh` on PATH (system or `[tools]`). See `assets/hk.pkl` + `assets/mise.toml`.

**Alternative (no `gh`)**: pinact's OS keyring. Run `pinact token set` once and enable it with a static `env { ["PINACT_KEYRING_ENABLED"] = "true" }`. The keyring auto-disables when `GITHUB_TOKEN` is set, so CI still uses its token. This fits the env-route (builtin command untouched) but requires each dev to store a token in their keychain.

### Keeping config out of the repo root (optional)

Most builtins need **no config file** (all `check_*`, `newlines`, `trailing_whitespace`, `mixed_line_ending`, `detect_private_key`, `yamlfmt`, `actionlint`, `zizmor`, `pinact`, `mise`). Root dotfiles only appear for the tunable opt-ins (`rumdl`, `typos`, `lychee`, `betterleaks`, `yamllint`, `taplo`).

**Gate: only suggest this when the project will have 3+ linters that carry a config file.** Below that, default to the per-tool root scaffolds in the notes above. A `.config/` dir for one or two files is overkill, and don't mention it. At 3+, offer to consolidate them under a single `.config/` directory.

When adopted, wire each tool to read from `.config/`: **prefer the env-var route (leaves the builtin command untouched); use `--config` override only where no env var exists** (it forces you to reproduce the builtin's other flags, which can drift across hk versions):

| Tool            | Route to `.config/`                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `rumdl`         | **native**: auto-discovers `.config/rumdl.toml`, no wiring                                                                                        |
| `yamllint`      | step `env { ["YAMLLINT_CONFIG_FILE"] = ".config/yamllint.yml" }` (ignored if a root `.yamllint` exists)                                           |
| `betterleaks`   | step `env { ["BETTERLEAKS_CONFIG"] = ".config/betterleaks.toml" }`                                                                                |
| `taplo`         | step `env { ["TAPLO_CONFIG"] = ".config/taplo.toml"; ["RUST_LOG"] = "warn" }` (re-add `RUST_LOG`; re-declaring `env` replaces the whole mapping)  |
| `typos`         | override `fix`/`check_diff` cmd with `--config .config/typos.toml` (no env var)                                                                   |
| `lychee`        | override `check` cmd with `--config .config/lychee.toml` (no env var)                                                                             |
| `markdown_lint` | override `check`/`fix` cmd with `--config .config/markdownlint.yaml` (no env var)                                                                 |

```pkl
local linters = new Mapping<String, Step> {
  ["yamllint"]    = (Builtins.yamllint)    { env { ["YAMLLINT_CONFIG_FILE"] = ".config/yamllint.yml" } }
  ["betterleaks"] = (Builtins.betterleaks) { env { ["BETTERLEAKS_CONFIG"]   = ".config/betterleaks.toml" } }
  ["taplo"]       = (Builtins.taplo)       { env { ["TAPLO_CONFIG"] = ".config/taplo.toml"; ["RUST_LOG"] = "warn" } }
  ["lychee"]      = (Builtins.lychee)      { check = "lychee --no-progress --config .config/lychee.toml {{ files }}" }
  // rumdl: nothing — just place the file at .config/rumdl.toml
}
```

## Docs:

- [hk.jdx.dev](https://hk.jdx.dev)
- [getting started](https://hk.jdx.dev/getting_started.html)
- [configuration](https://hk.jdx.dev/configuration.html)
- [builtins](https://hk.jdx.dev/builtins.html)
- [mise integration](https://hk.jdx.dev/mise_integration.html)
