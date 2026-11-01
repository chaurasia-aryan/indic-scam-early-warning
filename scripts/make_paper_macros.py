"""Turn the audit/encoder JSON results into LaTeX macros, tables and a figure. Every number in the paper comes from here."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

G = Path(__file__).resolve().parents[1] / "paper" / "generated"
A, I, X, Rd, E = [json.load(open(G / f)) for f in ["audit.json", "audit_icfd.json", "audit_indica.json", "reddit_yield.json", "enc_results.json"]]
M = []


def mac(name, val):
    M.append("\\newcommand{\\%s}{%s}" % (name, val))


def pct(x, d=1):
    return f"{100 * x:.{d}f}\\%"


def f3(x):
    return f"{x:.3f}"


def num(n):
    return f"{int(n):,}".replace(",", "{,}")


# --- H10k
h = A["dup"]["H10k"]
mac("HkN", num(h["n"])); mac("HkUnique", num(h["exact_unique"])); mac("HkDupPct", pct(h["exact_dup"]))
mac("HkTopCount", str(A["h10k_top_text_counts"][0]))
s = A["shortcut_H10k"]
mac("HkUrgAuc", f3(s["urgency_level_only_auc"])); mac("HkTrivAuc", f3(s["length_digits_url_only_auc"])); mac("HkFirstAuc", f3(s["first_word_only_auc"]))
mac("HkRandAuc", f3(A["cv_auc"]["H10k"]["random_5fold"])); mac("HkGroupAuc", f3(A["cv_auc"]["H10k"]["template_grouped_5fold"]))
# --- Ham14
a = A["dup"]["Ham14"]; t = A["dup"]["Ham14test"]
mac("HamN", num(a["n"])); mac("HamMasked", num(a["masked_unique"])); mac("HamMaskedPct", pct(a["masked_unique_frac"]))
mac("HamExactDupPct", pct(a["exact_dup"])); mac("HamTestN", num(t["n"])); mac("HamTestUnique", num(t["masked_unique"]))
mac("HamTestNN", pct(A["ham14_test_vs_train"]["nn_cos_ge_0.9"]["frac_ge_thr"], 2)); mac("HamTestExact", pct(A["ham14_test_vs_train"]["exact_overlap"], 1))
mac("HamRandAuc", f3(A["cv_auc"]["Ham14"]["random_5fold"])); mac("HamGroupAuc", f3(A["cv_auc"]["Ham14"]["template_grouped_5fold"]))
sh = A["shortcut_Ham14"]
mac("HamTrivHigh", str(sum(v >= 0.98 for v in sh.values()))); mac("HamTrivMin", f3(min(sh.values()))); mac("HamTrivMinLang", min(sh, key=sh.get))
pl = A["ham14_per_language_masked_unique"]; low = sorted(l for l, v in pl.items() if v <= 50)
mac("HamLowN", str(len(low))); mac("HamLowMax", str(max(pl[l] for l in low))); mac("HamLowMin", str(min(pl[l] for l in low)))
mac("TrHkHam", f3(A["transfer_hinglish"]["H10k->Ham14Hinglish"])); mac("TrHamHk", f3(A["transfer_hinglish"]["Ham14Hinglish->H10k"]))
# --- ICFD
sp = I["splits"]
for k, nm in [("train", "Tr"), ("validation", "Va"), ("test", "Te"), ("cross_domain", "Cd")]:
    mac(f"Icfd{nm}N", num(sp[k]["n"])); mac(f"Icfd{nm}Fraud", pct(sp[k]["fraud_frac"])); mac(f"Icfd{nm}Normal", num(sp[k]["normal"]))
mac("IcfdAllFraudAcc", pct(I["test_always_fraud"]["accuracy"])); mac("IcfdAllFraudF", pct(I["test_always_fraud"]["f1_fraud"]))
mac("IcfdAllFraudCi", f"{100 * I['test_always_fraud']['fpr_ci_if_zero_fp'][1]:.0f}\\%")
o = I["outcome_by_split_label"]
trn = o["train|normal"]
mac("IcfdTrNormalNA", pct(trn["N/A"] / sum(trn.values()))); mac("IcfdTeNormalFailed", str(o["test|normal"]["Failed"]))
t = I["tfidf_lr"]
mac("IcfdCvAuc", f3(t["train_cv"]["auroc"])); mac("IcfdTeAuc", f3(t["test"]["auroc"])); mac("IcfdVaAuc", f3(t["validation"]["auroc"])); mac("IcfdCdAuc", f3(t["cross_domain"]["auroc"]))
mac("IcfdTeFpr", pct(t["test"]["fpr"], 0)); mac("IcfdTeFpLo", pct(t["test"]["fpr_ci95"][0], 0)); mac("IcfdTeFpHi", pct(t["test"]["fpr_ci95"][1], 0))
mac("IcfdTeFp", str(t["test"]["false_alarms"])); mac("IcfdTeNormN", str(t["test"]["normals"]))
mac("IcfdCvFpr", pct(t["train_cv"]["fpr"])); mac("IcfdTeAcc", pct(t["test"]["accuracy"]))
mac("IcfdFirstTurnTe", pct(I["dup"]["first_turn_masked_overlap_test_in_train"])); mac("IcfdNNTe", pct(I["dup"]["test_nn_cos_ge_0.9_in_train"], 1))
# --- INDICA
x = X
mac("InN", num(x["ids_present_in_all_languages"])); mac("InLangs", str(len(x["languages"]))); mac("InFiles", num(x["files_per_language"]["english"]))
mac("InChinaPct", pct(x["english_context_markers"]["china_frac"])); mac("InIndiaN", str(x["english_context_markers"]["india_marker"]))
mac("InChinaN", num(x["english_context_markers"]["china_marker"]))
# --- Reddit
mac("RdScanned", num(Rd["posts_scanned_total"])); mac("RdMatched", num(Rd["keyword_matched_total"])); mac("RdCand", str(Rd["review_candidates"]))
mac("RdVerb", str(Rd["judged_verbatim_scam_utterances"])); mac("RdDeva", str(Rd["judged_with_devanagari"]))


# --- encoders
def e(enc, tr, ev, k="auroc"):
    return E[f"{enc}|{tr}|{ev}"][k]


for enc, nm in [("muril", "Mu"), ("xlmr", "Xl")]:
    mac(f"{nm}HamIid", f3(e(enc, "ham14", "ham14_val"))); mac(f"{nm}HkIid", f3(e(enc, "h10k", "h10k_val")))
    mac(f"{nm}HamOff", f3(e(enc, "ham14", "ham14_official_test"))); mac(f"{nm}HamOffTpr", pct(e(enc, "ham14", "ham14_official_test", "tpr"), 0))
    mac(f"{nm}HamToHk", f3(e(enc, "ham14", "h10k_all"))); mac(f"{nm}HamToHkTpr", pct(e(enc, "ham14", "h10k_all", "tpr"), 0))
    mac(f"{nm}HkToHinglish", f3(e(enc, "h10k", "ham14_hinglish_all")))
    mac(f"{nm}HkToOff", f3(e(enc, "h10k", "ham14_official_test"))); mac(f"{nm}HkToOffFpr", pct(e(enc, "h10k", "ham14_official_test", "fpr"), 0))
    oth = [e(enc, "h10k", f"ham14_{l}_all") for l in ["english", "hindi", "marathi"]]
    mac(f"{nm}HkToOtherLo", f3(min(oth))); mac(f"{nm}HkToOtherHi", f3(max(oth)))
    fp = [e(enc, "h10k", f"ham14_{l}_all", "fpr") for l in ["english", "hindi", "marathi"]]
    mac(f"{nm}HkToOtherFprLo", pct(min(fp), 0)); mac(f"{nm}HkToOtherFprHi", pct(max(fp), 0))
open(G / "macros.tex", "w").write("\n".join(M) + "\n")

# --- tables
L = ["Assamese", "Bengali", "English", "Gujarati", "Hindi", "Hinglish", "Kannada", "Kashmiri", "Malayalam", "Marathi", "Odia", "Punjabi", "Tamil", "Telugu"]
rows = [f"{l} & {pl[l]} & {sh[l]:.3f} \\\\" for l in L]
open(G / "tab_ham14_langs.tex", "w").write(
    "\\begin{tabular}{lrr}\n\\toprule\nLanguage & Templates / 1,000 & Trivial-feature AUROC \\\\\n\\midrule\n"
    + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")
evs = ["h10k_val", "ham14_val", "ham14_official_test", "h10k_all", "ham14_hinglish_all", "ham14_hindi_all", "ham14_marathi_all", "ham14_english_all"]
body = []
for enc, en in [("muril", "MuRIL"), ("xlmr", "XLM-R")]:
    for tr, tn in [("ham14", "Ham14"), ("h10k", "H10k")]:
        cells = []
        for ev in evs:
            k = f"{enc}|{tr}|{ev}"
            cells.append(f"{E[k]['auroc']:.2f}" if k in E else "--")
        body.append(f"{en} & {tn} & " + " & ".join(cells) + " \\\\")
open(G / "tab_enc.tex", "w").write(
    "\\begin{tabular}{llcccccccc}\n\\toprule\nEncoder & Trained on & H10k$^\\dagger$ & Ham14$^\\dagger$ & Ham14 off. & H10k all & Ham14 Hing. & Ham14 Hindi & Ham14 Mar. & Ham14 Eng. \\\\\n\\midrule\n"
    + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n")
isp = ["train", "validation", "test", "cross_domain"]
rows = [f"{k.replace('_', ' ')} & {num(sp[k]['n'])} & {num(sp[k]['normal'])} & {100 * sp[k]['fraud_frac']:.1f}\\% \\\\" for k in isp]
open(G / "tab_icfd.tex", "w").write("\\begin{tabular}{lrrr}\n\\toprule\nSplit & Conversations & Normal & Fraud \\\\\n\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n")

# --- figure
fig, ax = plt.subplots(1, 3, figsize=(9.2, 2.6))
names = ["H10k", "Ham14\n(train)", "Ham14\n(official test)"]
vals = [A["dup"]["H10k"]["masked_unique_frac"], A["dup"]["Ham14"]["masked_unique_frac"], A["dup"]["Ham14test"]["masked_unique_frac"]]
ax[0].bar(names, [100 * v for v in vals], color="#4C78A8"); ax[0].set_ylabel("distinct texts after masking (%)"); ax[0].set_title("(a) redundancy", fontsize=9)
for i, v in enumerate(vals):
    ax[0].text(i, 100 * v + 2, f"{100 * v:.0f}", ha="center", fontsize=8)
ax[0].set_ylim(0, 112)
ax[1].bar(["train", "val", "test", "cross-\ndomain"], [100 * sp[k]["fraud_frac"] for k in isp], color="#F58518")
ax[1].set_ylabel("fraud share (%)"); ax[1].set_title("(b) ICFD-31k split balance", fontsize=9); ax[1].set_ylim(0, 112)
for i, k in enumerate(isp):
    ax[1].text(i, 100 * sp[k]["fraud_frac"] + 2, f"{100 * sp[k]['fraud_frac']:.1f}", ha="center", fontsize=8)
w = 0.38
for j, (enc, en, c) in enumerate([("muril", "MuRIL", "#54A24B"), ("xlmr", "XLM-R", "#B279A2")]):
    ys = [e(enc, "ham14", "ham14_val"), e(enc, "ham14", "ham14_official_test"), e(enc, "ham14", "h10k_all"), e(enc, "h10k", "ham14_official_test")]
    ax[2].bar(np.arange(4) + (j - .5) * w, ys, w, label=en, color=c)
ax[2].set_xticks(range(4)); ax[2].set_xticklabels(["Ham14\nheld-out", "Ham14\nofficial", "Ham14\u2192\nH10k", "H10k\u2192\nHam14 off."], fontsize=7)
ax[2].set_ylim(0.5, 1.16); ax[2].set_ylabel("AUROC"); ax[2].set_title("(c) same models, other test sets", fontsize=9); ax[2].legend(fontsize=7, loc="upper right", ncol=2)
for a_ in ax:
    a_.tick_params(labelsize=7); a_.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(G / "fig_audit.pdf")
print(len(M), "macros")
