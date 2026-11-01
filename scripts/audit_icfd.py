"""ICFD-31k audit: split label balance, trivial baselines, false-alarm resolution, redundancy, shortcuts, and
re-split behaviour of a char-TF-IDF logistic regression. Writes paper/generated/audit_icfd.json."""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import StratifiedKFold, cross_val_predict
sys.path.insert(0, str(Path(__file__).parent))
from icfd_load import load_icfd

OUT = Path(__file__).resolve().parents[1] / "paper" / "generated"; OUT.mkdir(parents=True, exist_ok=True)

def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"),) * 2
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(c - h), float(c + h)

def text(t): return " ".join(x for _, x in t)
def mask(t): return re.sub(r"\s+", " ", re.sub(r"\d+", "<N>", t.lower())).strip()

def main():
    d = load_icfd(); d["text"] = d.turns.map(text); d["n_turns"] = d.turns.map(len); d["n_chars"] = d.text.str.len()
    R = {}
    R["splits"] = {s: dict(n=int(len(g)), fraud=int(g.y.sum()), normal=int((g.y == 0).sum()), fraud_frac=float(g.y.mean()))
                   for s, g in d.groupby("split")}
    te = d[d.split == "test"]
    # trivial predictors on the released test split
    allf = np.ones(len(te), int)
    R["test_always_fraud"] = dict(accuracy=float(accuracy_score(te.y, allf)), f1_fraud=float(f1_score(te.y, allf)),
                                   fpr=1.0, normals=int((te.y == 0).sum()), fpr_ci_if_zero_fp=wilson(0, int((te.y == 0).sum())))
    # what "normal" means per split: scam_outcome crosstab
    R["outcome_by_split_label"] = {f"{sp}|{'fraud' if lab else 'normal'}": g.outcome.fillna("None").value_counts().to_dict()
                                   for (sp, lab), g in d.groupby(["split", "y"])}
    # redundancy: exact / masked duplicates of whole transcripts and opening turns, test vs train
    tr = d[d.split == "train"]
    R["dup"] = {"exact_text_overlap_test_in_train": float(te.text.isin(set(tr.text)).mean()),
                "first_turn_masked_overlap_test_in_train": float(te.turns.map(lambda t: mask(t[0][1])).isin(set(tr.turns.map(lambda t: mask(t[0][1])))).mean()),
                "first_turn_masked_unique_frac_train": float(tr.turns.map(lambda t: mask(t[0][1])).nunique() / len(tr))}
    v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, max_features=300000)
    Xtr = v.fit_transform(tr.text); Xte = v.transform(te.text)
    sims = 1 - NearestNeighbors(n_neighbors=1, metric="cosine").fit(Xtr).kneighbors(Xte)[0][:, 0]
    R["dup"]["test_nn_cos_ge_0.9_in_train"] = float((sims >= 0.9).mean()); R["dup"]["test_nn_cos_median"] = float(np.median(sims))
    # detector trained on train, evaluated on each split
    clf = LogisticRegression(max_iter=3000, C=3.0, class_weight="balanced").fit(Xtr, tr.y)
    thr_scores = clf.predict_proba(Xtr)[:, 1]
    R["tfidf_lr"] = {}
    for s in ["validation", "test", "cross_domain"]:
        g = d[d.split == s]; p = clf.predict_proba(v.transform(g.text))[:, 1]; pred = (p >= 0.5).astype(int)
        nrm = (g.y == 0).values
        fp = int(((pred == 1) & nrm).sum())
        R["tfidf_lr"][s] = dict(auroc=float(roc_auc_score(g.y, p)), accuracy=float(accuracy_score(g.y, pred)),
                                f1_fraud=float(f1_score(g.y, pred)), normals=int(nrm.sum()), false_alarms=fp,
                                fpr=fp / max(nrm.sum(), 1), fpr_ci95=wilson(fp, int(nrm.sum())))
    # same model family, balanced re-split of the training pool (stratified 5-fold, normal-heavy like train)
    X, y = Xtr, tr.y.values
    p = cross_val_predict(LogisticRegression(max_iter=3000, C=3.0, class_weight="balanced"), X, y,
                          cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
    nr = y == 0; fp = int(((p >= .5) & nr).sum())
    R["tfidf_lr"]["train_cv"] = dict(auroc=float(roc_auc_score(y, p)), normals=int(nr.sum()), false_alarms=fp,
                                     fpr=fp / nr.sum(), fpr_ci95=wilson(fp, int(nr.sum())), accuracy=float(accuracy_score(y, p >= .5)))
    # trivial-feature shortcuts (length, turns), in the train pool
    F = np.c_[tr.n_turns, tr.n_chars, tr.n_chars / tr.n_turns]
    pf = cross_val_predict(LogisticRegression(max_iter=3000), (F - F.mean(0)) / F.std(0), y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
    R["shortcut_train"] = {"length_turns_only_auc": float(roc_auc_score(y, pf))}
    json.dump(R, open(OUT / "audit_icfd.json", "w"), indent=1)
    print(json.dumps(R, indent=1))

if __name__ == "__main__":
    main()
