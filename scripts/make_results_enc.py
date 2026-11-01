"""Score encoder predictions (data/enc_out/pred_*.json) against data/enc/eval/*.jsonl.
Per (encoder, train set, eval set): AUROC and FPR at the training-matched threshold 0.5, averaged over seeds,
with a bootstrap 95% CI over eval items (pooled over seeds). Writes paper/generated/enc_results.json."""
import glob, json, re, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]

def labels(name):
    return np.array([json.loads(l)["y"] for l in open(ROOT / "data/enc/eval" / f"{name}.jsonl", encoding="utf-8") if l.strip()])

def boot(y, P, stat, n=1000, seed=0):
    """Bootstrap over eval items; the statistic is the mean over seeds of the per-seed metric (same resample for all seeds)."""
    rng = np.random.default_rng(seed); vals = []
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        if 0 < y[i].mean() < 1: vals.append(np.mean([stat(y[i], p[i]) for p in P]))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))

def fpr(y, p): return float(((p >= .5) & (y == 0)).sum() / max((y == 0).sum(), 1))
def tpr(y, p): return float(((p >= .5) & (y == 1)).sum() / max((y == 1).sum(), 1))

runs = defaultdict(list)
for f in glob.glob(str(ROOT / "data/enc_out/pred_*.json")):
    m = re.match(r"pred_(\w+?)_(ham14|h10k)_s(\d+)(?:__(\w+))?\.json", Path(f).name)
    if m: runs[(m[1], m[2])].append(json.load(open(f)))
R = {}
for (enc, tr), preds_list in sorted(runs.items()):
    for ev in preds_list[0]:
        y = labels(ev) if (ROOT / "data/enc/eval" / f"{ev}.jsonl").exists() else None
        if y is None: continue
        P = np.array([pl[ev] for pl in preds_list if ev in pl])
        auc = [roc_auc_score(y, p) for p in P]
        pm = P.mean(0)
        R[f"{enc}|{tr}|{ev}"] = dict(n_seeds=len(P), n=int(len(y)), n_neg=int((y == 0).sum()), auroc=float(np.mean(auc)),
                                     auroc_seed_sd=float(np.std(auc)), auroc_ci=boot(y, P, roc_auc_score),
                                     fpr=float(np.mean([fpr(y, p) for p in P])), tpr=float(np.mean([tpr(y, p) for p in P])))
json.dump(R, open(ROOT / "paper/generated/enc_results.json", "w"), indent=1)
for k, v in R.items(): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a != "auroc_ci"}, [round(x, 3) for x in v["auroc_ci"]])
