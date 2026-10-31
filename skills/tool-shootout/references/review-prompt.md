# Independent review prompts

Send each prompt to a fresh reviewer with no other context. Don't share your opinion or the ranking. Keep `key.json` outside the reviewer's folder and don't let it list the parent folder.

## Blind fit rescore

```text
Blind scoring task. Don't use any skill or plugin.

Folder: <absolute path to the review folder>

Read only pack.json in that folder. It describes tools by code, with names removed.
Score every tool from 0 to 10 on every criterion, using only the written anchors and the evidence given. Don't guess which product a code is. If the evidence doesn't support a higher score, give the lower one.

Save rescored.json in that folder as {"tool-01": {"<criterion key>": score, ...}, ...}.
```

## Fact check

```text
Fact-check task. Don't use any skill or plugin.

Read claims.json at <absolute path>. It lists the claims a reader would rely on most, each with its source URL.
Open each source and mark the claim supported, partly, unsupported or unavailable. Unavailable means the source wouldn't open; don't look for a way around that. Name each error in one sentence.

Save fact_check.json beside it as {"supported": n, "partly": n, "unsupported": n, "unavailable": n, "errors": ["..."]}.
```

Say on the page that the reviewers share a model family with the writer, so agreement isn't independent human opinion.
