# Scoring method

`score.py` does all the arithmetic. You supply the judgements below.

## Gates come first

Each must-have is a gate with the value `pass`, `fail` or `unverified`. A weighted sum lets strength in one area hide a missing capability, so any tool with a `fail` ranks below every tool without one, whatever its total. Unknown means `unverified`, never `fail`.

Before gating, drop tools with no sign of life: no dated release in 12 months, no vendor docs for the current platform, and no dated first-hand use. List them in `excluded`.

## Fit scores

Score each criterion 0 to 10 against written anchors, and write the anchors before you score so all tools meet the same test. For example, on how deeply a tool captures something:

| Score | Meaning |
|---|---|
| 10 | Does it fully by default |
| 8 to 9 | Does it fully, behind a setting or with limits |
| 5 to 6 | A partial substitute |
| 3 to 4 | A weak signal |
| 1 | Barely |
| 0 | Doesn't, or isn't documented |

For privacy: local with no cloud 10, local with optional cloud 8, local with default telemetry 7, account sync 5, vendor cloud 2 to 3.

For value to one person: free and complete 10, cheap single seat 7 to 8, team product with a solo route 6, needs a server 4, seat minimum 1.

## Public feedback

- Each rating is pulled toward its platform's mean across the pool: `S = (v·R + 50·C) / (v + 50)`.
- Each source scores `7.0 + 5 × (S − C)`, clamped to 0 to 10. A tool average for its platform gets 7.0.
- Hacker News uses the share of positive comments, counting mixed as half, shrunk toward the pooled share with m = 10: `7.0 + 10 × (shrunk share − pooled share)`.
- Sources combine at G2 family 35%, Hacker News 30%, AlternativeTo 10%, Product Hunt 10%, and 5% each for Trustpilot, Gartner, App Store and TrustRadius. Absent sources are dropped and the rest renormalised, so absence is never a zero.
- A tool with no public evidence gets `public: null` and is ranked on fit alone.

## Totals, ties and confidence

- Total = fit share × fit + (1 − fit share) × public. The default fit share is 70%, so review manipulation can't dominate.
- A gap under 0.5 from a band's leader is a tie.
- High confidence needs two rating families verified on live pages with 100 or more ratings. Medium needs two families and 100 or more ratings. Everything else is Low. The label applies to public feedback, not to capability facts.

## Stability

`score.py` runs 1,000 random ±20% weight changes, equal weights, each criterion dropped, lower fit shares, and the point where each weight flips the winner. Under 70% of wins means the winner is unstable, so present a shortlist. These tests show robustness to the weights, not to the fit judgements, so say that on the page.

## The scorecard

`score.py` writes a `scorecard` block for tracking runs over time. Keep the two kinds of number apart, as the page does.

**Measured counts:** tools screened, tools passing every gate, ratings, reviews behind them, share verified live, first-hand tool mentions, steps tried and steps that worked, fact-check results, minutes, web calls and tokens.

**Judgement scores:** winner total, lead over the runner-up, share of weight tests won, evidence strength, and the blind reviewer's mean gap.

Evidence strength runs 0 to 100, and measures how much the run saw rather than how good the winner is:

| Part | Points | Full marks when |
|---|---|---|
| Ratings verified live | 30 | Every rating was read on a live page or official feed |
| First-hand comments | 25 | An average of 5 per ranked tool |
| Research steps that worked | 20 | Every logged step had status `ok` |
| Fact-check supported | 25 | Every checked claim was supported. Scores 0 until a fact check runs |

Under 40 means treat the ranking as a shortlist. A blind reviewer's mean gap over 2 points means the anchors are too loose, so tighten them and rescore. Compare numbers between runs only when the criteria and weights match; `track.py compare` warns when they don't.
