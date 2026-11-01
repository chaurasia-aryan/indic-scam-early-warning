"""Build Synthetic A JSONL from batch modules. Each module defines LANG and ROWS:
ROWS = [(scenario, label, channel, ask_turn, [turn texts, alternating initiator/target])]
scenario is a type id; seed_id = seed-<type>-<label>-01. Usage: python scripts/synth_a/build.py"""
import importlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
MODS = ["batch1_en", "batch1_hiLatn", "batch1_hiDeva", "batch1_mrDeva"]

def main():
    out = ROOT / "data" / "synthA"
    out.mkdir(parents=True, exist_ok=True)
    for m in MODS:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError:
            continue
        tag = mod.LANG.replace("-", "")
        n = 0
        with open(out / f"batch1_{tag}.jsonl", "w", encoding="utf-8") as fh:
            for i, (typ, label, ch, ask, turns) in enumerate(mod.ROWS, 1):
                rec = {"id": f"synthA-{tag}-{typ}-{label}-{i:04d}", "lang": mod.LANG, "channel": ch,
                       "label": label, "type": typ, "source": "synthA",
                       "seed_id": f"seed-{typ}-{label}-01", "ask_turn": ask,
                       "turns": [{"speaker": "initiator" if k % 2 == 0 else "target", "text": t}
                                 for k, t in enumerate(turns)]}
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
        print(mod.LANG, n)

if __name__ == "__main__":
    main()
