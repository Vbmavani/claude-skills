#!/usr/bin/env python3
"""Merge tier research JSON files, apply gap-check statuses for our product, render the filterable HTML table.

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
Research text comes from the web, so nothing in it may reach the page as markup.
"""
import argparse, html as htmllib, json, re, sys, collections
from pathlib import Path

REQUIRED = ["competitor", "tier", "dimension", "feature_area", "finding", "our_action", "source_url", "confidence"]
TIERS = {"Top", "Medium", "Peer"}
DIMENSIONS = {"advantage", "gap", "stand_out", "psychology"}
GROUPS = {"Missing", "Partial", "Already built"}
SAFE_TAGS = {"b", "strong", "i", "em", "br", "code", "a"}
SAFE_LINK = re.compile(r'\s+href="https?://[^"<>]*"(\s+target="_blank")?(\s+rel="[^"<>]*")?\s*')


def die(msg):
    sys.exit(f"Error: {msg}")


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        die(f"cannot read {path}: {e.strerror}")
    except ValueError as e:
        die(f"{path} is not valid JSON: {e}")


def load_rows(paths):
    rows, errors = [], []
    for p in paths:
        data = read_json(p)
        if not isinstance(data, list):
            errors.append(f"{p}: top level must be a list")
            continue
        for i, r in enumerate(data):
            if not isinstance(r, dict):
                errors.append(f"{p}[{i}] must be an object")
                continue
            missing = [k for k in REQUIRED if not str(r.get(k, "")).strip()]
            if missing:
                errors.append(f"{p}[{i}] missing {missing}")
            if r.get("tier") not in TIERS:
                errors.append(f"{p}[{i}] bad tier {r.get('tier')!r}")
            if r.get("dimension") not in DIMENSIONS:
                errors.append(f"{p}[{i}] bad dimension {r.get('dimension')!r}")
            if r.get("confidence") not in {"verified", "unverified"}:
                errors.append(f"{p}[{i}] bad confidence {r.get('confidence')!r}")
            if r.get("dimension") == "psychology" and not str(r.get("psychology", "")).strip():
                errors.append(f"{p}[{i}] psychology row has an empty psychology field")
            if not re.match(r"https?://", str(r.get("source_url", "")), re.I):
                errors.append(f"{p}[{i}] source_url must start with http:// or https://")
            rows.append(r)
    return rows, errors


def apply_status(rows, status):
    used = collections.Counter()
    for r in rows:
        r["our_status"], r["our_status_group"] = "", ""
        for i, rule in enumerate(status.get("rules", [])):
            if r.get("competitor") == rule.get("competitor") and str(r.get("finding", "")).startswith(rule.get("finding_starts", "\0")):
                r["our_status"], r["our_status_group"] = rule.get("status", ""), rule.get("group", "")
                used[i] += 1
                break
        else:
            for rule in status.get("area_rules", []):
                if r.get("feature_area") == rule.get("feature_area"):
                    r["our_status"], r["our_status_group"] = rule.get("status", ""), rule.get("group", "")
                    break
    unused = [rule.get("finding_starts") for i, rule in enumerate(status.get("rules", [])) if not used[i]]
    bad = [g for g in {x.get("group") for x in status.get("rules", []) + status.get("area_rules", [])} if g not in GROUPS]
    return unused, bad


def check_meta(meta):
    errors = []
    if not str(meta.get("title", "")).strip():
        errors.append("meta.json needs a title")
    stage_ids = {s.get("id") for s in meta.get("stages") or []}
    for kind, items in (("capability", meta.get("capabilities") or []), ("lever", meta.get("levers") or [])):
        for item in items:
            try:
                re.compile(item.get("match") or "")
            except re.error as e:
                errors.append(f"{kind} {item.get('name')!r}: bad match regex: {e}")
            if not item.get("match"):
                errors.append(f"{kind} {item.get('name')!r}: missing match regex")
    for cap in meta.get("capabilities") or []:
        if cap.get("status") not in {"Built", "Partial", "Missing"}:
            errors.append(f"bad capability status: {cap.get('name')!r} {cap.get('status')!r}")
        if cap.get("stage") not in stage_ids:
            errors.append(f"capability {cap.get('name')!r}: unknown stage {cap.get('stage')!r}")
    for key in ("callout", "footer"):
        for name, attrs in re.findall(r"<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)([^>]*)", str(meta.get(key) or "")):
            ok = name.lower() in SAFE_TAGS and (not attrs.strip() or (name.lower() == "a" and SAFE_LINK.fullmatch(attrs)))
            if not ok:
                errors.append(f"meta.json {key}: tag <{name}{attrs}> is not allowed")
    return errors


def page_text(s):
    """Escape text for the template: it lands in HTML and in JS strings that reach innerHTML."""
    return htmllib.escape(str(s)).replace("`", "&#96;").replace("$", "&#36;").replace("\\", "&#92;")


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
    status = read_json(a.status) if a.status else {}
    if not isinstance(status, dict):
        die(f"{a.status}: top level must be an object")
    unused, bad = apply_status(rows, status)
    if bad:
        print(f"Unknown status groups: {bad}", file=sys.stderr); sys.exit(1)
    if unused:
        print(f"WARNING: {len(unused)} status rules matched no row: {unused}", file=sys.stderr)
    for i, r in enumerate(rows):
        r["id"] = i

    meta = read_json(a.meta)
    if not isinstance(meta, dict):
        die(f"{a.meta}: top level must be an object")
    errors = check_meta(meta)
    if errors:
        print("Meta errors:\n  " + "\n  ".join(errors[:40]), file=sys.stderr)
        sys.exit(1)
    payload = {"rows": rows, **{k: meta.get(k) for k in
               ("generated", "callout", "takeaways", "footer", "stages", "capabilities", "levers")}}
    html = Path(a.template).read_text(encoding="utf-8")
    html = html.replace("__TITLE__", page_text(meta["title"])).replace("__SUBTITLE__", page_text(meta.get("subtitle", "")))
    html = html.replace("__PRODUCT__", page_text(meta.get("product", "Our product"))).replace(
        "__EYEBROW__", page_text(meta.get("eyebrow", "Competitor intelligence"))).replace(
        "__JOURNEY__", page_text(meta.get("journey_title", "The customer journey, stage by stage")))
    html = html.replace("/*__DATA__*/", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
    Path(a.out).write_text(html, encoding="utf-8")

    c = collections.Counter
    print(f"rows={len(rows)} competitors={len({r['competitor'] for r in rows})}")
    print("by tier:", dict(c(r["tier"] for r in rows)))
    print("by lens:", dict(c(r["dimension"] for r in rows)))
    print("by status:", dict(c(r["our_status_group"] or "-" for r in rows)))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
