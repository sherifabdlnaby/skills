# Cicd-fy an Existing Project

Guidance on converting a repo's CI/CD to the recommended shape, or auditing one that already is.

## Rules and Best Practices:

1. **Know the target.** The ideal end-state is the [`assets/`](../assets/.github/workflows/) workflows
   plus the topic references ([`checks.md`](checks.md), [`releases.md`](releases.md),
   [`publish.md`](publish.md), the matching [artifact page](artifacts/)). Convert *toward* that picture.
2. **Inventory before editing.** Discover what already builds, tests, releases, and publishes; don't
   assume (list below).
3. **Plan, then convert.** Map each workflow to its target shape and note conflicts before touching
   files. Cheap fixes first (naming, pins, permissions) before structural ones (release-model swap).
   Big-bang vs iterative is the user's call.
4. **A release-model change needs the user.** Moving to label-driven auto-tag changes how every future
   version is cut and what merging an unlabeled PR does — converse until the gate/fallback policy is
   agreed ([`releases.md`](releases.md)).
5. **Don't break the next release.** Keep the old release path working until the new one has cut a
   release (or a dry run proved it), then remove it.
6. Always converse with the user and discuss pros and cons unless directed otherwise.
7. **Copied assets don't reference the skill.** The skill won't always be available to future readers.

## Procedure

### 1. Inventory

- **Workflows.** List the CI config (`.github/workflows/*` or the platform's equivalent); for each: its
  triggers, the commands it actually runs, and whether those match the local tasks.
- **Release configs.** `.goreleaser.yml`, `.github/release-drafter.yml`, `.github/release.yml`,
  changelog files, version fields in manifests.
- **Release history.** How releases were actually cut so far: `git tag -l 'v*'`, `gh release list`, and
  who/what created the recent tags.
- **Artifacts.** What the repo publishes (image, binary, bundle, package), to where, and whether any of
  it is signed or attested today.
- **Repo settings.** Branch protection / rulesets and their required checks, merge method, existing
  labels, CODEOWNERS, update-bot config (Renovate / Dependabot) ([`hygiene.md`](hygiene.md)), and which
  security features are already on (Dependabot, secret/code scanning — [`security.md`](security.md)).
- Local Setup/Validations/Tests in a Makefile, Justfile, or Mise.
- **On another CI system** (Jenkins, CircleCI, …): inventory it the same way, then rebuild on the target
  platform via the greenfield path below — the references translate by concept, not per-platform.

### 2. Plan with the user

Two starting states:

- **Greenfield (no CI).** Lay down checks first ([`checks.md`](checks.md)), then the release contract
  ([`releases.md`](releases.md)) — seeding its labels and protecting the branch as it lands
  ([`hygiene.md`](hygiene.md)) — then the artifact pipeline ([artifact page](artifacts/) +
  [`publish.md`](publish.md)). Each lands as its own PR; checks alone is already a win.
- **Reshape existing CI.** Map each existing workflow to its target (rename, pin, split, or fold),
  decide the release model, and sequence: hardening (pins, permissions, concurrency) -> checks aligned
  with local tasks -> release contract -> publish/sign/attest.

Every project has its shape and requirements. Converse with the user on what to cover and what to not. Give them a list of topics we'll cover (unless told before).

### 3. Convert

Per area, follow the matching reference; copy from [`assets/`](../assets/.github/workflows/) and adapt.
Asset headers that address *you* ("Copy and adapt", `See references/…`, `SKILL.md` pointers) are
skill-facing — strip them from the landed file; keep the contract comments meant for the repo's
future readers.
Converse with the user where a reference says to (unlabeled-PR policy, autolabeler taxonomy, draft vs
auto-tag model).

### 4. Verify

`actionlint` + `zizmor` pass on every workflow; a `workflow_dispatch` dry run where one exists; a
scratch PR exercising the checks and the bump gate/preview; for the release path, an `-rc.N` dispatch
before trusting it with a stable version.

### 5. Document it

Follow [`docs.md`](docs.md): the README release paragraph + label table + Verify/Install text, the
minimal AGENTS.md/CLAUDE.md pointers (updated in place, never generated from scratch), and the
CONTRIBUTING.md scaffold (opt-out — skip only if the user declines).

## Checklist

The cicd-fy (or audit) isn't done until every box is accounted for (checked, or consciously waived by
the user):

### Checks

- [ ] Workflows named by purpose, not `ci.yml`
- [ ] CI runs the same commands as local (`mise run check` / `mise run test`), not YAML-only re-encodings
- [ ] The same checks run as pre-commit hooks.
- [ ] Checks trigger on PR + a `schedule` sweep + `workflow_dispatch`
- [ ] Failing checks help the author: auto-fix PR and/or a sticky how-to-fix comment (when applicable)

### Hardening

- [ ] Actions SHA-pinned with `# vX.Y.Z` comments; `actionlint` + `zizmor` pass
- [ ] Top-level read-only `permissions`, widened per job only
- [ ] `persist-credentials: false` except jobs that push with the checkout token (justified inline)
- [ ] Concurrency by intent: PR runs cancel superseded, publish runs queue
- [ ] No `${{ }}` interpolation inside `run:` blocks
- [ ] Tokens fed to tool installs / API calls ([`platforms/github.md`](platforms/github.md))

### Release

- [ ] Version bump is label-driven (`release:major`/`release:minor`/`release:patch`/`release:skip`); unlabeled PRs gated
      (fail + `release:minor` fallback on merge) with a sticky bump-preview comment, or another policy consciously chosen
- [ ] Tag + release cut automatically on merge; rapid-merge behavior understood
      ([`platforms/github.md`](platforms/github.md#gotchas))
- [ ] Notes generated from PRs (no hand-kept `CHANGELOG.md`); category labels actually group the notes
      (`.github/release.yml` or drafter template)
- [ ] release-drafter categories + autolabeler tailored to the repo's real change types (ci/documentation/dependencies/…)
- [ ] RC path exists: manual dispatch, `-rc.N`, `--prerelease`, never `--latest`; stable-after-rc uses
      `--notes-start-tag`
- [ ] Releases immutable: artifacts uploaded/signed before the release goes public
      ([`publish.md`](publish.md#the-publish-gate))

### Artifacts

- [ ] Build/publish uses the runtime's specialized tool ([artifact page](artifacts/) followed)
- [ ] x86-64 + ARM64 shipped; native runners preferred over emulation
- [ ] Every artifact has provenance (+ SBOM where it applies); registry artifacts signed keyless
- [ ] Release notes append a **Verify + Install** footer, generated by the release job
- [ ] Security scan wired (Trivy -> SARIF) where an image exists
- [ ] Rollback path known (Go `retract`, image alias re-point, release+tag delete)

### Hygiene

- [ ] Default branch protected; check + test jobs required; job names stable (ruleset updated with any rename)
- [ ] Impact + Kind labels seeded per the taxonomy ([`hygiene.md`](hygiene.md#label-taxonomy)) before the first gated PR
- [ ] Action pins have an updater (Renovate / Dependabot / pinact in the sweep)
- [ ] Publish jobs environment-gated where a human approves
- [ ] `timeout-minutes` set on every job; dead workflows pruned
- [ ] Badges checked. And match repo visibility and doesn't state the obvious. ([`hygiene.md`](hygiene.md#badges))
- [ ] LICENSE audited ([`hygiene.md`](hygiene.md#license)): exists, no placeholders, manifests agree,
      ships with the artifact; missing license surfaced to the user, never auto-picked

### Labels

([`hygiene.md`](hygiene.md#label-taxonomy))

- [ ] Consumer rule holds both directions: every seeded label appears in ≥1 consumer config (gate,
      autolabeler, notes config, dependabot.yml, stale config, contribute surfacing), and every
      consumer references only labels that exist
- [ ] Three-file agreement: release-drafter categories ≡ release.yml categories (titles + label sets);
      autolabeler output labels ⊆ notes-category labels
- [ ] No live synonym pairs (`feature`/`enhancement`, `fix`/`bug`, `docs`/`documentation`) unless
      deliberately mapped during adoption
- [ ] Bare `major`/`minor`/`patch` either absent or carrying the "NOT the release" Dep-bump
      descriptions (Dependabot auto-applies them with the dep's bump size); dependabot.yml labels
      both axes (`dependencies` + `release:patch`)
- [ ] Orphan sweep: `gh label list` vs the roster.

### Security

- [ ] Dependabot alerts + security updates on; version updates configured per ecosystem incl.
      `github-actions`, with cooldown + groups.
- [ ] Secret scanning on; push protection offered to the user
- [ ] Code scanning wired (CodeQL default setup; other scanners via SARIF); gates report-only unless
      the user armed them.
- [ ] Dependency review wired report-only ([`security.md`](security.md#dependency-review-action)); license
      policy derived from the repo's own LICENSE; arming offered, not assumed

### Community

- [ ] Stale policy set: PRs marked + closed on a cadence, issues scoped to awaiting-reply states or waived
- [ ] Closed threads lock after months of inactivity
- [ ] Abandoned-branch sweep exists (or consciously skipped); every janitor was landed dry-run first
- [ ] Community files placed per posture ([`community.md`](community.md#community-files))

### Docs

([`docs.md`](docs.md) carries the per-surface checklist)

- [ ] README: In sync with reality; and mentions (or link to) details on how to release/publish, etc
- [ ] AGENTS.md / CLAUDE.md: Agent instructions wired (use progressive disclosure)
- [ ] CONTRIBUTING.md scaffolded (opt-out) with links to sources of truth, or consciously declined
