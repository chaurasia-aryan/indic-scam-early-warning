import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import metrics  # noqa: E402
import validate  # noqa: E402


def rec(**kw):
    base = dict(id="a1", lang="en", channel="whatsapp", label="scam", type="kyc_bank",
                source="synthA", seed_id="s1", ask_turn=1,
                turns=[{"speaker": "initiator", "text": "Your bank account will be blocked today."},
                       {"speaker": "initiator", "text": "Share the OTP to keep it active."}])
    base.update(kw)
    return base


class ValidateTests(unittest.TestCase):
    def errs(self, r):
        return validate.validate_record(r, "t")[0]

    def test_valid_scam(self):
        self.assertEqual(self.errs(rec()), [])

    def test_valid_benign(self):
        r = rec(label="benign", type="kyc_bank", ask_turn=None)
        self.assertEqual(self.errs(r), [])

    def test_scam_needs_ask_turn_in_range(self):
        self.assertTrue(self.errs(rec(ask_turn=None)))
        self.assertTrue(self.errs(rec(ask_turn=2)))
        self.assertTrue(self.errs(rec(ask_turn=-1)))
        self.assertTrue(self.errs(rec(ask_turn=True)))  # bool is not an index

    def test_benign_must_not_have_ask_turn(self):
        self.assertTrue(self.errs(rec(label="benign", type="everyday", ask_turn=0)))

    def test_scam_type_cannot_be_everyday(self):
        self.assertTrue(self.errs(rec(type="everyday")))

    def test_script_must_match_lang(self):
        self.assertTrue(self.errs(rec(lang="hi-Deva")))  # English text labelled Devanagari
        deva = [{"speaker": "initiator", "text": "आपका खाता आज बंद हो जाएगा।"},
                {"speaker": "initiator", "text": "ओटीपी साझा करें।"}]
        self.assertEqual(self.errs(rec(lang="hi-Deva", turns=deva)), [])
        self.assertTrue(self.errs(rec(lang="en", turns=deva)))

    def test_unredacted_pii_flagged(self):
        for bad in ("call 9876543210 now", "pay to ramesh@okaxis", "open http://x.in/a", "mail a.b@gmail.com"):
            r = rec(turns=[{"speaker": "initiator", "text": bad}, {"speaker": "target", "text": "ok"}])
            self.assertTrue(self.errs(r), bad)

    def test_redaction_placeholders_pass(self):
        r = rec(turns=[{"speaker": "initiator", "text": "Call [PHONE] or pay to [UPI] via [URL]"},
                       {"speaker": "target", "text": "ok"}])
        self.assertEqual(self.errs(r), [])

    def test_cli_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            good, bad = Path(d) / "good.jsonl", Path(d) / "bad.jsonl"
            good.write_text(json.dumps(rec()) + "\n", encoding="utf-8")
            bad.write_text(json.dumps(rec(ask_turn=None)) + "\n", encoding="utf-8")
            run = lambda p: subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py"), str(p)],
                                           capture_output=True, text=True).returncode
            self.assertEqual(run(good), 0)
            self.assertEqual(run(bad), 1)

    def test_duplicate_id_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x.jsonl"
            f.write_text(json.dumps(rec()) + "\n" + json.dumps(rec()) + "\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate.py"), str(f)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("duplicate id", r.stdout)


class MetricsTests(unittest.TestCase):
    def test_flag_at_ask_turn_is_not_early(self):
        # scam asks at turn 2; scores cross 0.5 only at turn 2 -> not "before the ask"
        out = metrics.early_detection([np.array([0.1, 0.2, 0.9])], [1], [2], 0.5)
        self.assertEqual(out["flagged_before_ask"], 0.0)
        self.assertEqual(out["flagged_ever"], 1.0)

    def test_flag_before_ask_and_lead(self):
        out = metrics.early_detection([np.array([0.1, 0.9, 0.95, 0.99])], [1], [3], 0.5)
        self.assertEqual(out["flagged_before_ask"], 1.0)
        self.assertEqual(out["median_lead"], 2.0)  # flagged at turn 1, ask at turn 3

    def test_benign_fpr_counts_any_turn(self):
        scores = [np.array([0.1, 0.2]), np.array([0.1, 0.8]), np.array([0.0, 0.0]), np.array([0.6, 0.1])]
        out = metrics.early_detection(scores, [0, 0, 0, 0], [None] * 4, 0.5)
        self.assertEqual(out["benign_fpr"], 0.5)

    def test_threshold_at_fpr_respects_budget(self):
        rng = np.random.default_rng(0)
        benign = rng.random(1000)
        for fpr in (0.01, 0.05):
            thr = metrics.threshold_at_fpr(benign, fpr)
            self.assertLessEqual((benign >= thr).mean(), fpr)

    def test_temperature_scaling_reduces_overconfidence(self):
        rng = np.random.default_rng(1)
        y = rng.integers(0, 2, 2000)
        z = np.stack([-(2 * y - 1), (2 * y - 1)], 1) * 8.0 + rng.normal(0, 6, (2000, 2))
        T = metrics.fit_temperature(z, y)
        self.assertGreater(T, 1.0)
        for T_, expect_lower in ((1.0, False), (T, True)):
            p = metrics.softmax(z, T_)
            conf, corr = p.max(1), (p.argmax(1) == y).astype(float)
            if expect_lower:
                p0 = metrics.softmax(z, 1.0)
                e0 = metrics.ece_fn(p0.max(1), (p0.argmax(1) == y).astype(float))
                self.assertLess(metrics.ece_fn(conf, corr), e0)

    def test_bootstrap_ci_contains_mean(self):
        m, lo, hi = metrics.bootstrap_ci(np.random.default_rng(2).random(200))
        self.assertLessEqual(lo, m)
        self.assertLessEqual(m, hi)


if __name__ == "__main__":
    unittest.main()
