# Vendored skills

Skills other people wrote, copied in by `mise run skills:sync` from the sources pinned in
[`skills-lock.json`](../../skills-lock.json). Nothing here is edited or written up by us — each
skill's own `SKILL.md` is its documentation.

<p>
  <img src="https://img.shields.io/badge/All%20SKILL.md-26%2C072%20tokens-2f80ed?style=flat-square" alt="All SKILL.md: 26,072 tokens" />
  <img src="https://img.shields.io/badge/All%20Markdown-44%2C057%20tokens-2ea44f?style=flat-square" alt="All Markdown: 44,057 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; the total adds every
other Markdown file an agent can go on to read. Scripts, assets and config ship with a skill but are run rather
than read, so they are left out.

| Skill                                                             | Upstream                                                    | SKILL.md |    Total |
| ----------------------------------------------------------------- | ----------------------------------------------------------- | -------: | -------: |
| [`blast-radius`](blast-radius/)                                   | [cursor/plugins](https://github.com/cursor/plugins)         |    `890` |    `890` |
| [`codebase-design`](codebase-design/)                             | [mattpocock/skills](https://github.com/mattpocock/skills)   |  `1,349` |  `2,495` |
| [`correct`](correct/)                                             | [cursor/plugins](https://github.com/cursor/plugins)         |    `544` |    `544` |
| [`diagnosing-bugs`](diagnosing-bugs/)                             | [mattpocock/skills](https://github.com/mattpocock/skills)   |  `2,034` |  `2,034` |
| [`domain-modeling`](domain-modeling/)                             | [mattpocock/skills](https://github.com/mattpocock/skills)   |    `781` |  `1,939` |
| [`gh-stack`](gh-stack/)                                           | [github/gh-stack](https://github.com/github/gh-stack)       |  `2,282` |  `8,014` |
| [`handoff`](handoff/)                                             | [mattpocock/skills](https://github.com/mattpocock/skills)   |    `198` |    `198` |
| [`humanizer`](humanizer/)                                         | [blader/humanizer](https://github.com/blader/humanizer)     |  `7,383` | `10,407` |
| [`i-have-adhd`](i-have-adhd/)                                     | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) |  `1,743` |  `1,743` |
| [`improve-codebase-architecture`](improve-codebase-architecture/) | [mattpocock/skills](https://github.com/mattpocock/skills)   |  `1,354` |  `2,950` |
| [`in-your-own-words`](in-your-own-words/)                         | [cursor/plugins](https://github.com/cursor/plugins)         |     `72` |     `72` |
| [`ketchup`](ketchup/)                                             | [cursor/plugins](https://github.com/cursor/plugins)         |  `1,445` |  `1,445` |
| [`prototype`](prototype/)                                         | [mattpocock/skills](https://github.com/mattpocock/skills)   |    `642` |  `3,546` |
| [`show-me`](show-me/)                                             | [humanlayer/skills](https://github.com/humanlayer/skills)   |    `783` |    `783` |
| [`teach`](teach/)                                                 | [mattpocock/skills](https://github.com/mattpocock/skills)   |  `1,997` |  `3,855` |
| [`wait-what`](wait-what/)                                         | [mattpocock/skills](https://github.com/mattpocock/skills)   |    `102` |    `102` |
| [`why`](why/)                                                     | [cursor/plugins](https://github.com/cursor/plugins)         |    `124` |    `124` |
| [`writing-for-agents`](writing-for-agents/)                       | [mattpocock/skills](https://github.com/mattpocock/skills)   |  `2,349` |  `2,916` |

### Files

| Skill                           | File                                                                      |  Tokens |
| ------------------------------- | ------------------------------------------------------------------------- | ------: |
| `blast-radius`                  | [`SKILL.md`](blast-radius/SKILL.md)                                       |   `890` |
| `codebase-design`               | [`DEEPENING.md`](codebase-design/DEEPENING.md)                            |   `537` |
| `codebase-design`               | [`DESIGN-IT-TWICE.md`](codebase-design/DESIGN-IT-TWICE.md)                |   `609` |
| `codebase-design`               | [`SKILL.md`](codebase-design/SKILL.md)                                    | `1,349` |
| `correct`                       | [`SKILL.md`](correct/SKILL.md)                                            |   `544` |
| `diagnosing-bugs`               | [`SKILL.md`](diagnosing-bugs/SKILL.md)                                    | `2,034` |
| `domain-modeling`               | [`ADR-FORMAT.md`](domain-modeling/ADR-FORMAT.md)                          |   `618` |
| `domain-modeling`               | [`GLOSSARY-FORMAT.md`](domain-modeling/GLOSSARY-FORMAT.md)                |   `540` |
| `domain-modeling`               | [`SKILL.md`](domain-modeling/SKILL.md)                                    |   `781` |
| `gh-stack`                      | [`SKILL.md`](gh-stack/SKILL.md)                                           | `2,282` |
| `gh-stack`                      | [`references/commands.md`](gh-stack/references/commands.md)               | `2,699` |
| `gh-stack`                      | [`references/stack-design.md`](gh-stack/references/stack-design.md)       |   `946` |
| `gh-stack`                      | [`references/troubleshooting.md`](gh-stack/references/troubleshooting.md) | `2,087` |
| `handoff`                       | [`SKILL.md`](handoff/SKILL.md)                                            |   `198` |
| `humanizer`                     | [`AGENTS.md`](humanizer/AGENTS.md)                                        |   `799` |
| `humanizer`                     | [`CHANGELOG.md`](humanizer/CHANGELOG.md)                                  | `2,225` |
| `humanizer`                     | [`SKILL.md`](humanizer/SKILL.md)                                          | `7,383` |
| `i-have-adhd`                   | [`SKILL.md`](i-have-adhd/SKILL.md)                                        | `1,743` |
| `improve-codebase-architecture` | [`HTML-REPORT.md`](improve-codebase-architecture/HTML-REPORT.md)          | `1,596` |
| `improve-codebase-architecture` | [`SKILL.md`](improve-codebase-architecture/SKILL.md)                      | `1,354` |
| `in-your-own-words`             | [`SKILL.md`](in-your-own-words/SKILL.md)                                  |    `72` |
| `ketchup`                       | [`SKILL.md`](ketchup/SKILL.md)                                            | `1,445` |
| `prototype`                     | [`LOGIC.md`](prototype/LOGIC.md)                                          | `1,329` |
| `prototype`                     | [`SKILL.md`](prototype/SKILL.md)                                          |   `642` |
| `prototype`                     | [`UI.md`](prototype/UI.md)                                                | `1,575` |
| `show-me`                       | [`SKILL.md`](show-me/SKILL.md)                                            |   `783` |
| `teach`                         | [`GLOSSARY-FORMAT.md`](teach/GLOSSARY-FORMAT.md)                          |   `484` |
| `teach`                         | [`LEARNING-RECORD-FORMAT.md`](teach/LEARNING-RECORD-FORMAT.md)            |   `588` |
| `teach`                         | [`MISSION-FORMAT.md`](teach/MISSION-FORMAT.md)                            |   `349` |
| `teach`                         | [`RESOURCES-FORMAT.md`](teach/RESOURCES-FORMAT.md)                        |   `437` |
| `teach`                         | [`SKILL.md`](teach/SKILL.md)                                              | `1,997` |
| `wait-what`                     | [`SKILL.md`](wait-what/SKILL.md)                                          |   `102` |
| `why`                           | [`SKILL.md`](why/SKILL.md)                                                |   `124` |
| `writing-for-agents`            | [`SKILL-MECHANICS.md`](writing-for-agents/SKILL-MECHANICS.md)             |   `567` |
| `writing-for-agents`            | [`SKILL.md`](writing-for-agents/SKILL.md)                                 | `2,349` |
