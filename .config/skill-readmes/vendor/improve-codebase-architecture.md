# Improve Codebase Architecture

[Read the canonical skill instructions.](../../../skills/vendor/improve-codebase-architecture/SKILL.md)

Architecture problems often appear as friction: understanding one concept requires many files, tests miss the real integration points, or a module exposes almost as much complexity as it contains. This skill finds focused opportunities to move that complexity behind deeper modules.

The review starts with the area you name, or uses recent change history to find active parts of the codebase. It reads the project's domain model and architectural decisions, explores the selected code, and produces a visual HTML report in the system temporary directory. Each candidate includes the affected files, the source of friction, a before-and-after diagram, likely testing gains, and a recommendation strength. After you choose a candidate, a guided interview works through constraints, seams, interfaces, and surviving tests before implementation begins.

This is an exploration tool, not an automatic refactor. Its first report intentionally proposes no interfaces. The workflow requires the companion `codebase-design` skill, which this repository does
not currently vendor, plus grilling and domain-modeling skills. It favors changes that are likely to pay off in active code, so quiet areas may receive less attention. The report also loads Tailwind
and Mermaid from CDNs.

```text
/improve-codebase-architecture Focus on the order intake path.
```

Vendored from [Matt Pocock's skills repository](https://github.com/mattpocock/skills).
