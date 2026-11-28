# Someone else's PR

Covers: posting, gather, run, proof, the report, comments.

The goal is a fast, sound decision for the user: what the PR does, whether it works, and what to say.

## Posting

- **Default: post one review.** All findings go out in one GitHub review: overall findings in its body, inline ones on their lines. Load the **git** skill for the AI disclosure.
- **The event is `COMMENT`** unless the user picks approve or request changes.
- **Show the draft first** when the context calls for it: the user asked to see it, the review requests changes on a person's work, or a finding is a judgment the user may not share. Then post on
  their go, with their edits.
- **Unattended: post only** when the prompt that started the run says to post. Otherwise write the review to a file and name it in the report.

## Gather

One wide read into a file, then query it as questions come up. Check out in a separate worktree, so the user's branch and tree stay as they are.

```sh
state=$(mktemp)
gh pr view <pr> --json number,title,author,body,baseRefName,headRefName,files,reviews,comments,statusCheckRollup,closingIssuesReferences > "$state"
git worktree add --detach ../review-<pr> && cd ../review-<pr> && gh pr checkout <pr>
```

1. Read the description, the existing reviews and comments, the linked issues and earlier PRs, and what the user said in this chat.
2. Trace the change until you can say, per file, what it does and why it belongs in this PR. A file you cannot place is a finding.
3. **Run it when cheap**: the tests for the changed area, and the changed path itself (a CLI command, an endpoint, a page) when the repo's tasks make it one command. Skip what needs setup, secrets,
   or a device, and say what you skipped.
4. **CI**: for each failing check, the cause from its log, and whether this PR caused it.
5. **Proof**: does the PR show the change works (a test plan, tests for the new behavior, a screenshot or recording for UI)? Thin proof is an overall finding that asks the author for it, and a
   manual check for the user.
6. Run [Every review](../SKILL.md#every-review). Run no-comments and no-docs on the checkout, turn their edits into findings (`suggestion` blocks), then discard the edits.

## The report

In this order:

1. **Verdict**: approve, request changes, or comment, with the one to three reasons.
2. **What needs the user's hands**: failing CI, manual checks, missing proof.
3. **Tour**: what the PR does and how, where to start reading, what carries risk.
4. **Findings**: overall, then inline, drafted as the comments below.

## Comments

[Conventional Comments](https://conventionalcomments.org): `<label> (blocking|non-blocking): <subject>`, then the cost and the fix. Labels: `issue`, `suggestion`, `question`, `nitpick`,
`praise`, and `opinion` for an opinion. A concrete code change goes in a `suggestion` block. Name the coding rule in words a stranger understands, not by its ID alone.

Post with `gh api repos/<owner>/<repo>/pulls/<pr>/reviews --input review.json`, where `review.json` is
`{"event":"COMMENT","body":"<overall>","comments":[{"path":"a.go","line":42,"side":"RIGHT","body":"<inline>"}]}`.
