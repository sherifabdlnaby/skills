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
Converse with the user where a reference says to (unlabeled-PR policy, autolabeler taxonomy, draft vs
auto-tag model).

### 4. Verify

`actionlint` + `zizmor` pass on every workflow; a `workflow_dispatch` dry run where one exists; a
scratch PR exercising the checks and the bump gate/preview; for the release path, an `-rc.N` dispatch
before trusting it with a stable version.

### 5. Document it

The conversion isn't done until the README (or the repo's docs) says how a release is cut (label -> merge -> tag) and carries
the same Verify + Install text as the release footer. Also Update AGENTS.md or CLAUDE.md to give distilled hints for Agents to know how to extend.
([`publish.md`](publish.md#the-verify--install-footer)).

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

- [ ] Version bump is label-driven (`major`/`minor`/`patch`/`skip-release`); unlabeled PRs gated (fail
      + `minor` fallback on merge) with a sticky bump-preview comment, or another policy consciously chosen
- [ ] Tag + release cut automatically on merge; rapid-merge behavior understood
      ([`platforms/github.md`](platforms/github.md#gotchas))
- [ ] Notes generated from PRs (no hand-kept `CHANGELOG.md`); category labels actually group the notes
      (`.github/release.yml` or drafter template)
- [ ] release-drafter categories + autolabeler tailored to the repo's real change types (ci/docs/deps/…)
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
- [ ] Bump + category labels seeded before the first gated PR
- [ ] Action pins have an updater (Renovate / Dependabot / pinact in the sweep)
- [ ] Publish jobs environment-gated where a human approves
- [ ] `timeout-minutes` set on every job; dead workflows pruned; badges wired

### Security

- [ ] Dependabot alerts + security updates on; version updates configured per ecosystem incl.
      `github-actions`, with cooldown + groups.
- [ ] Secret scanning on; push protection offered to the user
- [ ] Code scanning wired (CodeQL default setup; other scanners via SARIF); gates report-only unless
      the user armed them.

### Community

- [ ] Stale policy set: PRs marked + closed on a cadence, issues scoped to awaiting-reply states or waived
- [ ] Closed threads lock after months of inactivity
- [ ] Abandoned-branch sweep exists (or consciously skipped); every janitor was landed dry-run first

### Docs

- [ ] README says how a release is cut and carries the Verify + Install text. As well as release labels.
- [ ] AGENTS.md or CLAUDE.md are updated as well.
