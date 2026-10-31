---
name: instagram-feed-improver
description: Improve a user's own Instagram feed toward topics they choose. Audits the feed, steers it with their own signals, then re-audits the same way and reports before and after. Use when someone wants to improve, clean up, reset or retrain their Instagram feed, algorithm, Reels or Explore, wants less of some topic and more of another, or asks what Instagram is showing them, even if they don't say "audit".
---

# Instagram Feed Improver

Measure the feed against the user's goal, change it using their own account signals, and measure again the same way. Instagram's ranking can't be edited, so this is curation of one account, and the honest result can be "no change yet".

## Before you start

Get these from the prompt, and ask only for what's missing:

- **Goal topics:** for example AI, business, motivation.
- **Keep list:** topics or people that aren't on goal but must not be removed, such as friends, family or a community.
- **Browser:** the user signs in themselves. Never enter a password. If they name Chrome, the Claude in Chrome extension must be connected.

Search the web for related terms to build `on_goal` and `off_goal` lists. Save them in the shape of `assets/keywords.template.json`. Keyword matches are a first pass; judge each item by author, caption and audio.

## Hard limits

- No follow requests, likes, comments or messages unless the user asks in this conversation.
- Show the unfollow list and get approval before any unfollow.
- Leave privacy and security settings alone.
- Stop for the day at any "try again later" or checkpoint prompt, and don't retry.
- Keep private people's names out of anything published. Report searches as categories.
- Audit data never goes in a public repo.

## Workflow

1. **Baseline.** Follow `references/collection.md`. Read in parallel tabs if the user wants speed. Save results and fill `assets/audit-template.md`.
2. **Publish the baseline** before changing anything.
3. **Check for the phone step.** Ask the user to open Your Algorithm in the app and set their topics. It's the most direct control. See `references/signals.md`.
4. **Steer.** One action at a time, in one tab, with irregular pauses: Not interested on off-goal suggested posts, then the Reels watching pattern in `references/collection.md`. Log every action.
5. **Re-audit** with the exact same routine.
6. **Compare blind.** Merge both runs, shuffle them, strip the run labels and have a separate agent rate every item. Then unblind and report each number with its sample size and margin. With one baseline, a same-day change is only a hint. Report side effects too, such as a wanted topic falling.
7. **Schedule checks** for days 1, 3, 7 and 14 if the user wants them.

## Reporting

Lead with whether the on-goal share moved and by how much. Include the sample size, what was changed, what only the phone app can do, and the limits. Never call a result an improvement if it's within baseline variation. Use `references/signals.md` for sourced claims and don't repeat unsourced blog weights.
