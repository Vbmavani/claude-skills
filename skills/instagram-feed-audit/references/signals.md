# What steers Instagram, with sources

Checked 31 Oct 2026. Meta publishes no weights or response times.

## Signals

- **Reels:** skips within 2 seconds, watching over 15 seconds, likes, saves, comments, profile clicks, reshares. Not interested and dismissals are negative. [Reels card](https://transparency.meta.com/features/explaining-ranking/ig-reels-chaining/)
- **Feed:** likes, comments, reshares, dwell time, sends, profile visits. Hide and Mute limit content. [Feed card](https://transparency.meta.com/features/explaining-ranking/ig-feed/)
- **Explore:** likes, saves, authors followed and visited, viewing time, Not Interested. [Explore card](https://transparency.meta.com/features/explaining-ranking/ig-explore/)
- **Search:** name match, click rates, profile visits, social graph. [Search card](https://transparency.meta.com/features/explaining-ranking/ig-search/)

## Controls

| Control | Where | Note |
|---|---|---|
| Your Algorithm | Phone app | Add topics or mark them less. [Instagram](https://about.instagram.com/blog/announcements/reels-algorithm-control) says it covers Feed, Reels and Explore. Confirm the user has it. |
| Not interested on Reels | Phone app | Not offered on the web. |
| Not interested on feed posts | Web and app | Works post by post. |
| Snooze suggested posts | Phone app | 30 days. |
| Reset suggested content | Phone app | Last resort. Can't be undone. Clears recommendations and rebuilds from new activity. [Meta](https://about.fb.com/news/2024/11/introducing-recommendations-reset-instagram/) |
| Ad topics | Accounts Center | Change only if ads conflict with the goal. |

## Measurement

- Nobody knows Instagram's response speed. TikTok bot studies report shifts within about 200 videos, but they start from blank accounts and may not transfer. [arXiv 2503.20231](https://arxiv.org/abs/2503.20231)
- One account is descriptive only. Use several baselines where possible and compare against baseline variation.

## Risk

Instagram's terms restrict automated access, and whether an assistant clicking for a user counts is unsettled. Action limits aren't published. Keep actions slow, irregular and few.

Treat "sends are the strongest signal", fixed weights and "48 hours to 2 weeks" as unverified blog claims.
