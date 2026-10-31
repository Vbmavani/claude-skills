# Row schema (one JSON object per finding)

```json
{"competitor":"Zenoti", "tier":"Top|Medium|Peer",
 "dimension":"advantage|gap|stand_out|psychology",
 "feature_area":"one short area from the list chosen for this run",
 "finding":"1–2 concrete sentences, with numbers where possible",
 "public_reaction":"short verbatim quote or close paraphrase from a real user, or empty",
 "psychology":"the mechanism (required on psychology rows)",
 "our_action":"build / copy / avoid / message: what we do about it",
 "source_url":"required", "source_date":"YYYY-MM or empty",
 "confidence":"verified|unverified"}
```
The build script sets `our_status`, `our_status_group` and `id`.

`feature_area`: pick 8–18 short areas that fit the category before research starts, and give all 3 agents the same list. For clinic software: Booking, Billing, Inventory, Marketing, Reporting, Mobile app, Pricing. For coding tools: Autocomplete, Agents, Context, Models, Pricing and limits, Privacy, Integrations.

## Lens rules
- **advantage**: the competitor's real edge, backed by evidence (users praise it, or it is a headline feature).
- **gap**: a feature they have or users ask for that we lack. It is only a claim until the gap check against our product confirms it.
- **stand_out**: a weakness or complaint about them, phrased as our move.
- **psychology**: fill the `psychology` field (the build fails without it, and a lever written in `public_reaction` is not counted). Name the bias (loss aversion, endowment and so on), explain how the feature uses it, then give the counter-move.

## Confidence
`verified` means the source shows the claim directly: a review quote, or a pricing or documentation page showing what the vendor offers.
`unverified` covers vendor claims about results or quality, aggregator summaries, search-snippet-only evidence that could not be opened, and analysis.
