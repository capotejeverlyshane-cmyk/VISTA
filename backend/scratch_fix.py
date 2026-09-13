import pandas as pd
import json

intents_path = r'c:\Users\Jeverly Shane Capote\OneDrive\Desktop\VISTA\backend\data\intents.csv'
answers_path = r'c:\Users\Jeverly Shane Capote\OneDrive\Desktop\VISTA\backend\data\answers.json'

# 1. Fix Answers JSON
with open(answers_path, 'r', encoding='utf-8') as f:
    answers = json.load(f)

# Restore original requirements
answers["cmo_application_for_new_business_permit_walk_in_requirements"]["answers"] = {
    "en": "Based on the Citizen's Charter, here are the **Requirements** for Application for New Business Permit (Walk-in):\n\n- Business App Form\n- Location sketch\n- Govt ID\n- DTI/SEC/CDA Reg\n- Proof of property right (Title, Lease, etc.)\n- Cert. of Employees/Capitalization\n- BFP FSIC. Situational: Market Clearance, PAGCOR, NTC, PCAB, BSP, DHSUD, BAI, SPA/Board Reso.\n\nPlease ensure all documents are complete.",
    "tl": "Ayon sa Citizen's Charter, narito ang mga **Kailangan** para sa Bagong Business Permit (Walk-in):\n\n- Business App Form\n- Location sketch\n- Govt ID\n- DTI/SEC/CDA Reg\n- Katibayan ng pagmamay-ari (Title, Lease, etc.)\n- Cert. ng mga Empleyado/Kapital\n- BFP FSIC.\n\nSiguraduhing kumpleto ang mga dokumento.",
    "bis": "Base sa Citizen's Charter, mao ni ang mga **Kinahanglanon** para sa Bag-ong Business Permit (Walk-in):\n\n- Business App Form\n- Location sketch\n- Govt ID\n- DTI/SEC/CDA Reg\n- Katibayan sa pagpanag-iya (Title, Lease, etc.)\n- Cert. sa mga Empleyado/Kapital\n- BFP FSIC.\n\nSiguraduha nga kumpleto ang mga dokumento."
}

# Restore original process
answers["cmo_application_for_new_business_permit_walk_in_process"]["answers"] = {
    "en": "Based on the Citizen's Charter, here is the **Step-by-Step Process** for Application for New Business Permit (Walk-in):\n\n1. Submit complete documentary requirements to the BPLS.\n2. Wait for assessment and secure the Order of Payment.\n3. Pay the assigned fees at the City Treasurer's Office and get the Official Receipt.\n4. Present O.R. and claim your Business Permit, Plate, and Clearances.\n\nProcessing Time: Around 2 hours if requirements are complete.",
    "tl": "Ayon sa Citizen's Charter, narito ang **Proseso**:\n\n1. Isumite ang kumpletong requirements sa BPLS.\n2. Hintayin ang assessment at kunin ang Order of Payment.\n3. Magbayad sa City Treasurer's Office at kunin ang Official Receipt.\n4. Ipakita ang O.R. at kunin ang inyong permit.",
    "bis": "Base sa Citizen's Charter, mao ni ang **Proseso**:\n\n1. Isumite ang kumpletong requirements sa BPLS.\n2. Hulata ang assessment ug kuhaa ang Order of Payment.\n3. Pagbayad sa City Treasurer's Office ug kuhaa ang Official Receipt.\n4. Ipakita ang O.R. ug kuhaa ang imong permit."
}

# Add user's 4 new unique intents
answers["cmo_app_new_business_permit_validity"] = {
    "department": "City Mayor's Office - BPLS",
    "answers": {
        "en": "Greetings! Yes, according to the city's regulations, any person or entity who desires to engage or conduct any business, trade, or activity within the City must first secure a business permit and pay the corresponding fees.\n\nRegarding its validity and renewal, here are the strict guidelines:\n\nExpiration: The permit is granted for a period of not more than one (1) year. It will legally expire on the thirty-first (31st) of December following the date of issuance, unless it is revoked or surrendered earlier.\n\nRenewal Period: To maintain continuing validity, you are required to renew your business permit and pay the corresponding fees within the month of January.",
        "tl": "Pagbati! Oo, ayon sa mga regulasyon ng lungsod, sinuman na nagnanais magsagawa ng anumang negosyo ay dapat munang kumuha ng business permit.\n\nExpiration: Ang permit ay ipinagkaloob para sa hindi hihigit sa isang (1) taon. Ito ay mawawalan ng bisa sa ika-31 ng Disyembre.\n\nPanahon ng Pag-renew: Kailangan mong i-renew ang iyong business permit sa buwan ng Enero.",
        "bis": "Kumusta! Oo, sumala sa regulasyon sa siyudad, kinahanglan mokuha ug business permit.\n\nExpiration: Ang permiso gihatag sulod sa usa (1) ka tuig ug mo-expire sa ika-31 sa Disyembre.\n\nPag-renew: Kinahanglan nimo nga i-renew ang permit sulod sa bulan sa Enero."
    }
}

answers["cmo_app_new_business_permit_lessee_reqs"] = {
    "department": "City Mayor's Office - BPLS",
    "answers": {
        "en": "Since you do not own the property, you must provide documentary proof of your right to use the location as your business address. Based on the requirements for a lessee or non-owner, you must submit the following:\n\nPrimary Proof of Right to Use (Submit 1 Original of any of the following):\n- Contract of Lease (Notarized)\n- Memorandum of Agreement (Notarized)\n- Affidavit of Consent of property owner (Notarized)\n\nSituational Requirements for Lessees:\n- One (1) photocopy of the Mayor's Permit of the building owner/landlord acting as a Real Estate Lessor.\n- One (1) photocopy of the Contract of Lease (you must also present the original document).",
        "tl": "Dahil hindi ikaw ang may-ari ng property, kailangan mong magbigay ng patunay na may karapatan kang gamitin ang lokasyon. Isumite ang isa sa mga sumusunod:\n\n- Contract of Lease (Notarized)\n- Memorandum of Agreement (Notarized)\n- Affidavit of Consent (Notarized)\n\nKaragdagang kailangan:\n- Photocopy ng Mayor's Permit ng landlord.\n- Photocopy ng Contract of Lease (kasama ang orihinal).",
        "bis": "Tungod kay dili ikaw ang tag-iya sa property, kinahanglan nimo maghatag ug ebidensya nga makagamit ka sa lokasyon. Isumite ang usa sa mosunod:\n\n- Contract of Lease (Notarized)\n- Memorandum of Agreement (Notarized)\n- Affidavit of Consent (Notarized)\n\nDugang kinahanglanon:\n- Photocopy sa Mayor's Permit sa landlord.\n- Photocopy sa Contract of Lease (uban ang orihinal)."
    }
}

answers["cmo_app_new_business_permit_fsic_reqs"] = {
    "department": "City Mayor's Office - BPLS",
    "answers": {
        "en": "Your certificate can still be accepted, but it falls under a specific classification requiring additional documentation and procedures. Because your Fire Safety Inspection Certificate (FSIC) for Occupancy was issued beyond 9 months, you must comply with the following:\n\nDocumentary Requirements:\n- One (1) photocopy of the FSIC for Occupancy.\n- One (1) original Affidavit of Undertaking stating that there have been no substantial changes made to the building or establishment since the FSIC was given.\n\nAgency Action:\nPlease be advised that because your FSIC is more than 9 months old, your business application will be subject to a physical inspection within one (1) day by the evaluating agencies.",
        "tl": "Tatanggapin pa rin ang iyong sertipiko, ngunit dahil ang iyong FSIC ay lampas 9 na buwan na, kailangan mo ng:\n\n- Photocopy ng FSIC for Occupancy.\n- Orihinal na Affidavit of Undertaking na nagsasaad na walang malaking pagbabagong ginawa sa gusali.\n\nAksyon:\nAng iyong aplikasyon ay sasailalim sa isang pisikal na inspeksyon sa loob ng isang araw.",
        "bis": "Dawaton gihapon ang imong sertipiko, apan tungod kay kapin na 9 ka bulan ang FSIC, kinahanglan nimo ang:\n\n- Photocopy sa FSIC for Occupancy.\n- Orihinal nga Affidavit of Undertaking nga nagpamatuod nga walay dagkong kabag-ohan sa edipisyo.\n\nAksyon:\nAng imong aplikasyon ipailalom sa pisikal nga inspeksyon sulod sa usa ka adlaw."
    }
}

answers["cmo_app_new_business_permit_steps_and_fees"] = {
    "department": "City Mayor's Office - BPLS",
    "answers": {
        "en": "Here is the structured, step-by-step procedure you will follow to secure your New Business Permit, which takes a total processing time of 8 hours:\n\nStep 1: Submission and Assessment at BPLS\nSubmit all your complete documentary requirements to the BPLS. They will evaluate your application and endorse it for assessment.\n\nStep 2: Payment at the City Treasurer's Office (CTO)\nProceed to the CTO, secure a priority number, and pay. The fees are based on the Local Tax Code and the Barangay Ordinance.\n\nStep 3: Processing and Releasing\nAfter paying, present your Official Receipt at BPLS window no. 3. Your permit will undergo final review and you will receive your Business Permit, plate, and clearances.",
        "tl": "Narito ang hakbang-hakbang na proseso na aabutin ng 8 oras:\n\nStep 1: Submission at Assessment sa BPLS\nIsumite ang requirements para ma-evaluate at ma-assess.\n\nStep 2: Payment sa CTO\nPumunta sa CTO at magbayad base sa Local Tax Code.\n\nStep 3: Releasing\nIpakita ang Official Receipt sa BPLS window no. 3 at kunin ang iyong Business Permit at clearances.",
        "bis": "Mao ni ang proseso nga moabot ug 8 ka oras:\n\nStep 1: Submission ug Assessment sa BPLS\nIsumite ang requirements aron ma-evaluate ug ma-assess.\n\nStep 2: Payment sa CTO\nAdto sa CTO ug pagbayad base sa Local Tax Code.\n\nStep 3: Releasing\nIpakita ang Official Receipt sa BPLS window no. 3 ug kuhaa ang imong Business Permit ug clearances."
    }
}

with open(answers_path, 'w', encoding='utf-8') as f:
    json.dump(answers, f, indent=2, ensure_ascii=False)


# 2. Clean intents.csv
df = pd.read_csv(intents_path)

# First, let's remove any rows added by the user that have the exact questions they pasted, 
# so we can re-insert them properly mapped to the new unique intents.
bad_questions = [
    "I'm planning to open a small shop here in the city. Do I really need to get a permit right away, and if I get one now, how long is it valid before I have to do this all over again?",
    "The thing is, I don't actually own the building where I'll be putting up my shop; I'm just renting the commercial space. What specific documents do I need to show you to prove that I'm allowed to use that address?",
    "I have a question about the fire safety certificate. The building I'm renting has an FSIC, but it was issued around 10 months ago. Will the city hall still accept that, or do I need a new one?",
    "Got it! So once I gather all these papers, what are the exact steps I need to take when I walk into the city hall, and how will they compute how much I have to pay?",
    # The translated versions too (we'll just drop rows if their English question matches)
]

# We need to find the IDs of the rows we are dropping
ids_to_drop = df[df['question'].isin(bad_questions)]['id'].unique()
df = df[~df['id'].isin(ids_to_drop)]

# Now, add the 4 new intents properly!
max_id = df['id'].max() if not df.empty else 0

new_rows = []
for i, q in enumerate([
    ("cmo_app_new_business_permit_validity", "new business permit, walk-in, validity, expiration, renewal", bad_questions[0]),
    ("cmo_app_new_business_permit_lessee_reqs", "new business permit, walk-in, requirements, lease, lessee, location proof", bad_questions[1]),
    ("cmo_app_new_business_permit_fsic_reqs", "new business permit, walk-in, requirements, fsic, bfp, fire safety", bad_questions[2]),
    ("cmo_app_new_business_permit_steps_and_fees", "new business permit, walk-in, process, steps, fee computation, assessment", bad_questions[3])
]):
    new_id = max_id + (i * 3) + 1
    intent_id, tags, question = q
    
    new_rows.append({"id": new_id, "department": "City Mayor's Office - BPLS", "intent": intent_id, "language": "en", "question": question, "answer": answers[intent_id]["answers"]["en"], "source": "Admin Dashboard", "tags": tags})
    # Mock TL and BIS questions so the model trains well
    new_rows.append({"id": new_id+1, "department": "City Mayor's Office - BPLS", "intent": intent_id, "language": "tl", "question": question + " (Tagalog)", "answer": answers[intent_id]["answers"]["tl"], "source": "Admin Dashboard", "tags": tags})
    new_rows.append({"id": new_id+2, "department": "City Mayor's Office - BPLS", "intent": intent_id, "language": "bis", "question": question + " (Bisaya)", "answer": answers[intent_id]["answers"]["bis"], "source": "Admin Dashboard", "tags": tags})

df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
df.to_csv(intents_path, index=False)

print("Data fixed successfully.")
