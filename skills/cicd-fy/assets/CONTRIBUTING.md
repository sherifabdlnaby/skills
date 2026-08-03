<!-- Template — adapt per repo (see references/docs.md). Every section is CONDITIONAL: delete what
     the repo doesn't have. Prefer linking the repo's source of truth over restating it; each
     `<link: …>` code span is a fill-in — replace it with a real link. -->
# Contributing

Thanks for pitching in! This page covers what's specific to contributing — project setup and everyday
commands live in the README (`<link: README setup section>`).

## Before you push

- One-time setup: see the README's Development section (`<link: README setup section>`) — the git
  hooks install themselves as part of it.
- Run `<check command>` (auto-fix: `<check command> --fix`) and `<test command>`. CI runs the same
  commands, so a green local run is a green PR.

## Opening a PR

- **Open an issue first** for anything larger than a fix — align before you build.
- **The PR title becomes the squash commit** on the default branch — write it like a changelog line.
- **Add one Impact label** — it decides the version your merge ships:

| Label           | Your merge cuts                |
| :-------------- | :----------------------------- |
| `release:major` | a breaking change — next major |
| `release:minor` | a new capability — next minor  |
| `release:patch` | a fix or chore — next patch    |
| `release:skip`  | no release                     |

  The 🔖 preview comment on your PR shows the exact version a merge would cut; the gate check stays
  red until a label is set.

## After the merge

The tag, release notes, and publish are automatic. Don't edit a changelog or bump a version in any
file — the pipeline stamps the version at build time.

## Reporting

- Bugs & ideas: open an issue (`<link: issue tracker>`).
- Vulnerabilities: report privately via our security policy (`<link: SECURITY.md>`) — never a
  public issue.

## Licensing

By contributing, you agree your contributions are licensed under the project's LICENSE
(`<link: LICENSE>`).
