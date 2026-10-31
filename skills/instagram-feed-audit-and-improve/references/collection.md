# Collection and action routine

Keep this fixed between audits, because a change in routine looks like a change in the feed. That includes the browser, window size and time of day; record them in the audit.

## Output

Save one JSONL file per run, with one line per item:

```json
{"surface": "home", "key": "stable id", "author": "", "caption": "", "audio": "", "suggested": false, "ad": false}
```

`surface` is `home` or `reels`. Mark `ad` from the Sponsored label. `window` data is lost on navigation and reading long data replaces the page, so finish a surface before exporting it, and export it before moving on. Following, Search and Settings aren't items; put them straight in the audit file.

## Tool notes

- `javascript_tool` calls time out around 45 seconds. Start an in-page async collector, store to `window`, and poll with short calls.
- Tool output is cut at about 1,000 characters. To read long data, replace `document.body` with one `<article>` holding the text, then call `get_page_text`. Navigate away afterwards to restore the page.
- Timers run slower with several tabs open: 90 Reels steps took about 15 minutes in four tabs. Use the same number of steps each time and report unique items.

## Home feed

Read `article` elements, scroll about 650px every 1.5 seconds, for 110 scrolls. Key by the post's `/p/` or `/reel/` link if it's in the DOM, otherwise by author and the first caption text.

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

1. Find a suggested off-goal post that isn't on the Keep list, then `scrollIntoView`.
2. Read the `svg[aria-label="More options"]` position inside that post.
3. Do a real click on it. Synthetic clicks are unreliable.
4. Find the menu item whose text is exactly `Not interested` and read its own position. Don't use a fixed offset, because the menu changes per post. If it isn't there, press Escape and move on.
5. Real click on that position, wait 3 to 5 seconds, and repeat.

Never click near the Follow button. One bad click once followed an account. After each click, check the post's button still reads as it did.

## Reels watching pattern

For 9 minutes, in one tab. A round trip through a tool takes longer than 2 seconds, so run this as an in-page loop rather than deciding each reel with tool calls:

1. Read the reel's visible text and match it against the `on_goal` keywords, plus the Keep list.
2. On a match, watch to the end, up to 90 seconds. Meta's positive watch label is watching more of a reel than most viewers do.
3. With no match, scroll on within 2 seconds. Meta's prediction of under-3-second watches counts skips within 2 seconds.

No likes or follows. Keyword gating misses reels with no caption text, so report the skipped count. On-goal watching this way favours captioned reels.
