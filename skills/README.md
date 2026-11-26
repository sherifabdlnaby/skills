# Skills

What each skill costs an agent's context window. The [project README](../README.md) says what each one does.

<p>
  <img src="https://img.shields.io/badge/All%20SKILL.md-41%2C343%20tokens-2f80ed?style=flat-square" alt="All SKILL.md: 41,343 tokens" />
  <img src="https://img.shields.io/badge/All%20Markdown-126%2C130%20tokens-2ea44f?style=flat-square" alt="All Markdown: 126,130 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| Skill                                                       | SKILL.md |    Total |
| ----------------------------------------------------------- | -------: | -------: |
| [`afk`](afk/)                                               |    `228` |    `228` |
| [`ai-disclosure`](ai-disclosure/)                           |  `1,141` |  `1,141` |
| [`ask-me`](ask-me/)                                         |    `437` |    `437` |
| [`cicd-fy`](cicd-fy/)                                       |  `1,542` | `15,981` |
| [`coding`](coding/)                                         |  `2,611` |  `2,611` |
| [`fast-feedback-mode`](fast-feedback-mode/)                 |    `394` |    `394` |
| [`git`](git/)                                               |  `1,846` | `13,456` |
| [`grill-me`](grill-me/)                                     |     `61` |     `61` |
| [`grilling`](grilling/)                                     |    `663` |    `663` |
| [`mise-fy`](mise-fy/)                                       |  `2,525` | `39,790` |
| [`no-comments`](no-comments/)                               |    `266` |    `266` |
| [`no-docs`](no-docs/)                                       |    `212` |    `212` |
| [`review`](review/)                                         |    `325` |    `325` |
| [`skill-fy`](skill-fy/)                                     |  `2,901` |  `6,389` |
| [`variants/afk-careful`](variants/afk-careful/)             |     `89` |     `89` |
| [`variants/afk-soon`](variants/afk-soon/)                   |    `166` |    `166` |
| [`variants/afk-yolo`](variants/afk-yolo/)                   |    `114` |    `114` |
| [`variants/watch-pr`](variants/watch-pr/)                   |    `660` |    `660` |
| [`variants/watch-pr-ci`](variants/watch-pr-ci/)             |    `261` |    `261` |
| [`variants/watch-pr-comments`](variants/watch-pr-comments/) |    `256` |    `256` |
| [`wait-what`](wait-what/)                                   |    `185` |    `185` |
| [`what-happened`](what-happened/)                           |  `1,090` |  `1,090` |
| [`vendor/`](vendor/README.md) (16 skills)                   | `23,370` | `41,355` |

### Files

| Skill                        | File                                                                                               |  Tokens |
| ---------------------------- | -------------------------------------------------------------------------------------------------- | ------: |
| `afk`                        | [`SKILL.md`](afk/SKILL.md)                                                                         |   `228` |
| `ai-disclosure`              | [`SKILL.md`](ai-disclosure/SKILL.md)                                                               | `1,141` |
| `ask-me`                     | [`SKILL.md`](ask-me/SKILL.md)                                                                      |   `437` |
| `cicd-fy`                    | [`SKILL.md`](cicd-fy/SKILL.md)                                                                     | `1,542` |
| `cicd-fy`                    | [`assets/CONTRIBUTING.md`](cicd-fy/assets/CONTRIBUTING.md)                                         |   `454` |
| `cicd-fy`                    | [`references/artifacts/docker.md`](cicd-fy/references/artifacts/docker.md)                         | `1,118` |
| `cicd-fy`                    | [`references/artifacts/go.md`](cicd-fy/references/artifacts/go.md)                                 |   `928` |
| `cicd-fy`                    | [`references/artifacts/packaged.md`](cicd-fy/references/artifacts/packaged.md)                     |   `659` |
| `cicd-fy`                    | [`references/checks.md`](cicd-fy/references/checks.md)                                             |   `709` |
| `cicd-fy`                    | [`references/cicd-fy.md`](cicd-fy/references/cicd-fy.md)                                           | `2,418` |
| `cicd-fy`                    | [`references/community.md`](cicd-fy/references/community.md)                                       | `1,088` |
| `cicd-fy`                    | [`references/docs.md`](cicd-fy/references/docs.md)                                                 |   `805` |
| `cicd-fy`                    | [`references/hygiene.md`](cicd-fy/references/hygiene.md)                                           | `1,842` |
| `cicd-fy`                    | [`references/platforms/github.md`](cicd-fy/references/platforms/github.md)                         | `1,664` |
| `cicd-fy`                    | [`references/publish.md`](cicd-fy/references/publish.md)                                           |   `630` |
| `cicd-fy`                    | [`references/releases.md`](cicd-fy/references/releases.md)                                         | `1,310` |
| `cicd-fy`                    | [`references/security.md`](cicd-fy/references/security.md)                                         |   `814` |
| `coding`                     | [`SKILL.md`](coding/SKILL.md)                                                                      | `2,611` |
| `fast-feedback-mode`         | [`SKILL.md`](fast-feedback-mode/SKILL.md)                                                          |   `394` |
| `git`                        | [`SKILL.md`](git/SKILL.md)                                                                         | `1,846` |
| `git`                        | [`references/attach.md`](git/references/attach.md)                                                 |   `546` |
| `git`                        | [`references/branches.md`](git/references/branches.md)                                             | `1,791` |
| `git`                        | [`references/commits.md`](git/references/commits.md)                                               |   `873` |
| `git`                        | [`references/pr-body.md`](git/references/pr-body.md)                                               | `1,876` |
| `git`                        | [`references/pull-requests.md`](git/references/pull-requests.md)                                   | `1,531` |
| `git`                        | [`references/rebase.md`](git/references/rebase.md)                                                 |   `835` |
| `git`                        | [`references/review-responses.md`](git/references/review-responses.md)                             | `1,416` |
| `git`                        | [`references/reviewing.md`](git/references/reviewing.md)                                           |   `229` |
| `git`                        | [`references/watch-flags.md`](git/references/watch-flags.md)                                       |   `666` |
| `git`                        | [`references/watch.md`](git/references/watch.md)                                                   | `1,847` |
| `grill-me`                   | [`SKILL.md`](grill-me/SKILL.md)                                                                    |    `61` |
| `grilling`                   | [`SKILL.md`](grilling/SKILL.md)                                                                    |   `663` |
| `mise-fy`                    | [`SKILL.md`](mise-fy/SKILL.md)                                                                     | `2,525` |
| `mise-fy`                    | [`assets/AGENTS.md`](mise-fy/assets/AGENTS.md)                                                     |   `859` |
| `mise-fy`                    | [`assets/README.md`](mise-fy/assets/README.md)                                                     | `1,185` |
| `mise-fy`                    | [`references/ci/github.md`](mise-fy/references/ci/github.md)                                       | `2,594` |
| `mise-fy`                    | [`references/ci.md`](mise-fy/references/ci.md)                                                     | `2,138` |
| `mise-fy`                    | [`references/dev.md`](mise-fy/references/dev.md)                                                   | `6,026` |
| `mise-fy`                    | [`references/docs.md`](mise-fy/references/docs.md)                                                 | `1,296` |
| `mise-fy`                    | [`references/env.md`](mise-fy/references/env.md)                                                   | `1,486` |
| `mise-fy`                    | [`references/hk.md`](mise-fy/references/hk.md)                                                     | `6,057` |
| `mise-fy`                    | [`references/hooks.md`](mise-fy/references/hooks.md)                                               |   `503` |
| `mise-fy`                    | [`references/install.md`](mise-fy/references/install.md)                                           |   `441` |
| `mise-fy`                    | [`references/mise-fy.md`](mise-fy/references/mise-fy.md)                                           | `2,516` |
| `mise-fy`                    | [`references/reference-setup-and-patterns.md`](mise-fy/references/reference-setup-and-patterns.md) | `2,558` |
| `mise-fy`                    | [`references/runtimes/node.md`](mise-fy/references/runtimes/node.md)                               | `1,462` |
| `mise-fy`                    | [`references/tasks.md`](mise-fy/references/tasks.md)                                               | `3,734` |
| `mise-fy`                    | [`references/tools.md`](mise-fy/references/tools.md)                                               | `4,410` |
| `no-comments`                | [`SKILL.md`](no-comments/SKILL.md)                                                                 |   `266` |
| `no-docs`                    | [`SKILL.md`](no-docs/SKILL.md)                                                                     |   `212` |
| `review`                     | [`SKILL.md`](review/SKILL.md)                                                                      |   `325` |
| `skill-fy`                   | [`SKILL.md`](skill-fy/SKILL.md)                                                                    | `2,901` |
| `skill-fy`                   | [`assets/SKILL-skeleton.md`](skill-fy/assets/SKILL-skeleton.md)                                    |   `369` |
| `skill-fy`                   | [`assets/reference-skeleton.md`](skill-fy/assets/reference-skeleton.md)                            |   `433` |
| `skill-fy`                   | [`references/scaffold.md`](skill-fy/references/scaffold.md)                                        | `1,440` |
| `skill-fy`                   | [`references/skill-fy.md`](skill-fy/references/skill-fy.md)                                        | `1,246` |
| `variants/afk-careful`       | [`SKILL.md`](variants/afk-careful/SKILL.md)                                                        |    `89` |
| `variants/afk-soon`          | [`SKILL.md`](variants/afk-soon/SKILL.md)                                                           |   `166` |
| `variants/afk-yolo`          | [`SKILL.md`](variants/afk-yolo/SKILL.md)                                                           |   `114` |
| `variants/watch-pr`          | [`SKILL.md`](variants/watch-pr/SKILL.md)                                                           |   `660` |
| `variants/watch-pr-ci`       | [`SKILL.md`](variants/watch-pr-ci/SKILL.md)                                                        |   `261` |
| `variants/watch-pr-comments` | [`SKILL.md`](variants/watch-pr-comments/SKILL.md)                                                  |   `256` |
| `wait-what`                  | [`SKILL.md`](wait-what/SKILL.md)                                                                   |   `185` |
| `what-happened`              | [`SKILL.md`](what-happened/SKILL.md)                                                               | `1,090` |
