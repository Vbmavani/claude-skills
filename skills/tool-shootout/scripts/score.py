#!/usr/bin/env python3
"""Score a research file and test how stable the winner is.

  score.py research.json scored.json

references/scoring.md explains the method; references/input-schema.md the input.
"""
import json, random, sys

BASE = 7.0
STAR_M, HN_M = 50, 10
FAMILY_WEIGHTS = {"g2": .35, "hn": .30, "alternativeto": .10, "producthunt": .10, "trustpilot": .05,
                  "gartner": .05, "appstore": .05, "trustradius": .05}
FAMILY = {"g2": "g2", "capterra": "g2", "getapp": "g2", "softwareadvice": "g2"}
TIE = 0.5


def stars(r):
    return r["rating"] * 5 / r.get("scale", 5)


def family(platform):
    return FAMILY.get(platform, platform)


def public_scores(tools):
    by_platform = {}
    for t in tools:
        for r in t.get("ratings", []):
            by_platform.setdefault(r["platform"], []).append(stars(r))
    means = {p: sum(v) / len(v) for p, v in by_platform.items()}
    h = [t.get("hn", {}) for t in tools]
    pos, mix, neg = (sum(x.get(k, 0) for x in h) for k in ("pos", "mix", "neg"))
    pooled = (pos + .5 * mix) / (pos + mix + neg) if pos + mix + neg else .5

    for t in tools:
        fams = {}
        for r in t.get("ratings", []):
            c, v = means[r["platform"]], r["count"]
            s = (v * stars(r) + STAR_M * c) / (v + STAR_M)
            fams.setdefault(family(r["platform"]), []).append((v, s - c))
        src = {f: min(10, max(0, BASE + 5 * sum(v * d for v, d in l) / sum(v for v, _ in l)))
               for f, l in fams.items() if sum(v for v, _ in l)}
        x = t.get("hn", {})
        n = x.get("pos", 0) + x.get("mix", 0) + x.get("neg", 0)
        if n:
            share = (x.get("pos", 0) + .5 * x.get("mix", 0)) / n
            src["hn"] = BASE + 10 * ((n * share + HN_M * pooled) / (n + HN_M) - pooled)
        weight = sum(FAMILY_WEIGHTS.get(f, .05) for f in src)
        t["public"] = sum(FAMILY_WEIGHTS.get(f, .05) * s for f, s in src.items()) / weight if src else None
        t["source_scores"] = {k: round(v, 2) for k, v in src.items()}
        t["confidence"] = confidence(t)
    return means, pooled


def confidence(t):
    def fams(rs):
        return len({family(r["platform"]) for r in rs})
    rs = t.get("ratings", [])
    live = [r for r in rs if r.get("verified")]
    if fams(live) >= 2 and sum(r["count"] for r in live) >= 100:
        return "High"
    if fams(rs) >= 2 and sum(r["count"] for r in rs) >= 100:
        return "Medium"
    return "Low"


def fit(t, weights, override=None):
    total = sum(weights.values()) or 1
    s = {**t["scores"], **(override or {})}
    return sum(weights[k] * s[k] for k in weights) / total


def total(t, weights, share, override=None):
    # A tool with no public evidence is judged on fit alone, never given a zero.
    f = fit(t, weights, override)
    return f if t["public"] is None else share * f + (1 - share) * t["public"]


def tier(t):
    return 0 if "fail" in t.get("gates", {}).values() else 1


def ranked(tools, weights, share, overrides=None):
    o = overrides or {}
    return sorted(tools, key=lambda t: (-tier(t), -total(t, weights, share, o.get(t["name"]))))


def assign_ranks(order, weights, share):
    leader, start = None, 1
    for i, t in enumerate(order, 1):
        v = total(t, weights, share)
        if leader is None or tier(leader) != tier(t) or total(leader, weights, share) - v >= TIE:
            leader, start = t, i
        t["rank"] = start
    for t in order:
        t["tied"] = sum(x["rank"] == t["rank"] for x in order) > 1


def sensitivity(tools, weights, share, worst):
    winner = ranked(tools, weights, share)[0]["name"]
    rng = random.Random(20261031)
    wins = {}
    runs = 1000
    for _ in range(runs):
        w = {k: v * rng.uniform(.8, 1.2) for k, v in weights.items()}
        n = ranked(tools, w, min(1, share * rng.uniform(.8, 1.2)))[0]["name"]
        wins[n] = wins.get(n, 0) + 1
    tests = [{"test": "Equal fit weights", "winner": ranked(tools, dict.fromkeys(weights, 1), share)[0]["name"]}]
    for k in weights:
        tests.append({"test": f"Drop {k}", "winner": ranked(tools, {**weights, k: 0}, share)[0]["name"]})
    for s in (.5, .3, .1, 0):
        tests.append({"test": f"Fit share {int(s * 100)}%", "winner": ranked(tools, weights, s)[0]["name"]})
    flips = []
    for pct in range(100, -1, -1):
        if ranked(tools, weights, pct / 100)[0]["name"] != winner:
            flips.append(f"Fit below about {pct + 1}% of the total")
            break
    base_sum = sum(weights.values())
    for k in weights:
        rest = base_sum - weights[k]
        for pct in range(round(weights[k] / base_sum * 100), 100):
            w = {x: v * (1 - pct / 100) / rest * base_sum for x, v in weights.items()} if rest else dict(weights)
            w[k] = pct / 100 * base_sum
            if ranked(tools, w, share)[0]["name"] != winner:
                flips.append(f"{k} above about {pct}% of fit")
                break
    if worst:
        o = ranked(tools, weights, share, worst)
        a, b = o[0], o[1]
        tests.append({"test": "Every uncertain score at its worst case", "winner": a["name"],
                      "scores": {x["name"]: round(total(x, weights, share, worst.get(x["name"])), 2) for x in (a, b)}})
    return {"runs": runs, "wins": wins, "winner_share": wins.get(winner, 0) / runs, "stable": wins.get(winner, 0) / runs >= .7,
            "tests": tests, "flips": flips}


def scorecard(data, order):
    """The numbers to track from run to run. Counts are measured, scores are judgement."""
    ratings = [r for t in order for r in t.get("ratings", [])]
    log = data.get("run_log", [])
    comments = sum(sum(t.get("hn", {}).get(k, 0) for k in ("pos", "mix", "neg")) for t in order)
    no_public = sum(t["public"] is None for t in order)
    conf = {c: sum(t["confidence"] == c for t in order) for c in ("High", "Medium", "Low")}
    ok = sum(r.get("status") == "ok" for r in log)
    verified = sum(bool(r.get("verified")) for r in ratings)
    fact = data.get("fact_check") or {}
    checked = sum(fact.get(k, 0) for k in ("supported", "partly", "unsupported", "unavailable"))
    gap = order[0]["total"] - order[1]["total"] if len(order) > 1 else None
    # Each part runs 0 to 1, and the weights sit in references/scoring.md.
    strength = (30 * min(1, verified / max(1, len(ratings))) + 25 * min(1, comments / (5 * len(order)))
                + 20 * (ok / len(log) if log else 0) + 25 * (fact.get("supported", 0) / checked if checked else 0))
    return {"candidates": data.get("candidates_screened", len(order) + len(data.get("excluded", []))),
            "ranked": len(order), "pass_gates": sum(t["tier"] == 1 for t in order),
            "winner_total": order[0]["total"], "winner_gap": None if gap is None else round(gap, 2),
            "winner_stability_pct": round(data["sensitivity"]["winner_share"] * 100),
            "ratings": len(ratings), "reviews_behind_ratings": sum(r["count"] for r in ratings),
            "ratings_verified_pct": round(100 * verified / len(ratings)) if ratings else 0,
            "first_hand_comments": comments, "tools_without_public_evidence": no_public, "confidence": conf,
            "steps_tried": len(log), "steps_ok": ok, "steps_failed": sum(r.get("status") == "failed" for r in log),
            "evidence_strength": round(strength)}


def main(src, dst):
    data = json.load(open(src, encoding="utf-8"))
    pool = data["tools"]
    weights = {c["key"]: c["weight"] for c in data["criteria"]}
    share = data.get("fit_share", .7)
    for t in pool:
        missing = [k for k in weights if k not in t["scores"]]
        if missing:
            sys.exit(f"{t['name']}: no score for {missing}")
    means, pooled = public_scores(pool)
    tools = [t for t in pool if not t.get("pool_only")]
    for t in tools:
        t["fit"] = round(fit(t, weights), 3)
        t["total"] = round(total(t, weights, share), 3)
        t["tier"] = tier(t)
    order = ranked(tools, weights, share)
    assign_ranks(order, weights, share)
    data["tools"] = order
    data["pool_only"] = [{"name": t["name"], "fit": round(fit(t, weights), 2), "public": t["public"],
                          "total": round(total(t, weights, share), 2)} for t in pool if t.get("pool_only")]
    data["platform_means"] = {k: round(v, 3) for k, v in means.items()}
    data["hn_pooled_share"] = round(pooled, 3)
    data["sensitivity"] = sensitivity(order, weights, share, data.get("uncertain_scores"))
    data["scorecard"] = scorecard(data, order)
    json.dump(data, open(dst, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for t in order:
        pub = "none" if t["public"] is None else f"{t['public']:.2f}"
        print(f"{t['rank']}{'=' if t['tied'] else ' '} {t['name']}: fit {t['fit']:.2f}, public {pub}, total {t['total']:.2f}, {t['confidence']}")
    s = data["sensitivity"]
    print("Scorecard:", json.dumps(data["scorecard"]))
    print(f"Winner held {s['winner_share']:.0%} of {s['runs']} weight tests. Flips: {s['flips'] or 'none found'}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
