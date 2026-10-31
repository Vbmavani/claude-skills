# claude-skills

A collection of my Claude skills. Each skill lives in its own folder under `skills/`.

## Skills

| Skill | What it does |
|---|---|
| [compare-and-review](skills/compare-and-review) | Runs the same task with and without a skill, gets a blind review of both outputs, measures time and tokens, and publishes a comparison with a verdict. |
| [instagram-feed-improver](skills/instagram-feed-improver) | Improves your own Instagram feed toward topics you choose: audits it, steers it with your own signals, then re-audits the same way and reports before and after. |

## Install

Copy a skill folder into `~/.claude/skills/`:

```bash
cp -R skills/compare-and-review ~/.claude/skills/
```

## Contributing

`main` only accepts changes through a pull request.
