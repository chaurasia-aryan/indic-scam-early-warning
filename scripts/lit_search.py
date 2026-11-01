"""Literature search against open scholarly APIs (OpenAlex, arXiv, Semantic Scholar, ACL Anthology via OpenAlex).
Prints raw title / year / venue / id and the first 300 chars of the abstract, and writes everything to
lit_results/<query>.jsonl so every claim in research_log.md can be traced to a saved record.

Usage: python scripts/lit_search.py "scam detection Hinglish" [--per 25]
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

UA = {"User-Agent": "indic-scam-lit-search/0.1 (mailto:aryan.chaurasia@somaiya.edu)"}

def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    return json.dumps({"_error": str(err)})

def inv(idx):
    if not idx: return ""
    words = {}
    for w, pos in idx.items():
        for p in pos: words[p] = w
    return " ".join(words[k] for k in sorted(words))

def openalex(q, per):
    u = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": q, "per-page": per, "sort": "relevance_score:desc",
         "select": "display_name,publication_year,doi,primary_location,abstract_inverted_index,id"})
    d = json.loads(get(u))
    if "_error" in d: return [{"src": "openalex", "error": d["_error"]}]
    return [{"src": "openalex", "title": w["display_name"], "year": w["publication_year"], "id": w.get("doi") or w["id"],
             "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
             "abstract": inv(w.get("abstract_inverted_index"))} for w in d.get("results", [])]

def arxiv(q, per):
    u = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": "all:" + q, "max_results": per, "sortBy": "relevance"})
    ns = {"a": "http://www.w3.org/2005/Atom"}
    try:
        root = ET.fromstring(get(u))
    except ET.ParseError:
        return [{"src": "arxiv", "error": "parse"}]
    out = []
    for e in root.findall("a:entry", ns):
        out.append({"src": "arxiv", "title": re.sub(r"\s+", " ", e.find("a:title", ns).text).strip(),
                    "year": e.find("a:published", ns).text[:4], "id": e.find("a:id", ns).text,
                    "venue": "arXiv", "abstract": re.sub(r"\s+", " ", e.find("a:summary", ns).text).strip()})
    return out

def s2(q, per):
    u = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(
        {"query": q, "limit": per, "fields": "title,year,venue,externalIds,abstract"})
    d = json.loads(get(u))
    if "_error" in d or "data" not in d: return [{"src": "s2", "error": d.get("_error") or str(d)[:100]}]
    return [{"src": "s2", "title": p["title"], "year": p.get("year"), "id": (p.get("externalIds") or {}).get("DOI") or p["paperId"],
             "venue": p.get("venue"), "abstract": p.get("abstract") or ""} for p in d["data"]]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("query"); ap.add_argument("--per", type=int, default=20)
    ap.add_argument("--show", type=int, default=300)
    a = ap.parse_args()
    rows = []
    for fn in (openalex, arxiv, s2):
        rows += fn(a.query, a.per)
    Path("lit_results").mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", a.query.lower()).strip("_")[:60]
    with open(f"lit_results/{slug}.jsonl", "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    for r in rows:
        if "error" in r: print(f"[{r['src']}] ERROR {r['error']}"); continue
        print(f"[{r['src']}] {r['year']} | {r['title']} | {r['venue']} | {r['id']}")
        if a.show and r["abstract"]: print("     ", r["abstract"][:a.show])
