# Improve Codebase Architecture

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-1%2C342%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 1,342 tokens" />
  <img src="https://img.shields.io/badge/Total-2%2C972%20tokens-2ea44f?style=flat-square" alt="Total: 2,972 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                                       | Tokens |
| ------------------------------------------ | -----: |
| [`HTML-REPORT.md`](HTML-REPORT.md)         |  1,596 |
| [`SKILL.md`](SKILL.md)                     |  1,342 |
| [`agents/openai.yaml`](agents/openai.yaml) |     34 |

<!-- token-estimates:end -->

[Read the canonical skill instructions.](SKILL.md)

Architecture problems often appear as friction: understanding one concept requires many files, tests miss the real integration points, or a module exposes almost as much complexity as it contains. This skill finds focused opportunities to move that complexity behind deeper modules.

The review starts with the area you name, or uses recent change history to find active parts of the codebase. It reads the project's domain model and architectural decisions, explores the selected code, and produces a visual HTML report in the system temporary directory. Each candidate includes the affected files, the source of friction, a before-and-after diagram, likely testing gains, and a recommendation strength. After you choose a candidate, a guided interview works through constraints, seams, interfaces, and surviving tests before implementation begins.

This is an exploration tool, not an automatic refactor. Its first report intentionally proposes no interfaces. The workflow requires the companion `codebase-design` skill, which this repository does
not currently vendor, plus grilling and domain-modeling skills. It favors changes that are likely to pay off in active code, so quiet areas may receive less attention. The report also loads Tailwind
and Mermaid from CDNs.

```text
/improve-codebase-architecture Focus on the order intake path.
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
