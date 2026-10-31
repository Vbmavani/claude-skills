# Collection and action routine

Keep this fixed between audits, because a change in routine looks like a change in the feed. That includes the browser, window size and time of day; record them in the audit.

## Output

Save one JSONL file per run, with one line per item:

```json
{"surface": "home", "key": "stable id", "author": "", "caption": "", "audio": "", "suggested": false, "ad": false}
```

`surface` is `home` or `reels`. Mark `ad` by the rules under each surface. `window` data is lost on navigation and reading long data replaces the page, so finish a surface before exporting it, and export it before moving on. Following, Search and Settings aren't items; put them straight in the audit file.

## Parallel tabs

Reads run in parallel by default: open one tab per surface (Home, Reels, and one for Search, Following and Settings), start each collector, then poll them in turn. Account actions are never parallel.

Keep the layout the same in every run, and leave the window alone during a run. Check the window size in every tab, because it changes what loads. Background tabs throttle timers, so Reels takes longer: count steps, not minutes, and confirm that items are arriving in each tab within the first 30 seconds.

## Tool notes

- `javascript_tool` calls time out around 45 seconds. Start an in-page async collector, store to `window`, and poll with short calls.
- Tool output is cut at about 1,000 characters. To read long data, replace `document.body` with one `<article>` holding the text, then call `get_page_text`. Navigate away afterwards to restore the page. `get_page_text` is the export; don't retype the data by hand.
- Timers run slower with several tabs open: 90 Reels steps took about 15 minutes in four tabs. Use the same number of steps each time and report unique items.

## Home feed

Read `article` elements, scroll about 650px every 1.5 seconds, for 110 scrolls. Key by the post's `/p/` or `/reel/` link if it's in the DOM, otherwise by author and the first caption text.

Ads usually have no `Sponsored` text in the DOM. Mark a post as an ad if it has no `/p/` or `/reel/` link and no author link. In one live run the text check found none of 21 ads.

Captions start with noise. Drop `Liked by` lines, which name other people, and repeated author names.

Merge afterwards: Instagram re-renders posts and sometimes drops the "Suggested for you" label. Treat a post as suggested if any copy had the label.

## Reels

90 steps at about 4 seconds each on `/reels/`. The URL holds the reel ID. Start at the parent of the most visible `video` and walk up while the element holds exactly one video, keeping the highest one with text. The text can be 13 or more levels up, so don't cap the walk. Scroll the largest scrollable `div` by 0.9 of the viewport. Mute the video.

A call-to-action line where the author should be (`Learn more`, `See details`, `Get quote`) marks an ad, and the real author is the next line. `Suggested` can't be read here, because nearly every reel shows Follow, so report it as not measured.

## Search

Open `/explore/search/`, focus the input, and read the text after `Clear All`, matching case-insensitively. Classify rows by type.

## Following

Click the following count; a direct URL doesn't open the list. It may stop loading partway. Don't force it, and treat what loaded as a sample.

## Explore

Tiles usually have no text, and opening one jumps into the Reels player. Report Explore topics as not measurable on the web.

## Settings

Links are under `/accounts/settings/v2/`. On the web, Content preferences holds Sensitive content and Content from accounts that you don't follow, and Hidden Words covers comments and messages only.

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
