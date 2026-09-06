# hk (pre-commit / git hooks)

Guidance on managing git hooks with hk, the mise-native pre-commit tool.

Read [assets/mise.toml](../assets/mise.toml) and [assets/.config/hk.pkl](../assets/.config/hk.pkl)

## Rules and Best Practices:

1. All linters should be managed by mise.
2. Do not install `pkl`; hk bundles a Pkl evaluator (`pklr`), so no separate install is needed
   (exception: the `pkl`/`pkl_format` lint builtins shell out to the `pkl` CLI).
3. **For custom linters/tests, delegate to a mise task.** Avoid putting logic in `hk.pkl` where possible.
4. Pin the version in both `amends`/`import` URLs to the hk in `[tools]`. Bump by editing both URLs; `hk init` only creates a file for a repo without one, and `--force` overwrites the tiers.
5. Always use a linter hk builtin settings.
6. **Steps live in tier mappings named by moment** (`commitGates` / `pushGates`, see `assets/.config/hk.pkl`); hooks only compose tiers. The scaffold
   stubs `pushGates` empty to be filled late if no gates defined.
7. **`check` mounts the union of all tiers** (`steps { ...commitGates; ...pushGates }`) and is the one command CI runs; local hooks mount
   subsets by cost (`pre-commit` = commitGates, `pre-push` = pushGates). Anything outside the union — an inline hook step, an unmounted tier —
   is invisible to CI.
8. Avoid adding linter files to root directory when they can live elsewhere (e.g .config/); to keep using Builtins prefer the linter's config env var, and splice `--config` into the builtin's own
   command where it has none. Then prove the config is read: a config the tool cannot find falls back to defaults and the step stays green, a **vacuous green**, the check that passes
   because it checked nothing. Every wiring below ends with the test that rules one out.

## Notes & Gotchas:

- **`hk check` and `hk fix` are the same command** the subcommand only sets the default mode;
  `-c/--check` and `-f/--fix` flip it (so `hk check --fix` mutates, `hk fix --check` is dry-run).
  `check_first = true` runs check before fix; `{{files}}` expands to matched files.
- **`fix = true` in pre-commit requires `stash = "git"`** to only check staged files.
- **Profiles are runtime opt-in** (`profiles = List("slow")` + `--slow`/`--profile`), for expensive steps within a mounted tier — not a
  substitute for tier membership.
- **Scope flags**: default is **uncommitted changes** (staged + unstaged). `--all` (whole tree), `--pr` (only files changed vs the default
  branch, `= --from-ref DEFAULT_BRANCH --to-ref HEAD`), `--staged` (staged files only, without stashing unstaged changes; conflicts with `--all`).
- **Git 2.54+ uses config-based hooks**: install writes `hook.<name>.command` into git
  config and leaves `.git/hooks/` untouched, so hk coexists with other hook managers;
  older Git falls back to script shims (`--legacy` forces them). Don't hand-edit
  `.git/hooks`. Beware: a forced per-repo install on top of a global one (`--force-local`)
  fires hooks **twice** per event.
- **Drive one `check` task off this**, not two: stay on `hk check` and forward an
  opt-in `--fix`, with no branching on subcommand. That `check` task is the repo's
  standard lint contract (same command CI and the pre-commit hook run); see
  [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md#check-lint).
- **`hk check` needs its own `check` hook**; it does _not_ fall back to `pre-commit` (`Hook 'check' not found`). Deliberately define **no**
  `fix` hook — `hk check --fix` covers write mode.
- **Manage ignores in one place**: define `local commonIgnores = List(...)` and assign
  top-level `exclude = commonIgnores`, which applies to every step (see `assets/.config/hk.pkl`).
  hk already honors `.gitignore` (`walk_ignore = true`), so this list is only for
  _committed_ paths you don't want linted (vendored/generated/snapshots/minified). A
  step's own `exclude` **stacks** (unions) on top of the global one; it does _not_
  replace it (despite the config docs saying "overrides"), so never re-list the common
  ones per step. Use `List(...)`, not a Pkl `Listing` (the field is typed `String |
  List`).
- **Introspect with `hk config dump|get|explain|sources`** (and `hk validate`) when a
  setting behaves unexpectedly; `explain` shows the winning source. Precedence: CLI >
  `HK_*` env > git config > project `hk.pkl` > user config (`~/.config/hk/config.pkl`;
  the old `.hkrc.pkl` is deprecated, removed in hk v2) > defaults;
  `exclude`/`skip_steps`/`skip_hooks` **union** across sources rather than overriding.
- **`hk check --plan --json`** prints the resolved plan without running it; feed it to tooling (e.g. completions: `… --json --no-progress | jq -r '.steps[].name'`).
- **CI "must be already formatted" gate**: `fail_on_fix = true` + `stage = false` makes a fixing hook fail (without staging) when it changes anything, so CI rejects unformatted code.
- **Pin hk to a full `MAJOR.MINOR.PATCH`** in `[tools]` _and_ match it in `hk.pkl`'s `amends`/`import` URLs. A partial pin like `hk = "1.54"` resolves to the git tag `v1.54`, which doesn't exist →
  `404 Not Found` on install. Use `1.54.0`.
- **The `actionlint` builtin needs `shellcheck` pinned.** actionlint shells out to shellcheck to lint workflow `run:` blocks; missing or unpinned, it fails. Add both to `[tools]`.

## Setup & Templates.

Install via mise, setup via postinstall hook in reference mise.toml.
Check the hk.pkl to baseline scaffold.

## Linters

### Defining Linters

hk ships [builtins](https://hk.jdx.dev/builtins.html), ready-made configs for popular linters. Always prefer a builtin over hand-rolled config (they're maintained and pre-tuned), so check the builtins
list first. run `hk builtins` to list all linters builtins (or grep for the one you're looking for).

### Recommended Linters

Beyond Popular Runtime Linters (check that yourself, and take a look at builtins). The following Linters are highly recommended and you should always suggest to the user:

- mise: lint the mise config itself.
- File hygiene: newlines, trailing_whitespace, mixed_line_ending, byte_order_marker, check_added_large_files, check_case_conflict, check_merge_conflict, check_symlinks,
  check_executables_have_shebangs, detect_private_key (cheap, complements betterleaks).
- GitHub Actions: actionlint (lint), zizmor (security), pinact (pin to SHAs; needs a token, see its note).
- Structure: yamllint (structure only, see its note), taplo (TOML lint + format; alt: `tombi`).
- lychee: broken links, anchors included (what keeps progressive disclosure from rotting; see its note).
- Confirm with the user first, each is noisy on a real tree and gets a scaffolded config: betterleaks, typos, rumdl, yamlfmt (notes below).

You can recommend to the user other linters based on the project. Use Builtins list of inspiration.

#### Specific Linters Notes

##### lychee (https://github.com/lycheeverse/lychee)

By default, make lychee check for local .md files, only check for online links after confirming with user. Configure this in `.config/lychee.toml` (wired by splicing `--config` into the builtin —
see the [`.config/` table below](#linter-config-lives-in-config-default); a root `lychee.toml` auto-loads without wiring if the repo keeps a root layout): `offline = true` resolves
local/relative links and skips http(s), which then show as `👻 Excluded` rather than checked. See this repo's `.config/lychee.toml`.

- **Set `include_fragments = "anchor-only"`.** Without it lychee only checks that a link's
  target *file* exists and ignores the `#anchor`, so a link to a renamed or deleted
  heading passes green. Anchored cross-file links are how progressive disclosure
  points into a section (`references/publish.md#the-publish-gate`); when one rots
  silently the agent lands at the top of the page and reads the wrong material.
  No Markdown linter covers this: rumdl's `MD051` resolves anchors only within the
  document it's linting, and `MD057` checks file existence while ignoring the
  fragment — nothing joins the two. Cheap to enable, and it's the check that makes
  lychee worth having over a Markdown linter's link rules.
  **The value is an enum, not a bool.** `include_fragments = true` fails to parse
  and takes the *entire* config file down with it — lychee reports only
  `Error while loading config: Cannot load configuration file`, naming no key, and
  every other setting (`offline`, ...) is lost with it. Use `anchor-only` for
  `#section` links; `full` adds text fragments (`#:~:text=`) that docs repos don't
  use. After enabling, confirm a known-bad anchor actually fails.

- **`exclude_path` entries are regexes matched against the whole path**, not globs or
  literals. So `.mise` also matches `/mise`, and one bad entry can silently drop a whole
  subtree. When that happens lychee prints `No files found for this input source` and
  exits `0` with `✅ 0 OK`, a **vacuous green**. Don't scope
  inputs with `exclude_path`; let hk pass the file list (it already honors `.gitignore`
  + `commonIgnores`). After wiring lychee up, confirm the run reports a non-zero `OK`
  count, otherwise it's checking nothing.

##### rumdl (https://github.com/rvben/rumdl)

Fast markdownlint-compatible Markdown linter **and formatter**. **Confirm with the user
before enabling**: its default rule set turns on the whole markdownlint suite, which is
noisy on prose/docs repos (`MD013` line-length alone flagged ~350 issues in this repo,
pure noise). The builtin shells out to the `rumdl` CLI (add `rumdl` to `[tools]`) and
auto-discovers `.config/rumdl.toml` natively (a root `rumdl.toml`/`.rumdl.toml` also works). `check` reports; the
`pre-commit`/`--fix` path runs `rumdl check --fix` and rewrites files. When enabled,
**scaffold a `.config/rumdl.toml`** so the user has an obvious place to tune
rules. See this repo's `.config/rumdl.toml`.

- **Ask the user whether they want table formatting** (and cell padding); it's a stylistic
  opt-in. That's `MD060` (`table-cell-alignment`, alias `table-format`), and it's **OFF
  by default**. Enabling it isn't enough; pick a style: `[MD060] style = "aligned"`
  pads every cell so columns line up visually (the cell-padding most people mean).
  Other values: `aligned-no-space` (no pad inside the delimiter row), `compact`
  (single-space, normalized), `tight` (no padding at all), `any` (don't enforce). The
  fixer respects `:--`/`--:` alignment markers.
- **Line-length (`MD013`) auto-fix is opt-in.** The rule is report-only until `[MD013] reflow = true`; then `--fix` wraps offenders. The default `reflow-mode` is the safe one most of the times.
  Enable the auto-fix after aligning with user; this can cause a lot of retrospective fixes that user might want to avoid. `200` is a good start.
- **Scope it on prose-heavy/docs repos.** If the user only wants table formatting, set `[global] enable = ["MD055", "MD056", "MD058", "MD060"]` (this **replaces** the default set, so only these run;
  use `extend-enable` to *add* to defaults instead).
- **Drop a stray cache dir** with `[global] cache = false`; otherwise rumdl writes a `.rumdl_cache/` next to the files (hk only lints staged files, so the cache buys little).

##### ruff (https://github.com/astral-sh/ruff)

Python lint (`ruff`) + format (`ruff_format`), native binary, no Python runtime needed.

- **It drops a `.ruff_cache/` in the repo root.** hk hands it a few staged files per run, so the
  cache buys ~nothing and costs a root dir. Turn it off with a step `env { ["RUFF_NO_CACHE"] = "true" }`.
  **The value must be `true`/`false`**: `"1"` is rejected outright (`invalid value '1' for
  '--no-cache'`), and every ruff step then fails.

##### typos (https://github.com/crate-ci/typos)

Spell-checks source. It produces project-specific false positives (jargon, identifiers,
example tokens), so **confirm with the user before enabling**. When enabled, **scaffold
a `.config/typos.toml`** (wired by splicing `--config` into the builtin, see the table below) with commented `extend-exclude`, `extend-words`,
`extend-identifiers`, and `extend-ignore-re` examples so the user has an obvious place
to silence false positives. See this repo's `.config/typos.toml`.

##### yamllint (https://github.com/adrienverge/yamllint)

Runs `yamllint --strict`. Its **error-level** rules are the structural ones you want:
syntax errors, **duplicate keys**, bad indentation/nesting. Its **warning-level**
defaults are cosmetic and noisy (`line-length`, `truthy`, `comments`, `document-start`).
If the user only wants structure/spec validation (not style), scaffold a `.config/yamllint.yml`
(wired via the `YAMLLINT_CONFIG_FILE` step env, see the table below) that disables the cosmetic rules:

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

Secret scanner (gitleaks-compatible). Real codebases hit false positives (example keys,
test fixtures), so **confirm with the user before enabling**. When enabled, **scaffold
a `.config/betterleaks.toml`** with `[extend] useDefault = true` (keep the built-in
rules) plus a fully commented-out `[allowlist]`. See this repo's `.config/betterleaks.toml`.

- **betterleaks never auto-discovers its config, at any path.** A `.betterleaks.toml`
  sitting in the repo root is decorative: scanning with it present is byte-identical to
  scanning with no config at all, a vacuous green for every allowlist entry. Only `BETTERLEAKS_CONFIG` (see the table below) or
  `--config` loads it, so a repo that "has a betterleaks config" has probably been
  scanning on defaults for as long as it's had one. Wire the env var the moment you
  scaffold the file, and prove it: an intentionally malformed config must make the step
  fail loudly.
- **Comment out the whole `[allowlist]` block, not just its entries.** A block whose
  `paths`/`regexes`/`stopwords` are all empty is a hard config error (`[[allowlists]] must
  contain at least one check for: commits, paths, regexes, or stopwords`), so the usual
  "scaffold with everything commented" shape kills the step the first time the config is
  actually read. Uncomment the block and at least one entry together.

##### pinact (https://github.com/suzuki-shunsuke/pinact)

Pins GitHub Actions (and reusable workflows) to commit SHAs. It calls the GitHub API to
resolve a tag to a SHA, so **without a token it hits the anonymous rate limit** and
can't resolve. Pass a token, but don't commit one or set it in a shared `[env]`. pinact
reads `PINACT_GITHUB_TOKEN` (its own var, higher priority) then `GITHUB_TOKEN`.

**Recommended**: prefer `$GITHUB_TOKEN` (CI injects it) and fall back to the dev's `gh`
login locally. hk `env` values are static strings (no command substitution), so the token
can't come from an `env` entry; instead **prepend it to the builtin's own command** so
it stays in sync with the builtin (no restating flags):

```pkl
["pinact"] = (Builtins.pinact) {
  check_diff = "PINACT_GITHUB_TOKEN=\"${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || true)}\" " + Builtins.pinact.check_diff
  fix        = "PINACT_GITHUB_TOKEN=\"${GITHUB_TOKEN:-$(gh auth token 2>/dev/null || true)}\" " + Builtins.pinact.fix
}
```

`gh` missing or not logged in yields an empty token, so pinact runs unauthenticated
(rate-limited) rather than failing the commit; `${GITHUB_TOKEN:-…}` means `gh` is never called
in CI. Needs `gh` on PATH (system or `[tools]`). See `assets/.config/hk.pkl` + `assets/mise.toml`.

**Alternative (no `gh`)**: pinact's OS keyring. Run `pinact token set` once and enable it
with a static `env { ["PINACT_KEYRING_ENABLED"] = "true" }`. The keyring auto-disables
when `GITHUB_TOKEN` is set, so CI still uses its token. This fits the env-route (builtin
command untouched) but requires each dev to store a token in their keychain.

### Linter Config Lives in `.config/` (default)

**When the `.config/` layout applies:**

- **Mise-fy-ing a project**: the default — scaffold `hk.pkl` and every linter config under `.config/` from the start.
- **Adding one linter to an existing repo**: follow the repo's existing layout; don't relocate anything as a side effect.
- **Adding 3+ config-carrying linters at once**: offer the user to consolidate under `.config/` first, then add.
- **Auditing**: 3+ relocatable config files at the root → raise migrating to `.config/` as a non-blocking suggestion.

Wire each tool to read from `.config/` by the cheapest route it supports: **native discovery >
env var > splicing `--config` into the builtin's own command**. Never retype a builtin's command
to add a flag; restating it pins today's flags into your `hk.pkl` and silently drops whatever the
builtin gains on the next hk bump. Splice instead, with `String.replaceAll` on the builtin's own
string (hk's bundled Pkl evaluator has **no `replaceFirst`**, only `replaceAll`):

| Tool            | Route to `.config/`                                                                                                                              |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `rumdl`         | **native**: auto-discovers `.config/rumdl.toml`, no wiring                                                                                       |
| `yamllint`      | step `env { ["YAMLLINT_CONFIG_FILE"] = ".config/yamllint.yml" }` (ignored if a root `.yamllint` exists)                                          |
| `betterleaks`   | step `env { ["BETTERLEAKS_CONFIG"] = ".config/betterleaks.toml" }` (**required** — nothing is auto-discovered, see above)                        |
| `taplo`         | step `env { ["TAPLO_CONFIG"] = ".config/taplo.toml"; ["RUST_LOG"] = "warn" }` (re-add `RUST_LOG`; re-declaring `env` replaces the whole mapping) |
| `typos`         | splice `--config .config/typos.toml` into `fix`/`check_diff` (no env var)                                                                        |
| `lychee`        | splice `--config .config/lychee.toml` into `check` (no env var)                                                                                  |
| `markdown_lint` | splice `--config .config/markdownlint.yaml` into `check`/`fix` (no env var)                                                                      |

```pkl
local linters = new Mapping<String, Step> {
  ["yamllint"]    = (Builtins.yamllint)    { env { ["YAMLLINT_CONFIG_FILE"] = ".config/yamllint.yml" } }
  ["betterleaks"] = (Builtins.betterleaks) { env { ["BETTERLEAKS_CONFIG"]   = ".config/betterleaks.toml" } }
  ["taplo"]       = (Builtins.taplo)       { env { ["TAPLO_CONFIG"] = ".config/taplo.toml"; ["RUST_LOG"] = "warn" } }
  ["lychee"]      = (Builtins.lychee) {
    check = Builtins.lychee.check.replaceAll("lychee ", "lychee --config .config/lychee.toml ")
  }
  // typos' check_diff is a multi-line shell script, so append-at-the-end doesn't work; splice at
  // the binary name and both commands keep whatever flags the builtin carries.
  ["typos"] = (Builtins.typos) {
    check_diff = Builtins.typos.check_diff.replaceAll("typos ", "typos --config .config/typos.toml ")
    fix        = Builtins.typos.fix.replaceAll("typos ", "typos --config .config/typos.toml ")
  }
  // rumdl: nothing — just place the file at .config/rumdl.toml
}
```

**Prove every route after wiring it.** A config that isn't found is a vacuous green: the tool
falls back to defaults and the step still passes. Check each one against a case only the config
changes (an accepted word for `typos`, a cosmetic rule for `yamllint`, `👻 Excluded` counts plus a
non-zero `OK` for `lychee`), or point it at a deliberately broken file and confirm the step fails.

## Docs:

- [hk.jdx.dev](https://hk.jdx.dev)
- [getting started](https://hk.jdx.dev/getting_started.html)
- [configuration](https://hk.jdx.dev/configuration.html)
- [builtins](https://hk.jdx.dev/builtins.html)
- [mise integration](https://hk.jdx.dev/mise_integration.html)
