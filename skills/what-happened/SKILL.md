---
name: what-happened
description: Catch me up on this chat since my last message.
license: MIT
disable-model-invocation: true
metadata:
  author: sherifabdlnaby
  version: "0.1.0"
---

# what-happened

Catch the user up on what changed in this chat since the last message they wrote, and help them understand each change, not only where it stands. Then lay out every call waiting on them so they can
make it from this reply alone. Notifications and subagent results are not their messages. Assume the user remembers their last message and nothing after it.

## Voice

- **Plain words, short sentences**, like one person catching up another. Say what changed for the user, not how you did it: "the tests pass", not "CI is green".
- **Leave out hashes, paths, commands, build numbers, and test counts** unless the user needs one to act.
- **Use names the user knows** for each PR, branch, or agent, never a label you invented.
- **A fact that needs context** gets the context, or stays out.

## Gather

- **Read-only turn.** Do not change code, start an app or a job, or post anything. Visuals come only from what you already have.
- **Collect** your own work since that message, subagent reports, and messages from anyone else in the chat. Check the current state of each PR, CI run, or agent the chat touched.
- **Check each number** you will show against its source; say so when you correct one.
- **An action item is a call only the user can take**: a product choice, an approval, an irreversible action, access you lack. Include ones raised before their last message that still wait. Work you
  can do yourself is not one, and never invent one to fill the reply.
- **Per item**, collect its link, what it changes for users, the evidence for your pick, its risk, and your pick. Write "unknown" for a needed fact you lack.

## Write

Spend words on the calls, not the story.

1. **One opening sentence** naming what waits on the user, or that nothing does. Nothing happened and nothing waits: say so and stop.
2. **What happened, pictures first.** Screenshots and videos the work produced, inline; then any diagram that explains a change. Then one bullet per thing the user asked for: what came of it, and
   whether it is done, running, failed, or not checked. Write it as you would say it ("Search was slow from a missing index"), each line true when read alone. Name bugs found and fixed on the way.
   Keep this part under 100 words, not counting pictures. At most three lines that change what the user knows or must do, then one line on work left that you can do yourself.
3. **Action items.** Ask the call the user owns (merge, approve, pick) and give your pick, including any step you would take first, anything that must happen first, and anything irreversible. Name
   each PR, issue, or agent by number or link.
   - **One item**: one bullet with the call, pick, user impact, evidence, and risk.
   - **Items sharing a call**: the call and pick once, then one bullet per item, riskiest first. Give each item's risk even when low ("Low risk: only the colors change").
   - **A call between options**: each option with what it gets the user and what it costs; those costs are its risk.
   - **About 30 words per item.** Never cut or merge items to fit a word count: no count in place of a list, no link in place of an item.
   - **Cost of waiting** only when it is more than a delay: a deadline, lost data.

## Visuals

- **A visual is a picture**: a screenshot, video, Mermaid diagram, chart, or generated image. A Markdown table is not one.
- **Draw what is easier as a picture**: how a system works, a PR stack with each PR's state, a before and after, options side by side. Never draw a status list, the action items, or unconnected boxes.
- **Small**: at most six boxes, at most eight plain words in each.
- **Never give a fact twice**, in text or across visuals.
- **Only real artifacts.** A visible change with no screenshot gets "No screenshot yet" and a line on what changed on screen. Never invent a number or picture a screen you did not capture.
