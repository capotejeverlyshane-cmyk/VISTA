import json
import pandas as pd

ANSWERS_FILE = 'data/answers.json'
INTENTS_FILE = 'data/intents.csv'

NEW_DATA = {
    "cmo_new_business_permit": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "To apply for a **New Business Permit**, you can do it via Walk-in or Online.\n\n---\n### 🏢 Walk-in Application\n\n**Steps:**\n1. Submit complete documentary requirements to the BPLS (Business Permit and Licensing Section).\n2. Wait for assessment and secure the Order of Payment.\n3. Pay the assigned fees at the City Treasurer's Office and get the Official Receipt.\n4. Present O.R. and claim your Business Permit, Plate, and Clearances.\n\n**Requirements:**\n- DTI/SEC/CDA Registration\n- Location plan or sketch\n- Proof of right to use location (Title, Lease Contract, etc.)\n- Barangay Clearance\n\n💰 **Cost:** Depends on capitalization and classification.\n⏱️ **Processing Time:** Around 2 hours if requirements are complete.",
            "tl": "Para mag-apply ng **Bagong Business Permit**, maaari itong gawin via Walk-in o Online.\n\n---\n### 🏢 Walk-in Application\n\n**Steps:**\n1. Isumite ang kumpletong requirements sa BPLS.\n2. Hintayin ang assessment at kunin ang Order of Payment.\n3. Magbayad sa City Treasurer's Office at kunin ang Official Receipt.\n4. Ipakita ang O.R. at kunin ang inyong Business Permit, Plate, at Clearances.\n\n**Mga Kailangan:**\n- DTI/SEC/CDA Registration\n- Location plan o sketch\n- Katibayan ng pagmamay-ari o Lease Contract ng pwesto\n- Barangay Clearance\n\n💰 **Bayad:** Depende sa kapital at klase ng negosyo.\n⏱️ **Processing Time:** Tinatayang 2 oras kung kumpleto ang requirements.",
            "bis": "Aron maka-apply og **Bag-ong Business Permit**, pwede nimo buhaton via Walk-in o Online.\n\n---\n### 🏢 Walk-in Application\n\n**Steps:**\n1. Isumite ang kumpletong requirements sa BPLS.\n2. Hulata ang assessment ug kuhaa ang Order of Payment.\n3. Pagbayad sa City Treasurer's Office ug kuhaa ang Official Receipt.\n4. Ipakita ang O.R. ug kuhaa ang imong Business Permit, Plate, ug Clearances.\n\n**Mga Kinahanglanon:**\n- DTI/SEC/CDA Registration\n- Location plan o sketch\n- Katibayan sa pagpanag-iya o Lease Contract sa pwesto\n- Barangay Clearance\n\n💰 **Bayad:** Magdepende sa kapital ug klase sa negosyo.\n⏱️ **Processing Time:** Mga 2 ka oras kung kumpleto ang requirements."
        },
        "questions": [
            ("en", "How to apply for a new business permit?"),
            ("en", "What are the requirements for a new business permit?"),
            ("en", "Process of getting a new business permit"),
            ("tl", "Paano kumuha ng bagong business permit?"),
            ("tl", "Ano ang mga kailangan para sa business permit?"),
            ("bis", "Unsaon pagkuha og bag-ong business permit?"),
            ("bis", "Unsa ang requirements sa business permit?"),
            ("bis", "Gusto ko magkuha og business permit")
        ]
    },
    "cmo_renew_business_permit": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "To **Renew your Business Permit** (done every January), follow these steps:\n\n---\n### 🏢 Renewal Process\n\n**Steps:**\n1. Submit documentary requirements (Previous Mayor's Permit, Declaration of Gross Sales, Barangay Clearance).\n2. Get assessed and secure the Order of Payment.\n3. Pay at the City Treasurer's Office and get the Official Receipt.\n4. Claim your renewed Business Permit and Clearances.\n\n💰 **Cost:** Based on gross sales declaration and local tax code.\n⏱️ **Processing Time:** Around 2-3 hours.",
            "tl": "Para i-**Renew ang inyong Business Permit** (ginagawa tuwing Enero), sundin ang mga sumusunod:\n\n---\n### 🏢 Renewal Process\n\n**Steps:**\n1. Isumite ang requirements (Nakaraang Mayor's Permit, Declaration of Gross Sales, Barangay Clearance).\n2. Magpa-assess at kunin ang Order of Payment.\n3. Magbayad sa City Treasurer's Office at kunin ang Official Receipt.\n4. Kunin ang inyong na-renew na Business Permit.\n\n💰 **Bayad:** Depende sa gross sales declaration.\n⏱️ **Processing Time:** Tinatayang 2-3 oras.",
            "bis": "Para mag-**Renew sa inyong Business Permit** (buhaton kada Enero), sunda kining mga steps:\n\n---\n### 🏢 Renewal Process\n\n**Steps:**\n1. Isumite ang requirements (Nakaagi nga Mayor's Permit, Declaration of Gross Sales, Barangay Clearance).\n2. Magpa-assess ug kuhaa ang Order of Payment.\n3. Pagbayad sa City Treasurer's Office ug kuhaa ang Official Receipt.\n4. Kuhaa ang inyong na-renew nga Business Permit.\n\n💰 **Bayad:** Depende sa gross sales declaration.\n⏱️ **Processing Time:** Mga 2-3 ka oras."
        },
        "questions": [
            ("en", "How to renew my business permit?"),
            ("en", "What are the requirements for business permit renewal?"),
            ("en", "Business permit renewal process"),
            ("tl", "Paano mag-renew ng business permit?"),
            ("tl", "Ano kailangan para i-renew ang permit?"),
            ("bis", "Unsaon pag renew sa business permit?"),
            ("bis", "Unsa ang requirements para mag renew og permit?"),
            ("bis", "Pag renew sa negosyo permit")
        ]
    },
    "cmo_retire_business_permit": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "If you are closing your business, you need to apply for **Retirement of Business Permit** to avoid accumulating penalties.\n\n---\n### 📋 Process\n\n**Steps:**\n1. Submit a letter of intent to retire the business, along with the Original Mayor's Permit, Business Plate, and BIR Clearance.\n2. BPLS will process the retirement and CTO will assess any remaining tax liabilities.\n3. Pay any outstanding fees at the City Treasurer's Office.\n4. Receive the Certificate of Business Retirement.",
            "tl": "Kung magsasara na ang iyong negosyo, kailangan mong mag-apply ng **Retirement of Business Permit** upang hindi maipon ang penalties.\n\n---\n### 📋 Proseso\n\n**Steps:**\n1. Isumite ang letter of intent para ipasara ang negosyo, kasama ang Original Mayor's Permit, Business Plate, at BIR Clearance.\n2. I-poproseso ng BPLS ang retirement at i-aassess ng CTO kung may natitirang tax liabilities.\n3. Bayaran ang mga natitirang obligasyon sa City Treasurer's Office.\n4. Kunin ang Certificate of Business Retirement.",
            "bis": "Kung manira na ang imong negosyo, kinahanglan ka mag-apply og **Retirement of Business Permit** para dili magpatong-patong ang penalties.\n\n---\n### 📋 Proseso\n\n**Steps:**\n1. Isumite ang letter of intent nga magpasira sa negosyo, uban ang Original Mayor's Permit, Business Plate, ug BIR Clearance.\n2. I-process sa BPLS ang retirement ug i-assess sa CTO kung naa pay utang nga taxes.\n3. Bayri ang mga nabilin nga obligasyon sa City Treasurer's Office.\n4. Kuhaa ang Certificate of Business Retirement."
        },
        "questions": [
            ("en", "How to close my business?"),
            ("en", "Retirement of business permit process"),
            ("en", "What to do if I stop my business?"),
            ("tl", "Paano magpasara ng negosyo?"),
            ("tl", "Retirement ng business permit paano?"),
            ("bis", "Unsaon pagpasira sa negosyo?"),
            ("bis", "Unsaon pag apply og retirement sa business?"),
            ("bis", "Manira nako sa ako negosyo")
        ]
    },
    "cmo_mtop_franchise": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "To apply for a **Motorized Tricycle Operators Permit (MTOP) / Franchise**, follow these steps:\n\n---\n### 🛺 MTOP Process\n\n**Steps:**\n1. Submit requirements to BPLS (LTO CR/OR, Driver's License, Barangay Clearance, Traffic Clearance, Tricycle Unit).\n2. Wait for validation and secure Order of Payment.\n3. Pay fees at the City Treasurer's Office.\n4. Receive your MTOP Mayor's Permit.\n\n💰 **Cost:** Mayor's Permit Fee ~₱100.00, Traffic Clearance ~₱50.00, Sticker ~₱75.00.\n⏱️ **Processing Time:** Around 4 hours.",
            "tl": "Para mag-apply ng **Motorized Tricycle Operators Permit (MTOP) o Prangkisa**, sundin ito:\n\n---\n### 🛺 Proseso ng MTOP\n\n**Steps:**\n1. Isumite ang requirements sa BPLS (LTO CR/OR, Driver's License, Barangay Clearance, Traffic Clearance, Tricycle Unit).\n2. Hintayin ang validation at kunin ang Order of Payment.\n3. Magbayad ng fees sa City Treasurer's Office.\n4. Kunin ang inyong MTOP Mayor's Permit.\n\n💰 **Bayad:** Mayor's Permit Fee ~₱100.00, Traffic Clearance ~₱50.00, Sticker ~₱75.00.\n⏱️ **Processing Time:** Tinatayang 4 oras.",
            "bis": "Para mag-apply og **Motorized Tricycle Operators Permit (MTOP) o Prangkisa**, sunda kini:\n\n---\n### 🛺 Proseso sa MTOP\n\n**Steps:**\n1. Isumite ang requirements sa BPLS (LTO CR/OR, Driver's License, Barangay Clearance, Traffic Clearance, Tricycle Unit).\n2. Hulata ang validation ug kuhaa ang Order of Payment.\n3. Pagbayad og fees sa City Treasurer's Office.\n4. Kuhaa ang imong MTOP Mayor's Permit.\n\n💰 **Bayad:** Mayor's Permit Fee ~₱100.00, Traffic Clearance ~₱50.00, Sticker ~₱75.00.\n⏱️ **Processing Time:** Mga 4 ka oras."
        },
        "questions": [
            ("en", "How to get a tricycle franchise?"),
            ("en", "Requirements for MTOP application"),
            ("en", "Motorized Tricycle Operators Permit process"),
            ("tl", "Paano kumuha ng prangkisa sa tricycle?"),
            ("tl", "Ano ang mga kailangan para sa MTOP?"),
            ("bis", "Unsaon pagkuha og prangkisa sa tricycle?"),
            ("bis", "Unsa ang requirements sa MTOP?"),
            ("bis", "Mag apply og prangkisa para sa tricycle")
        ]
    },
    "cmo_release_impounded_vehicle": {
        "department": "City Mayor's Office - TMDS",
        "answers": {
            "en": "If your vehicle was impounded, here is how you can **Release an Impounded Vehicle**:\n\n---\n### 🏍️ Releasing Process\n\n**Steps:**\n1. Submit the Citation Ticket/Impounding Receipt, Driver's License OR, and Vehicle CR/OR to TMDS.\n2. Attend the scheduled **Traffic Seminar** (usually Tuesdays/Thursdays).\n3. After the seminar, sign the logbook and claim your impounded vehicle.\n\n⏱️ **Processing Time:** Around 1 hour and 20 minutes (including seminar).",
            "tl": "Kung na-impound ang iyong sasakyan, narito kung paano ito makuha (**Releasing of Impounded Vehicle**):\n\n---\n### 🏍️ Proseso\n\n**Steps:**\n1. Isumite ang Citation Ticket/Impounding Receipt, Driver's License OR, at Vehicle CR/OR sa TMDS.\n2. Umattend sa naka-schedule na **Traffic Seminar** (kadalasan ay Martes/Huwebes).\n3. Pagkatapos ng seminar, pumirma sa logbook at kunin ang na-impound na sasakyan.\n\n⏱️ **Processing Time:** Tinatayang 1 oras at 20 minuto (kasama ang seminar).",
            "bis": "Kung na-impound ang imong sakyanan o motor, mao ni ang proseso sa pagkuha (**Releasing of Impounded Vehicle**):\n\n---\n### 🏍️ Proseso\n\n**Steps:**\n1. Isumite ang Citation Ticket/Impounding Receipt, Driver's License OR, ug Vehicle CR/OR sa TMDS.\n2. Mu-attend sa naka-schedule nga **Traffic Seminar** (kasagaran Martes o Huwebes).\n3. Human sa seminar, pirma sa logbook ug kuhaa ang na-impound nga sakyanan.\n\n⏱️ **Processing Time:** Mga 1 ka oras ug 20 minutos (apil ang seminar)."
        },
        "questions": [
            ("en", "How to claim my impounded motorcycle?"),
            ("en", "Process for releasing an impounded vehicle"),
            ("en", "I need to get my impounded car back"),
            ("tl", "Paano kukunin ang na-impound na motor?"),
            ("tl", "Ano ang proseso para makuha ang impounded na sasakyan?"),
            ("bis", "Unsaon pagkuha sa na impound nga motor?"),
            ("bis", "Asa mokuha sa na impound nga sakyanan?"),
            ("bis", "Proseso para makuha ang impounded unit")
        ]
    },
    "cmo_building_permit": {
        "department": "City Mayor's Office - Building Official",
        "answers": {
            "en": "To construct or modify a structure, you need to apply for a **Building Permit**.\n\n---\n### 🏗️ Building Permit Process\n\n**Steps:**\n1. Submit required structural plans and documents to the Office of the Building Official (OBO).\n2. Proceed to the City Treasurer's Office to pay the filing fee.\n3. Secure clearances from BFP (Fire Safety), CPDO (Locational), and other relevant offices.\n4. OBO evaluates the plans. Once approved, pay the final building permit fees.\n5. Receive the approved Building Permit.\n\n⏱️ **Processing Time:** Takes several days depending on the completeness of documents.",
            "tl": "Para magtayo o mag-modify ng istraktura, kailangan mong mag-apply ng **Building Permit**.\n\n---\n### 🏗️ Proseso ng Building Permit\n\n**Steps:**\n1. Isumite ang mga structural plans at dokumento sa Office of the Building Official (OBO).\n2. Magbayad ng filing fee sa City Treasurer's Office.\n3. Kumuha ng clearances mula sa BFP (Fire Safety), CPDO (Locational), at iba pang opisina.\n4. I-eevaluate ng OBO ang plano. Kapag naaprubahan, bayaran ang final building permit fees.\n5. Kunin ang approved na Building Permit.\n\n⏱️ **Processing Time:** Aabutin ng ilang araw depende sa pagiging kumpleto ng requirements.",
            "bis": "Para magtukod o mag-modify og building, kinahanglan nimo mag-apply og **Building Permit**.\n\n---\n### 🏗️ Proseso sa Building Permit\n\n**Steps:**\n1. Isumite ang mga structural plans ug dokumento sa Office of the Building Official (OBO).\n2. Pagbayad og filing fee sa City Treasurer's Office.\n3. Pagkuha og clearances gikan sa BFP (Fire Safety), CPDO (Locational), ug uban pang opisina.\n4. I-evaluate sa OBO ang plano. Kung ma-aprubahan, bayri ang final building permit fees.\n5. Kuhaa ang na-aprubahan nga Building Permit.\n\n⏱️ **Processing Time:** Muabot og pipila ka adlaw depende kung kumpleto ba ang requirements."
        },
        "questions": [
            ("en", "How to apply for a building permit?"),
            ("en", "What are the requirements for building a house?"),
            ("en", "Process for building permit application"),
            ("tl", "Paano kumuha ng building permit?"),
            ("tl", "Ano ang mga kailangan para sa building permit?"),
            ("bis", "Unsaon pagkuha og building permit?"),
            ("bis", "Unsa ang mga requirements sa building permit?"),
            ("bis", "Magtukod ko ug balay unsay kailangan")
        ]
    }
}

def main():
    print("Loading existing answers.json...")
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        answers_data = json.load(f)
    
    print("Loading existing intents.csv...")
    intents_df = pd.read_csv(INTENTS_FILE)
    
    # Determine the next ID for intents.csv
    next_id = intents_df['id'].max() + 1 if not intents_df.empty else 1
    new_rows = []
    
    for intent, data in NEW_DATA.items():
        if intent not in answers_data:
            print(f"Adding new intent to answers: {intent}")
            answers_data[intent] = {
                "department": data["department"],
                "answers": data["answers"]
            }
            
            # Prepare rows for intents.csv
            for lang, question in data["questions"]:
                answer_text = data["answers"].get(lang, "")
                tags = intent.replace("cmo_", "").replace("_", ", ")
                new_rows.append({
                    "id": next_id,
                    "department": data["department"],
                    "intent": intent,
                    "language": lang,
                    "question": question,
                    "answer": answer_text,
                    "source": "Citizen Charter",
                    "tags": tags
                })
                next_id += 1
        else:
            print(f"Intent {intent} already exists in answers.json. Skipping.")

    # Write back answers.json
    print("Saving updated answers.json...")
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(answers_data, f, indent=2, ensure_ascii=False)
        
    # Write back intents.csv
    if new_rows:
        print(f"Adding {len(new_rows)} new questions to intents.csv...")
        new_df = pd.DataFrame(new_rows)
        intents_df = pd.concat([intents_df, new_df], ignore_index=True)
        intents_df.to_csv(INTENTS_FILE, index=False)
    
    print("Done!")

if __name__ == "__main__":
    main()
