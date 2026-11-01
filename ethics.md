# Data collection and ethics protocol

Draft for faculty / college sign-off. Donated conversations are not collected until this is approved. Public-forum text (below) was started earlier on the project owner's instruction, with the controls listed in that section; the sign-off should cover it too.

## What is collected
Scam and benign conversations donated by volunteers (typically screenshots), plus public scam scripts from advisories, news and forums.

## Consent
- Volunteers are 18+ and give informed consent through a short form saying: what is collected, that it is redacted before anyone else sees it, that the redacted text may appear in a public dataset, and that they can withdraw at any time before release.
- Two separate tick-boxes: (1) use for research, (2) include in the public release. The release is limited to conversations with both ticked.

## Redaction (before anything is stored in the repo)
Replace with placeholders: person names -> `[NAME]`, phone numbers -> `[PHONE]`, UPI IDs -> `[UPI]`, account / card numbers -> `[ACCT]`, links -> `[URL]`, email -> `[EMAIL]`, addresses -> `[ADDR]`. Amounts and scam wording stay.
`scripts/validate.py` flags leftover phone / UPI / URL patterns.

## Storage
- Raw screenshots are never committed and are deleted after transcription and redaction.
- Only redacted text enters `data/real/`.
- Donor identities are not recorded with the conversations.

## Release
Synthetic data, code and taxonomy are released openly. Real conversations are released only where the donor ticked release; otherwise they are used for evaluation only and not distributed.

## Safety
The released synthetic data contains realistic scam scripts. The paper's release note says the data is for detection research and notes the dual-use risk. No new attack technique is presented beyond what is already in public advisories.

## Public forum data (added 2026-10-04)
Some real conversations come from public Reddit posts in which victims quote or transcribe scam chats, read through the Arctic Shift public research archive (the Reddit site itself refuses unauthenticated scraping, and we do not evade that).
- Raw post text lives only in `data/raw_scrape/` (gitignored) and is never released or committed.
- Only the quoted scam conversation is kept, redacted as above, with no usernames, post ids, URLs or timestamps; the narrative around it is dropped.
- The redacted conversations are used as an evaluation set and are not redistributed as text. The release lists only counts, subreddit names and the extraction script, so no one can look up an individual author.
- Posts whose authors delete them later cannot be tracked, so the test set is frozen once and the paper says so. This is an ethics-board question for the faculty, and Reddit's terms and API rules apply to the archive's source data.
