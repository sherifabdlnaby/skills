# Security

The repo-side security features watching the code and its dependencies: Dependabot (alerts + update
PRs), secret scanning, and code scanning. The concepts (dep vulnerability alerts, automated updates,
leak detection, SAST) port to any forge; the features named are GitHub's. Complements the per-workflow
hardening in [SKILL.md's `## Always`](../SKILL.md#always) and the artifact scan in
[`artifacts/docker.md`](artifacts/docker.md#scan).

## Rules and Best Practices:

1. **Report-only by default; offer the gates to the user.** Scanners report to the Security tab without
   failing PRs. why: findings in existing code must not brick unrelated work. The blocking upgrades —
   push protection, a dependency-review check failing PRs that add a known-vulnerable dep, CodeQL as a
   required check — are worth having: suggest them, let the user consciously arm each.
2. Version and Deps Upkeep:
   2. **Use Dependabot: for alerts, security updates, version updates.** Enable alerts + security
      updates and configure version updates in `.github/dependabot.yml` per ecosystem including `github-actions` itself for action pin upkeep.
   3. Renovate is the alternative to Dependabot when its grouping rules or regex managers
      are needed.
   3. Regardless of tool you use, make it open PR according to Label taxonomy of the repo (so deps PR don't get auto-closed, etc)..
      check ([`hygiene.md`](hygiene.md)).
3. **Cooldown new releases; group the noise.** `cooldown` (days, settable per semver level) waits out
   the compromised-fresh-release window before adopting a version; `groups` collapse related bumps into
   one PR. why: day-zero adoption is how supply-chain attacks spread, and a flood of single-dep PRs
   gets rubber-stamped, not reviewed.
4. **Secret scanning on; push protection is the strongest gate to suggest.** Scanning alerts after a
   leak; push protection blocks the push itself. why: a secret that reaches a commit is burned —
   revoke and rotate, deleting the commit un-leaks nothing — so the push is the only cheap moment to
   stop it. (A core pattern set is push-blocked by default wherever secret scanning is on.)
5. **Code scanning: CodeQL default setup first.** It picks languages, query suite, and triggers on its
   own; move to the advanced workflow only for a custom build, extra query packs, or path excludes.
   Other scanners join the same Security tab via SARIF upload (Trivy —
   [`artifacts/docker.md`](artifacts/docker.md#scan); zizmor has a SARIF mode too).

## Notes & Gotchas:

- **First enable on an existing repo meets the whole backlog**: expect a burst of alerts and
  security-update PRs; triage before enabling any gate.


## Dependency Review Action

[`dependency-review.yml`](../assets/.github/workflows/dependency-review.yml) is an example of action that reviews the dependency
delta a PR introduces and show vulnerabilities and licenses diff against the dependency graph. Helpful to eliminate vulns being added in.
- **Declarative:** Wire using a config-file, make the file set where it's most intuitive (in .config or in .github depending on where the repo has most related config)
- Shipped `warn-only` + `comment-summary-in-pr: on-failure` (need write access); unless user requested otherwise.
- **License policy: `allow-licenses` / `deny-licenses` are mutually exclusive** (SPDX ids). Derive
  the choice from the repo's own LICENSE.
- **Needs the dependency graph**: default-on for public repos; private repos need GitHub Code
  Security.
