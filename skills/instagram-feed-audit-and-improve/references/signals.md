# What steers Instagram, with sources

Checked 31 Oct 2026. Meta publishes no weights or response times.

## Signals

- **Reels:** predictions include watching under 3 seconds (inputs include skips within 2 seconds of opening, and dismissals), watching more of a reel than 95% of viewers of that length, commenting, resharing and following. Not interested filters similar content. The 15-second line on this card is an input for reusing audio, not a general watch signal. [Reels card](https://transparency.meta.com/features/explaining-ranking/ig-reels-chaining/)
- **Feed:** likes, comments, reshares, dwell time, sends, profile visits. Hide and Mute limit content. [Feed card](https://transparency.meta.com/features/explaining-ranking/ig-feed/)
- **Explore:** likes, saves, authors followed and visited, viewing time, Not Interested. [Explore card](https://transparency.meta.com/features/explaining-ranking/ig-explore/)
- **Search:** name match, click rates, profile visits, social graph. [Search card](https://transparency.meta.com/features/explaining-ranking/ig-search/)

## Controls

| Control | Where | Note |
|---|---|---|
| Your Algorithm | Phone app | Add topics or mark them less. [Instagram](https://about.instagram.com/blog/announcements/reels-algorithm-control) says it covers Feed, Reels and Explore, and that it rolled out globally in English. Confirm the user has it. |
| Not interested on Reels | Phone app | Not offered on the web. |
| Not interested on feed posts | Web and app | Works post by post. |
| Snooze suggested posts | Phone app | 30 days. [Meta](https://about.fb.com/news/2022/08/testing-ways-to-control-what-you-see-on-instagram/) |
| Reset suggested content | Phone app | Last resort. Clears recommendations across Explore, Reels and Feed, which then rebuild from new activity. Meta doesn't say it can be undone, so treat it as permanent. It doesn't remove follows. [Meta](https://about.fb.com/news/2024/11/introducing-recommendations-reset-instagram/) |
| Ad topics | Accounts Center | Change only if ads conflict with the goal. |

## Measurement

- Nobody knows Instagram's response speed. A TikTok bot study reports shifts within about 200 videos, but it used newly made bots on another platform, so it may not transfer. [arXiv 2503.20231](https://arxiv.org/abs/2503.20231)
- One account is descriptive only. Use several baselines where possible and compare against baseline variation. `scripts/compare_runs.py` treats a change as noise unless it clears both the sampling margin and the spread between baselines.
- Items recur between runs, so the margin is approximate. It leaves out rater error too, so read it as a minimum.

## Risk

Instagram's terms restrict automated access, and whether an assistant clicking for a user counts is unsettled. Action limits aren't published; the 30-action cap in this skill is a cautious default, not a known safe number. Keep clicks slow and few. Reels skips aren't clicks; the 9-minute limit caps those. The aim is normal personal use, so don't add anything meant to disguise automation.

Treat "sends are the strongest signal", fixed weights and "48 hours to 2 weeks" as unverified blog claims.
