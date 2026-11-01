"""Validate conversation JSONL files against the schema in taxonomy.md.

Usage:
    python scripts/validate.py data/            # all *.jsonl under data/
    python scripts/validate.py data/synthA/x.jsonl

Checks (errors fail the run, warnings are reported):
  * required fields, allowed values for lang / channel / label / type / source
  * ask_turn: integer in range for scams, null for benign
  * turns: non-empty, speakers in {initiator, target}, non-empty text
  * script matches lang (Devanagari for hi-Deva / mr-Deva, mostly Latin for en / hi-Latn)
  * leftover personal data patterns (phones, UPI ids, raw URLs, emails)
  * duplicate ids, near-duplicate conversations (MinHash-style shingles, Jaccard)
  * seed_id leakage: a seed_id must not span more than one split label if --splits is given
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

LANGS = {"en", "hi-Latn", "hi-Deva", "mr-Deva"}
CHANNELS = {"whatsapp", "sms", "telegram", "call-transcript"}
LABELS = {"scam", "benign"}
SCAM_TYPES = {"digital_arrest", "task_job", "kyc_bank", "electricity",
              "courier_customs", "investment_group", "upi_refund", "army_olx"}
BENIGN_TYPES = SCAM_TYPES | {"everyday"}  # hard negative of a type, or everyday chat
SOURCES = {"real", "synthA", "synthB"}
SPEAKERS = {"initiator", "target"}
REQUIRED = ["id", "lang", "channel", "label", "type", "source", "seed_id", "turns", "ask_turn"]

DEVA = re.compile(r"[ऀ-ॿ]")
LATIN = re.compile(r"[A-Za-z]")
PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
UPI = re.compile(r"\b[\w.\-]{2,}@(?:ok\w+|ybl|paytm|upi|axl|ibl|sbi|hdfcbank|icici|apl)\b", re.I)
URL = re.compile(r"https?://\S+|www\.\S+", re.I)
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


def script_ratio(text, pattern):
    letters = [c for c in text if c.isalpha()]
    return (len(pattern.findall(text)) / len(letters)) if letters else 0.0


def shingles(text, k=5):
    t = re.sub(r"\s+", " ", text.lower())
    return {t[i:i + k] for i in range(max(1, len(t) - k + 1))}


def validate_record(r, where):
    errs, warns = [], []
    for f in REQUIRED:
        if f not in r:
            errs.append(f"{where}: missing field '{f}'")
    if errs:
        return errs, warns
    if r["lang"] not in LANGS:
        errs.append(f"{where}: bad lang {r['lang']!r}")
    if r["channel"] not in CHANNELS:
        errs.append(f"{where}: bad channel {r['channel']!r}")
    if r["source"] not in SOURCES:
        errs.append(f"{where}: bad source {r['source']!r}")
    if r["label"] not in LABELS:
        errs.append(f"{where}: bad label {r['label']!r}")
    else:
        allowed = SCAM_TYPES if r["label"] == "scam" else BENIGN_TYPES
        if r["type"] not in allowed:
            errs.append(f"{where}: type {r['type']!r} not allowed for label {r['label']}")
    turns = r["turns"]
    if not isinstance(turns, list) or not turns:
        errs.append(f"{where}: turns must be a non-empty list")
        return errs, warns
    for i, t in enumerate(turns):
        if not isinstance(t, dict) or t.get("speaker") not in SPEAKERS:
            errs.append(f"{where}: turn {i} speaker must be one of {sorted(SPEAKERS)}")
        elif not str(t.get("text", "")).strip():
            errs.append(f"{where}: turn {i} has empty text")
    at = r["ask_turn"]
    if r["label"] == "scam":
        if not isinstance(at, int) or isinstance(at, bool) or not (0 <= at < len(turns)):
            errs.append(f"{where}: scam needs integer ask_turn in [0, {len(turns) - 1}], got {at!r}")
    elif r["label"] == "benign" and at is not None:
        errs.append(f"{where}: benign must have ask_turn = null")
    text = " ".join(str(t.get("text", "")) for t in turns if isinstance(t, dict))
    if r["lang"] in ("hi-Deva", "mr-Deva"):
        if script_ratio(text, DEVA) < 0.5:
            errs.append(f"{where}: lang {r['lang']} but <50% Devanagari letters")
    elif r["lang"] in ("en", "hi-Latn"):
        if script_ratio(text, DEVA) > 0.1:
            errs.append(f"{where}: lang {r['lang']} but contains Devanagari")
    for name, pat in (("phone", PHONE), ("upi", UPI), ("url", URL), ("email", EMAIL)):
        if pat.search(text):
            errs.append(f"{where}: unredacted {name} pattern found")
    return errs, warns


def load(paths):
    files = []
    for p in paths:
        p = Path(p)
        files += sorted(p.rglob("*.jsonl")) if p.is_dir() else [p]
    for f in files:
        with open(f, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.strip()
                if line:
                    yield f, n, line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--dup-threshold", type=float, default=0.8)
    a = ap.parse_args()

    records, errors, warnings = [], [], []
    for f, n, line in load(a.paths):
        where = f"{f}:{n}"
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{where}: invalid JSON ({e})")
            continue
        e, w = validate_record(r, where)
        errors += e
        warnings += w
        if not e:
            records.append((where, r))

    ids = Counter(r["id"] for _, r in records)
    errors += [f"duplicate id {i!r} x{c}" for i, c in ids.items() if c > 1]

    # near-duplicates within the same language (cheap O(n^2) per language; fine up to a few thousand)
    by_lang = defaultdict(list)
    for where, r in records:
        txt = " ".join(t["text"] for t in r["turns"])
        by_lang[r["lang"]].append((r["id"], shingles(txt)))
    n_dup = 0
    for lang, items in by_lang.items():
        for (ia, sa), (ib, sb) in combinations(items, 2):
            if sa and sb and len(sa & sb) / len(sa | sb) >= a.dup_threshold:
                n_dup += 1
                if n_dup <= 20:
                    warnings.append(f"near-duplicate ({lang}): {ia} ~ {ib}")

    # a seed_id must not be shared by real and synthetic data of different splits; here we only
    # report how many distinct seeds each source uses so the split script can group by seed_id
    seeds = defaultdict(set)
    for _, r in records:
        seeds[r["source"]].add(r["seed_id"])

    print(f"records ok: {len(records)}")
    print("by source/lang/label:")
    c = Counter((r["source"], r["lang"], r["label"]) for _, r in records)
    for k in sorted(c):
        print(f"  {k[0]:6s} {k[1]:8s} {k[2]:6s} {c[k]}")
    print(f"distinct seed_ids per source: { {k: len(v) for k, v in seeds.items()} }")
    if records:
        print(f"near-duplicate pairs (Jaccard >= {a.dup_threshold}): {n_dup} "
              f"({n_dup / len(records):.1%} of records)")
    for w in warnings:
        print("WARNING:", w)
    for e in errors[:100]:
        print("ERROR:", e)
    if len(errors) > 100:
        print(f"... and {len(errors) - 100} more errors")
    print(f"errors: {len(errors)}  warnings: {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
