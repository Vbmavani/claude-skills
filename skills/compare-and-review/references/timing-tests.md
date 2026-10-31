# Timing tests

Use this when the question is speed, such as sequential work against parallel agents.

- **Run one test at a time.** Concurrent runs slow each other down and spoil the timing.
- **Clear shared state between runs,** such as open browser sessions, and don't start the next run until the last one has saved its result. Sessions can look idle while subagents still run.
- **Time from inside the run.** Have each run record `date +%s` at the start and end.
- **Test more than one size.** Small tasks hide scaling problems. Twenty parallel browsers failed where six worked.
- **Add a no-AI control.** A plain script doing the same work separates tool limits from agent overhead, and it usually explains the result.
- **Check correctness as well as speed.** A fast run that drops results hasn't won. Compare results across runs.
- **Report tokens too,** using `scripts/session_usage.py`.
- **Use bash for shell loops.** zsh doesn't split an unquoted list of words, which silently tests only one item.

Note anything that makes a run unclean, such as a failed first pass or batched work.
