# claude-skills

A collection of my Claude skills. Each skill lives in its own folder under `skills/`.

## Skills

| Skill | What it does |
|---|---|
| [compare-and-review](skills/compare-and-review) | Runs the same task with and without a skill, gets a blind review of both outputs, measures time and tokens, and publishes a comparison with a verdict. |

## Install

Copy a skill folder into `~/.claude/skills/`:

```bash
cp -R skills/compare-and-review ~/.claude/skills/
```

## Contributing

`main` only accepts changes through a pull request. Before your first commit in a clone, turn on the pre-commit check:

```bash
git config core.hooksPath .githooks
```

The check blocks a commit that contains secrets or personal details. It runs local pattern checks, then an AI review of the staged changes with the `claude` CLI. If the review can't run, the commit is blocked.

It needs two things:

- A GitHub noreply address as your commit email.
- A personal terms file at `~/.config/claude-skills/personal-terms.txt`, with one term per line and `#` for comments. Keep this file out of the repo, or set `PERSONAL_TERMS_FILE` to use another location.
