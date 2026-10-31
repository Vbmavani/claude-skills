#!/usr/bin/env python3
"""Keep a history of runs and show what changed between them.

  track.py compare <previous.json> <scored.json>     adds a "changes" block to scored.json
  track.py save <scored.json> [--home DIR]           stores the run and appends one history row
  track.py latest "<use case>" [--home DIR]          prints the newest saved run for that use case
  track.py history "<use case>" [--home DIR]         prints every run as a table
"""
import argparse, json, pathlib, re, shutil

HOME = pathlib.Path.home() / ".claude" / "tool-shootout"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def load(path):
    return json.load(open(path, encoding="utf-8"))


def fmt(old, new, digits=2):
    if old is None and new is None:
        return "none"
    if old is None or new is None:
        return f"{'none' if old is None else format(old, f'.{digits}f')} → {'none' if new is None else format(new, f'.{digits}f')}"
    return f"{new:.{digits}f} ({new - old:+.{digits}f})"


def compare(a):
    old, new = load(a.previous), load(a.current)
    before = {t["name"]: t for t in old["tools"]}
    after = {t["name"]: t for t in new["tools"]}
    rows = []
    for name, t in after.items():
        p = before.get(name)
        if not p:
            rows.append({"tool": name, "rank": f"new at {t['rank']}", "total": f"{t['total']:.2f}",
                         "public": "none" if t["public"] is None else f"{t['public']:.2f}", "note": "New this run"})
            continue
        moved = p["rank"] - t["rank"]
        notes = [] if t.get("price") == p.get("price") else [f"Price: {p.get('price')} → {t.get('price')}"]
        if moved or abs(t["total"] - p["total"]) >= .1 or notes:
            rows.append({"tool": name, "rank": f"{p['rank']} → {t['rank']}", "total": fmt(p["total"], t["total"]),
                         "public": fmt(p["public"], t["public"]), "note": "; ".join(notes)})
    for name, p in before.items():
        if name not in after:
            rows.append({"tool": name, "rank": f"{p['rank']} → out", "total": f"{p['total']:.2f}",
                         "public": "none" if p["public"] is None else f"{p['public']:.2f}", "note": "Dropped this run"})
    w_old, w_new = old["tools"][0]["name"], new["tools"][0]["name"]
    summary = f"Winner stayed {w_new}." if w_old == w_new else f"Winner changed from {w_old} to {w_new}."
    summary += f" {len(rows)} of {len(after)} tools moved, were added or left. Scores compare only if weights match."
    if {c["key"]: c["weight"] for c in old["criteria"]} != {c["key"]: c["weight"] for c in new["criteria"]}:
        summary += " The weights differ between these runs, so score changes may come from that."
    new["changes"] = {"previous_date": old.get("date"), "summary": summary, "rows": rows}
    json.dump(new, open(a.current, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(summary)
    for r in rows:
        print(f"  {r['tool']}: rank {r['rank']}, total {r['total']} {r['note']}")


def save(a):
    d = load(a.scored)
    folder = pathlib.Path(a.home) / slug(d["use_case"])
    (folder / "runs").mkdir(parents=True, exist_ok=True)
    dest = folder / "runs" / f"{d['date']}.json"
    n = 2
    while dest.exists():
        dest = folder / "runs" / f"{d['date']}-{n}.json"
        n += 1
    shutil.copyfile(a.scored, dest)
    c = d["scorecard"]
    row = {"date": d["date"], "run": dest.name, "winner": d["tools"][0]["name"], "url": d.get("artifact_url"),
           **{k: c[k] for k in ("winner_total", "winner_gap", "winner_stability_pct", "evidence_strength", "ranked",
                                "ratings_verified_pct", "first_hand_comments")}}
    with open(folder / "history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Saved {dest}")


def rows(a):
    path = pathlib.Path(a.home) / slug(a.use_case) / "history.jsonl"
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def latest(a):
    r = rows(a)
    if r:
        print(pathlib.Path(a.home) / slug(a.use_case) / "runs" / r[-1]["run"])


def history(a):
    print("date | winner | total | lead | stability | evidence | tools")
    for r in rows(a):
        print(f"{r['date']} | {r['winner']} | {r['winner_total']:.2f} | {r['winner_gap']} | {r['winner_stability_pct']}% | {r['evidence_strength']}/100 | {r['ranked']}")


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("compare"); s.add_argument("previous"); s.add_argument("current"); s.set_defaults(fn=compare)
for name, fn, arg in (("save", save, "scored"), ("latest", latest, "use_case"), ("history", history, "use_case")):
    s = sub.add_parser(name); s.add_argument(arg); s.add_argument("--home", default=str(HOME)); s.set_defaults(fn=fn)
a = p.parse_args()
a.fn(a)
