# fast-feedback-mode

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-394%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 394 tokens" />
  <img src="https://img.shields.io/badge/Total-394%20tokens-2ea44f?style=flat-square" alt="Total: 394 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    394 |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/fast-feedback-mode` for a tight, interactive build-and-try loop. It makes only enough of each requested change for you to see or use it, reports back briefly, and waits for your next adjustment.
Where useful, a mock can expose the intended experience before slower supporting work is complete.

Tests, checks, formatting, documentation, and commits are deferred so they do not interrupt iteration. Say `finalize` when the direction is settled to request that deferred work; finalizing does not
imply a commit, which must be requested separately. This mode improves feedback speed at the cost of leaving the work unverified and incomplete until finalization.
