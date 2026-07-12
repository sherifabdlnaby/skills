# CI repo hygiene

Repo-level settings and upkeep that keep the pipelines honest. Distinct from the per-workflow hardening
in [SKILL.md's `## Always`](../SKILL.md#always): these live in the repo's settings and support files,
not inside the workflow YAML. GitHub mechanics named; the concepts port to any forge.

## Rules and Best Practices:

1. **Protect the default branch with the checks you built.** A ruleset (or branch protection) requiring
   a PR + the check and test jobs to pass.
2. Protect main branch, only allow modification via PRs.
3. **Required checks are wired by job name; keep names stable.** Renaming a workflow or job orphans the
   required check.
4. **Pins need an updater.** SHA-pinned actions don't move; without upkeep, pinning trades supply-chain
   risk for CVE rot. Wire  Dependabot to bump the pinned SHAs (both keep the `# vX.Y.Z`
   comment in sync), or run `pinact` in the scheduled sweep.
5. **Gate publish jobs behind an environment when a human should approve.** A protected environment
   (required reviewers) on the job that pushes and signs never on the check jobs, which must stay
   frictionless.
6. **CODEOWNERS routes review to the pipeline's owners.** Cover the paths that can change what CI runs
   (`.github/`, the task runner config); pair with required review in the ruleset so a workflow edit
   always gets a second pair of eyes.
7. Enable Auto Delete on Merge.

## Notes & Gotchas:

- **Scheduled workflows auto-disable after 60 days without repo activity** (public GitHub repos) — the
  `schedule` sweep silently stops. An update bot's PRs (rule 4) usually keep the repo active; still
  check after quiet periods.
- **Rulesets over classic branch protection**: they layer, apply across branches by pattern, and
  export/import as JSON — so the protection itself can be reviewed and restored, not just remembered.
