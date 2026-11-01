# Taxonomy

## Languages (`lang`)
| code | description |
|---|---|
| `en` | English (Indian usage) |
| `hi-Latn` | Hinglish: Hindi written in Roman script, often code-mixed with English |
| `hi-Deva` | Hindi in Devanagari |
| `mr-Deva` | Marathi in Devanagari |

## Channels (`channel`)
`whatsapp`, `sms`, `telegram`, `call-transcript`

## Scam types (`type`, only when `label == "scam"`)
| id | name | typical arc |
|---|---|---|
| `digital_arrest` | Police / agency impersonation ("digital arrest") | Parcel or SIM "linked to a crime" -> video call -> "stay on call" -> transfer to "verify" funds |
| `task_job` | Task / job / internship scam | Easy online job -> small payout -> deposit for a "prepaid task" -> larger deposits |
| `kyc_bank` | Bank / KYC update | "Account will be blocked" -> link or APK -> OTP / card details |
| `electricity` | Electricity disconnection | "Bill unpaid, power cut tonight" -> call this number -> app install / payment |
| `courier_customs` | Courier / customs parcel | "Parcel held, fee due" -> payment link or call |
| `investment_group` | WhatsApp / Telegram investment-tips group | Free tips -> small wins -> "VIP" deposit -> withdrawal blocked |
| `upi_refund` | UPI "sent by mistake" / refund | Money "sent to you by mistake" -> "return it" or collect request / screen share |
| `army_olx` | "Army officer" buyer on OLX-style listings | Wants to buy quickly -> "QR code to receive" -> sends a collect request |

## Benign hard negatives (`label == "benign"`, `type` = matching `hard_neg_of`)
Each scam type has a legitimate look-alike so detectors can't just learn "mentions bank / police / parcel":
| `hard_neg_of` | benign look-alike |
|---|---|
| `digital_arrest` | genuine police station call about a passport or lost-phone report |
| `task_job` | genuine recruiter / HR scheduling an interview; real internship offer |
| `kyc_bank` | genuine bank KYC reminder that points to the branch or official app, with no OTP request |
| `electricity` | genuine bill reminder from the utility |
| `courier_customs` | genuine delivery partner confirming an address or time |
| `investment_group` | friends discussing mutual funds / SIPs |
| `upi_refund` | friend or family member actually requesting UPI money |
| `army_olx` | genuine buyer negotiating price and pickup |
Plus `everyday` for ordinary chats with no look-alike.

## `ask_turn`
Index (0-based, into `turns`) of the first turn that asks the target for any of:
money / payment, an OTP or PIN, installing an app, screen sharing, or personal or financial data.
Scam conversations must have one; benign ones have `ask_turn = null`.
The earliness metric is "was the scam flagged before `ask_turn`?"
