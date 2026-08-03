# CI checks

The lint / test / validation workflows that gate every PR. These rules are platform-agnostic; the GHA
reference workflows live in [`assets/`](../assets/.github/workflows/), their mechanics and caveats in
[`platforms/github.md`](platforms/github.md#check-workflows).

## Rules and Best Practices:

1. **Same command as local.** The lint workflow runs the project's own check task (`mise run check`), the
   test workflow its test task is thin YAML wrappers, nothing re-encoded. why: when local, the pre-commit
   hook, and CI all call one task, behavior can't drift. You must explain to user why we can't do this to get an exception.
2. **Align with the pre-commit hooks.** Wire the same checks as hooks (the mise-fy skill's hk reference);
   hook and CI differ only in scope: staged files (hook) vs branch diff (PR) vs whole tree (schedule).
3. **Trigger on PR + a `schedule` sweep + `workflow_dispatch`.** Daily for lint, weekly for heavy builds.
   why: the cron catches rot on the default branch (a dep, base image, or pinned action going bad)
   between PRs; manual dispatch is the escape hatch.
4. **Failing checks help the author.** When fixable: an auto-fix PR (bot branch, self-closing) and/or
   one sticky PR comment saying exactly what to run locally (`mise run check --fix --pr`) — never just
   a red X. Surface errors as file/line annotations where the platform supports them
   ([Annotations](platforms/github.md#annotations)).

## Reference workflows

Ship **one** of the two check shapes, not both (mechanics in
[`platforms/github.md`](platforms/github.md#check-workflows)):

- [`check.yml`](../assets/.github/workflows/check.yml) — report-only: fails with an annotation and keeps
  one sticky comment pointing at the exact local fix command, deleted when green. Suits any repo.
- [`check.autofix.yml`](../assets/.github/workflows/check.autofix.yml) — auto-fix PR: pushes fixes to a
  self-closing bot PR; needs write access, no fork support by design.

A test workflow is the same thin shape: checkout -> tools -> `mise run test`. An image's build/test/scan
gate is [`build-test-scan.yml`](../assets/.github/workflows/build-test-scan.yml)
([`artifacts/docker.md`](artifacts/docker.md)).

## Notes & Gotchas:

- **Don't gate on a whole-tree pass until the tree is clean.** An existing repo carries lint debt; run
  the mise-fy skill's retrospective lint pass first, or the first scheduled sweep fails on legacy debt.
- **Fork PRs get a read-only token**, so comment/label steps 403 — detect and skip
  ([`platforms/github.md`](platforms/github.md#gotchas)).
- **Color is off in CI by default.** Set `CLICOLOR_FORCE: "1"` / `FORCE_COLOR: "1"` so linter output
  stays readable in the logs.
- **Required checks are wired by job name; keep names stable.** Renaming a workflow or job orphans the
  required check.
