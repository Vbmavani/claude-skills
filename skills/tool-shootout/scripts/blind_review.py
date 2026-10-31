#!/usr/bin/env python3
"""Have a fresh reviewer rescore fit without seeing names or scores, then measure the agreement.

  blind_review.py pack <scored.json> --out <folder>/pack.json --key <elsewhere>/key.json
  blind_review.py score <scored.json> --rescored <folder>/rescored.json --key <elsewhere>/key.json

Keep the key outside the reviewer's folder.
"""
import argparse, json, pathlib, random


def load(p):
    return json.load(open(p, encoding="utf-8"))


def pack(a):
    out, key = pathlib.Path(a.out).resolve(), pathlib.Path(a.key).resolve()
    if out.parent == key.parent:
        raise SystemExit("--key must be in a different folder from --out")
    d = load(a.scored)
    tools = list(d["tools"])
    random.SystemRandom().shuffle(tools)
    mapping = {f"tool-{i + 1:02d}": t["name"] for i, t in enumerate(tools)}
    names = [t["name"] for t in tools]

    def scrub(text):
        text = str(text or "")
        for n in names:
            text = text.replace(n, "this tool")
        return text

    public = {"use_case": d["use_case"], "criteria": [{k: c[k] for k in ("key", "label", "anchors")} for c in d["criteria"]],
              "tools": [{"code": code, "category": t.get("category"), "price": scrub(t.get("price")), "storage": scrub(t.get("storage")),
                         "capabilities": {k: scrub(v.get("text")) for k, v in t.get("capabilities", {}).items()},
                         "evidence": scrub(t.get("evidence"))} for code, t in zip(mapping, tools)]}
    out.parent.mkdir(parents=True, exist_ok=True)
    key.parent.mkdir(parents=True, exist_ok=True)
    json.dump(public, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    json.dump(mapping, open(key, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"Wrote {len(tools)} blinded tools to {out}")


def score(a):
    d, rescored, mapping = load(a.scored), load(a.rescored), load(a.key)
    weights = {c["key"]: c["weight"] for c in d["criteria"]}
    tools = {t["name"]: t for t in d["tools"]}
    gaps, per_tool, theirs = [], {}, {}
    for code, s in rescored.items():
        t = tools[mapping[code]]
        g = [abs(s[k] - t["scores"][k]) for k in weights]
        gaps += g
        per_tool[t["name"]] = round(sum(g) / len(g), 2)
        theirs[t["name"]] = sum(weights[k] * s[k] for k in weights) / sum(weights.values())
    def pick(fits):
        return max(d["tools"], key=lambda t: (t["tier"], fits[t["name"]]))["name"]
    mine = {n: t["fit"] for n, t in tools.items()}
    same = pick(theirs) == pick(mine)
    d["review"] = {"tools_rescored": len(rescored), "mean_gap": round(sum(gaps) / len(gaps), 2),
                   "within_one_point_pct": round(100 * sum(x <= 1 for x in gaps) / len(gaps)),
                   "same_top_fit": same, "reviewer_top_fit": pick(theirs),
                   "biggest_gaps": sorted(per_tool.items(), key=lambda x: -x[1])[:3]}
    json.dump(d, open(a.scored, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(json.dumps(d["review"]))


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("pack"); s.add_argument("scored"); s.add_argument("--out", required=True); s.add_argument("--key", required=True); s.set_defaults(fn=pack)
s = sub.add_parser("score"); s.add_argument("scored"); s.add_argument("--rescored", required=True); s.add_argument("--key", required=True); s.set_defaults(fn=score)
a = p.parse_args()
a.fn(a)
