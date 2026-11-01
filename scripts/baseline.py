"""Character n-gram TF-IDF + logistic regression baseline, scored after every turn (prefix of the conversation).

Usage: python scripts/baseline.py --train data/synthA --test data/real [--fpr 0.05]
Training examples are all prefixes of each training conversation (label = conversation label, but scam prefixes that
end *after* ask_turn are kept as positives too, since the detector must stay on). Reports AUROC on the full
conversation, early-detection metrics at a threshold fixed on training-benign scores (so no test peeking).
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).parent))
from metrics import binary_auroc, early_detection, threshold_at_fpr, bootstrap_ci


def load(paths, langs=None):
    recs = []
    for p in paths:
        p = Path(p)
        for f in (sorted(p.rglob("*.jsonl")) if p.is_dir() else [p]):
            for line in open(f, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    if langs is None or r["lang"] in langs:
                        recs.append(r)
    return recs


def prefixes(r):
    texts = [" ".join(t["text"] for t in r["turns"][: k + 1]) for k in range(len(r["turns"]))]
    return texts


def run(train, test, fpr=0.05, seed=0):
    Xt, yt = [], []
    for r in train:
        for t in prefixes(r):
            Xt.append(t); yt.append(int(r["label"] == "scam"))
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)
    clf = LogisticRegression(max_iter=2000, C=3.0, class_weight="balanced", random_state=seed)
    clf.fit(vec.fit_transform(Xt), yt)
    score = lambda recs: [clf.predict_proba(vec.transform(prefixes(r)))[:, 1] for r in recs]
    tr_scores = score(train)
    thr = threshold_at_fpr([s.max() for s, r in zip(tr_scores, train) if r["label"] == "benign"], fpr)
    te_scores = score(test)
    y = [int(r["label"] == "scam") for r in test]
    asks = [r["ask_turn"] if r["ask_turn"] is not None else 0 for r in test]
    out = early_detection(te_scores, y, asks, thr)
    out["auroc"] = binary_auroc(y, [s.max() for s in te_scores])
    out["n_test"] = len(test)
    out["threshold"] = thr
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", nargs="+", required=True)
    ap.add_argument("--test", nargs="+", required=True)
    ap.add_argument("--fpr", type=float, default=0.05)
    a = ap.parse_args()
    print(json.dumps(run(load(a.train), load(a.test), a.fpr), indent=1))
