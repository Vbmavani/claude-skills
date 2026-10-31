# research.json

`assets/example-input.json` is a worked example from a Mac tracking comparison. It shows the format; its rating URLs point to each tool's main page, so don't reuse them as sources.

## Scored by score.py

```json
{
  "fit_share": 0.7,
  "criteria": [{"key": "privacy", "label": "Privacy", "weight": 25, "anchors": "Local 10; vendor cloud 3"}],
  "gates": [{"key": "solo", "label": "One person can use it"}],
  "uncertain_scores": {"Tool A": {"privacy": 3}},
  "tools": [{
    "name": "Tool A",
    "category": "Time tracker",
    "scores": {"privacy": 7},
    "gates": {"solo": "pass"},
    "ratings": [{"platform": "g2", "label": "G2", "rating": 4.4, "count": 498, "url": "https://…", "verified": false}],
    "hn": {"pos": 2, "mix": 3, "neg": 2}
  }]
}
```

- `platform` is one of `g2`, `capterra`, `getapp`, `softwareadvice`, `producthunt`, `alternativeto`, `trustpilot`, `gartner`, `appstore`, `trustradius`.
- `scale` is optional and defaults to 5.
- `verified` is true only for a figure read on the live page or from an official feed.
- Leave out a rating you couldn't find. Never enter a zero.
- Add `"pool_only": true` to a tool that informs the platform means but isn't ranked.

## Added after scoring

| Field | Source |
|---|---|
| `fact_check` | The fact-check reviewer's counts. Rerun `score.py` so evidence strength includes them |
| `run_metrics` | `{minutes, web_calls, total_tokens}` from `session_usage.py` |
| `review` | Written by `blind_review.py score` |
| `changes` | Written by `track.py compare` |
| `artifact_url` | The published link, added before `track.py save` |

## Read by build_page.py

Top level:

| Field | Content |
|---|---|
| `title` | Page name, two to four words, for example "Mac Tracker Shootout" |
| `use_case`, `date` | Shown above the headline |
| `headline`, `lede` | The answer and one or two supporting sentences |
| `why` | List of strings, or `{text, url}` |
| `case_against`, `alternative` | Strings |
| `checks` | List of `{title, body}` for the user to do |
| `limits` | List of strings or `{text, url}` |
| `columns` | List of `{key, label}`, one per table capability column |
| `excluded` | List of `{name, url, status, why}` |
| `extra_tables` | Optional list of `{title, intro, columns, rows, note}`, where each cell is a string or `{text, url}` |
| `candidates_screened` | Number of tools considered before gating |
| `run_log` | List of `{tried, purpose, status, result}`, with status `ok`, `partial` or `failed` |

Per tool:

| Field | Content |
|---|---|
| `url`, `price`, `storage`, `maintenance` | Strings. `maintenance` carries a date |
| `capabilities` | Object keyed by column, each `{text, level}`. Level is 3 full, 2 partial, 1 weak, 0 none |
| `praise`, `complaint` | String or `{text, url}`. Write "Not found" when there is nothing |
| `gate_note` | Why the tool passed or failed |
| `evidence` | Short plain summary of what supports the fit scores, for the blind reviewer |
