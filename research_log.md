# Literature search log

Started 2026-10-04. Raw results from every search are saved in `lit_results/` (made by `scripts/lit_search.py`),
so each line below can be checked against a saved record.

## How the search was done
- Google Scholar refuses automated requests (HTTP 403). The Chrome extension was not connected, so I could not use
  Scholar through the browser either. **Someone still has to run the Scholar searches by hand** (list at the bottom).
- Semantic Scholar rate-limited me (HTTP 429), so it contributed nothing.
- What did work: the OpenAlex API and the arXiv API, called directly from a script. Abstracts were read in full from the
  API output, not from a summary written by another model.
- OpenAlex and arXiv are not Scholar. A paper missing from here can still exist.

## Correction to an earlier claim
My first note said none of 28 recent scam-conversation papers covered Indian languages, so the gap looked wide open.
**That was wrong.** It came from a model-written summary of search results. Reading the abstracts directly turned up ICFD-31k.

## Papers read (abstract, plus the repo README and dataset card for ICFD-31k)
| Paper | What it does | What it leaves open |
|---|---|---|
| **ICFD-31k**, Ahuja, Prateek, Singh, IJCAI-ECAI 2026 (doi 10.24963/ijcai.2026/786; github.com/SPELLAILab/ICFD-31k) | Calls itself the first Indian conversational fraud dataset. 31,000+ phone-call transcripts in English and Hinglish, 10 fraud types plus 5 unseen types, labels every 3 seconds for streaming detection, Cohen's kappa 0.534. Fine-tuned RoBERTa reaches F1 99.6 (full call) and 95.6 (streaming); streaming model catches 99.8% of fraud with median detection time 30 s. | The dataset card says the data is synthetic and "does not replace validation on real calls". Only English/Hinglish, so no Devanagari Hindi and no Marathi. Phone-call style, not chat apps. F1 near 99.6 on synthetic text suggests the task is easy in-distribution. Calibration and false alarms on look-alike benign chats are not mentioned. |
| **Open-Jev / CallScreenBench**, Ren et al., arXiv 2609.23959 | Qwen3-4B tuned with LoRA gives a calibrated scam probability after every caller turn (AUROC .974, calibration error .052). Reports false alarms and decision timing. | The authors say all callers are synthetic and the recipe was selected with test-set exposure. English only (nothing in the abstract suggests otherwise). |
| **PreScam**, arXiv 2605.12243 | 11,573 conversation instances built from user-submitted scam reports, 20 categories. Tasks: predict when a scam is about to end, and the scammer's next action. | Predicts progression, not "scam or not" at a fixed false-alarm rate. Language not stated in the abstract, so I cannot say it is non-Indian. |
| **Anatomy of Scam Scenarios**, arXiv 2606.16052 | 102,054 real incident reports, taxonomy of 18 scenarios, conversation-aware detection for bank customer interactions. | Not Indian languages, as far as the abstract says. |
| **Making Sense of Scams**, arXiv 2604.23973 | Alignment-based hints on real scam dialogues, 30-person user study. | Study of hint design, not a language-coverage paper. |
| **Incremental Risk Assessment of Progressive Elder Financial Scams**, FLICS 2026 (doi 10.1109/flics70075.2026.11621900) | Re-scores risk after every turn, 2 to 8 turns per dialogue, four small models. | Constructed dataset of investment, charity and tech-support scams; no Indian languages mentioned. |
| **SCRIPTMIND**, EACL Industry 2026 | 571 Korean phone-scam cases, 22,712 training instances; an 11B model beats GPT-4o by 13%. | Korean only. |
| **Cybercrime complaint classification for Hinglish**, arXiv 2412.16614 | Classifies Hinglish cybercrime complaints from I4C data (HingRoBERTa, 74.41% accuracy). | Classifies a written complaint after the crime, not a live conversation. |
| **Multilingual Smishing Detection for Indian Dialects**, Zenodo 2026 | SMS phishing detection for Indian languages and Hinglish. | Single SMS messages. I only saw a truncated abstract; not verified further. |
| **FiMI**, NPCI, arXiv 2602.05794 | Finance language model for India trained on English, Hindi and Hinglish. | Not a scam detector. |
| **VISHGUARD**, Scientific Data 2026 | 3,000 synthetic audio calls in English, French and Arabic. | No Indian languages. |

## What this means for the project
- "First Indian-language early scam detection" is **not** a safe claim. ICFD-31k got there first for English/Hinglish phone calls.
- What I could not find in the sources above (the Scholar check could still contradict this):
  1. Devanagari Hindi or Marathi scam conversations.
  2. Any real (not generated) Indian scam conversations used as a test set.
  3. Scams in chat apps (WhatsApp, Telegram) rather than phone calls.
  4. A test of whether a detector trained on generated Indian conversations still works on real ones. ICFD-31k's own
     card says this is unverified, and a score of 99.6 on generated text makes the question worth asking.
  5. False alarms on benign look-alike conversations, together with calibration, for Indian languages.
- A claim that would hold up better: **"Do detectors trained on generated Indian scam conversations work on real ones,
  and do they still work in Hindi and Marathi?"** It uses ICFD-31k as a baseline rather than competing with it.
  The risk is unchanged: it needs a real test set, and that is the hard part to collect.

## To do before writing the Introduction
- Google Scholar by hand: "scam detection Hinglish", "scam detection Hindi Devanagari", "scam detection Marathi",
  "digital arrest scam detection", "conversational fraud detection India", "ICFD-31k" (cited-by list), "CallScreenBench" (cited-by list).
- Read ICFD-31k in full (paper PDF is in the repo under `paper/`) and run its baselines on a few real conversations.
- Open the two Hugging Face Indian scam datasets and read sample rows (so far only their cards were read).
- Check whether ICFD-31k's test set shares generation templates with its training set.

## Web check of public Indian scam datasets (2026-10-04, dataset cards read via WebFetch)
Searched Hugging Face / Kaggle / GitHub for real Indian-language scam conversation data. Provenance as stated on the cards:
| Dataset | Size / languages | Provenance as stated |
|---|---|---|
| DatasetNewUser/Indian_Cyber_Scam_PhoneCall_Hinglish_Dataset (copy of ysangam/...) | ~10,000 records; en, hi, Hinglish; Apache-2.0 | Card does not say real or synthetic; no collection method given |
| anmolshrivastav/scam_ham_india_14_languages | 14,000 short texts, 14 languages incl. mr, hi; MIT | Card says "models realistic communication patterns"; no collection method; single messages |
| ggirishg/MultiFraudAlign | 28,708 dialogues; en, hi, ko, Hinglish; CC BY-NC | Fully synthetic (Qwen2.5-72B-Instruct) |
| Ridham115/indian-scam-sms-synthetic-audited | 1,580 short messages | Synthetic by its name; not opened |
| Kaggle mealss/call-transcripts-scam-determinations | 60 transcripts | Not opened; language not checked |
Not opened (only seen in search results, claims unverified): sidzzz07/scamshield-dataset, karanverma19/trilingual_fraud_consumer_protection_v2, a GitHub project claiming 1,406 Hindi fraud-call transcripts.
Takeaway: none of the opened cards documents real collected conversations in Devanagari Hindi or Marathi. Synthetic Indian scam data is already plentiful, so another generated set adds little; the real test set is the contribution.
