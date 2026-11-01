# Synthetic A: hand-written in-session (no paid API)

Synthetic A conversations are written by the assistant in the working session from the scenario list below, then
checked with `scripts/validate.py`. Each scenario ("seed") is written once per language, so every seed_id appears
in all four languages; the split script must group by seed_id to avoid leakage across languages.

## Rules
- 6 to 10 turns, alternating initiator / target, initiator first.
- Scam: the first request for money, OTP/PIN, app install, screen share, or personal/financial data is at `ask_turn`.
  Aim to vary `ask_turn` between 2 and 6, so earliness is measurable (not always at the last turn).
- Benign look-alike: same vocabulary (bank, police, parcel, UPI...) but no such request, `ask_turn = null`.
- Targets behave like real people: confused, suspicious, half-compliant, hinglish typos in `hi-Latn`.
- No real phone numbers, URLs, UPI ids, emails. Use `[link]`, `[number]`, `[upi]` placeholders.
- No real people, banks, agencies named as culprits beyond generic references (e.g. "bank", "police").
- Do not copy phrasing from ICFD-31k or other datasets.

## Seeds per type (batch 1: one scam + one benign hard negative each, 8 types x 4 langs x 2 = 64)
1. digital_arrest: parcel with illegal items in target's name -> "CBI officer" video call -> stay on call -> transfer.
   Benign: police station calls about passport verification.
2. task_job: "like YouTube videos, earn per task" -> small payout -> deposit for prepaid task. Benign: HR schedules interview.
3. kyc_bank: "KYC expires today" -> install APK / share OTP. Benign: bank reminds to visit branch / official app.
4. electricity: "bill unpaid, power cut at 9:30 pm" -> call officer / install app. Benign: utility bill reminder.
5. courier_customs: "parcel held, pay customs fee". Benign: delivery partner confirms address and slot.
6. investment_group: free stock tips group -> VIP deposit. Benign: friends discussing SIP.
7. upi_refund: "sent Rs 5000 by mistake, return it" -> collect request. Benign: sibling asking for dinner split.
8. army_olx: "army buyer" sends QR to "receive" money. Benign: buyer negotiating pickup of a sofa.
