"""Yield of the public-forum route: how many verbatim scam utterances could be recovered from scraped Reddit posts.
Reads the pull logs and the frozen review set (data/raw_scrape/cand_short_frozen.json, gitignored). The list JUDGED
holds indices of candidates that one reviewer (the first author's assistant) judged to be a verbatim scam utterance
(a call script line, message or threat quoted by the victim). Writes paper/generated/reddit_yield.json."""
import glob, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
raw = ROOT / "data/raw_scrape"
JUDGED = [5, 109, 111, 116, 117, 161, 190, 200, 219, 222, 237, 239]
R = {"subreddits": {}}
for f in sorted(glob.glob(str(raw / "all_*.log"))):
    last = [l for l in open(f, encoding="utf-8") if "scanned" in l][-1]
    m = re.match(r"(\S+) (\S+) scanned (\d+) kept (\d+)", last)
    R["subreddits"][m[1]] = dict(scanned_through=m[2][:10], posts_scanned=int(m[3]), keyword_matched=int(m[4]))
R["posts_scanned_total"] = sum(v["posts_scanned"] for v in R["subreddits"].values())
R["keyword_matched_total"] = sum(v["keyword_matched"] for v in R["subreddits"].values())
cand = json.load(open(raw / "cand_short_frozen.json", encoding="utf-8"))
dev = re.compile(r"[ऀ-ॿ]")
R["review_candidates"] = len(cand)
R["judged_verbatim_scam_utterances"] = len(JUDGED)
R["judged_with_devanagari"] = sum(bool(dev.search(cand[i]["text"])) for i in JUDGED)
R["judged_multi_turn"] = 0
R["judged_benign_counterparts"] = 0
json.dump(R, open(ROOT / "paper/generated/reddit_yield.json", "w"), indent=1)
print(json.dumps(R, indent=1))
