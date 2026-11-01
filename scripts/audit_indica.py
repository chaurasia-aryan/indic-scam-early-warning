"""INDICA text audit: identifier-level parallelism across languages and cultural-context markers in the English side.
Writes paper/generated/audit_indica.json."""
import json, os, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
base = ROOT / "data/public/indica/Text_samples"
langs = sorted(os.listdir(base))
stem = lambda f: re.sub(r"^json_all_", "", f)
ids = {l: {lab: {stem(f) for f in os.listdir(base / l / lab)} for lab in os.listdir(base / l)} for l in langs}
all_ids = set.intersection(*[set().union(*ids[l].values()) for l in langs])
R = {"languages": [l.replace("Text_", "") for l in langs],
     "files_per_language": {l.replace("Text_", ""): sum(len(os.listdir(base / l / lab)) for lab in os.listdir(base / l)) for l in langs},
     "distinct_ids_per_language": {l.replace("Text_", ""): len(set().union(*ids[l].values())) for l in langs},
     "ids_present_in_all_languages": len(all_ids)}
# label agreement across languages for shared ids
lab_of = {l: {i: lab for lab, s in ids[l].items() for i in s} for l in langs}
R["ids_with_identical_label_in_all_languages"] = sum(len({lab_of[l][i] for l in langs}) == 1 for i in all_ids)
# context markers in English side
CN = re.compile(r"\b(?:WeChat|Alipay|yuan|RMB|Beijing|Shanghai|Guangzhou|Shenzhen|Zhejiang|Hangzhou|Mr\.? (?:Zhang|Wang|Li|Liu|Chen|Zhao|Huang)|Manager (?:Zhang|Wang|Li|Liu|Chen)|(?:Zhang|Wang|Liu|Chen|Zhao|Huang) (?:Manager|sir|ma'am|Mr|Ms)|Taobao|JD\.com|Meituan|Didi|Ping An|UnionPay|ID card|identity card|public security bureau)\b", re.I)
IN = re.compile(r"\b(?:UPI|Aadhaar|Aadhar|rupee|rupees|Rs\.?|₹|PAN card|IFSC|Paytm|PhonePe|GPay|Google Pay|SBI|HDFC|ICICI|Mumbai|Delhi|Bangalore|Chennai|Kolkata|lakh|crore)\b", re.I)
tot = cn = ind = both = 0
for lab in os.listdir(base / "Text_english"):
    for f in os.listdir(base / "Text_english" / lab):
        t = open(base / "Text_english" / lab / f, encoding="utf-8", errors="ignore").read()
        a, b = bool(CN.search(t)), bool(IN.search(t)); tot += 1; cn += a; ind += b; both += a and b
R["english_context_markers"] = dict(files=tot, china_marker=cn, india_marker=ind, both=both,
                                    china_frac=cn / tot, india_frac=ind / tot)
R["source_corpus_in_filenames"] = collections.Counter("TeleAntiFraud-28k" in f for lab in os.listdir(base / "Text_english") for f in os.listdir(base / "Text_english" / lab))[True] / tot
json.dump(R, open(ROOT / "paper/generated/audit_indica.json", "w"), indent=1)
print(json.dumps(R, indent=1))
