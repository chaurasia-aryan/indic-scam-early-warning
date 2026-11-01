"""Extract quoted messages (block quotes, code blocks, long quoted strings) from locally held public posts.
Outputs candidates to data/raw_scrape/quote_candidates.jsonl (gitignored). Labels are added by hand afterwards."""
import glob, json, re, html
from pathlib import Path
root = Path(__file__).resolve().parents[1] / "data" / "raw_scrape"
seen, out = set(), []
for f in glob.glob(str(root / "all_*.jsonl")) + [str(root / "posts_keyword.jsonl"), str(root / "posts_weekly.jsonl")]:
    for line in open(f, encoding="utf-8"):
        p = json.loads(line)
        if p["id"] in seen: continue
        seen.add(p["id"])
        t = html.unescape(p.get("selftext") or "")
        if t in ("", "[removed]", "[deleted]"): continue
        cands = []
        # consecutive block-quote lines
        for m in re.finditer(r"(?:^[ \t]*>[ \t]?.*\n?)+", t, re.M):
            q = re.sub(r"(?m)^[ \t]*>[ \t]?", "", m.group(0)).strip()
            if len(q) >= 40: cands.append(("blockquote", q))
        for m in re.finditer(r"```(.+?)```", t, re.S):
            if len(m.group(1).strip()) >= 40: cands.append(("code", m.group(1).strip()))
        for m in re.finditer(r"[\"“]([^\"“”]{50,600})[\"”]", t):
            cands.append(("quoted", m.group(1).strip()))
        for kind, q in cands:
            out.append(dict(post=p["id"], sub=p["subreddit"], title=p["title"], kind=kind, text=q))
with open(root / "quote_candidates.jsonl", "w", encoding="utf-8") as fh:
    for o in out: fh.write(json.dumps(o, ensure_ascii=False) + "\n")
print(len(seen), "posts ->", len(out), "candidates from", len({o["post"] for o in out}), "posts")
