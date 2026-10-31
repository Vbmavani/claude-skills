---
name: tool-shootout
description: Find the best software tools for a use case and publish an interactive comparison artifact. Researches the top 15 tools from the internet, checks what each one really does, gathers public sentiment, gives each a feedback score out of 10, ranks them with adjustable weights, tests how stable the winner is, and recommends one with reasons. Use whenever the user asks for the best tool or app for something, wants tools compared with metrics, asks "which X should I use", "top 10 X", "alternatives to X", "X vs Y vs Z", or wants public opinion or ratings on a set of tools, even if they don't say "comparison". Not for finding Claude skills or comparing skills.
---

# Tool Shootout

Turn "what's the best tool for this?" into a ranked, evidence-backed comparison page. The value is in finding out what each tool really does. Popular tools often don't do the job, so capability is checked first and sentiment second. Report a weak evidence base as plainly as a strong winner.

## Before you start

Settle these from the request. Ask only if a wrong guess would waste the run, otherwise state your assumption and go.

- **Use case:** the job, the platform, and who will use it (one person or a team).
- **Must-haves:** the capabilities a tool can't lack. Turn each into a gate.
- **Criteria and weights:** usually 4 to 6, adding to 100. The user's named needs weigh most. Add privacy when the tool handles sensitive data.
- **Count:** 15 tools unless the user says otherwise.

Then check for an earlier run, since a repeat is what makes the numbers trackable:

```bash
python3 scripts/track.py latest "<use case>"
```

If one exists, reuse its criteria, weights and use-case wording exactly, so scores can be compared, unless the user wants them changed. Say which run you found.

Keep a run log from the first step: what you tried, why, whether it worked, and what came back. It goes on the page, failures included, because the reader needs to know what the scores rest on.

Run the `scripts/` commands below with their full path inside this skill's folder. Work in a new folder named for the use case.

## Workflow

### 1. Discover candidates

Run 8 to 10 discovery searches in different framings: "best X", "alternatives to <leader>", "X for <platform>", and category names. Pool the results and count how many independent sources name each tool. Listicles favour whoever pays or ranks well, so treat them as a source of names only.

### 2. Research in parallel

Use the `deep-research` skill's coordinator pattern when it's available: split the pool into natural categories and spawn one subagent per category, in one message. Add one track for public sentiment. If subagents aren't available, work through the categories in turn.

Give every researcher the same brief: what the tool really does for each must-have, price, data location, latest dated release, and every rating with its count and URL. Tell them to write "not found" and never invent a rating, and to flag anything over 12 months old as stale. Read `references/evidence.md` and pass on its access rules, because a researcher that hits a block will otherwise try to work around it.

### 3. Collect the free evidence

For each finalist, run:

```bash
python3 scripts/collect.py hn "Tool Name"
python3 scripts/collect.py github owner/repo
python3 scripts/collect.py apple --term "Tool Name"
```

Read the Hacker News comments yourself. Count only first-hand users, leaving out vendors and affiliates, and label each one positive, mixed or negative. Check that an App Store match is the right product and note when it's a companion app, because several products share names. A wrong match poisons the score silently.

### 4. Try the blocked sources once

Try each of Reddit, X, YouTube, G2, Capterra, Trustpilot and Product Hunt once, by web search and by a direct fetch. A refusal is a finding. Record it in the run log and the limits, then move on. Follow the access rules in `references/evidence.md`.

### 5. Settle conflicts with a hands-on check

When sources disagree about a finalist, look for primary evidence: its source code, its docs, or the tool itself. If the user already has it installed, a status or health read can settle what web research can't. Ask first unless the user has already said to, and read status only, never recorded personal data, messages or documents. List anything you can't settle as a check for the user, naming the exact setting or test that would decide it.

### 6. Score

Read `references/scoring.md` for the anchors and method, and `references/input-schema.md` for the file format. Write `research.json`, gate before you score, then run:

```bash
python3 scripts/score.py research.json scored.json
```

Don't hand-calculate or adjust any score. If a number looks wrong, fix the input. Read the printed ranking and the flip conditions; they tell you when the honest answer is a tie or depends on what the user values.

### 7. Argue against the winner

Before writing the verdict, look for evidence against the winner: its worst complaints, licence or pricing changes, unverified allegations. Record those allegations as unverified. Add the uncertain scores to `uncertain_scores` and rerun `score.py` to see whether the win survives. If it comes down to a tie, say so.

### 8. Get an independent review

You chose the scores, so have someone else test them, using `references/review-prompt.md`:

```bash
python3 scripts/blind_review.py pack scored.json --out review/pack.json --key <scratchpad>/key.json
python3 scripts/blind_review.py score scored.json --rescored review/rescored.json --key <scratchpad>/key.json
```

Send the first prompt between those two commands. Then pick the 8 claims a reader would rely on most, write them to `claims.json`, and send the fact-check prompt. Put its counts in `fact_check` in `research.json`, rerun `score.py`, and rerun the `score` command above. Fix any error it finds. If reviewers can't be spawned, leave these fields out and say so; never fill them in yourself.

### 9. Measure the run and compare it

```bash
python3 scripts/session_usage.py <session.jsonl>
python3 scripts/track.py compare <previous.json> scored.json
```

Session logs are under `~/.claude/projects/`. Put minutes, web calls and total tokens in `run_metrics`. If you can't read the log, leave them out. Total tokens include cached reads, so don't call them billed cost. Skip `compare` on a first run.

### 10. Build, check and publish

Add the headline, reasons, case against, checks, limits and run log to `scored.json`, then run:

```bash
python3 scripts/build_page.py scored.json report.html
```

`build_page.py` refuses a file with missing fields. Then check the page once: use the Artifact tool's preview or `ArtifactCheck` where available, otherwise a screenshot. Confirm the tool table and chart really rendered, since a script error leaves a blank page that still publishes. Recompute two or three totals against the script output. If you can't look at the page, say so in your reply. Publish `report.html` with the Artifact tool, using `icon: "chart"`.

The artifact is private until the user shares it, so tell them that if it's meant for someone else.

Finally, add the link as `artifact_url` and save the run:

```bash
python3 scripts/track.py save scored.json
```

This keeps the run and one history row in `~/.claude/tool-shootout/`, so the next run can compare against it even after this folder is gone. `track.py history "<use case>"` prints the trend.

## What to write

- **Headline:** the answer as a sentence, naming the pick.
- **Why:** three or four reasons tied to the user's words.
- **Case against:** the strongest evidence against the pick, with its source.
- **Pick something else if:** the condition from the flip tests, in plain language.
- **Limits:** every source that failed, how many comments and ratings the scores rest on, which ratings are unverified snippets, and any legal, consent or security duty the tool brings.

If the tool records people, stores credentials or handles regulated data, say what the user must check before relying on it.

## Honesty rules

- Separate **measured** counts from **judgement** scores, and label both.
- Call it a tie when the gap is under 0.5, and name the side it leans to.
- Never present a score to two decimals as precision. It's a fixed calculation on rough inputs.
- Credit the losing tools with what they do better.
- If a step failed or used a workaround, report it.

## Final reply

Give the artifact link, a table of the top four, the key numbers (winner total, lead, weight tests won, evidence strength, fact-check result, and any change since the last run), why the pick won, the checks the user must do, and how far to trust the scores. State anything you couldn't verify, including an unviewed page.
