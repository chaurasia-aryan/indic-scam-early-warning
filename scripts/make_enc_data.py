"""Build data/enc/{train,eval}/*.jsonl for the encoder experiments. Splits are grouped by masked text so templates
cannot leak between train and validation."""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from audit import load, mask

ROOT = Path(__file__).resolve().parents[1]
h, a, t = load()
rng = np.random.default_rng(0)

def grouped_split(df, frac=0.8):
    g = df.text.map(mask)
    keys = np.array(sorted(g.unique()), dtype=object); rng.shuffle(keys)
    tr = set(keys[: int(len(keys) * frac)])
    m = g.isin(tr)
    return df[m], df[~m]

def dump(df, path, cols=("text", "y", "lang")):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for r in df[list(cols)].itertuples(index=False):
            fh.write(json.dumps(dict(zip(cols, r)), ensure_ascii=False) + "\n")
    print(path.name, len(df), "scam frac", round(float(df.y.mean()), 3))

h_tr, h_va = grouped_split(h); a_tr, a_va = grouped_split(a)
E = ROOT / "data" / "enc"
dump(h_tr, E / "train" / "h10k.jsonl"); dump(a_tr, E / "train" / "ham14.jsonl")
dump(h_va, E / "eval" / "h10k_val.jsonl"); dump(a_va, E / "eval" / "ham14_val.jsonl")
dump(t, E / "eval" / "ham14_official_test.jsonl")
dump(h, E / "eval" / "h10k_all.jsonl")
dump(a[a.lang == "Hinglish"], E / "eval" / "ham14_hinglish_all.jsonl")
dump(a[a.lang == "Hindi"], E / "eval" / "ham14_hindi_all.jsonl")
dump(a[a.lang == "Marathi"], E / "eval" / "ham14_marathi_all.jsonl")
dump(a[a.lang == "English"], E / "eval" / "ham14_english_all.jsonl")
