# Debate against the user

The user is side A and a single subagent is side B. Everything else stays the same: the brief, the rounds, the transcript script and the blind judge.

## Setup

- Ask the user for their position in one or two sentences if it isn't clear.
- Offer one of three uses: **decide** (a real choice), **practice** (the opponent plays a named role, such as an investor or interviewer), or **swap sides** (the user defends what they disagree with).
- Save the user's position to `rounds/a-opening.md` word for word.
- Tell them they can say `end` at any point, and that the judge will score what exists by then.

## Running a round

1. Start side B with the opening prompt from `references/debater-prompts.md`, and add the opponent rules below. It can read `rounds/a-opening.md`, so it answers the user's real position.
2. Show the user side B's round in full.
3. Save the user's reply word for word to the next `a-` file, without tidying it. Pass that file's path to side B.
4. Repeat through closing. The user doesn't have to follow the headings or word limits.

If the user ends early, build the transcript from the rounds both sides finished.

## Opponent rules

Add this to each prompt for side B:

```text
You are arguing against a person, and agreeing to be polite would fail them. Stay on your position through the whole debate. Concede a point only when they give a better argument or new evidence. Repetition, confidence or frustration aren't reasons to concede. When you do concede, name what changed your mind and keep arguing the rest. Attack the argument, never the person.
```

Stay tough until the debate ends. Coaching comes after the judge's result.

If the user becomes distressed, or the topic turns out to be about their safety or wellbeing, stop the debate and respond to them as a person.

## The judge

Use the same prompt. The labels stay random. The judge may still guess who the human is from the writing style, so mention that in the report's `--note`.

Accept the user's claims marked "I'd estimate" or similar as estimates, and let the judge mark down what has no support, the same as for side B.

## Coaching notes

Once `judge.json` exists, write `coaching.md` from the transcript and the judge's result, then pass it to `build_report.py` with `--coaching`. Use these headings:

```markdown
## Your strongest point
## Your weakest assumption
## What you dodged
## What to find out next
```

Quote the user's actual words, and keep each section to 1 or 2 sentences.
