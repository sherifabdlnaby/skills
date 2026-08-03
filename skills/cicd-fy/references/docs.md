# Project Docs (README, AGENTS.md & CONTRIBUTING.md)

A cicd-fy or audit isn't finished until the docs teach a **human** how releases work, an **agent** the
PR flow it must follow, and an **outside contributor** how to land a change. Three surfaces:

- **README.md** -> the human: how a release is cut, how to trust the artifact.
- **AGENTS.md / CLAUDE.md** -> the agent: the release/label concept, and CI it can't discover, the mise -> hk -> ci linkage.
- **CONTRIBUTING.md** -> the outside contributor. Refer to [assets/CONTRIBUTING.md](../assets/CONTRIBUTING.md) for inspiration.
- **Github Releases** -> How to install/download/pull and how to Attest/Verify.

## Rules and Best Practices:

- **Update in place; never generate AGENTS.md/CLAUDE.md or README.md from scratch.** This skill
  contributes *sections* to docs the repo already has, and only modify **its own sections**
- **Link the source of truth instead of restating it.** The release contract lives in the release
  workflow's header, the label roster in the seeded labels, commands in the task runner. Docs point;
  they don't mirror.
- **Task-runner-agnostic.** Say "CI runs the same commands as local"
- **Concise and dense.** One short section per surface; no tour.

## README.md (humans)

- **How a release is cut**, one paragraph: Impact label -> merge -> tag -> publish, all automatic. A
  tiny table of the four `release:*` labels so contributors know what to pick
  ([`hygiene.md`](hygiene.md#label-taxonomy)).
- **The Verify + Install text**, same as the release footer
  ([`publish.md`](publish.md#the-verify--install-footer)).
- **Badges** per the roster and visibility rules ([`hygiene.md`](hygiene.md#badges)).

## AGENTS.md / CLAUDE.md (agents)

Don't mention the structure, or list files these are easily discoverable by humans and agents.
Introduce the concept of labels, how releases are created, how bumps are determined.

## CONTRIBUTING.md (outside contributors)

**Opt-out**: scaffold it by default when landing the release contract (skip only if the user
declines) — it's the file GitHub shows on the new-PR screen, so it carries the Impact-label
instruction. Every section is conditional on the repo actually having the feature; prefer
placeholder links to the repo's source of truth over restating it. Sections
([assets/CONTRIBUTING.md](../assets/CONTRIBUTING.md)):

1. **Setup** — one line linking the README's setup section.
2. **Before you push** — check/test commands; hooks self-install via setup.
3. **Opening a PR** — issue-first for large changes; PR title = the squash commit; the Impact-label
   table + what the preview comment means.
4. **After the merge** — tag/release/publish are automatic; what not to edit.
5. **Reporting** — issues for bugs; SECURITY.md for vulnerabilities (link only if it exists).
6. **Licensing** — the inbound=outbound sentence, linking [LICENSE](hygiene.md#license).

## Audit checklist

- [ ] README: release paragraph + `release:*` label table + Verify/Install text + badges.
- [ ] CONTRIBUTING.md present (or consciously declined); sections match what the repo actually has;
      links point at sources of truth, not copies of them.
- [ ] Docs updated in place — no generated-from-scratch AGENTS.md/CLAUDE.md, repo structure respected.
