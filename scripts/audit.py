"""Audit of public Indian scam-text datasets: redundancy, template structure, trivial-feature shortcuts, leakage.
Writes results to paper/generated/audit.json (numbers used by the paper are read from there, never typed)."""
import json, re, sys
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_predict
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "generated"; OUT.mkdir(parents=True, exist_ok=True)

def mask(t):
    t = re.sub(r"https?://\S+|www\.\S+", "<URL>", str(t))
    t = re.sub(r"[0-9०-९০-৯౦-౯௦-௯൦-൯೦-೯૦-૯੦-੯୦-୯]+", "<N>", t)
    return re.sub(r"\s+", " ", t).strip().lower()

def load():
    h = pd.read_csv(ROOT / "data/public/hinglish10k.csv")
    h = pd.DataFrame({"text": h.text, "y": h.label.astype(int), "lang": "Hinglish", "ds": "H10k", "meta_urg": h.urgency_level})
    a = pd.read_csv(ROOT / "data/public/ham14.csv"); a["y"] = (a.label == "scam").astype(int); a["ds"] = "Ham14"
    t = pd.read_csv(ROOT / "data/public/ham14_test.csv"); t["y"] = (t.label == "scam").astype(int); t["ds"] = "Ham14test"
    return h, a[["text", "y", "language", "ds"]].rename(columns={"language": "lang"}), t[["text", "y", "language", "ds"]].rename(columns={"language": "lang"})

def dup_stats(df):
    m = df.text.map(mask)
    return dict(n=len(df), exact_unique=int(df.text.nunique()), exact_dup=float(1 - df.text.nunique() / len(df)),
                masked_unique=int(m.nunique()), masked_unique_frac=float(m.nunique() / len(df)))

def nn_overlap(train_txt, test_txt, thr=0.9):
    v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True).fit(list(train_txt) + list(test_txt))
    nn = NearestNeighbors(n_neighbors=1, metric="cosine").fit(v.transform(train_txt))
    d, _ = nn.kneighbors(v.transform(test_txt))
    sim = 1 - d[:, 0]
    return dict(frac_ge_thr=float((sim >= thr).mean()), median_sim=float(np.median(sim)))

def cv_auc(X, y, groups=None, seed=0):
    clf = LogisticRegression(max_iter=2000, C=3.0)
    cv = GroupKFold(5) if groups is not None else StratifiedKFold(5, shuffle=True, random_state=seed)
    p = cross_val_predict(clf, X, y, cv=cv, groups=groups, method="predict_proba")[:, 1]
    return float(roc_auc_score(y, p))

def tfidf_X(txt):
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True).fit_transform(txt)

def trivial_feats(txt):
    t = pd.Series(list(txt))
    return np.c_[t.str.len(), t.str.count(r"\d"), t.str.contains(r"https?://|www\.").astype(int), t.str.count(r"[!?]"), t.str.split().str.len()]

def main():
    h, a, t = load()
    R = {"dup": {k: dup_stats(d) for k, d in [("H10k", h), ("Ham14", a), ("Ham14test", t)]}}
    # train/test leakage of the released test split
    R["ham14_test_vs_train"] = {"exact_overlap": float(t.text.isin(set(a.text)).mean()),
                                 "masked_overlap": float(t.text.map(mask).isin(set(a.text.map(mask))).mean()),
                                 "nn_cos_ge_0.9": nn_overlap(a.text, t.text)}
    # random split vs template-held-out (group = masked text) AUROC with char tf-idf
    for name, d in [("H10k", h), ("Ham14", a)]:
        X, y = tfidf_X(d.text), d.y.values
        g = pd.factorize(d.text.map(mask))[0]
        R.setdefault("cv_auc", {})[name] = {"random_5fold": cv_auc(X, y), "template_grouped_5fold": cv_auc(X, y, g)}
    R["ham14_per_language_masked_unique"] = {l: int(g.text.map(mask).nunique()) for l, g in a.groupby("lang")}
    R["h10k_top_text_counts"] = [int(c) for c in h.text.value_counts().head(5).values]
    # trivial shortcuts
    Xh = trivial_feats(h.text); R["shortcut_H10k"] = {"length_digits_url_only_auc": cv_auc(Xh, h.y.values)}
    urg = pd.get_dummies(h.meta_urg).values.astype(float); R["shortcut_H10k"]["urgency_level_only_auc"] = cv_auc(urg, h.y.values)
    fw = h.text.str.split().str[0].str.lower()
    R["shortcut_H10k"]["first_word_only_auc"] = cv_auc(pd.get_dummies(fw).values.astype(float), h.y.values)
    # per-language trivial shortcut in Ham14
    R["shortcut_Ham14"] = {l: cv_auc(trivial_feats(g.text), g.y.values) for l, g in a.groupby("lang")}
    # cross-dataset transfer on the Hinglish slice
    ah = a[a.lang == "Hinglish"]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True).fit(list(h.text) + list(ah.text))
    def fit_eval(tr, te):
        clf = LogisticRegression(max_iter=2000, C=3.0).fit(vec.transform(tr.text), tr.y)
        return float(roc_auc_score(te.y, clf.predict_proba(vec.transform(te.text))[:, 1]))
    R["transfer_hinglish"] = {"H10k->Ham14Hinglish": fit_eval(h, ah), "Ham14Hinglish->H10k": fit_eval(ah, h)}
    json.dump(R, open(OUT / "audit.json", "w"), indent=1)
    print(json.dumps(R, indent=1))

if __name__ == "__main__":
    main()
