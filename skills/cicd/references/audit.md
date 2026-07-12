# CI/CD audit

Audit an existing repo's CI/CD against the skill. The local-dev side (tools, tasks, pre-commit hooks)
is the **mise-fy** skill's audit — run that one too when the repo's tooling setup is in scope.

## Procedure

1. **Inventory.** List `.github/workflows/*`, release configs (`.goreleaser.yml`,
   `.github/release-drafter.yml`, `.github/release.yml`), and how releases were actually cut so far
   (`git tag -l 'v*'`, `gh release list`).
2. **Compare** against the checklist; note each miss with the file it lives in.
3. **Plan with the user.** Cheap fixes first (naming, pins, permissions) before structural ones
   (release-model swap). Big-bang vs iterative is their call.
4. **Fix** from [`assets/`](../assets/.github/workflows/) and the runtime pages ([go](go.md) /
   [docker](docker.md) / [packaged](packaged.md)); verify with `actionlint` + `zizmor`, and a
   `workflow_dispatch` dry run where one exists.

## Checklist

The audit isn't done until every box is accounted for (checked, or consciously waived by the user):

### Checks

- [ ] Workflows named by purpose, not `ci.yml`
- [ ] CI runs the same commands as local (`mise run check` / `mise run test`), not YAML-only re-encodings
- [ ] The same checks run as pre-commit hooks (e.g. hk, the hook runner from the mise-fy skill)
- [ ] Checks trigger on PR + a `schedule` sweep + `workflow_dispatch`
- [ ] Failing checks help the author: auto-fix PR and/or a sticky how-to-fix comment (when applicable)

### Hardening

- [ ] Actions SHA-pinned with `# vX.Y.Z` comments; `actionlint` + `zizmor` pass
- [ ] Top-level read-only `permissions`, widened per job only
- [ ] `persist-credentials: false` except jobs that push with the checkout token (justified inline)
- [ ] Concurrency by intent: PR runs cancel superseded, publish runs queue
- [ ] No `${{ }}` interpolation inside `run:` blocks
- [ ] Tokens fed to tool installs / API calls ([github.md](github.md))

### Release

- [ ] Version bump is label-driven (`major`/`minor`/`patch`/`skip-release`); unlabeled PRs gated (fail
      + `patch` fallback on merge) with a sticky bump-preview comment, or another policy consciously chosen
- [ ] Tag + release cut automatically on merge; rapid-merge behavior understood ([github.md](github.md))
- [ ] Notes generated from PRs (no hand-kept `CHANGELOG.md`); category labels actually group the notes
      (`.github/release.yml` or drafter template)
- [ ] RC path exists: manual dispatch, `-rc.N`, `--prerelease`, never `--latest`; stable-after-rc uses
      `--notes-start-tag`
- [ ] Releases immutable: artifacts uploaded/signed before the release goes public

### Artifacts

- [ ] Build/publish uses the runtime's specialized tool (Router page followed)
- [ ] x86-64 + ARM64 shipped; native runners preferred over emulation
- [ ] Every artifact has provenance (+ SBOM where it applies); registry artifacts signed keyless
- [ ] Verification commands documented for consumers
- [ ] Security scan wired (Trivy -> SARIF) where an image exists
- [ ] Rollback path known (Go `retract`, image alias re-point, release+tag delete)
