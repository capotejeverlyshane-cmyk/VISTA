import json
import pandas as pd
import os

ANSWERS_FILE = 'data/answers.json'
INTENTS_FILE = 'data/intents.csv'

NEW_DATA = {
    "cmo_use_of_facility": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "To request the **Use of Government Facilities** (like the City Gym or Plazas) for events:\n\n---\n### 🏢 Facility Reservation\n\n**Steps:**\n1. Submit a formal request letter to the City Mayor at least one (1) week before the event.\n2. Once approved, coordinate with the General Services Office (GSO) for logistics.\n3. Pay the corresponding rental fees (if applicable) at the City Treasurer's Office.\n4. Secure the approved permit from the Mayor's Office.\n\n💰 **Cost:** Depends on the facility and duration.\n⏱️ **Processing Time:** 1-2 days for approval.",
            "tl": "Para humiram ng **Government Facilities** (tulad ng City Gym o Plaza) para sa inyong event:\n\n---\n### 🏢 Pag-reserve ng Pasilidad\n\n**Steps:**\n1. Isumite ang request letter sa City Mayor, isang (1) linggo bago ang event.\n2. Kapag naaprubahan, makipag-ugnayan sa General Services Office (GSO) para sa logistics.\n3. Magbayad ng rental fee (kung mayroon) sa City Treasurer's Office.\n4. Kunin ang approved na permit sa opisina ng Mayor.\n\n💰 **Bayad:** Depende sa pasilidad at oras ng gamit.\n⏱️ **Processing Time:** 1-2 araw para sa pag-apruba.",
            "bis": "Para makagamit sa **Government Facilities** (parehas sa City Gym o Plaza) para sa inyong event:\n\n---\n### 🏢 Pag-reserve sa Pasilidad\n\n**Steps:**\n1. Isumite ang request letter sa City Mayor, usa (1) ka semana usa ang event.\n2. Kung ma-aprubahan na, pag-coordinate sa General Services Office (GSO).\n3. Pagbayad sa rental fee (kung naa) sa City Treasurer's Office.\n4. Kuhaa ang approved nga permit sa opisina sa Mayor.\n\n💰 **Bayad:** Depende sa pasilidad ug unsa kadugay gamiton.\n⏱️ **Processing Time:** 1-2 ka adlaw para ma-aprubahan."
        },
        "questions": [
            ("en", "How to rent the city gym?"),
            ("en", "Process for using government facilities"),
            ("en", "Can I borrow the plaza for an event?"),
            ("tl", "Paano manghiram ng gym sa city hall?"),
            ("tl", "Permit para gamitin ang plaza"),
            ("bis", "Unsaon paghulam sa city gym?"),
            ("bis", "Mag pa event mi sa plaza kinsa duolon"),
            ("bis", "Reservation of government facility")
        ]
    },
    "cmo_use_of_vehicle": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "To request the **Use of Government Vehicles** (Ambulance, Rescue, or Service Vehicles):\n\n---\n### 🚑 Vehicle Request\n\n**Steps:**\n1. Submit a letter of request specifying the date, destination, and purpose.\n2. For emergency dispatch (Ambulance/Rescue), contact the City Disaster Risk Reduction Management Office (CDRRMO) directly.\n3. For non-emergencies, wait for the Mayor's approval and Trip Ticket issuance.\n\n💰 **Cost:** Free for emergencies.\n⏱️ **Processing Time:** Immediate for emergencies; 1 day for non-emergency.",
            "tl": "Para humiling ng paggamit ng **Government Vehicles** (Ambulansya, Rescue, o Service):\n\n---\n### 🚑 Proseso ng Pag-request\n\n**Steps:**\n1. Isumite ang request letter na nagsasaad ng petsa, destinasyon, at layunin.\n2. Para sa emergencies (Ambulansya), tumawag direkta sa CDRRMO.\n3. Para sa non-emergencies, hintayin ang apruba ng Mayor at ang Trip Ticket.\n\n💰 **Bayad:** Libre para sa emergencies.\n⏱️ **Processing Time:** Agad-agad para sa emergency; 1 araw para sa iba.",
            "bis": "Para manghulam o mugamit og **Government Vehicles** (Ambulansya, Rescue, o Service):\n\n---\n### 🚑 Proseso sa Pag-request\n\n**Steps:**\n1. Isumite ang request letter nga naay petsa, adtoan, ug rason.\n2. Para sa mga emergency (Ambulansya), tawag diretso sa CDRRMO.\n3. Para sa dili emergency, hulata ang approval sa Mayor ug ang Trip Ticket.\n\n💰 **Bayad:** Libre para sa mga emergency.\n⏱️ **Processing Time:** Diretso kung emergency; 1 ka adlaw kung dili."
        },
        "questions": [
            ("en", "How to request an ambulance?"),
            ("en", "Can we borrow the city service vehicle?"),
            ("en", "Process for requesting government vehicle"),
            ("tl", "Paano humiram ng sasakyan ng munisipyo?"),
            ("tl", "Request ng ambulansya paano?"),
            ("bis", "Unsaon paghulam sa service sa munisipyo?"),
            ("bis", "Gusto mi mu request og ambulansya"),
            ("bis", "Borrow government vehicle for event")
        ]
    },
    "cmo_firecracker_permit": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "To sell firecrackers and pyrotechnics during the holidays, you must secure a **Special Permit to Sell Firecrackers**.\n\n---\n### 🎆 Firecracker Permit Process\n\n**Steps:**\n1. Secure clearance from the Philippine National Police (PNP) and Bureau of Fire Protection (BFP).\n2. Submit clearances and application to the BPLS.\n3. Pay the required fees at the City Treasurer's Office.\n4. Claim your permit and set up only at the designated Firecracker Zone.\n\n💰 **Cost:** Varies per space/stall.\n⏱️ **Processing Time:** 1 to 2 days.",
            "tl": "Upang magbenta ng paputok tuwing holidays, kailangang kumuha ng **Special Permit to Sell Firecrackers**.\n\n---\n### 🎆 Proseso ng Permit\n\n**Steps:**\n1. Kumuha ng clearance mula sa PNP at BFP.\n2. Isumite ang clearances at application sa BPLS.\n3. Magbayad ng fee sa City Treasurer's Office.\n4. Kunin ang permit at magtayo lamang ng pwesto sa designated Firecracker Zone.\n\n💰 **Bayad:** Nakadepende sa pwesto.\n⏱️ **Processing Time:** 1 hanggang 2 araw.",
            "bis": "Para makabaligya og pabuto inig holidays, kinahanglan mokuha og **Special Permit to Sell Firecrackers**.\n\n---\n### 🎆 Proseso sa Permit\n\n**Steps:**\n1. Pagkuha daan og clearance gikan sa PNP ug BFP.\n2. Isumite ang clearances ug application didto sa BPLS.\n3. Pagbayad sa fee sa City Treasurer's Office.\n4. Kuhaa ang permit ug pagpwesto lang sa gi-assign nga Firecracker Zone.\n\n💰 **Bayad:** Magdepende sa pwesto.\n⏱️ **Processing Time:** 1 hantod 2 ka adlaw."
        },
        "questions": [
            ("en", "How to get a permit to sell firecrackers?"),
            ("en", "Permit for selling fireworks"),
            ("en", "Where to apply for firecracker stall?"),
            ("tl", "Paano kumuha ng permit para magbenta ng paputok?"),
            ("tl", "Permit para sa tindahan ng paputok"),
            ("bis", "Unsaon pagkuha og permit para mamaligya og pabuto?"),
            ("bis", "Asa maka apply og pwesto sa pabuto?"),
            ("bis", "Requirements sa pagbaligya og firecrackers")
        ]
    },
    "cmo_market_stall": {
        "department": "City Economic Enterprise",
        "answers": {
            "en": "To rent a space or stall at the public market, you need to apply for a **Market Stall Lease**.\n\n---\n### 🏪 Market Stall Application\n\n**Steps:**\n1. Inquire at the City Economic Enterprise Management and Development Office (CEEMDO) for vacant stalls.\n2. Submit a letter of intent to the Mayor.\n3. Once approved, secure a Market Clearance.\n4. Pay the initial deposit and rental fees at the City Treasurer's Office.\n5. Sign the Lease Contract and proceed with the Business Permit application.\n\n💰 **Cost:** Depends on the stall location and size.\n⏱️ **Processing Time:** Varies based on availability.",
            "tl": "Para umupa ng pwesto sa palengke, kailangan mong mag-apply ng **Market Stall Lease**.\n\n---\n### 🏪 Proseso\n\n**Steps:**\n1. Magtanong sa CEEMDO kung may bakanteng pwesto.\n2. Isumite ang letter of intent sa Mayor.\n3. Kapag naaprubahan, kumuha ng Market Clearance.\n4. Magbayad ng deposit at upa sa City Treasurer's Office.\n5. Pumirma sa Lease Contract at mag-apply na ng Business Permit.\n\n💰 **Bayad:** Depende sa laki at lokasyon ng pwesto.\n⏱️ **Processing Time:** Depende sa availability ng pwesto.",
            "bis": "Para maka-arkila og pwesto sa palengke, kinahanglan mag-apply og **Market Stall Lease**.\n\n---\n### 🏪 Proseso\n\n**Steps:**\n1. Pag-inquire sa CEEMDO kung naay bakante nga pwesto.\n2. Isumite ang letter of intent ngadto sa Mayor.\n3. Kung ma-aprubahan na, pagkuha og Market Clearance.\n4. Pagbayad sa deposit ug abang didto sa City Treasurer's Office.\n5. Pirma sa Lease Contract ug pag-apply na og Business Permit.\n\n💰 **Bayad:** Magdepende sa kadako ug lokasyon sa pwesto.\n⏱️ **Processing Time:** Magdepende kung naay bakante."
        },
        "questions": [
            ("en", "How to rent a market stall?"),
            ("en", "Application for public market space"),
            ("en", "Process for leasing a stall in the public market"),
            ("tl", "Paano umupa ng pwesto sa palengke?"),
            ("tl", "Requirements para kumuha ng pwesto sa palengke"),
            ("bis", "Unsaon pag arkila og pwesto sa palengke?"),
            ("bis", "Asa maka apply og pwesto sa public market?"),
            ("bis", "Gusto nako mamaligya sa palengke")
        ]
    },
    "cmo_cert_of_appearance": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "Official guests, auditors, or government employees visiting the city can secure a **Certificate of Appearance**.\n\n---\n### 📜 Certificate of Appearance\n\n**Steps:**\n1. Present your Travel Order or official ID to the CMO Receiving Clerk or HRMO.\n2. Log in to the visitor's logbook.\n3. Wait for the drafting and signing of the certificate by the authorized official.\n4. Claim the signed Certificate of Appearance.\n\n💰 **Cost:** Free.\n⏱️ **Processing Time:** 5 to 10 minutes.",
            "tl": "Ang mga opisyal na bisita o empleyado ng gobyerno na bumisita sa lungsod ay maaaring kumuha ng **Certificate of Appearance**.\n\n---\n### 📜 Proseso\n\n**Steps:**\n1. Ipakita ang Travel Order o official ID sa CMO Receiving Clerk o HRMO.\n2. Pumirma sa visitor's logbook.\n3. Hintayin ang paggawa at pagpirma ng authorized official sa certificate.\n4. Kunin ang pirmadong Certificate of Appearance.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** 5 hanggang 10 minuto.",
            "bis": "Ang mga opisyal nga bisita o empleyado sa gobyerno nga nibisita sa syudad pwede mokuha og **Certificate of Appearance**.\n\n---\n### 📜 Proseso\n\n**Steps:**\n1. Ipakita ang inyong Travel Order o official ID sa CMO Receiving Clerk o HRMO.\n2. Pirma sa visitor's logbook.\n3. Hulata nga himuon ug pirmahan sa authorized official ang certificate.\n4. Kuhaa ang pinirmahan nga Certificate of Appearance.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** 5 hantod 10 minutos."
        },
        "questions": [
            ("en", "How to get a certificate of appearance?"),
            ("en", "Where to sign for certificate of appearance?"),
            ("en", "I need a cert of appearance for my travel order"),
            ("tl", "Paano kumuha ng certificate of appearance?"),
            ("tl", "Saan pwede magpa-certificate of appearance?"),
            ("bis", "Unsaon pagkuha og certificate of appearance?"),
            ("bis", "Asa pwede maka pirma para cert of appearance?"),
            ("bis", "Certificate of appearance para sa travel")
        ]
    },
    "cmo_tree_cutting": {
        "department": "City Mayor's Office - CENRO",
        "answers": {
            "en": "To cut down trees, especially those posing hazards or for construction, you need a **Mayor's Endorsement for Tree Cutting**.\n\n---\n### 🌳 Tree Cutting Permit\n\n**Steps:**\n1. Secure a Barangay Clearance / No Objection Certificate for tree cutting.\n2. Submit a request letter to the City Environment and Natural Resources Office (CENRO) with pictures of the tree.\n3. CENRO will inspect the tree and endorse the request to the Mayor and DENR.\n4. Secure the final Tree Cutting Permit from the DENR.\n\n💰 **Cost:** Inspection is usually free; DENR fees may apply.\n⏱️ **Processing Time:** 3 to 5 days (includes inspection).",
            "tl": "Para magputol ng puno, lalo na kung ito ay delikado o para sa konstruksyon, kailangan ng **Mayor's Endorsement for Tree Cutting**.\n\n---\n### 🌳 Proseso ng Permit\n\n**Steps:**\n1. Kumuha ng Barangay Clearance / No Objection Certificate.\n2. Isumite ang request letter sa CENRO kasama ang litrato ng puno.\n3. I-inspeksyon ng CENRO ang puno at i-eendorso sa Mayor at DENR.\n4. Kunin ang pinal na Tree Cutting Permit sa DENR.\n\n💰 **Bayad:** Kadalasan libre ang inspection; maaaring may bayad sa DENR.\n⏱️ **Processing Time:** 3 hanggang 5 araw (kasama ang inspeksyon).",
            "bis": "Para mamutol og kahoy, labi na kung delikado o tungod sa construction, kinahanglan og **Mayor's Endorsement for Tree Cutting**.\n\n---\n### 🌳 Proseso sa Permit\n\n**Steps:**\n1. Pagkuha og Barangay Clearance / No Objection Certificate.\n2. Isumite ang request letter sa CENRO uban ang litrato sa kahoy.\n3. I-inspeksyon sa CENRO ang kahoy ug i-endorse sa Mayor ug DENR.\n4. Kuhaa ang final nga Tree Cutting Permit sa DENR.\n\n💰 **Bayad:** Kasagaran libre ang inspection; naa poy bayad sa DENR.\n⏱️ **Processing Time:** 3 ngadto sa 5 ka adlaw (apil ang inspection)."
        },
        "questions": [
            ("en", "How to get a permit to cut a tree?"),
            ("en", "Process for tree cutting permit"),
            ("en", "The tree is dangerous, how to request cutting?"),
            ("tl", "Paano kumuha ng permit magputol ng puno?"),
            ("tl", "Permit para pumutol ng kahoy"),
            ("bis", "Unsaon pagkuha og permit para mamutol og kahoy?"),
            ("bis", "Delikado na ang kahoy unsaon pag pa putol?"),
            ("bis", "Tree cutting permit process")
        ]
    },
    "cmo_excavation_permit": {
        "department": "City Mayor's Office - Engineering",
        "answers": {
            "en": "For road diggings or installation of pipes/cables, an **Excavation Permit** must be secured.\n\n---\n### 🚧 Excavation Permit\n\n**Steps:**\n1. Submit your project plans and a request letter to the City Engineering Office (CEO).\n2. Secure clearances from traffic management and the affected barangay.\n3. Pay the excavation fees and deposit/bond at the City Treasurer's Office.\n4. Present the receipt and receive the approved Excavation Permit.\n\n💰 **Cost:** Depends on the area/length of excavation.\n⏱️ **Processing Time:** 2 to 3 days.",
            "tl": "Para sa paghuhukay sa kalsada (pagkabit ng tubo/kable), kailangan ng **Excavation Permit**.\n\n---\n### 🚧 Proseso ng Permit\n\n**Steps:**\n1. Isumite ang plano ng proyekto at request letter sa City Engineering Office (CEO).\n2. Kumuha ng clearances mula sa traffic management at barangay.\n3. Magbayad ng excavation fee at bond sa City Treasurer's Office.\n4. Ipakita ang resibo para makuha ang Excavation Permit.\n\n💰 **Bayad:** Depende sa haba/laki ng huhukayin.\n⏱️ **Processing Time:** 2 hanggang 3 araw.",
            "bis": "Para sa pagpangubkob sa kalsada (pagtaod og tubo o kable), kinahanglan og **Excavation Permit**.\n\n---\n### 🚧 Proseso sa Permit\n\n**Steps:**\n1. Isumite ang plano sa proyekto ug request letter sa City Engineering Office (CEO).\n2. Pagkuha og clearance gikan sa traffic management ug barangay.\n3. Pagbayad sa excavation fee ug bond sa City Treasurer's Office.\n4. Ipakita ang resibo aron makuha ang Excavation Permit.\n\n💰 **Bayad:** Magdepende sa gidak-on sa kubkubon.\n⏱️ **Processing Time:** 2 hantod 3 ka adlaw."
        },
        "questions": [
            ("en", "How to get an excavation permit?"),
            ("en", "Permit for digging the road"),
            ("en", "We need to install pipes, what permit do we need?"),
            ("tl", "Paano kumuha ng excavation permit?"),
            ("tl", "Permit para maghukay sa kalsada"),
            ("bis", "Unsaon pagkuha og excavation permit?"),
            ("bis", "Permit para makakubkob sa kalsada"),
            ("bis", "Magtaod mi og tubo sa dalan unsay permit")
        ]
    },
    "cmo_pesos_job_fair": {
        "department": "City Mayor's Office - PESO",
        "answers": {
            "en": "To participate in or inquire about a **Job Fair**, the Public Employment Service Office (PESO) is the main contact.\n\n---\n### 👔 Job Fair Participation\n\n**Steps:**\n1. Visit the PESO office or check the official City Government Facebook page for upcoming Job Fair announcements.\n2. Prepare multiple copies of your Resume/Bio-data with recent 2x2 ID pictures.\n3. Pre-register online or walk-in during the Job Fair day at the venue (usually the City Gym).\n4. Proceed to the interview booths of your target companies.\n\n💰 **Cost:** Completely Free.\n⏱️ **Processing Time:** Same day interview.",
            "tl": "Para sumali o mag-inquire tungkol sa **Job Fair**, ang PESO ang inyong lalapitan.\n\n---\n### 👔 Pagsali sa Job Fair\n\n**Steps:**\n1. Pumunta sa PESO o tignan ang official Facebook page ng City Government para sa mga anunsyo ng Job Fair.\n2. Maghanda ng maraming kopya ng Resume/Bio-data at 2x2 pictures.\n3. Mag-register online o mag-walk-in sa mismong araw ng Job Fair.\n4. Pumunta sa mga interview booth ng mga kumpanya.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** Interview sa mismong araw.",
            "bis": "Para moapil o mag-inquire bahin sa **Job Fair**, ang PESO ang inyong adtoan.\n\n---\n### 👔 Pag-apil sa Job Fair\n\n**Steps:**\n1. Adto sa PESO o i-check ang official Facebook page sa City Government para sa announcements sa Job Fair.\n2. Pag-andam og daghang kopya sa imong Resume/Bio-data ug 2x2 pictures.\n3. Pag-register daan online o walk-in inig adlaw mismo sa Job Fair.\n4. Adto sa interview booth sa mga kumpanya nga imong apply-an.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** Interview sa maong adlaw."
        },
        "questions": [
            ("en", "When is the next job fair?"),
            ("en", "How to join the city job fair?"),
            ("en", "Requirements for job fair application"),
            ("tl", "Kailan ang susunod na job fair?"),
            ("tl", "Paano sumali sa job fair ng munisipyo?"),
            ("bis", "Kanus a ang sunod nga job fair?"),
            ("bis", "Unsaon pag apil sa job fair sa city hall?"),
            ("bis", "Gusto ko mangapply sa job fair")
        ]
    }
}

def main():
    print("Loading existing answers.json...")
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            answers_data = json.load(f)
    else:
        answers_data = {}
    
    print("Loading existing intents.csv...")
    if os.path.exists(INTENTS_FILE):
        intents_df = pd.read_csv(INTENTS_FILE)
    else:
        intents_df = pd.DataFrame(columns=["id", "department", "intent", "language", "question", "answer", "source", "tags"])
    
    next_id = intents_df['id'].max() + 1 if not intents_df.empty else 1
    new_rows = []
    
    for intent, data in NEW_DATA.items():
        if intent not in answers_data:
            print(f"Adding new intent to answers: {intent}")
            answers_data[intent] = {
                "department": data["department"],
                "answers": data["answers"]
            }
            
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
                    "source": "Citizen Charter (Part 3)",
                    "tags": tags
                })
                next_id += 1
        else:
            print(f"Intent {intent} already exists in answers.json. Skipping.")

    print("Saving updated answers.json...")
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(answers_data, f, indent=2, ensure_ascii=False)
        
    if new_rows:
        print(f"Adding {len(new_rows)} new questions to intents.csv...")
        new_df = pd.DataFrame(new_rows)
        intents_df = pd.concat([intents_df, new_df], ignore_index=True)
        intents_df.to_csv(INTENTS_FILE, index=False)
    
    print("CMO Part 3 Population Complete!")

if __name__ == "__main__":
    main()
