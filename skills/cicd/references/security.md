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
2. **Dependabot is the one bot: alerts, security updates, version updates.** Enable alerts + security
   updates (auto-PRs fixing vulnerable deps), and configure version updates in `.github/dependabot.yml`
   per ecosystem including `github-actions` — one config covers dep bumps and action-pin upkeep
   ([`hygiene.md`](hygiene.md)). (Renovate is the alternative when its grouping rules or regex managers
   are needed.)
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
