# pr-watch flags

Every knob of [`scripts/pr-watch.py`](../scripts/pr-watch.py). The commands in
[`watch.md`](./watch.md) are the happy path; come here when they do not fit. `--help` on each
subcommand is the authority when the two disagree.

## `watch`

| flag                               | default             | what it does                                                                                                             |
| ---------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `--pr`                             | current branch's PR | number or URL                                                                                                            |
| `--repo`                           | from the PR URL     | `owner/repo`; needed when `--pr` is a number outside the repo                                                            |
| `--watcher`                        | `default`           | state namespace; one per concurrent watcher on the same PR                                                               |
| `--state`                          | derived             | explicit snapshot path, overrides `--watcher`                                                                            |
| `--until`                          | `quiet`             | `green`: all checks passed. `quiet`: green, no review pending, silence for `--comment-grace`. `closed`: only merge/close |
| `--on`                             | `all`               | what wakes the caller: any of `fail,done,review,comment,state`                                                           |
| `--max-total`                      | none                | budget in seconds; persisted per watcher, reset by a push, ends with `DONE`                                              |
| `--stale-pct`                      | `30`                | with a budget: percent of it without any change before `STALE`, repeated at each step                                    |
| `--stale`                          | `1800`              | without a budget: seconds without any change before `STALE`, repeated; `0` disables                                      |
| `--max-wait`                       | `540`               | per-episode cap, returns `QUIET`; fits under a 10-minute tool timeout. Raise it for a background shell                   |
| `--comment-grace`                  | `120`               | `--until quiet` only: silence after green before `DONE`                                                                  |
| `--min-interval`, `--max-interval` | self-paced          | poll gap overrides; the default is 10-30s hot, 60s cold                                                                  |

State lives under `$WATCH_STATE_DIR`, else the system temp dir, one file per watcher.

## `poke`

| flag               | default  | what it does                                                                          |
| ------------------ | -------- | ------------------------------------------------------------------------------------- |
| `--pr`, `--repo`   | as above |                                                                                       |
| `--hold`           | `10`     | seconds to stay ready on a plain flick                                                |
| `--stay`           | off      | hold the PR ready until a bot review lands or `--max-wait`; allowed on a flicked head |
| `--max-wait`       | `480`    | `--stay` only: cap in seconds                                                         |
| `--register-grace` | `180`    | `--stay` only: revert early when no bot review request or new check appears within    |
| `--dry-run`        | off      | print the plan, change nothing                                                        |

The marker file sits beside the watcher state; a leftover one is reverted by the next `watch` or
`poke` run on that PR.
