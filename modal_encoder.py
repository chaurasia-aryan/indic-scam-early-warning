"""Fine-tune multilingual encoders on public Indian scam-text sets and score every evaluation file.

One unit = (encoder, train set, seed). Output per unit: /out/pred_<tag>.json {eval_name: [prob_scam per row]},
skipped if it already exists, so interrupted runs resume.

    modal run modal_encoder.py                 # all units
    modal run modal_encoder.py --seeds 0       # smoke test
    modal volume get scam-enc-out / data/enc_out
Extra evaluation files can be added later with `modal run modal_encoder.py::rescore` (reloads saved checkpoints).
"""
import modal

app = modal.App("scam-encoders")
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch", "transformers", "accelerate", "scikit-learn", "numpy", "sentencepiece")
         .add_local_dir("data/enc", "/data/enc", copy=True))
out_vol = modal.Volume.from_name("scam-enc-out", create_if_missing=True)
hf_vol = modal.Volume.from_name("hf-cache", create_if_missing=True)
VOLS = {"/out": out_vol, "/root/.cache/huggingface": hf_vol}

ENCODERS = {"muril": "google/muril-base-cased", "xlmr": "FacebookAI/xlm-roberta-base"}
TRAIN_SETS = ["ham14", "h10k"]
MAX_LEN, EPOCHS, LR, BATCH = 128, 3, 3e-5, 32


def _read(p):
    import json
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def _predict(model, tok, texts, dev):
    import torch
    model.eval(); probs = []
    with torch.no_grad():
        for i in range(0, len(texts), 128):
            b = tok(texts[i:i + 128], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to(dev)
            probs += torch.softmax(model(**b).logits.float(), -1)[:, 1].cpu().tolist()
    return probs


def _eval_all(model, tok, dev):
    import glob, os
    return {os.path.basename(f)[:-6]: _predict(model, tok, [r["text"] for r in _read(f)], dev)
            for f in sorted(glob.glob("/data/enc/eval/*.jsonl"))}


@app.function(image=image, gpu="A10G", timeout=3600, volumes=VOLS)
def unit(enc, train_set, seed):
    import json, os, random, time
    import numpy as np, torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup
    tag = f"{enc}_{train_set}_s{seed}"
    out_vol.reload()
    if os.path.exists(f"/out/pred_{tag}.json"):
        return f"skip {tag}"
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    dev = "cuda"
    tok = AutoTokenizer.from_pretrained(ENCODERS[enc])
    model = AutoModelForSequenceClassification.from_pretrained(ENCODERS[enc], num_labels=2).to(dev)
    rows = _read(f"/data/enc/train/{train_set}.jsonl")
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    steps = EPOCHS * ((len(rows) + BATCH - 1) // BATCH)
    sch = get_linear_schedule_with_warmup(opt, int(0.06 * steps), steps)
    t0 = time.time()
    for ep in range(EPOCHS):
        model.train(); random.shuffle(rows)
        for i in range(0, len(rows), BATCH):
            b = rows[i:i + BATCH]
            x = tok([r["text"] for r in b], truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt").to(dev)
            loss = model(**x, labels=torch.tensor([r["y"] for r in b]).to(dev)).loss
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sch.step(); opt.zero_grad()
    preds = _eval_all(model, tok, dev)
    json.dump(preds, open(f"/out/pred_{tag}.json", "w"))
    model.save_pretrained(f"/out/ckpt_{tag}"); tok.save_pretrained(f"/out/ckpt_{tag}")
    json.dump({"train_minutes": (time.time() - t0) / 60, "n_train": len(rows)}, open(f"/out/done_{tag}.json", "w"))
    out_vol.commit()
    return f"done {tag} in {(time.time() - t0) / 60:.1f} min"


@app.function(image=image, gpu="A10G", timeout=3600, volumes=VOLS)
def rescore(enc, train_set, seed, suffix):
    """Score evaluation files added after training; writes /out/pred_<tag>__<suffix>.json."""
    import json
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tag = f"{enc}_{train_set}_s{seed}"
    out_vol.reload()
    tok = AutoTokenizer.from_pretrained(f"/out/ckpt_{tag}")
    model = AutoModelForSequenceClassification.from_pretrained(f"/out/ckpt_{tag}").to("cuda")
    json.dump(_eval_all(model, tok, "cuda"), open(f"/out/pred_{tag}__{suffix}.json", "w"))
    out_vol.commit()
    return tag


@app.local_entrypoint()
def main(seeds: str = "0,1,2", encs: str = "muril,xlmr"):
    units = [(e, t, int(s)) for e in encs.split(",") for t in TRAIN_SETS for s in seeds.split(",")]
    for r in unit.starmap(units):
        print(r)
