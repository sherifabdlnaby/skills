# grilling

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-578%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 578 tokens" />
  <img src="https://img.shields.io/badge/Total-578%20tokens-2ea44f?style=flat-square" alt="Total: 578 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    578 |

<!-- token-estimates:end -->

`grilling` turns an unclear plan, design, decision, or idea into a shared, explicit understanding through a rigorous interview. See [`SKILL.md`](SKILL.md) for the canonical agent instructions.

## How It Works

The interview maps decisions as a tree and asks only the questions whose prerequisites are settled. Each round covers the current frontier, gives a recommended answer, accepts answers outside the
suggested options, and uses the response to reveal the next set of decisions.

Facts available from the project or tools are researched instead of being passed back as questions. The interview ends only when no branches remain and the user confirms the shared understanding. It
is a clarification step, not approval to implement the result.

## Use

Invoke it directly with a request to grill or stress-test an idea, or use the manual entry point:

```text
/grill-me [what to stress-test]
```

## Fork

Forked from **Matt Pocock**'s [`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) and
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me) in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT).

The fork preserves upstream's design tree, frontier rounds, fact-finding, and completion rule. It replaces upstream's fixed Markdown question format with the host's native ask-the-user interface,
keeps free-text answers available, and uses an inline numbered format only when that interface is unavailable.
