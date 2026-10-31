# Collection and action routine

Keep this fixed between audits, because a change in routine looks like a change in the feed.

## Tool notes

- `javascript_tool` calls time out around 45 seconds. Start an in-page async collector, store to `window`, and poll with short calls.
- Tool output is cut at about 1,000 characters. To read long data, replace `document.body` with one `<article>` holding the text, then call `get_page_text`. Navigate away afterwards to restore the page.
- Timers run slower with several tabs open: 90 Reels steps took about 15 minutes in four tabs. Use the same number of steps each time and report unique items.

## Home feed

Read `article` elements, scroll about 650px every 1.1 to 1.8 seconds, for 110 scrolls. Key by author and the first caption text.

Merge afterwards: Instagram re-renders posts and sometimes drops the "Suggested for you" label. Treat a post as suggested if any copy had the label.

## Reels

90 steps at about 4 seconds each on `/reels/`. The URL holds the reel ID. Walk up from the most visible `video` until the text contains `Likes`, `Follow` or `more`. Scroll the largest scrollable `div` by 0.9 of the viewport.

## Search

Open `/explore/search/`, focus the input, and read the text after `Clear all`. Classify rows by type.

## Following

Click the following count; a direct URL doesn't open the list. It may stop loading partway. Don't force it, and treat what loaded as a sample.

## Explore

Tiles usually have no text, and opening one jumps into the Reels player. Report Explore topics as not measurable on the web.

## Settings

Links are under `/accounts/settings/v2/`. On the web, Content preferences holds only Sensitive content, and Hidden Words covers comments and messages only.

## Not interested

1. Find a suggested off-goal post, then `scrollIntoView`.
2. Read the `svg[aria-label="More options"]` position.
3. Do a real click on it. Synthetic clicks are unreliable.
4. The menu item sits about 49px right and 96px below the button. Confirm the offset with the actual element once per session.
5. Real click on Not interested, wait 3 to 5 seconds, and repeat.

Never click near the Follow button. One bad click once followed an account.

## Reels watching pattern

For 9 minutes: stay 22 to 31 seconds on on-goal reels and leave others within 2 seconds. No likes or follows. Meta lists 2-second skips as negative and watching over 15 seconds as positive.
