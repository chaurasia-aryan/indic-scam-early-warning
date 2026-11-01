# Licensing

| Component | License |
|---|---|
| Code (`scripts/`, `tests/`, `modal_encoder.py`) | MIT, see `LICENSE` |
| Manuscript (`paper/main.tex`, generated tables/figures) and docs (`*.md`) | CC BY 4.0 |
| Hand-written synthetic set (`data/synthA/`, `prompts/`) | CC BY 4.0 |
| Data derived from third-party datasets (`data/enc/`) | Retains the upstream license (below) |

## Third-party datasets (derived subsets in `data/enc/`)
- `anmolshrivastav/scam_ham_india_14_languages` (ham14): MIT. Copyright remains with its authors.
- `DatasetNewUser/Indian_Cyber_Scam_PhoneCall_Hinglish_Dataset` (ICFD, a copy of `ysangam/...`): Apache-2.0. Files were reformatted/subsetted; see `scripts/make_enc_data.py`.

Check each upstream dataset card for its exact copyright line before redistributing. Reddit-sourced text is not released (`data/raw_scrape/` is gitignored).
