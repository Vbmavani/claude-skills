#!/usr/bin/env python3
"""Fill the report template from a scored file and check the result.

  build_page.py scored.json out.html

Exits non-zero when something the page promises is missing.
"""
import json, pathlib, re, sys

TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "assets" / "report_template.html"
REQUIRED = ["title", "use_case", "date", "headline", "lede", "why", "case_against", "limits", "run_log"]


def main(src, dst):
    data = json.load(open(src, encoding="utf-8"))
    errors = [f"missing field: {k}" for k in REQUIRED if not data.get(k)]
    tools = data.get("tools", [])
    if "scorecard" not in data:
        errors.append("not scored: run score.py first")
    for t in tools:
        for k in ("name", "url", "price", "maintenance", "praise", "complaint"):
            if not t.get(k):
                errors.append(f"{t.get('name', '?')}: missing {k}")
        for r in t.get("ratings", []):
            if not r.get("url"):
                errors.append(f"{t['name']}: rating on {r['platform']} has no source URL")
    if errors:
        sys.exit("\n".join(errors))
    if len(tools) != 15:
        print(f"Note: {len(tools)} ranked tools, not 15. Say why on the page.")
    # Evidence comes from the web, so keep it from closing the script tag.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    page = TEMPLATE.read_text(encoding="utf-8")
    title = re.sub(r"[<>&]", "", data["title"])
    page = page.replace("__TITLE__", title).replace("__DATA__", payload)
    pathlib.Path(dst).write_text(page, encoding="utf-8")
    print(f"Wrote {dst}, {len(page) // 1024} KB, {len(tools)} tools")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
