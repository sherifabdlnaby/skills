# hk (pre-commit / git hooks)

Guidance on managing git hooks with hk, the mise-native pre-commit tool.

Read [mise.toml][../assets/mise.toml] and [mise.toml][../assets/hk.pkl]

## Rules and Best Practices:

1. All linters should be managed by mise.
2. Do not install `pkl`, and use hk version > v1.48 that include built in pkl support.
3. **Make `--mise` the default** with `HK_MISE=1` in `mise.toml`'s `[env]`, so every hk invocation (hooks and manual) runs in mise's environment without passing `--mise`.
4. \*\*For custom linters/tests delegate to a mise task. Do not add logic in hk.pkl as much as possible.
5. Pin the `<VER>` in the `amends`/`import` URLs; regenerate with `hk init`, don't hardcode from memory.

## Notes & Gotchas:

- **`hk check` and `hk fix` are the same command** the subcommand only sets the default mode; `-c/--check` and `-f/--fix` flip it (so `hk check --fix` mutates, `hk fix --check` is dry-run). `check_first = true` runs check before fix; `{{files}}` expands to matched files.
- **Scope flags**: default is **staged** files. `--all` (whole tree), `--pr` (only files changed vs the default branch — `= --from-ref DEFAULT_BRANCH --to-ref HEAD`;
- **Git 2.54+ uses config-based hooks** — install writes `hook.<name>.command` into git config and leaves `.git/hooks/` untouched, so hk coexists with other hook managers; older Git falls back to script shims (`--legacy` forces them). Don't hand-edit `.git/hooks`. Beware: a forced per-repo install on top of a global one (`--force-local`) fires hooks **twice** per event.
- **Drive one `check` task off this**, not two: stay on `hk check` and forward an opt-in `--fix` — no branching on subcommand. See the `check` task in [`reference-setup-and-patterns.md`](reference-setup-and-patterns.md).
- **`hk check`/`hk fix` need their own `check`/`fix` hooks** — they do _not_ fall back to `pre-commit` (`Hook 'check' not found`). DRY it: define `local linters: Mapping<String, Step>` once and assign `steps = linters` in both the `check` and `pre-commit` hooks (see `assets/hk.pkl`). Same builtins, both check and fix commands; the hook's `fix` flag picks the mode.
- **Manage ignores in one place**: define `local commonIgnores = List(...)` and assign top-level `exclude = commonIgnores` — it applies to every step (see `assets/hk.pkl`). hk already honors `.gitignore` (`walk_ignore = true`), so this list is only for _committed_ paths you don't want linted (vendored/generated/snapshots/minified). A step's own `exclude` **stacks** (unions) on top of the global one — it does _not_ replace it (despite the config docs saying "overrides"), so never re-list the common ones per step. Use `List(...)`, not a Pkl `Listing` (the field is typed `String | List`).
- **Introspect with `hk config dump|get|explain|sources`** (and `hk validate`) when a setting behaves unexpectedly — `explain` shows the winning source. Precedence: CLI > `HK_*` env > git config (local) > `.hkrc.pkl` (user) > git config (global) > `hk.pkl` > defaults; `exclude`/`skip_steps`/`skip_hooks` **union** across sources rather than overriding.
- **`hk check --plan --json`** prints the resolved plan without running it; feed it to tooling (e.g. completions: `… --json --no-progress | jq -r '.steps[].name'`).
- **CI "must be already formatted" gate**: `fail_on_fix = true` + `stage = false` makes a fixing hook fail (without staging) when it changes anything, so CI rejects unformatted code.
- **Pin hk to a full `MAJOR.MINOR.PATCH`** in `[tools]` _and_ match it in `hk.pkl`'s `amends`/`import` URLs. A partial pin like `hk = "1.48"` resolves to the git tag `v1.48`, which doesn't exist → `404 Not Found` on install. Use `1.48.0`.
- **A builtin that wraps a CLI needs that CLI in `[tools]`.** Builtins for external tools (lychee, ruff, actionlint, zizmor, pinact, betterleaks, …) shell out, so a missing tool fails the run (mise prints a `mise use …` hint). Builtins bundled into hk (newlines, the `check_*` family, pkl/pkl_format on v1.48+) need nothing extra.
- **Builtins get renamed/deprecated across hk releases** — e.g. `check_byte_order_marker` → `byte_order_marker`. Pkl prints a deprecation warning on `mise install`/`hk` runs; heed it (and re-run `hk init` against your pinned version rather than copying names from memory).

## Setup & Templates.

Install via mise, setup via postinstall hook in reference mise.toml.
Check the hk.pkl to baseline scaffold.

## Linters

### Defining Linters

hk comes with [builtins](https://hk.jdx.dev/builtins.html) Configurations for popular Linters. ALWAYS CHECK AND USE BUILTIN before trying to set you custom logic.

### Recommended Linters

Beyond Popular Runtime Linters (check that yourself, and take a look at builtins). The following Linters are recommended:

- mise: Lint mise file itself.
- newlines
- trailing_whitespace
- check_added_large_files (block large blobs; default >500KB)
- zizmor (Github Actions Security)
- pinact (Github Actions pin SHAs)
- actionlint (Github Action Linter)
- check_executables_have_shebangs
- check_case_conflict
- check_merge_conflict
- check_byte_order_marker
- betterleaks (see note below — confirm + scaffold an ignore file)
- typos ( must confirm with user, can generate a ton of false positives, see note below — confirm + scaffold an ignore file)
- lychee: Lint Broken Links
- pkl + pkl_format: when the repo has `.pkl` files (e.g. `hk.pkl`). These shell out to the `pkl` CLI, so add `pkl` to `[tools]`. hk's bundled pkl only parses its own config (`hk.pkl`); it does **not** back these linter builtins, so without the tool they fail with `No version is set for shim: pkl`.

You can recommend to the user other linters based on the project. Use Builtins list of inspiration.

#### Specific Linters Notes

##### lychee (https://github.com/lycheeverse/lychee)

By default, make lychee check for local .md files, only check for online links after confirming with user.
Configure this in a `lychee.toml` at the repo root (auto-loaded): `offline = true` resolves local/relative links and skips http(s), which then show as `👻 Excluded` rather than checked. See this repo's `lychee.toml`.

- **`exclude_path` entries are regexes matched against the whole path**, not globs or literals. So `.mise` also matches `/mise`, and one bad entry can silently drop a whole subtree. When that happens lychee prints `No files found for this input source` and exits `0` with `✅ 0 OK` — a **green vacuous pass, not a real check**. Don't scope inputs with `exclude_path`; let hk pass the file list (it already honors `.gitignore` + `commonIgnores`). After wiring lychee up, confirm the run reports a non-zero `OK` count, otherwise it's checking nothing.

##### typos (https://github.com/crate-ci/typos)

Spell-checks source. It produces project-specific false positives (jargon, identifiers, example tokens), so **confirm with the user before enabling**. When enabled, **scaffold a `typos.toml`** at the repo root with commented `extend-exclude` / `extend-words` / `extend-identifiers` / `extend-ignore-re` examples so the user has an obvious place to silence false positives. See this repo's `typos.toml`.

##### betterleaks (https://github.com/betterleaks/betterleaks)

Secret scanner (gitleaks-compatible). Real codebases hit false positives (example keys, test fixtures), so **confirm with the user before enabling**. When enabled, **scaffold a `.betterleaks.toml`** at the repo root with `[extend] useDefault = true` (keep the built-in rules) plus a commented `[allowlist]` (`paths` / `regexes` / `stopwords`). See this repo's `.betterleaks.toml`.

## Docs:

- [hk.jdx.dev](https://hk.jdx.dev)
- [getting started](https://hk.jdx.dev/getting_started.html)
- [configuration](https://hk.jdx.dev/configuration.html)
- [builtins](https://hk.jdx.dev/builtins.html)
- [mise integration](https://hk.jdx.dev/mise_integration.html)
