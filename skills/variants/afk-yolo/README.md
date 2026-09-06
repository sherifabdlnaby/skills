# afk-yolo

<!-- token-estimates:start -->

<p>
  <img src="https://img.shields.io/badge/SKILL.md-114%20tokens-2f80ed?style=flat-square" alt="SKILL.md: 114 tokens" />
  <img src="https://img.shields.io/badge/Total-114%20tokens-2ea44f?style=flat-square" alt="Total: 114 tokens" />
</p>

Token estimates use tiktoken's `o200k_base` encoding. `SKILL.md` is the entry prompt; total includes every
UTF-8 text file in the skill package except its generated `README.md`. Binary files are omitted.

| File                   | Tokens |
| ---------------------- | -----: |
| [`SKILL.md`](SKILL.md) |    114 |

<!-- token-estimates:end -->

[Canonical skill instructions](SKILL.md)

Use `/afk-yolo` when you want the most progress possible while away without allowing destructive actions. It extends the [`/afk`](../../afk/README.md) contract to include handling review feedback and
watching a pull request until its checks pass.

Its autonomy still stops before data loss, deployment or publication, force-pushing shared branches, and deleting remote data. Compared with the base mode, it accepts more non-destructive judgment
calls in exchange for completing more of the delivery loop.
