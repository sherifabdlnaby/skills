# Vendored skills

Skills other people wrote, copied in by `mise run skills:sync` from the sources pinned in
[`skills-lock.json`](../../skills-lock.json). Nothing here is edited or written up by us — each
skill's own `SKILL.md` is its documentation.

<p>
  <img src="https://img.shields.io/badge/All%20SKILL.md-16%2C805%20tokens-2f80ed?style=flat-square" alt="All SKILL.md: 16,805 tokens" />
  <img src="https://img.shields.io/badge/All%20Markdown-30%2C225%20tokens-2ea44f?style=flat-square" alt="All Markdown: 30,225 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| Skill                                                             | Upstream                                                  | SKILL.md |   Total |
| ----------------------------------------------------------------- | --------------------------------------------------------- | -------: | ------: |
| [`domain-modeling`](domain-modeling/)                             | [mattpocock/skills](https://github.com/mattpocock/skills) |    `766` | `1,917` |
| [`gh-stack`](gh-stack/)                                           | [github/gh-stack](https://github.com/github/gh-stack)     |  `2,070` | `6,873` |
| [`handoff`](handoff/)                                             | [mattpocock/skills](https://github.com/mattpocock/skills) |    `182` |   `182` |
| [`humanizer`](humanizer/)                                         | [blader/humanizer](https://github.com/blader/humanizer)   |  `6,633` | `7,174` |
| [`improve-codebase-architecture`](improve-codebase-architecture/) | [mattpocock/skills](https://github.com/mattpocock/skills) |  `1,342` | `2,938` |
| [`prototype`](prototype/)                                         | [mattpocock/skills](https://github.com/mattpocock/skills) |    `642` | `3,546` |
| [`show-me`](show-me/)                                             | [humanlayer/skills](https://github.com/humanlayer/skills) |    `775` |   `775` |
| [`teach`](teach/)                                                 | [mattpocock/skills](https://github.com/mattpocock/skills) |  `1,946` | `3,804` |
| [`wait-what`](wait-what/)                                         | [mattpocock/skills](https://github.com/mattpocock/skills) |    `100` |   `100` |
| [`writing-for-agents`](writing-for-agents/)                       | [mattpocock/skills](https://github.com/mattpocock/skills) |  `2,349` | `2,916` |

### Files

| Skill                           | File                                                                      |  Tokens |
| ------------------------------- | ------------------------------------------------------------------------- | ------: |
| `domain-modeling`               | [`ADR-FORMAT.md`](domain-modeling/ADR-FORMAT.md)                          |   `618` |
| `domain-modeling`               | [`CONTEXT-FORMAT.md`](domain-modeling/CONTEXT-FORMAT.md)                  |   `533` |
| `domain-modeling`               | [`SKILL.md`](domain-modeling/SKILL.md)                                    |   `766` |
| `gh-stack`                      | [`SKILL.md`](gh-stack/SKILL.md)                                           | `2,070` |
| `gh-stack`                      | [`references/commands.md`](gh-stack/references/commands.md)               | `2,242` |
| `gh-stack`                      | [`references/stack-design.md`](gh-stack/references/stack-design.md)       |   `946` |
| `gh-stack`                      | [`references/troubleshooting.md`](gh-stack/references/troubleshooting.md) | `1,615` |
| `handoff`                       | [`SKILL.md`](handoff/SKILL.md)                                            |   `182` |
| `humanizer`                     | [`AGENTS.md`](humanizer/AGENTS.md)                                        |   `541` |
| `humanizer`                     | [`SKILL.md`](humanizer/SKILL.md)                                          | `6,633` |
| `improve-codebase-architecture` | [`HTML-REPORT.md`](improve-codebase-architecture/HTML-REPORT.md)          | `1,596` |
| `improve-codebase-architecture` | [`SKILL.md`](improve-codebase-architecture/SKILL.md)                      | `1,342` |
| `prototype`                     | [`LOGIC.md`](prototype/LOGIC.md)                                          | `1,329` |
| `prototype`                     | [`SKILL.md`](prototype/SKILL.md)                                          |   `642` |
| `prototype`                     | [`UI.md`](prototype/UI.md)                                                | `1,575` |
| `show-me`                       | [`SKILL.md`](show-me/SKILL.md)                                            |   `775` |
| `teach`                         | [`GLOSSARY-FORMAT.md`](teach/GLOSSARY-FORMAT.md)                          |   `484` |
| `teach`                         | [`LEARNING-RECORD-FORMAT.md`](teach/LEARNING-RECORD-FORMAT.md)            |   `588` |
| `teach`                         | [`MISSION-FORMAT.md`](teach/MISSION-FORMAT.md)                            |   `349` |
| `teach`                         | [`RESOURCES-FORMAT.md`](teach/RESOURCES-FORMAT.md)                        |   `437` |
| `teach`                         | [`SKILL.md`](teach/SKILL.md)                                              | `1,946` |
| `wait-what`                     | [`SKILL.md`](wait-what/SKILL.md)                                          |   `100` |
| `writing-for-agents`            | [`SKILL-MECHANICS.md`](writing-for-agents/SKILL-MECHANICS.md)             |   `567` |
| `writing-for-agents`            | [`SKILL.md`](writing-for-agents/SKILL.md)                                 | `2,349` |
