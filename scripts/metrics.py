"""Metrics shared by every experiment script.

softmax / fit_temperature / ece_fn / pm are carried over from qlora-calibration-paper/make_results.py
(same definitions, so numbers are comparable across the two papers). The scam-specific part is
the early-detection metrics: a scam conversation is scored after every turn, and we ask whether it
was flagged *before* the first turn that asks the target for something (`ask_turn`).
"""
import numpy as np
from sklearn.metrics import roc_auc_score


def softmax(z, T=1.0):
    z = z / T
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def fit_temperature(z, y):
    """Grid-search temperature minimising NLL. z: (N, C) logits, y: (N,) class ids."""
    grid = np.logspace(-1, 1.3, 300)
    nll = [-np.mean(np.log(softmax(z, T)[np.arange(len(y)), y] + 1e-12)) for T in grid]
    return float(grid[int(np.argmin(nll))])


def ece_fn(conf, correct, n_bins=15):
    edges = np.linspace(0, 1, n_bins + 1)
    out = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            out += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return out


def pm(mean, lo, hi, d=3):
    return f"{mean:.{d}f} \\scriptsize[{lo:.{d}f}, {hi:.{d}f}]"


def binary_auroc(y, score):
    y = np.asarray(y)
    return roc_auc_score(y, score) if 0 < y.mean() < 1 else float("nan")


def threshold_at_fpr(benign_scores, fpr):
    """Smallest threshold such that at most `fpr` of benign scores are >= threshold."""
    s = np.sort(np.asarray(benign_scores))
    k = int(np.floor(len(s) * (1 - fpr)))
    k = min(max(k, 0), len(s) - 1)
    return float(s[k]) + 1e-12  # strictly above the (1 - fpr) quantile


def early_detection(turn_scores, labels, ask_turns, threshold):
    """Early-warning metrics for one threshold.

    turn_scores: list of 1-D arrays, scam probability after turn 0..n-1 of each conversation
    labels:      1 for scam, 0 for benign
    ask_turns:   index of first asking turn for scams (ignored for benign)
    Returns dict:
      flagged_before_ask  share of scams with score >= threshold at some turn strictly before ask_turn
      flagged_ever        share of scams flagged at any turn
      median_lead         median (ask_turn - first_flag_turn) over scams flagged before the ask
      benign_fpr          share of benign conversations flagged at any turn
    A flag at turn k means the model had seen turns 0..k; ask_turn itself is not "before" the ask.
    """
    first_flag = []
    for s in turn_scores:
        idx = np.where(np.asarray(s) >= threshold)[0]
        first_flag.append(int(idx[0]) if len(idx) else None)
    scam_i = [i for i, y in enumerate(labels) if y == 1]
    ben_i = [i for i, y in enumerate(labels) if y == 0]
    before = [i for i in scam_i if first_flag[i] is not None and first_flag[i] < ask_turns[i]]
    ever = [i for i in scam_i if first_flag[i] is not None]
    lead = [ask_turns[i] - first_flag[i] for i in before]
    return dict(
        flagged_before_ask=len(before) / max(len(scam_i), 1),
        flagged_ever=len(ever) / max(len(scam_i), 1),
        median_lead=float(np.median(lead)) if lead else float("nan"),
        benign_fpr=sum(first_flag[i] is not None for i in ben_i) / max(len(ben_i), 1),
    )


def bootstrap_ci(values, stat=np.mean, n_boot=2000, seed=0):
    """Percentile bootstrap CI over conversations (resample indices)."""
    rng = np.random.default_rng(seed)
    v = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(v), size=(n_boot, len(v)))
    boots = np.array([stat(v[i]) for i in idx])
    return float(stat(v)), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
