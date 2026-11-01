"""Weekly-window keyword pull of public posts from the Arctic Shift research archive (wide windows time out).
Raw output stays in data/raw_scrape/ (gitignored, never released)."""
import json, time, datetime as dt, urllib.request, urllib.parse, urllib.error
from pathlib import Path

SUBS = ["india", "IndiaTech", "IndianStockMarket"]
QUERY = "scam"
START, END = dt.date(2024, 1, 1), dt.date(2026, 10, 1)
KEEP = ["id", "created_utc", "title", "selftext", "num_comments", "score", "subreddit"]
root = Path(__file__).resolve().parents[1] / "data" / "raw_scrape"
out, prog = root / "posts_weekly.jsonl", root / "weekly_done.txt"
seen = {json.loads(l)["id"] for l in open(out, encoding="utf-8")} if out.exists() else set()
done = set(prog.read_text().split("\n")) if prog.exists() else set()

def get(**kw):
    url = "https://arctic-shift.photon-reddit.com/api/posts/search?" + urllib.parse.urlencode(kw)
    for wait in (4, 10, 20):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "academic-research-script"}), timeout=60))["data"]
        except Exception:
            time.sleep(wait)
    return None

with open(out, "a", encoding="utf-8") as fh, open(prog, "a") as pf:
    d0 = START
    while d0 < END:
        d1 = d0 + dt.timedelta(days=7)
        for s in SUBS:
            key = f"{s}|{d0}"
            if key in done:
                continue
            d = get(subreddit=s, query=QUERY, limit=100, after=str(d0), before=str(d1))
            if d is None:
                print("FAIL", key, flush=True); continue
            for p in d:
                if p["id"] not in seen:
                    seen.add(p["id"]); fh.write(json.dumps({k: p.get(k) for k in KEEP}, ensure_ascii=False) + "\n")
            fh.flush(); pf.write(key + "\n"); pf.flush()
            print(key, len(d), "total", len(seen), flush=True)
            time.sleep(1.5)
        d0 = d1
print("DONE", len(seen))
