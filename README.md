# claude-skills

A collection of my Claude skills. Each skill lives in its own folder under `skills/`.

## Skills

| Skill | What it does |
|---|---|
| [compare-and-review](skills/compare-and-review) | Runs the same task with and without a skill, gets a blind review of both outputs, measures time and tokens, and publishes a comparison with a verdict. |
| [debate-partner](skills/debate-partner) | Runs a structured debate on any question or idea, between two isolated agents or between an agent and you, then a blind judge checks sources, scores both sides and gives a verdict. |
| [tool-shootout](skills/tool-shootout) | Finds the top 15 tools for a use case, checks what each one really does, scores public feedback out of 10, and publishes an interactive comparison with tracked numbers and a recommendation. |
| [instagram-feed-audit-and-improve](skills/instagram-feed-audit-and-improve) | Audits your own Instagram feed, improves it toward topics you choose with your own signals, or does both and reports a blind before and after. It runs only what you ask for. |

## Install

Copy a skill folder into `~/.claude/skills/`:

```bash
cp -R skills/compare-and-review ~/.claude/skills/
```

## Contributing

`main` only accepts changes through a pull request.
