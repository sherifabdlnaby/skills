# Community control

Scheduled janitors that keep contribution flow healthy on a repo taking outside contributions: stale
PRs and issues, necro-comments on old threads, abandoned branches. They complement
[`hygiene.md`](hygiene.md) (settings & upkeep);

## Rules and Best Practices:

1. **Land every janitor in dry-run, then arm it.** These workflows close, lock, and delete; ship the
   first version observe-only and discuss with user.
2. **Stale policy: aggressive on PRs, conservative on issues.** PRs rot — conflicts accumulate and the
   code moves under them — so mark stale after ~14–60 days and close a couple of weeks later, with a
   comment saying reopen-when-rebased. Blanket auto-closing *issues* is community-hostile (valid bug
   reports die silently); scope issue-staleness to awaiting-reply states (`needs-more-info`,
   `cannot-reproduce`) or use long horizons. Tool: [`actions/stale`](https://github.com/actions/stale)
   (first-party) on the schedule sweep.
3. **Exempt by label, not by memory.** `exempt-issue-labels` / `exempt-pr-labels` for what must never
   go stale (`pinned`, `security`, roadmap items); the stale timer already resets on any activity one
   "still relevant" comment keeps a thread alive, which is the point. The close comment states how to
   reopen.
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
