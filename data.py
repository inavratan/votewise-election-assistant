"""
data.py — ELECTION DATA

Comprehensive election data structs including timelines, states, documents, FAQs.
"""

__all__ = [
    "ELECTION_TIMELINE",
    "STATE_ELECTIONS",
    "VOTER_DOCUMENTS",
    "VOTER_RIGHTS",
    "FAQ_DATA",
    "AI_PREDICTIONS",
    "CONCIERGE_FALLBACKS"
]

ELECTION_TIMELINE = [
    {
        "id": "registration",
        "title": "Voter Registration",
        "icon": "📝",
        "duration": "Continuous",
        "description": "The process of registering eligible citizens to vote.",
        "details": [
            "Use <a href='https://voters.eci.gov.in/' target='_blank'>Form 6</a> for new registration (online at nvsp.in or offline).",
            "Use <a href='https://voters.eci.gov.in/' target='_blank'>Form 6B</a> for linking Aadhaar with Electoral Roll.",
            "Must be 18 years old on the qualifying date (typically Jan 1).",
            "Overseas Indian citizens use <a href='https://voters.eci.gov.in/' target='_blank'>Form 6A</a>."
        ],
        "key_dates_example": "Qualifying Date: Jan 1, 2024",
        "status": "completed"
    },
    {
        "id": "electoral_roll",
        "title": "Electoral Roll Publication",
        "icon": "📜",
        "duration": "30-60 Days",
        "description": "Publication of the voter list for public scrutiny.",
        "details": [
            "Draft roll is published first for public view.",
            "Periods are given for claims (adding names) and objections (removing names).",
            "Final electoral roll is published after resolving all claims.",
            "Continuous updating happens till the last date of nomination."
        ],
        "key_dates_example": "Final Roll Date: Jan 5, 2024",
        "status": "completed"
    },
    {
        "id": "announcement",
        "title": "Election Announcement",
        "icon": "📢",
        "duration": "1 Day",
        "description": "ECI officially announces the election schedule.",
        "details": [
            "The Model Code of Conduct (MCC) comes into effect immediately.",
            "MCC prevents the ruling party from misusing official machinery.",
            "Schedule details phases, polling dates, and counting dates."
        ],
        "key_dates_example": "Announcement Date: March 16, 2024",
        "status": "completed"
    },
    {
        "id": "nomination",
        "title": "Nomination Filing",
        "icon": "📋",
        "duration": "7-10 Days",
        "description": "Candidates file their nomination papers.",
        "details": [
            "Filing period lasts about 7 days after notification.",
            "Scrutiny of papers is done usually the day after filing closes.",
            "Candidates can withdraw nominations within 2 days of scrutiny.",
            "Final list of contesting candidates is published after withdrawals."
        ],
        "key_dates_example": "Filing Deadline: April 4, 2024",
        "status": "completed"
    },
    {
        "id": "campaign",
        "title": "Campaign Period",
        "icon": "📣",
        "duration": "14+ Days",
        "description": "Political parties and candidates campaign for votes.",
        "details": [
            "Strict spending limits apply to candidates.",
            "Rallies, public meetings, and door-to-door campaigns are held.",
            "Campaigning ends 48 hours before polling starts (Silence Period).",
            "During the Silence Period, no public meetings or loud campaigns are allowed."
        ],
        "key_dates_example": "Campaigning Ends: April 17, 2024 (5 PM)",
        "status": "current"
    },
    {
        "id": "polling",
        "title": "Polling Day",
        "icon": "🗳️",
        "duration": "1 Day",
        "description": "Voters cast their votes at polling stations.",
        "details": [
            "Typically open from 7 AM to 6 PM.",
            "Anyone in the queue at 6 PM is allowed to vote.",
            "EVMs (Electronic Voting Machines) and VVPATs are used.",
            "VVPAT slip is visible for 7 seconds to verify the vote.",
            "Indelible ink is applied to the left index finger."
        ],
        "key_dates_example": "Polling Date: April 19, 2024",
        "status": "upcoming"
    },
    {
        "id": "counting",
        "title": "Counting & Results",
        "icon": "📊",
        "duration": "1 Day",
        "description": "Votes are counted and results are declared.",
        "details": [
            "EVMs are kept in strong rooms under heavy security.",
            "Postal ballots are counted first.",
            "EVM votes are counted round-by-round.",
            "Winning candidates are given a certificate of election."
        ],
        "key_dates_example": "Counting Date: June 4, 2024",
        "status": "upcoming"
    },
    {
        "id": "formation",
        "title": "Government Formation",
        "icon": "🏛️",
        "duration": "Post-Results",
        "description": "The winning party or coalition forms the government.",
        "details": [
            "Requires a simple majority (50% + 1 seats) in the house.",
            "The President (or Governor) invites the leader of the majority.",
            "Elected representatives take the oath of office."
        ],
        "key_dates_example": "Swearing-in: Mid-June 2024",
        "status": "upcoming"
    }
]

STATE_ELECTIONS = {
    "maharashtra": {
        "name": "Maharashtra",
        "seats_lok_sabha": 48,
        "seats_vidhan_sabha": 288,
        "last_election_year": 2019,
        "registered_voters": "8.9 Crore",
        "turnout_percentage": "61.02%",
        "upcoming_election": "Late 2024",
        "fun_fact": "Maharashtra has 48 Lok Sabha constituencies, the second highest in India after UP."
    },
    "delhi": {
        "name": "Delhi",
        "seats_lok_sabha": 7,
        "seats_vidhan_sabha": 70,
        "last_election_year": 2020,
        "registered_voters": "1.4 Crore",
        "turnout_percentage": "62.59%",
        "upcoming_election": "2025",
        "fun_fact": "Delhi is a National Capital Territory with its own Legislative Assembly."
    },
    "karnataka": {
        "name": "Karnataka",
        "seats_lok_sabha": 28,
        "seats_vidhan_sabha": 224,
        "last_election_year": 2023,
        "registered_voters": "5.3 Crore",
        "turnout_percentage": "73.19%",
        "upcoming_election": "2028",
        "fun_fact": "Karnataka witnessed its highest-ever voter turnout of 73.19% in 2023."
    },
    "tamil_nadu": {
        "name": "Tamil Nadu",
        "seats_lok_sabha": 39,
        "seats_vidhan_sabha": 234,
        "last_election_year": 2021,
        "registered_voters": "6.2 Crore",
        "turnout_percentage": "72.81%",
        "upcoming_election": "2026",
        "fun_fact": "The state often sees high voter participation across all demographics."
    },
    "uttar_pradesh": {
        "name": "Uttar Pradesh",
        "seats_lok_sabha": 80,
        "seats_vidhan_sabha": 403,
        "last_election_year": 2022,
        "registered_voters": "15+ Crore",
        "turnout_percentage": "60.80%",
        "upcoming_election": "2027",
        "fun_fact": "UP sends the highest number of MPs (80) to the Lok Sabha."
    },
    "west_bengal": {
        "name": "West Bengal",
        "seats_lok_sabha": 42,
        "seats_vidhan_sabha": 294,
        "last_election_year": 2021,
        "registered_voters": "7.3 Crore",
        "turnout_percentage": "81.70%",
        "upcoming_election": "2026",
        "fun_fact": "West Bengal consistently records among the highest voter turnouts in the country."
    },
    "gujarat": {
        "name": "Gujarat",
        "seats_lok_sabha": 26,
        "seats_vidhan_sabha": 182,
        "last_election_year": 2022,
        "registered_voters": "4.9 Crore",
        "turnout_percentage": "64.33%",
        "upcoming_election": "2027",
        "fun_fact": "The home state of Mahatma Gandhi has 26 Lok Sabha seats."
    },
    "rajasthan": {
        "name": "Rajasthan",
        "seats_lok_sabha": 25,
        "seats_vidhan_sabha": 200,
        "last_election_year": 2023,
        "registered_voters": "5.2 Crore",
        "turnout_percentage": "74.62%",
        "upcoming_election": "2028",
        "fun_fact": "A vibrant state where the Election Commission sets up booths even for a single voter deep in the desert."
    },
    "madhya_pradesh": {
        "name": "Madhya Pradesh",
        "seats_lok_sabha": 29,
        "seats_vidhan_sabha": 230,
        "last_election_year": 2023,
        "registered_voters": "5.6 Crore",
        "turnout_percentage": "77.15%",
        "upcoming_election": "2028",
        "fun_fact": "Madhya Pradesh is the second-largest state in India by area."
    },
    "bihar": {
        "name": "Bihar",
        "seats_lok_sabha": 40,
        "seats_vidhan_sabha": 243,
        "last_election_year": 2020,
        "registered_voters": "7.3 Crore",
        "turnout_percentage": "57.05%",
        "upcoming_election": "2025",
        "fun_fact": "Bihar was the first state where the innovative 'Panchayat Elections' system was tested widely."
    }
}

VOTER_DOCUMENTS = [
    {"id": "epic", "name": "EPIC (Voter ID Card)", "description": "Primary document issued by ECI."},
    {"id": "aadhaar", "name": "Aadhaar Card", "description": "12-digit unique identity number."},
    {"id": "pan", "name": "PAN Card", "description": "Permanent Account Number by Income Tax Dept."},
    {"id": "passport", "name": "Indian Passport", "description": "Issued by Ministry of External Affairs."},
    {"id": "driving_license", "name": "Driving License", "description": "Valid DL issued by RTO."},
    {"id": "bank_passbook", "name": "Bank/Post Office Passbook", "description": "Must have a photograph attached."},
    {"id": "mnrega", "name": "MNREGA Job Card", "description": "Issued under the rural employment scheme."},
    {"id": "health_insurance", "name": "Health Insurance Smart Card", "description": "Issued by Ministry of Labour."},
    {"id": "pension", "name": "Pension Document", "description": "Must contain a photograph."},
    {"id": "govt_id", "name": "Govt Service ID Card", "description": "Issued by Central/State Govt/PSU with photo."},
    {"id": "mps_mlas_id", "name": "Official Identity Cards", "description": "Issued to MPs/MLAs/MLCs."},
    {"id": "udid", "name": "Unique Disability ID (UDID)", "description": "Card issued to PwD by the Govt."}
]

VOTER_RIGHTS = [
    {"title": "Paid leave on polling day", "desc": "Under Section 135B of the RPA, employers must grant a paid holiday on voting day."},
    {"title": "Voting past closing time", "desc": "Anyone in the queue at the 6 PM cutoff time has the right to vote, no matter how long it takes."},
    {"title": "Accessibility for PwD", "desc": "Ramps, braille on EVMs, and wheelchair access are guaranteed for Persons with Disabilities."},
    {"title": "NOTA Option", "desc": "Right to register a 'None of the Above' vote on the EVM."},
    {"title": "Challenge Vote", "desc": "If someone else has cast a vote in your name, you can cast a 'Tendered Vote' using a ballot paper."},
    {"title": "Secrecy of Ballot", "desc": "Your vote is completely secret and cannot be disclosed forcefully."}
]

FAQ_DATA = [
    {"q": "How do I register to vote?", "a": "You can register online via the NVSP portal (nvsp.in) by filling <a href='https://voters.eci.gov.in/' target='_blank'>Form 6</a>, or offline by submitting it to your local Electoral Registration Officer (ERO)."},
    {"q": "What is the age requirement to vote?", "a": "You must be 18 years old on the qualifying date (typically January 1st, April 1st, July 1st, or October 1st of the year) to be eligible."},
    {"q": "What is NOTA?", "a": "NOTA stands for 'None Of The Above'. It was introduced in 2013 and allows you to express your disapproval of all contesting candidates."},
    {"q": "How does an EVM work?", "a": "An Electronic Voting Machine (EVM) lets you cast your vote by pressing the blue button next to your chosen candidate's symbol. A beep confirms the vote."},
    {"q": "What is VVPAT?", "a": "Voter Verifiable Paper Audit Trail (VVPAT) prints a slip showing the candidate you voted for. It is visible through a glass window for 7 seconds before dropping into a sealed box."},
    {"q": "Can NRIs vote?", "a": "Yes, Non-Resident Indians (NRIs) can vote if they have not acquired citizenship of any other country. They must fill <a href='https://voters.eci.gov.in/' target='_blank'>Form 6A</a> and vote in person in India."},
    {"q": "Who is eligible for a postal ballot?", "a": "Service voters (armed forces), election officials, essential service workers, PwD voters, and seniors (85+ years) are eligible for postal ballots."},
    {"q": "What if my name is missing from the voter list?", "a": "If your name is not on the final electoral roll, you cannot vote, even if you have an EPIC card in hand. Check your name online beforehand."},
    {"q": "What are the spending limits for candidates?", "a": "For Lok Sabha (Parliamentary), candidates can spend up to ₹95 lakhs. For Vidhan Sabha (Assembly), the limit is up to ₹40 lakhs, depending on the state."},
    {"q": "What is the Model Code of Conduct?", "a": "The MCC is a set of guidelines by the ECI for parties and candidates during elections to ensure free and fair polls. It applies from the announcement until results."},
    {"q": "How do I find my polling booth?", "a": "You can locate your polling booth online at the ECI Electoral Search portal (electoralsearch.in), or by calling the Voter Helpline at 1950."},
    {"q": "Can I vote with an Aadhaar card instead of Voter ID?", "a": "Yes! If you don't have an EPIC card, you can use any of the 11 alternative photo ID documents approved by the ECI, including an Aadhaar card."},
    {"q": "What happens if an EVM malfunctions?", "a": "If an EVM malfunctions, it is immediately replaced by a reserve machine. The votes cast on the previous machine are safely recorded in its control unit."},
    {"q": "Is it mandatory to link Aadhaar with Voter ID?", "a": "No, it is currently voluntary under <a href='https://voters.eci.gov.in/' target='_blank'>Form 6B</a>. It is done to verify identities and clean up duplicated names in the electoral list."},
    {"q": "How is a government formed after the results?", "a": "A party or coalition that secures more than 50% of the seats (a simple majority) gets invited by the President/Governor to form the government."}
]

AI_PREDICTIONS = {
    "registration": "The registration phase is crucial. Ensure you fill <a href='https://voters.eci.gov.in/' target='_blank'>Form 6</a> well ahead of deadlines.",
    "announcement": "Elections are announced! The Model Code of Conduct is now actively applied.",
    "nomination": "Candidates are preparing their affidavits for nomination.",
    "campaign": "It's campaign season! Stay informed but avoid misinformation. Follow the 48-hour silence period rules.",
    "polling": "Don't forget to take a valid Photo ID to the polling station. Early morning voting is usually faster.",
    "counting": "Results day! Keep checking official ECI feeds for accurate round-by-round counting.",
    "formation": "A new government is being sworn in based on the democratic mandate."
}

CONCIERGE_FALLBACKS = [
    {"keywords": ["register", "nvsp", "form 6", "enroll"], "response": "To register, submit <a href='https://voters.eci.gov.in/' target='_blank'>Form 6</a> online at the Voter's Service Portal or through the Voter Helpline App. You must be 18 years old on the qualifying date."},
    {"keywords": ["document", "id", "aadhaar", "epic", "booth", "carry"], "response": "You can vote using your EPIC (Voter ID). If you don't have it, you can use one of 11 alternative photo IDs, such as an Aadhaar Card, PAN Card, Indian Passport, or Driving License."},
    {"keywords": ["evm", "vvpat", "machine", "work", "slip", "beep"], "response": "The EVM registers your vote when you press the blue button next to the candidate's symbol. The VVPAT machine will then show a printed slip through a glass window for 7 seconds to confirm your choice."},
    {"keywords": ["age", "18", "qualifying", "old"], "response": "You must be at least 18 years of age on a qualifying date (Jan 1, Apr 1, Jul 1, or Oct 1) to be eligible to vote in India."},
    {"keywords": ["nota", "none", "reject"], "response": "NOTA stands for 'None of the Above'. It allows you to officially register your rejection of all contesting candidates. It is usually the last button on the EVM."},
    {"keywords": ["mcc", "code", "conduct", "model", "rules"], "response": "The Model Code of Conduct (MCC) is a set of guidelines issued by the ECI to regulate political parties and candidates prior to elections, ensuring a level playing field."},
    {"keywords": ["nri", "overseas", "abroad", "foreign"], "response": "Yes, NRIs holding an Indian passport can vote! You must register using <a href='https://voters.eci.gov.in/' target='_blank'>Form 6A</a>. However, you must be physically present at your designated polling booth in India to cast your vote."},
    {"keywords": ["address", "shift", "form 8", "correction"], "response": "To change your address, correct your name, or update your photo, you need to submit <a href='https://voters.eci.gov.in/' target='_blank'>Form 8</a> online or offline."},
    {"keywords": ["delete", "remove", "death", "form 7"], "response": "To delete a name from the voter list (e.g., due to shifting or death), you must submit <a href='https://voters.eci.gov.in/' target='_blank'>Form 7</a>."},
    {"keywords": ["pwd", "disability", "disabled", "wheelchair", "blind"], "response": "The ECI provides special facilities for Persons with Disabilities (PwD), including wheelchair access, braille on EVMs, free transport, and the option to vote from home using postal ballots in certain cases."},
    {"keywords": ["home", "senior", "85", "postal", "ballot"], "response": "Senior citizens above 85 years of age and Persons with Disabilities (40% benchmark) are eligible to vote from home using postal ballots. They must fill Form 12D within 5 days of the election notification."},
    {"keywords": ["find booth", "location", "station", "search"], "response": "You can find your polling booth location by visiting the <a href='https://electoralsearch.eci.gov.in/' target='_blank'>Electoral Search portal</a> and entering your EPIC number or personal details."},
    {"keywords": ["time", "hours", "open", "close"], "response": "Polling stations generally remain open from 7:00 AM to 6:00 PM. However, times may vary slightly based on the state or specific security situations."},
    {"keywords": ["slip", "download", "print"], "response": "You can download your digital Voter Information Slip from the ECI portal or the Voter Helpline App. It contains your polling booth details but is NOT valid as an ID proof for voting."},
    {"keywords": ["lost", "duplicate", "replacement"], "response": "If you lost your Voter ID (EPIC), you can apply for a duplicate one by submitting <a href='https://voters.eci.gov.in/' target='_blank'>Form 8</a> and selecting the option for 'Issue of Replacement EPIC without correction'."},
    {"keywords": ["holiday", "leave", "paid"], "response": "Yes, polling day is a declared paid holiday for all employees under Section 135B of the Representation of the People Act, 1951, so they can cast their votes."},
    {"keywords": ["hello", "hi", "namaste", "hey"], "response": "Namaste! I am VoteWise, your AI election guide. What would you like to know about the Indian election process or your voter rights today?"},
    {"keywords": ["votewise", "creator"], "response": "I am VoteWise, an AI Concierge designed to help Indian citizens understand the election process, register to vote, and know their rights."}
]
