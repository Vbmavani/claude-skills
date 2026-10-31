# Blind review prompt

Fill in the folder path, then send this to a fresh reviewer. Adjust step 4 to the task, and drop it if the outputs make no factual claims.

```text
Blind review task: compare two outputs written from the same brief. Don't use any skill or plugin.

Folder: <absolute path to the review folder>

Read only files in that folder, and don't list its parent. Nothing is sent to anyone.

1. Read brief.md first. Before opening the outputs, write down 8 to 10 weighted criteria (weights total 100) for what would make the output most useful and trustworthy for the person in the brief.
2. Read set-x.md and set-y.md.
3. Score each from 0 to 10 on every criterion, with one sentence of evidence quoting the output. Give each a weighted total out of 100.
4. Fact-check: pick the 8 most decision-relevant sourced claims from each output, open each source, and mark each supported, partly supported, unsupported or source unavailable. Report the counts and name any errors.
5. Count, using a script rather than by eye, the measures that matter for this task, such as words, sources, or items produced.
6. Check each output against the brief: does it meet every requirement, and does it invent anything? Say "none" if none.
7. Compare the main conclusions. Note where they disagree and which looks better supported.
8. Give a final verdict: which one you'd use, your percentage split out of 100, and the single biggest reason you could be wrong.
9. Say what you'd take from each to make one best version.

Label every score and percentage as judgement. Only counts and fact-check results are measured.

Save the complete result to comparison.md in that folder.
```
