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
   risk for CVE rot. Wire Dependabot to bump the pinned SHAs (it keeps the `# vX.Y.Z` comment in
   sync — [`security.md`](security.md)), or run `pinact` in the scheduled sweep.
5. **Gate publish jobs behind an environment when a human should approve.** A protected environment
   (required reviewers) on the job that pushes and signs never on the check jobs, which must stay
   frictionless.
6. **CODEOWNERS routes review to the pipeline's owners.** Cover the paths that can change what CI runs
   (`.github/`, the task runner config); pair with required review in the ruleset so a workflow edit
   always gets a second pair of eyes.
7. Enable Auto Delete on Merge.
8. Add a Auto-Close PR Rule and Auto Clean Branches that are merged or too old. Check [community](community.md) for details.

## Notes & Gotchas:


## Label taxonomy

A Repo label taxonomy has to be intuitive and have no overlapping meaning, or ambiguous meanings.
An example of ambiguity: a label that just says `major` can be ambiguous; does it mean this is a major release ?
or did dependabot bump major version of dependency (that doesn't necessarily mean it causes a major version).

Below is a recommended label taxonomy; use if the repo doesn't have an established pattern already.

| Axis                                          | Label               | Color    | Example description                         | Consumers                                                       |
| :-------------------------------------------- | :------------------ | :------- | :------------------------------------------ | :-------------------------------------------------------------- |
| Impact — what does merging do to the release? | `release:major`     | `b60205` | Merge cuts a major release (breaking)       | bump gate + release job; keys 💥 Breaking Changes in notes      |
|                                               | `release:minor`     | `0e8a16` | Merge cuts a minor release (new capability) | bump gate + release job                                         |
|                                               | `release:patch`     | `1d76db` | Merge cuts a patch release (fix/chore)      | bump gate + release job; dependabot.yml                         |
|                                               | `release:skip`      | `fbca04` | Merge cuts no release                       | release job (cut nothing)                                       |
| Dep bump — how big was the dep's own bump?    | `major`             | `0366d6` | Dependency major bump — NOT the release     | Dependabot auto-labeling; triage                                |
|                                               | `minor`             | `0366d6` | Dependency minor bump — NOT the release     | Dependabot auto-labeling; triage                                |
|                                               | `patch`             | `0366d6` | Dependency patch bump — NOT the release     | Dependabot auto-labeling; triage                                |
| Kind — what sort of change?                   | `security`          | `d93f0b` | Security fix or hardening                   | notes category; stale-exempt                                    |
|                                               | `enhancement`*      | `a2eeef` | New feature or request                      | autolabeler; notes category                                     |
|                                               | `bug`*              | `d73a4a` | Something isn't working                     | autolabeler; notes category; issue forms                        |
|                                               | `dependencies`      | `0366d6` | Dependency update                           | dependabot.yml; autolabeler; notes category; stale-exempt (PRs) |
|                                               | `ci`                | `cfd3d7` | CI, build, or workflow change               | autolabeler; notes category                                     |
|                                               | `documentation`*    | `0075ca` | Improvements or additions to documentation  | autolabeler; notes category                                     |
| State — where is this issue in triage?        | `needs-more-info`   | `d876e3` | Awaiting reporter's reply; may go stale     | stale scope; issue forms                                        |
|                                               | `no-stale`          | `0052cc` | Never auto-closed by the stale janitor      | stale-exempt                                                    |
| Invitation — can outsiders pick it up?        | `good first issue`* | `7057ff` | Good for newcomers                          | GitHub contribute surfacing                                     |
|                                               | `help wanted`*      | `008672` | Extra attention is needed                   | GitHub contribute surfacing                                     |

`*` = a GitHub default label, adopted as-is (exists on every fresh repo; keep its color and
description). Create the rest.

- **Impact is prefixed `release:*` on purpose.** Dependabot auto-applies labels literally named
  `major`/`minor`/`patch` AND not configurable.
- **`dependencies` + `release:patch` go in dependabot.yml** (`labels:` per ecosystem — a custom list
  *replaces* Dependabot's defaults, so `dependencies` must be re-listed). A human relabels the rare
  dep bump that changes the project's own API.
- **`security` and `dependencies` are also stale-exempt**: a security thread must never auto-close;
  Dependabot manages its own PR lifecycle ([`community.md`](community.md)).
- **Janitor marker labels (`Stale` by default) are consumer-owned**: don't seed them, don't flag
  them as orphans.

## Badges

Badges answer a visitor's first questions: does it build, do tests pass, how covered, is it safe to
depend on.
- Avoid adding badges that say nothing (e.g. `PRs welcome`, a hand-flipped `maintained`)
- Avoid stating the obvious... GitHub's UI already shows it next to the README (language, stars, license).

Recommended set for **public** repos:

- **CI / checks** — the check workflow's `badge.svg`; keyed to the workflow *filename*, a rename breaks it.
- **Tests** — the test workflow's `badge.svg` (skip when checks + tests are one workflow).
- **Coverage** — Codecov / Coveralls; ships together with the upload step, never before.
- **Version** — registry-native where the artifact lives (npm, pkg.go.dev, image tag); else latest
  GitHub release.
- **Supported runtimes** — the manifest via the registry (`pypi/pyversions`, `engines`, `go.mod`).
- **Vulns / scan** — the scheduled security-scan workflow's `badge.svg`; or the user's scanner if
  they run one.

**Private repos**: only GitHub's own workflow badges work — they respect repo permissions. shields.io
and external services can't read a private repo; their badges render broken or need a token embedded
in the README. Set = the CI / tests / scan workflow badges, full stop.

## LICENSE

Audit the project's LICENSE:
- **Manifests agree**: the manifest's license field (`package.json`, `pyproject.toml`, crate, ...)
  carries the same SPDX id as the LICENSE file.
- **Ships with the artifact**: the LICENSE lands in the published tarball / bundle / image.
- **Coarse compatibility flag only**: a strong-copyleft dep inside a permissive project gets
  *flagged* for a human.
- **Missing entirely** -> surface prominently and let the user pick; **never auto-pick a license**
  (a legal commitment).

Relevant: the pipeline can audit dependencies' licenses ([`security.md`](security.md#dependency-review-action)).
