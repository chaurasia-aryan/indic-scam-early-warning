"""Page through all public posts of a subreddit (no text query, which times out) via the Arctic Shift archive and keep
scam-related ones locally. Raw output stays in data/raw_scrape/ (gitignored, never released).
Usage: python scripts/pull_reddit_all.py india 2023-01-01"""
import json, re, sys, time, urllib.request, urllib.parse
from pathlib import Path

sub, start = sys.argv[1], sys.argv[2]
KW = re.compile(r"scam|fraud|phish|OTP|KYC|digital arrest|spam call|cyber ?crime|fake (?:call|message|link|job)|"
                r"telegram.{0,30}(?:task|job)|part.?time job|upi|sextortion|नकली|धोखा|फ्रॉड|घोटाळा|ठग", re.I)
KEEP = ["id", "created_utc", "title", "selftext", "num_comments", "score", "subreddit"]
out = Path(__file__).resolve().parents[1] / "data" / "raw_scrape" / f"all_{sub}.jsonl"
after, scanned, kept = start, 0, 0
with open(out, "a", encoding="utf-8") as fh:
    while True:
        url = "https://arctic-shift.photon-reddit.com/api/posts/search?" + urllib.parse.urlencode(
            {"subreddit": sub, "limit": 100, "sort": "asc", "after": after})
        data = None
        for wait in (3, 10, 30, 60):
            try:
                data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "academic-research-script"}), timeout=90))["data"]
                break
            except Exception:
                time.sleep(wait)
        if not data:
            print("END", scanned, kept, flush=True); break
        for p in data:
            if KW.search((p.get("title") or "") + " " + (p.get("selftext") or "")):
                fh.write(json.dumps({k: p.get(k) for k in KEEP}, ensure_ascii=False) + "\n"); kept += 1
        scanned += len(data)
        after = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(data[-1]["created_utc"] + 1))
        if scanned % 2000 == 0:
            fh.flush(); print(sub, after, "scanned", scanned, "kept", kept, flush=True)
        time.sleep(0.7)
