LANG = "en"
ROWS = [
 # digital_arrest
 ("digital_arrest", "scam", "call-transcript", 6, [
  "Hello, am I speaking to the owner of this mobile number? This is the cyber crime branch, Mumbai.",
  "Yes, that's me. What is this about?",
  "A parcel booked in your name was seized at the airport. It contains passports and illegal tablets. A case has been registered against your Aadhaar.",
  "What? I haven't sent any parcel. There must be a mistake.",
  "Sir, do not disconnect this call. You will now be connected to a senior officer on video. Keep your camera on and tell nobody, it is a confidential investigation.",
  "Okay, okay. But I am scared, what should I do?",
  "To prove your funds are clean, transfer your savings to the RBI verification account. It will be refunded after the check. Tell me your account balance now."]),
 ("digital_arrest", "benign", "call-transcript", None, [
  "Good afternoon, this is the local police station. Am I speaking with Mr. Kulkarni? Your passport application is at the verification stage.",
  "Yes, I applied last week. Is something missing?",
  "No, this is routine. An officer will visit your registered address tomorrow between 11 and 1 to confirm that you live there.",
  "I'll be home. Should I keep any documents ready?",
  "Just your original Aadhaar and the rent agreement if you are a tenant. The officer will show an ID card, you can check it.",
  "Great. Can I also come to the station if that is easier?",
  "Yes, you can visit the passport desk any weekday morning. No payment is needed for the verification. Thank you, sir."]),
 # task_job
 ("task_job", "scam", "whatsapp", 4, [
  "Hi! We found your profile on a job portal. Part-time work from home, earn Rs 3000 to 8000 daily by liking videos. Interested?",
  "What kind of work exactly? Is there any fee?",
  "No fee for registration. You just like and screenshot. First task done, here is Rs 150 as a trial payout, please check your account.",
  "Oh I got the money. That was quick!",
  "Yes! Now you are eligible for premium tasks with 30% commission. Pay Rs 1000 as a task deposit, you will get Rs 1300 back in 10 minutes.",
  "Okay I sent it. Where is my money?",
  "Congratulations, the next task needs Rs 5000 and returns Rs 7000. Do it fast or the batch will close."]),
 ("task_job", "benign", "whatsapp", None, [
  "Hello Neha, this is Pooja from the HR team at Verma Analytics. We liked your resume for the data intern role.",
  "Hi Pooja, thank you! I'm very interested.",
  "Are you available for a 30 minute video interview on Thursday at 3 pm?",
  "Yes, Thursday works. Should I prepare anything?",
  "Please keep your resume handy and be ready to discuss your project. I will email the meeting invite from our official address.",
  "Perfect, I'll check my mail. Thanks again.",
  "You're welcome. Nothing is required from your side except the interview. See you Thursday."]),
 # kyc_bank
 ("kyc_bank", "scam", "sms", 0, [
  "Dear customer, your bank KYC has expired and your account will be blocked today. Update immediately by installing the app: [link]",
  "I did my KYC last year, who is this?",
  "Sir, this is the bank KYC department. Records show it is pending. Please install the KYC app, it will take two minutes.",
  "Is it safe? I got no such mail from the bank.",
  "Yes, it is the official update. After installing, tell me the OTP you receive to finish verification.",
  "I'm not comfortable giving an OTP.",
  "Then your account will be frozen in one hour and you will lose access to your salary."]),
 ("kyc_bank", "benign", "sms", None, [
  "Dear customer, your KYC is due for periodic update. Please visit your home branch with ID proof or use the official bank app. Ignore if already done.",
  "Thanks. Can I do it online?",
  "Yes, you can submit documents in the app under Services, or at the branch. Our staff will never ask for your OTP, PIN or CVV.",
  "Okay, I'll go to the branch on Saturday.",
  "Branch is open on Saturday from 10 am to 2 pm. Please carry your Aadhaar and PAN.",
  "Got it, thanks."]),
 # electricity
 ("electricity", "scam", "whatsapp", 2, [
  "Your electricity connection will be disconnected tonight at 9:30 pm because last month's bill is unpaid. Call the officer immediately: [number]",
  "But I paid my bill on the 5th. Who is this?",
  "Sir, the payment was not updated in our system. Install the electricity board app from the link to confirm and pay Rs 10 for verification.",
  "I don't want to install anything unknown.",
  "Then the line will be cut tonight and reconnection will cost Rs 5000. Just pay the verification fee and share your screen so I can fix it.",
  "I'll check with the office tomorrow.",
  "Sir, by then it will be too late. Last warning."]),
 ("electricity", "benign", "sms", None, [
  "Reminder: your electricity bill of Rs 1,240 for the month of August is due on 18 September. Pay via the official website, app or at the customer care centre.",
  "I think I already paid. Can I check?",
  "You can view your payment history in the official app under Bill History. If payment is already made, please ignore this message.",
  "Found it, it's paid. Thanks.",
  "Thank you for paying on time."]),
 # courier_customs
 ("courier_customs", "scam", "sms", 2, [
  "Your parcel is held at the customs office. Address incomplete.",
  "I'm not expecting any parcel. From whom?",
  "A gift parcel from abroad. Customs duty of Rs 2,450 is pending. Pay at [link] today, otherwise it will be returned and a penalty applies.",
  "Why would I pay duty on a gift I don't know about?",
  "Sir, the sender has already declared it. Enter your card details on the page to release it. Parcel will be destroyed after 24 hours."]),
 ("courier_customs", "benign", "sms", None, [
  "Hi, I am the delivery executive for your order. I am near your building. Can you confirm the flat number?",
  "It's B-402, second tower.",
  "Thanks. I will be there in 10 minutes. Please keep your phone with you so I can call if I get lost.",
  "Okay, will do.",
  "Delivered. Have a nice day!"]),
 # investment_group
 ("investment_group", "scam", "telegram", 4, [
  "Welcome to our free stock tips group. Our analysts gave 80% returns last month. Check the screenshots above.",
  "Looks good. How do I join the tips?",
  "Tips are free for the first week. Just follow the calls at 9:15 sharp.",
  "I followed the first call and made a small profit, nice.",
  "You are lucky! Our VIP members get guaranteed IPO allotments. Deposit Rs 25,000 on our trading platform to join VIP today.",
  "I deposited. Now I want to withdraw some profit.",
  "To withdraw you need to pay 20% tax first, Rs 10,000. Then it will be released."]),
 ("investment_group", "benign", "whatsapp", None, [
  "Did you start your SIP yet? I put Rs 3000 a month in an index fund.",
  "Not yet. Is it risky?",
  "Markets go up and down, so people usually stay invested for years. It's not guaranteed.",
  "Which app do you use?",
  "I use the one from my bank, but you can compare a few. Read the fund factsheet before you decide.",
  "Thanks, I'll read up this weekend."]),
 # upi_refund
 ("upi_refund", "scam", "call-transcript", 2, [
  "Hello sir, I accidentally sent Rs 5000 to your number instead of my friend's. Please check your account.",
  "I haven't received anything yet. Let me look.",
  "It should be there. Please return it right now. I will send you a request, just approve it and enter your PIN.",
  "Wait, a request to approve? Isn't that for receiving money?",
  "Yes sir, just approve once, it will refund me. Or if you cannot, share your screen and I will do it for you.",
  "No, I'll check with my bank first.",
  "Sir, I am a poor man, please do this for me, my child is in hospital."]),
 ("upi_refund", "benign", "whatsapp", None, [
  "Hey, I paid Rs 2400 for dinner last night and just sent you Rs 1200 for your half of the cab. We're even.",
  "Oh nice, got the notification. Thanks!",
  "Cool. Next dinner is on me."]),
 # army_olx
 ("army_olx", "scam", "whatsapp", 4, [
  "Hello, I saw your sofa listing. I am posted with the army and can't visit. I'll buy it at your price.",
  "Okay, thanks. Pickup would need to be arranged by you.",
  "My men will pick it up. Let me pay you first. I'll send a QR code, you scan it to receive the money.",
  "Scan to receive? I thought QR codes are for paying.",
  "No, with army security it works differently. Just scan the QR and enter your PIN. Rs 8000 will arrive instantly.",
  "My account debited Rs 8000 instead!",
  "Sorry, system error. Scan another code and it will be returned double."]),
 ("army_olx", "benign", "whatsapp", None, [
  "Hi, is the sofa still available? Would you take Rs 7000?",
  "I can do Rs 8000, it's in good condition.",
  "Okay Rs 7500 final, I can pick it up on Sunday with a tempo.",
  "Deal. Sunday at 11, I will share the address when you reach the area.",
  "Great, I will pay by UPI after I see it."]),
]
