"""Pull public posts for a subreddit from the Arctic Shift research archive (paginated by created_utc).
Raw output stays in data/raw_scrape/ (gitignored, never released). Usage: python scripts/pull_reddit.py IndiaScams 5000"""
import json, sys, time, urllib.request, urllib.parse
from pathlib import Path

sub, cap = sys.argv[1], int(sys.argv[2])
out = Path(__file__).resolve().parents[1] / "data" / "raw_scrape" / f"{sub}_posts.jsonl"
after, n = "2000-01-01", 0
KEEP = ["id", "created_utc", "title", "selftext", "num_comments", "score", "link_flair_text", "subreddit"]
with open(out, "w", encoding="utf-8") as fh:
    while n < cap:
        q = urllib.parse.urlencode({"subreddit": sub, "limit": 100, "sort": "asc", "after": after})
        req = urllib.request.Request("https://arctic-shift.photon-reddit.com/api/posts/search?" + q,
                                     headers={"User-Agent": "academic-research-script"})
        try:
            data = json.load(urllib.request.urlopen(req, timeout=60))["data"]
        except Exception as e:
            print("err", e); time.sleep(5); continue
        if not data:
            break
        for p in data:
            fh.write(json.dumps({k: p.get(k) for k in KEEP}, ensure_ascii=False) + "\n")
        n += len(data)
        after = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(data[-1]["created_utc"] + 1))
        print(n, after, flush=True)
        time.sleep(0.5)
print("total", n)
