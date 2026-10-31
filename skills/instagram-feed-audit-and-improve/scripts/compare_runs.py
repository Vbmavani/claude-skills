#!/usr/bin/env python3
"""Blind audit runs for rating, then score the ratings with noise estimates."""
import argparse
import json
import math
import random
from collections import defaultdict
from pathlib import Path

LABELS = {"on_goal", "keep", "off_goal", "unclear"}
Z = 1.96


def read_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_run(path):
    """Read a run, keeping one row per item and any flag set on a duplicate."""
    items = {}
    for row in read_jsonl(path):
        missing = {"surface", "key"} - row.keys()
        if missing:
            raise SystemExit(f"{path}: row is missing {sorted(missing)}")
        item_id = (row["surface"], row["key"])
        seen = items.setdefault(item_id, row)
        for flag in ("suggested", "ad"):
            seen[flag] = bool(seen.get(flag) or row.get(flag))
    return items


def blind(args):
    if args.key.resolve().parent == args.out.resolve().parent:
        raise SystemExit("--key must be in a different folder from --out")
    runs = [("before", index, load_run(path)) for index, path in enumerate(args.before)]
    runs += [("after", index, load_run(path)) for index, path in enumerate(args.after or [])]

    unique = {}
    for _, _, items in runs:
        for item_id, row in items.items():
            unique.setdefault(item_id, row)

    rng = random.SystemRandom()
    order = list(unique)
    rng.shuffle(order)
    blind_ids = {item_id: f"i{index:05d}" for index, item_id in enumerate(order)}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for item_id in order:
            row = unique[item_id]
            public = {name: row.get(name, "") for name in ("surface", "author", "caption", "audio")}
            handle.write(json.dumps({"blind_id": blind_ids[item_id], **public}, ensure_ascii=False) + "\n")

    key = [
        {
            "group": group,
            "run": index,
            "items": [
                {"blind_id": blind_ids[item_id], "surface": item_id[0], "suggested": row["suggested"], "ad": row["ad"]}
                for item_id, row in items.items()
            ],
        }
        for group, index, items in runs
    ]
    args.key.parent.mkdir(parents=True, exist_ok=True)
    args.key.write_text(json.dumps(key), encoding="utf-8")
    print(f"Wrote {len(order)} unique items to {args.out}. Keep {args.key} away from the rater.")


def wilson(hits, total):
    """Return the 95% Wilson interval for a share."""
    if not total:
        return 0.0, 0.0
    share = hits / total
    denominator = 1 + Z * Z / total
    centre = share + Z * Z / (2 * total)
    margin = Z * math.sqrt(share * (1 - share) / total + Z * Z / (4 * total * total))
    return max(0.0, (centre - margin) / denominator), min(1.0, (centre + margin) / denominator)


def tally(items, ratings):
    """Count one run for one surface. Ads are excluded from the share."""
    counts = defaultdict(int)
    for item in items:
        counts["items"] += 1
        counts["suggested"] += item["suggested"]
        if item["ad"]:
            counts["ads"] += 1
            continue
        counts["rated"] += 1
        counts[ratings[item["blind_id"]]] += 1
    counts["share"] = counts["on_goal"] / counts["rated"] if counts["rated"] else 0.0
    counts["low"], counts["high"] = wilson(counts["on_goal"], counts["rated"])
    return dict(counts)


def verdict(before, after):
    """Compare the mean of the runs, using baseline spread when there is any."""
    base = sum(run["share"] for run in before) / len(before)
    last = sum(run["share"] for run in after) / len(after)
    change = last - base

    def variance(runs):
        return sum(run["share"] * (1 - run["share"]) / max(run["rated"], 1) for run in runs) / len(runs) ** 2

    margin = Z * math.sqrt(variance(before) + variance(after))
    spread = max(run["share"] for run in before) - min(run["share"] for run in before)
    noise = abs(change) <= max(margin, spread)
    return {"change": change, "margin": margin, "baseline_spread": spread, "within_noise": noise, "baselines": len(before)}


def score(args):
    ratings = {}
    for row in read_jsonl(args.ratings):
        if row.get("label") not in LABELS:
            raise SystemExit(f"Bad label in {row}")
        ratings[row["blind_id"]] = row["label"]

    key = json.loads(args.key.read_text(encoding="utf-8"))
    needed = {item["blind_id"] for run in key for item in run["items"] if not item["ad"]}
    missing = needed - ratings.keys()
    if missing:
        raise SystemExit(f"{len(missing)} items have no rating, for example {sorted(missing)[:3]}")

    report = {}
    for surface in sorted({item["surface"] for run in key for item in run["items"]}):
        runs = {"before": [], "after": []}
        for run in key:
            items = [item for item in run["items"] if item["surface"] == surface]
            runs[run["group"]].append(tally(items, ratings))
        report[surface] = dict(runs)
        if runs["before"] and runs["after"]:
            report[surface]["comparison"] = verdict(runs["before"], runs["after"])
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    blind_parser = commands.add_parser("blind")
    blind_parser.add_argument("--before", required=True, nargs="+", type=Path)
    blind_parser.add_argument("--after", nargs="+", type=Path)
    blind_parser.add_argument("--out", required=True, type=Path)
    blind_parser.add_argument("--key", required=True, type=Path)
    blind_parser.set_defaults(run=blind)

    score_parser = commands.add_parser("score")
    score_parser.add_argument("--ratings", required=True, type=Path)
    score_parser.add_argument("--key", required=True, type=Path)
    score_parser.set_defaults(run=score)

    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
