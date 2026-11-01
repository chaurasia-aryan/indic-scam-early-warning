# Early scam detection in Indian-language conversations

Working title: *How Early Can We Warn? Detecting Conversational Scams in Hindi, Hinglish and Marathi.*

## Question
Real scams (digital arrest, task/job, KYC, UPI refund...) unfold over a conversation. Can a detector
(1) work in Indian languages as well as in English, (2) flag the scam before the first request for money, an OTP,
an app install or personal data, and (3) do so without constantly raising false alarms on look-alike benign chats?

## Status
Pivoted from building a new dataset to **auditing the public ones** (no real Indian-language scam conversations are public; forum mining recovered 12 single-line utterances).
Manuscript: `paper/main.tex` (pdflatex + bibtex; every number comes from `paper/generated/*.json` via `scripts/make_paper_macros.py`).
Reproduce: `scripts/audit.py`, `scripts/audit_icfd.py`, `scripts/audit_indica.py`, `scripts/make_enc_data.py`, `modal_encoder.py` (GPU), `scripts/make_results_enc.py`, `scripts/reddit_yield.py`, `scripts/make_paper_macros.py`.
Datasets are downloaded into `data/public/` (gitignored); Reddit raw text stays in `data/raw_scrape/` (gitignored, never released).
The hand-written Synthetic A set (64 records, `scripts/synth_a/`) is not used in the paper.

## Layout
| Path | Purpose |
|---|---|
| `taxonomy.md` | languages, 8 scam types, benign hard negatives, definition of `ask_turn` |
| `ethics.md` | consent, redaction and release protocol (needs faculty sign-off before any real data is collected) |
| `research_log.md` | novelty check: queries, closest papers, what they do not cover |
| `data/{real,synthA,synthB}/` | JSONL conversations (one per line); see schema below |
| `scripts/validate.py` | schema, script/language, redaction and near-duplicate checks |
| `scripts/metrics.py` | calibration helpers (from the QLoRA paper) and early-detection metrics |
| `tests/` | `python -m unittest discover -s tests` |
| `prompts/` | prompts used to generate synthetic data |
| `paper/` | IEEEtran manuscript and generated tables |

## Record schema
```json
{"id": "synthA-hiLatn-kyc-0001", "lang": "hi-Latn", "channel": "whatsapp", "label": "scam",
 "type": "kyc_bank", "source": "synthA", "seed_id": "seed-kyc-03", "ask_turn": 2,
 "turns": [{"speaker": "initiator", "text": "..."}, {"speaker": "target", "text": "..."}]}
```
Benign records use `ask_turn: null` and `type` = the scam type they imitate, or `everyday`.

## Commands
```
pip install -r requirements.txt
python -m unittest discover -s tests
python scripts/validate.py data/
```

## Data and ethics
Synthetic data is generated for detection research. Real conversations are donated, redacted and used only as
described in `ethics.md`.

## License
Code: MIT (`LICENSE`). Paper, docs and original synthetic data: CC BY 4.0. Third-party-derived data keeps its upstream license. See `NOTICE.md`.
