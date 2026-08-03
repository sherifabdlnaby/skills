# Community control

Scheduled janitors that keep contribution flow healthy on a repo taking outside contributions —
stale PRs and issues, necro-comments on old threads, abandoned branches — plus the
[community files](#community-files) GitHub recognizes. They complement [`hygiene.md`](hygiene.md)
(settings & upkeep);

## Rules and Best Practices:

1. **Land every janitor in dry-run, then arm it.** These workflows close, lock, and delete; ship the
   first version observe-only and discuss with user.
2. **Stale policy: aggressive on PRs, conservative on issues.** PRs rot — conflicts accumulate and the
   code moves under them — so mark stale after ~14–60 days and close a couple of weeks later, with a
   comment saying reopen-when-rebased. Blanket auto-closing *issues* is community-hostile (valid bug
   reports die silently); scope issue-staleness to awaiting-reply states (`needs-more-info`,
   `cannot-reproduce`) or use long horizons. Tool: [`actions/stale`](https://github.com/actions/stale)
   (first-party) on the schedule sweep.
3. **Exempt by label, not by memory.** `no-stale` for what must never
   go stale.
4. The close comment states how to  reopen.
5. Exempt `dependencies` PRs too: Dependabot rebases and supersedes its own PRs, and a
   stale-close makes it stop recreating that update.
4. **Lock closed threads after a quiet period.** Necro-comments on long-closed issues go unseen and
   drag dead context; locking pushes people to open a fresh issue that links back. Tool:
   [`dessant/lock-threads`](https://github.com/dessant/lock-threads) (issues, PRs, discussions). Lock,
   never delete; give the inactivity window months (locking a week-old close reads as a slammed door).
5. **Branch cleanup: the setting first, a sweep second.** Auto-delete-on-merge
   ([`hygiene.md`](hygiene.md)) already handles the main flow. For abandoned branches (no PR, or a
   closed unmerged one), prefer a thin scheduled task over `gh api` — there is no first-party action,
   and a janitor with delete rights is a poor place for a third-party dep.

## Notes & Gotchas:

- **First run on an old repo meets the whole backlog.** `actions/stale` caps mutations per sweep
  (`operations-per-run`) to stay under API rate limits, so an old repo drains over several sweeps —
  expected, don't crank the cap on day one.
- **Janitor comments don't retrigger workflows.** `GITHUB_TOKEN` events don't recurse
  ([`platforms/github.md`](platforms/github.md#gotchas)) — a stale-bot comment won't re-run CI, and the
  janitors can't loop each other.
- **The schedule itself can go stale.** Scheduled workflows auto-disable after 60 days without repo
  activity ([`hygiene.md`](hygiene.md)) — the exact repos quiet enough to need janitors are the ones
  whose janitors stop.
- **Least privilege still applies**: stale + lock need `issues: write` + `pull-requests: write`; only
  the branch sweep needs `contents: write`. Separate jobs, separate grants.

## Community files

The special files GitHub recognizes (from the root, `.github/`, or `docs/`; an org-level `.github`
repo can hold org-wide defaults, which per-repo files override). Suggest each **contextually** — at
the step that makes it relevant:

| File                                     | Posture                                                                                     | Context that makes it relevant                                                                                  |
| :--------------------------------------- | :------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------- |
| `CONTRIBUTING.md`                        | **Opt-out: scaffold by default** ([`docs.md`](docs.md), [asset](../assets/CONTRIBUTING.md)) | the release contract — it carries the Impact-label instruction GitHub shows on the new-PR screen                |
| `SECURITY.md`                            | On human mention                                                                            | the security step — the paperwork half of private vulnerability reporting ([`security.md`](security.md))        |
| `.github/ISSUE_TEMPLATE/` + `config.yml` | On human mention                                                                            | the janitors — issue forms feed the State labels the stale policy reads                                         |
| `PULL_REQUEST_TEMPLATE.md`               | On human mention                                                                            | the release contract — an Impact-label reminder checklist (CONTRIBUTING carries the rule)                       |
| `SUPPORT.md`, `DISCUSSION_TEMPLATE/`     | Only if Discussions is on                                                                   | otherwise they restate "open an issue"                                                                          |
| `FUNDING.yml` (`.github/` only)          | **Explicit user request only — never scaffold unprompted**                                  | personal/monetary; not the agent's call                                                                         |
| `GOVERNANCE.md`, `CITATION.cff`          | Explicit user request only                                                                  | multi-maintainer process / academic citation                                                                    |
