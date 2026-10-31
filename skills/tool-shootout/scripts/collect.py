#!/usr/bin/env python3
"""Pull free, keyless evidence for a tool. Prints JSON to stdout.

  collect.py hn "Tool Name" [--months 24] [--max 50]
  collect.py github owner/repo
  collect.py apple --id 123456 | --term "Tool Name" [--entity macSoftware]

A refused request is reported in the output and never retried with other
headers, so the caller can record it as a gap.
"""
import argparse, datetime, html, json, os, re, sys, urllib.error, urllib.parse, urllib.request

UA = "tool-shootout/1.0 (Claude skill)"


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


def hn(a):
    since = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=a.months * 30)).timestamp())
    q = urllib.parse.urlencode({"query": f'"{a.name}"', "tags": "comment", "hitsPerPage": a.max,
                                "numericFilters": f"created_at_i>{since}"})
    data, err = get(f"https://hn.algolia.com/api/v1/search_by_date?{q}")
    if err:
        return {"source": "hn", "tool": a.name, "error": err}
    return {"source": "hn", "tool": a.name, "total_hits": data.get("nbHits"), "comments": [
        {"url": f"https://news.ycombinator.com/item?id={h['objectID']}", "author": h.get("author"),
         "date": (h.get("created_at") or "")[:10], "text": clean(h.get("comment_text"))[:1200]}
        for h in data.get("hits", [])]}


def github(a):
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    repo, err = get(f"https://api.github.com/repos/{a.repo}", headers)
    if err:
        return {"source": "github", "repo": a.repo, "error": err}
    rel, rel_err = get(f"https://api.github.com/repos/{a.repo}/releases/latest", headers)
    return {"source": "github", "repo": a.repo, "stars": repo.get("stargazers_count"),
            "pushed_at": repo.get("pushed_at"), "archived": repo.get("archived"),
            "license": (repo.get("license") or {}).get("spdx_id"),
            "latest_release": None if rel_err else {"tag": rel.get("tag_name"), "date": rel.get("published_at")}}


def apple(a):
    if a.id:
        url = f"https://itunes.apple.com/lookup?id={a.id}&country={a.country}"
    else:
        q = urllib.parse.urlencode({"term": a.term, "entity": a.entity, "country": a.country, "limit": 5})
        url = f"https://itunes.apple.com/search?{q}"
    data, err = get(url)
    if err:
        return {"source": "apple", "error": err}
    return {"source": "apple", "results": [
        {"name": r.get("trackName"), "seller": r.get("sellerName"), "kind": r.get("kind"), "url": r.get("trackViewUrl"),
         "rating": r.get("averageUserRating"), "count": r.get("userRatingCount"), "version": r.get("version"),
         "updated": r.get("currentVersionReleaseDate"), "price": r.get("formattedPrice")}
        for r in data.get("results", [])]}


p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
s = sub.add_parser("hn"); s.add_argument("name"); s.add_argument("--months", type=int, default=24); s.add_argument("--max", type=int, default=50); s.set_defaults(fn=hn)
s = sub.add_parser("github"); s.add_argument("repo"); s.set_defaults(fn=github)
s = sub.add_parser("apple"); s.add_argument("--id"); s.add_argument("--term"); s.add_argument("--entity", default="macSoftware"); s.add_argument("--country", default="us"); s.set_defaults(fn=apple)
a = p.parse_args()
result = a.fn(a)
print(json.dumps(result, indent=1, ensure_ascii=False))
sys.exit(1 if "error" in result else 0)
