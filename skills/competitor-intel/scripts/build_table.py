#!/usr/bin/env python3
"""Merge tier research JSON files, apply code-check statuses for our product, render the filterable HTML table.

Usage:
  python3 -I build_table.py --inputs tier_top.json tier_medium.json tier_peer.json \
      --status code_check.json --meta meta.json --out 2026-10-31_competitor-intel_v1.html

Inputs
  tier_*.json  : arrays of rows, schema in references/row-schema.md
  code_check.json : {"rules":[{"competitor":"Zenoti","finding_starts":"Zenoti has a large",
                      "group":"Missing|Partial|Already built","status":"evidence + file:line"}],
                     "area_rules":[{"feature_area":"WhatsApp","group":"Partial","status":"..."}]}
  meta.json    : {"title","subtitle","product","eyebrow","generated","callout"(html),"takeaways":[{"h","p"}],"footer"(html)}
Exits non-zero on schema errors so a broken dataset never ships.
"""
import argparse, json, sys, collections
from pathlib import Path

REQUIRED = ["competitor", "tier", "dimension", "feature_area", "finding", "our_action", "source_url", "confidence"]
DIMENSIONS = {"advantage", "gap", "stand_out", "psychology"}
GROUPS = {"Missing", "Partial", "Already built"}


def load_rows(paths):
    rows, errors = [], []
    for p in paths:
        data = json.loads(Path(p).read_text())
        if not isinstance(data, list):
            errors.append(f"{p}: top level must be a list")
            continue
        for i, r in enumerate(data):
            missing = [k for k in REQUIRED if not str(r.get(k, "")).strip()]
            if missing:
                errors.append(f"{p}[{i}] missing {missing}")
            if r.get("dimension") not in DIMENSIONS:
                errors.append(f"{p}[{i}] bad dimension {r.get('dimension')!r}")
            if r.get("confidence") not in {"verified", "unverified"}:
                errors.append(f"{p}[{i}] bad confidence {r.get('confidence')!r}")
            rows.append(r)
    return rows, errors


def apply_status(rows, status):
    used = collections.Counter()
    for r in rows:
        r.setdefault("our_status", "")
        r.setdefault("our_status_group", "")
        for i, rule in enumerate(status.get("rules", [])):
            if r["competitor"] == rule["competitor"] and r["finding"].startswith(rule["finding_starts"]):
                r["our_status"], r["our_status_group"] = rule["status"], rule["group"]
                used[i] += 1
                break
        else:
            for rule in status.get("area_rules", []):
                if r["feature_area"] == rule["feature_area"]:
                    r["our_status"], r["our_status_group"] = rule["status"], rule["group"]
                    break
    unused = [rule["finding_starts"] for i, rule in enumerate(status.get("rules", [])) if not used[i]]
    bad = [g for g in {x.get("group") for x in status.get("rules", []) + status.get("area_rules", [])} if g not in GROUPS]
    return unused, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--status")
    ap.add_argument("--meta", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template", default=str(Path(__file__).resolve().parent.parent / "assets" / "table_template.html"))
    a = ap.parse_args()

    rows, errors = load_rows(a.inputs)
    if errors:
        print("Schema errors:\n  " + "\n  ".join(errors[:40]), file=sys.stderr)
        sys.exit(1)
    if a.status:
        unused, bad = apply_status(rows, json.loads(Path(a.status).read_text()))
        if bad:
            print(f"Unknown status groups: {bad}", file=sys.stderr); sys.exit(1)
        if unused:
            print(f"WARNING: {len(unused)} status rules matched no row: {unused}", file=sys.stderr)
    for i, r in enumerate(rows):
        r["id"] = i

    meta = json.loads(Path(a.meta).read_text())
    for cap in meta.get("capabilities", []):
        if cap.get("status") not in {"Built", "Partial", "Missing"}:
            print(f"Bad capability status: {cap}", file=sys.stderr); sys.exit(1)
    payload = {"rows": rows, **{k: meta.get(k) for k in
               ("generated", "callout", "takeaways", "footer", "stages", "capabilities", "levers")}}
    html = Path(a.template).read_text()
    html = html.replace("__TITLE__", meta["title"]).replace("__SUBTITLE__", meta.get("subtitle", ""))
    html = html.replace("__PRODUCT__", meta.get("product", "Our product")).replace(
        "__EYEBROW__", meta.get("eyebrow", "Competitor intelligence")).replace(
        "__JOURNEY__", meta.get("journey_title", "The customer journey, stage by stage"))
    html = html.replace("/*__DATA__*/", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
    Path(a.out).write_text(html)

    c = collections.Counter
    print(f"rows={len(rows)} competitors={len({r['competitor'] for r in rows})}")
    print("by tier:", dict(c(r["tier"] for r in rows)))
    print("by lens:", dict(c(r["dimension"] for r in rows)))
    print("by status:", dict(c(r["our_status_group"] or "-" for r in rows)))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
