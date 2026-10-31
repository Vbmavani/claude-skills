# competitor-intel

Competitor intelligence for any product, or for just an idea. Give it whatever you have: a one-line idea, a website URL, an app-store link, a deck or doc, code repos, or a live app. It researches competitors in three tiers and publishes a visual, filterable intel page:

- **Where you stand**: a customer-journey rail with a ring per stage. Every capability is checked against your idea, site, docs or code.
- **Market pressure**: a dot-strip gap chart (one dot per competitor), a bubble battleground, evidence by competitor, and psychology lever meters.
- **Explorer**: every sourced finding in a scrollable, sortable table. It has 4 lenses (their advantages, what you're missing, how you stand out, the psychology and how to beat it) and filters by tier, competitor, area, status and confidence.

## Install
```bash
cp -R skills/competitor-intel ~/.claude/skills/
```
Then ask for something like:
- "competitor analysis for my idea: a WhatsApp-first booking app for salons"
- "who are the competitors of https://example.com and what are we missing?"
- "refresh the competitor table"

## Quick start (manual)
```bash
scripts/new_run.sh                      # creates runs/<today>/ from templates/starter/
# fill the tier_*.json files, code_check.json and meta.json
python3 -I scripts/build_table.py --inputs runs/<date>/tier_*.json \
  --status runs/<date>/code_check.json --meta runs/<date>/meta.json \
  --out runs/<date>/<date>_competitor-intel_v1.html
```
Build `templates/starter/` to see the empty template. `examples/2026-10-31_clinozy/` is a full worked example: a clinic SaaS checked against its code, 214 findings, 16 competitors.

## Layout
| Path | What it is |
|---|---|
| `SKILL.md` | The workflow: start run, get product context, tier, research with 3 agents, check gaps, build, verify, publish |
| `references/` | Row schema, tiering, review mining, psychology levers, product context (idea, URL, doc, repo or app), credits to the 15 source skills |
| `scripts/build_table.py` | Validates, merges, applies the gap check and renders the page (Python 3, standard library only) |
| `scripts/new_run.sh` | Starts a run folder from the starter template, or from the last run with `--from-latest` |
| `assets/table_template.html` | The page design (light and dark, no build step) |
| `templates/starter/` | Blank starter data marked EXAMPLE |
| `examples/` | Worked examples (data only; build them to view) |
| `evals/` | Task evals and trigger evals |
