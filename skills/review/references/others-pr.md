# Someone else's PR

Commands are the usual call, cached; on a miss, read `--help`.

## Gather

One wide read into a file, and a separate worktree so the user's branch stays as it is.

```sh
state=$(mktemp)
gh pr view <pr> --json number,title,author,body,baseRefName,headRefName,files,reviews,comments,statusCheckRollup,closingIssuesReferences > "$state"
git worktree add --detach ../review-<pr> && cd ../review-<pr> && gh pr checkout <pr>
```

1. **Trace** until each file has a what and a why-here. A file you cannot place is a finding.
2. **Run it when cheap**: the tests for the changed area, and the changed path itself when the repo makes it one command. Say what you skipped (setup, secrets, a device).
3. **Proof**: a test plan, tests for the new behavior, a screenshot for UI. Thin proof is an overall finding that asks the author for it, and a manual check for the user.
4. **[Every review](../SKILL.md#every-review)**, as a reviewer: you edit nothing.
5. Remove the worktree when the review is posted or handed over: `git worktree remove ../review-<pr>`.

## Report

1. **Verdict**: approve, request changes, or comment, with one to three reasons.
2. **Needs the user's hands**: failing CI and its cause, manual checks, missing proof.
3. **Tour**: what the PR does, where to start reading, what carries risk.
4. **Findings**: overall, then inline, drafted as they will post.

## Post

- **One review, event `COMMENT`** unless the user picks another. Overall findings in its body, inline ones on their lines. Load the **git** skill for the AI disclosure.
- **Show the draft first** when the user asked, the verdict is request changes on a person's work, or a finding is a judgment the user may not share.
- **Unattended**: post only when the prompt that started the run says to. Otherwise write the review to a file and name it in the report.
- **[Conventional Comments](https://conventionalcomments.org)**, plus an `opinion` label. A code change goes in a `suggestion` block. Name the coding rule in words a stranger understands.
