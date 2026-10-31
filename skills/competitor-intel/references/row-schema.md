# Row schema (one JSON object per finding)

```json
{"competitor":"Zenoti", "tier":"Top|Medium|Peer",
 "dimension":"advantage|gap|stand_out|psychology",
 "feature_area":"Booking|Leads/CRM|WhatsApp|Billing/GST|Pharmacy|Inventory|Photos/EMR|Marketing|Memberships/Packages|Reporting|Mobile app|Onboarding/Support|Pricing|Integrations|AI|Positioning|Tasks|Users/Branches",
 "finding":"1–2 concrete sentences, with numbers where possible",
 "public_reaction":"short verbatim quote or close paraphrase from a real user, or empty",
 "psychology":"the mechanism (required on psychology rows)",
 "our_action":"build / copy / avoid / message: what we do about it",
 "source_url":"required", "source_date":"YYYY-MM or empty",
 "confidence":"verified|unverified"}
```
The build script adds `our_status`, `our_status_group` and `id`.

## Lens rules
- **advantage**: the competitor's real edge, backed by evidence (users praise it, or it is a headline feature).
- **gap**: a feature they have or users ask for that we lack. It is only a claim until the gap check against our product confirms it.
- **stand_out**: a weakness or complaint about them, phrased as our move.
- **psychology**: name the bias (loss aversion, endowment and so on), explain how the feature uses it, then give the counter-move.

## Confidence
`verified` means the source shows the claim directly: a review quote, a pricing page or a documentation page.
`unverified` covers vendor marketing claims, aggregator summaries, search-snippet-only evidence that could not be opened, and analysis.
