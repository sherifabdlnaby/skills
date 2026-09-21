# Attaching media

Covers: `--attach` on create/edit/comment, body-file placement and alt text, screenshot framing (margin around the subject), failed-upload recovery.

`--attach <file>` uploads a local image or video into the body. Repeatable, and on `gh pr create`,
`gh pr edit` and `gh pr comment`. Use it. A version number is not a preflight. Only if `gh` rejects
the flag as unknown is this `gh` older than 2.99.0.

When to attach a picture, and where it sits in the body: [`pr-body.md`](./pr-body.md#visuals).

A thread reply cannot take a file; put the picture on the PR-level comment or in the body, and link it
from the thread. That constraint is [`review-responses.md`](./review-responses.md).

## How it works

**The body file decides where it lands.** Write the Markdown reference where you want the media, then
attach the same path: `gh` swaps the reference for the uploaded URL and keeps the alt text you wrote.
In a PR body that place is the **Visuals** block, or the changelog bullet or review guide stop that
the picture supports.

```bash
gh pr create --draft --assignee @me --body-file /tmp/pr-body.md \
  --attach ./before.png --attach ./after.png
```

With `/tmp/pr-body.md` carrying the references, alt text and all:

```markdown
**Changes** <!-- pr:changes -->

- *Empty results* now explain what to do next.

  | Before                           | After                                            |
  | -------------------------------- | ------------------------------------------------ |
  | ![Bare empty list](./before.png) | ![Empty list with a call to action](./after.png) |
```

Outside a body file, alt text follows the path after `#`, as in
`--attach './login.png#The login error state'`; without it the filename becomes the alt text. Video is a
player and has no alt text. Alt text is public, so [SKILL.md](../SKILL.md) voice applies.

**A failed upload does not fail the PR.** Partial success still creates the PR and prints its URL, then
exits non-zero. Read the URL. Read that exit code as "nothing happened" and run create again, and the
user has two PRs. Add what failed with `gh pr edit --attach`.

## Screenshot framing

**Leave a margin.** Capture the subject with a band of surrounding page so the reader can place the
shot: neighbouring content, chrome, sibling panels. A flush crop of the widget alone loses that
orientation.
