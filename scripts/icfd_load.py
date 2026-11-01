"""Load ICFD-31k source conversations (zstd jsonl shards) from data/public/icfd into a DataFrame."""
import glob, io, json, ast
from pathlib import Path
import pandas as pd, zstandard

def load_icfd(root=None):
    root = Path(root or Path(__file__).resolve().parents[1] / "data" / "public" / "icfd")
    rows = []
    for f in sorted(glob.glob(str(root / "*.jsonl.zst"))):
        split = Path(f).name.split("-")[0]
        with open(f, "rb") as fh:
            for line in io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8"):
                r = json.loads(line)
                tr = r["transcript"]
                if isinstance(tr, str):
                    tr = ast.literal_eval(tr)
                rm = r.get("release_metadata")
                if isinstance(rm, str):
                    try: rm = ast.literal_eval(rm)
                    except Exception: rm = {}
                rows.append(dict(split=split, session_id=r["session_id"], y=int(r["final_verdict"] == "YES"),
                                 turns=[(t["speaker"], t["text"]) for t in tr],
                                 scenario=r.get("scenario"), agent=r.get("agent_persona"), customer=r.get("customer_persona"),
                                 outcome=r.get("scam_outcome"), meta=rm, chunks=r.get("chunk_level_analysis")))
    return pd.DataFrame(rows)
