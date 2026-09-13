import json
import pandas as pd
import os

ANSWERS_FILE = 'data/answers.json'
INTENTS_FILE = 'data/intents.csv'

NEW_DATA = {
    "cmo_mayors_clearance": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "To secure a **Mayor's Clearance** (for employment, firearm license, etc.), follow these steps:\n\n---\n### 📄 Mayor's Clearance Process\n\n**Steps:**\n1. Present your requirements (Barangay Clearance, Police Clearance) at the CMO Receiving Section.\n2. Get the Order of Payment and pay at the City Treasurer's Office.\n3. Return to the CMO with the Official Receipt to claim your Mayor's Clearance.\n\n💰 **Cost:** ~₱50.00 to ₱100.00 (varies by purpose).\n⏱️ **Processing Time:** Around 15-30 minutes.",
            "tl": "Para kumuha ng **Mayor's Clearance** (para sa trabaho, lisensya ng baril, atbp.), sundin ito:\n\n---\n### 📄 Proseso\n\n**Steps:**\n1. Ipakita ang requirements (Barangay Clearance, Police Clearance) sa CMO Receiving Section.\n2. Kunin ang Order of Payment at magbayad sa City Treasurer's Office.\n3. Bumalik sa CMO dala ang Official Receipt para makuha ang Mayor's Clearance.\n\n💰 **Bayad:** ~₱50.00 hanggang ₱100.00 (depende sa layunin).\n⏱️ **Processing Time:** Tinatayang 15-30 minuto.",
            "bis": "Para mokuha og **Mayor's Clearance** (para sa trabaho, lisensya sa pusil, ug uban pa), sunda kini:\n\n---\n### 📄 Proseso\n\n**Steps:**\n1. Ipakita ang imong requirements (Barangay Clearance, Police Clearance) sa CMO Receiving Section.\n2. Kuhaa ang Order of Payment ug pagbayad sa City Treasurer's Office.\n3. Balik sa CMO dala ang Official Receipt aron makuha ang Mayor's Clearance.\n\n💰 **Bayad:** ~₱50.00 hantod ₱100.00 (depende sa gamit).\n⏱️ **Processing Time:** Mga 15-30 minutos."
        },
        "questions": [
            ("en", "How to get a Mayor's clearance?"),
            ("en", "Requirements for mayor clearance"),
            ("en", "Where do I get a clearance from the Mayor?"),
            ("tl", "Paano kumuha ng Mayor's clearance?"),
            ("tl", "Ano kailangan sa mayor's clearance?"),
            ("bis", "Unsaon pagkuha og mayor's clearance?"),
            ("bis", "Unsa ang requirements sa mayor's clearance?"),
            ("bis", "Kailangan nako mayor clearance para sa trabaho")
        ]
    },
    "cmo_occupational_permit": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "All employees working in the city must secure an **Occupational Permit** or Mayor's Working Permit.\n\n---\n### 👨‍💼 Occupational Permit Process\n\n**Steps:**\n1. Submit requirements (Health Certificate from CHO, Police Clearance, and receipt of Police Clearance).\n2. Present documents to the BPLS for assessment.\n3. Pay the Occupational Permit fee at the City Treasurer's Office.\n4. Present the Official Receipt and claim the printed ID/Permit.\n\n💰 **Cost:** ~₱150.00 (varies by position).\n⏱️ **Processing Time:** Around 20-30 minutes.",
            "tl": "Lahat ng empleyado sa lungsod ay kailangang kumuha ng **Occupational Permit** o Mayor's Working Permit.\n\n---\n### 👨‍💼 Proseso\n\n**Steps:**\n1. Isumite ang requirements (Health Certificate mula CHO, Police Clearance).\n2. Ipakita ang mga dokumento sa BPLS para sa assessment.\n3. Magbayad ng fee sa City Treasurer's Office.\n4. Ipakita ang Official Receipt at kunin ang Occupational Permit.\n\n💰 **Bayad:** ~₱150.00 (depende sa posisyon).\n⏱️ **Processing Time:** Tinatayang 20-30 minuto.",
            "bis": "Tanan empleyado sa syudad kinahanglan mokuha og **Occupational Permit** o Mayor's Working Permit.\n\n---\n### 👨‍💼 Proseso\n\n**Steps:**\n1. Isumite ang requirements (Health Certificate gikan sa CHO, Police Clearance).\n2. Ipakita ang mga dokumento sa BPLS para ma-assess.\n3. Bayri ang permit fee sa City Treasurer's Office.\n4. Ipakita ang Official Receipt ug kuhaa ang Occupational Permit.\n\n💰 **Bayad:** ~₱150.00 (depende sa posisyon).\n⏱️ **Processing Time:** Mga 20-30 minutos."
        },
        "questions": [
            ("en", "How to apply for an occupational permit?"),
            ("en", "What are the requirements for Mayor's working permit?"),
            ("en", "Process of getting occupational permit"),
            ("tl", "Paano kumuha ng occupational permit?"),
            ("tl", "Working permit requirements"),
            ("bis", "Unsaon pagkuha og occupational permit?"),
            ("bis", "Unsay requirements sa working permit sa mayor?"),
            ("bis", "Mokuha ko og permit kay manarbaho ko")
        ]
    },
    "cmo_mtop_transfer": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "If you bought or sold a tricycle, you need to apply for an **MTOP Transfer of Ownership**.\n\n---\n### 🔄 Transfer Process\n\n**Steps:**\n1. Submit the Deed of Sale, Original MTOP Franchise, LTO CR/OR, and Barangay Clearance to BPLS.\n2. Secure the Order of Payment.\n3. Pay the Transfer Fee and other dues at the City Treasurer's Office.\n4. Present the receipt and claim the updated MTOP under the new owner's name.\n\n💰 **Cost:** Transfer Fee is around ~₱200.00.\n⏱️ **Processing Time:** Around 2-3 hours.",
            "tl": "Kung ikaw ay bumili o nagbenta ng tricycle, kailangan mong mag-apply para sa **MTOP Transfer of Ownership**.\n\n---\n### 🔄 Proseso ng Transfer\n\n**Steps:**\n1. Isumite ang Deed of Sale, Original MTOP, LTO CR/OR, at Barangay Clearance sa BPLS.\n2. Kunin ang Order of Payment.\n3. Bayaran ang Transfer Fee sa City Treasurer's Office.\n4. Kunin ang bagong MTOP franchise na nakapangalan na sa bagong may-ari.\n\n💰 **Bayad:** Ang Transfer Fee ay nasa ~₱200.00.\n⏱️ **Processing Time:** Tinatayang 2-3 oras.",
            "bis": "Kung nipalit o nagbaligya ka og tricycle, kinahanglan ka mag-apply para sa **MTOP Transfer of Ownership**.\n\n---\n### 🔄 Proseso sa Transfer\n\n**Steps:**\n1. Isumite ang Deed of Sale, Original MTOP, LTO CR/OR, ug Barangay Clearance sa BPLS.\n2. Kuhaa ang Order of Payment.\n3. Bayri ang Transfer Fee sa City Treasurer's Office.\n4. Kuhaa ang bag-ong MTOP franchise nga nakapangalan na sa bag-ong tag-iya.\n\n💰 **Bayad:** Ang Transfer Fee kay mga ~₱200.00.\n⏱️ **Processing Time:** Mga 2-3 ka oras."
        },
        "questions": [
            ("en", "How to transfer tricycle franchise ownership?"),
            ("en", "MTOP transfer of ownership process"),
            ("en", "I bought a tricycle, how to transfer MTOP?"),
            ("tl", "Paano ilipat ang pangalan ng prangkisa ng tricycle?"),
            ("tl", "Requirements para sa transfer ng MTOP"),
            ("bis", "Unsaon pag transfer sa pangalan sa prangkisa?"),
            ("bis", "Nipalit ko og tricycle unsaon pagbalhin sa mtop?"),
            ("bis", "Transfer of ownership sa tricycle")
        ]
    },
    "cmo_driver_id": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Tricycle and Trisikad drivers must secure a **Driver's Identification Card** from the CMO.\n\n---\n### 🪪 Driver's ID Process\n\n**Steps:**\n1. Present your Professional Driver's License, Police Clearance, and MTOP Franchise to the BPLS.\n2. Get assessed and secure an Order of Payment.\n3. Pay the ID fee at the City Treasurer's Office.\n4. Proceed to ID picture capturing and claim your printed ID.\n\n💰 **Cost:** ~₱50.00 - ₱100.00.\n⏱️ **Processing Time:** Around 30-45 minutes.",
            "tl": "Ang mga driver ng tricycle at trisikad ay kailangang kumuha ng **Driver's Identification Card** mula sa CMO.\n\n---\n### 🪪 Proseso ng Driver's ID\n\n**Steps:**\n1. Ipakita ang Professional Driver's License, Police Clearance, at MTOP Franchise sa BPLS.\n2. Kumuha ng Order of Payment.\n3. Magbayad ng ID fee sa City Treasurer's Office.\n4. Magpa-picture at kunin ang printed na ID.\n\n💰 **Bayad:** ~₱50.00 - ₱100.00.\n⏱️ **Processing Time:** Tinatayang 30-45 minuto.",
            "bis": "Ang mga drayber sa tricycle ug trisikad kinahanglan mokuha og **Driver's Identification Card** gikan sa CMO.\n\n---\n### 🪪 Proseso sa Driver's ID\n\n**Steps:**\n1. Ipakita ang Professional Driver's License, Police Clearance, ug MTOP Franchise sa BPLS.\n2. Kuhaa ang Order of Payment.\n3. Pagbayad sa ID fee sa City Treasurer's Office.\n4. Pagpa-picture ug kuhaa ang imong printed nga ID.\n\n💰 **Bayad:** ~₱50.00 - ₱100.00.\n⏱️ **Processing Time:** Mga 30-45 minutos."
        },
        "questions": [
            ("en", "How to get a tricycle driver's ID?"),
            ("en", "Requirements for MTOP driver ID"),
            ("en", "I need a driver's ID for my tricycle"),
            ("tl", "Paano kumuha ng ID ng driver ng tricycle?"),
            ("tl", "Ano kailangan para sa driver's ID?"),
            ("bis", "Unsaon pagkuha og ID sa drayber sa tricycle?"),
            ("bis", "Asa makakuha og driver's id para sa trisikad?"),
            ("bis", "Requirements sa tricycle driver ID")
        ]
    },
    "cmo_special_permit": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "For events, motorcades, recuridas, or promotional activities, you need a **Mayor's Special Permit**.\n\n---\n### 🎉 Special Permit Process\n\n**Steps:**\n1. Submit a formal Request Letter addressed to the City Mayor, indicating the details of the event/activity.\n2. Once approved and signed by the Mayor or City Administrator, proceed to the BPLS for assessment.\n3. Pay the Special Permit fee at the City Treasurer's Office.\n4. Claim the printed Special Permit.\n\n💰 **Cost:** Depends on the nature of the activity.\n⏱️ **Processing Time:** 1 to 2 working days (depending on approval).",
            "tl": "Para sa mga events, motorcade, recurida, o promotional activities, kailangan mo ng **Mayor's Special Permit**.\n\n---\n### 🎉 Proseso\n\n**Steps:**\n1. Isumite ang pormal na Request Letter sa City Mayor na naglalaman ng detalye ng aktibidad.\n2. Kapag naaprubahan, pumunta sa BPLS para sa assessment.\n3. Magbayad ng Special Permit fee sa City Treasurer's Office.\n4. Kunin ang inyong Special Permit.\n\n💰 **Bayad:** Depende sa klase ng aktibidad.\n⏱️ **Processing Time:** 1 hanggang 2 araw (depende sa pag-apruba).",
            "bis": "Para sa mga events, motorcade, recurida, o promotional activities, kinahanglan nimo og **Mayor's Special Permit**.\n\n---\n### 🎉 Proseso\n\n**Steps:**\n1. Pagpasa og Request Letter para sa City Mayor nga naay detalye sa inyong aktibidad.\n2. Kung ma-aprubahan na, adto sa BPLS para ma-assess.\n3. Pagbayad sa Special Permit fee didto sa City Treasurer's Office.\n4. Kuhaa ang inyong Special Permit.\n\n💰 **Bayad:** Magdepende sa klase sa aktibidad.\n⏱️ **Processing Time:** 1 ngadto sa 2 ka adlaw (depende sa approval)."
        },
        "questions": [
            ("en", "How to get a permit for a motorcade?"),
            ("en", "Special permit for events"),
            ("en", "How to apply for Mayor's special permit?"),
            ("tl", "Paano kumuha ng permit para sa event?"),
            ("tl", "Permit para sa motorcade o recurida"),
            ("bis", "Unsaon pagkuha og permit para mag motorcade?"),
            ("bis", "Permit para mag pa event"),
            ("bis", "Unsay requirements sa special permit?")
        ]
    },
    "cmo_marriage_solemnization": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "Couples can request the City Mayor to officiate their wedding through **Marriage Solemnization**.\n\n---\n### 💍 Solemnization Process\n\n**Steps:**\n1. Secure a Marriage License from the Local Civil Registrar (LCR).\n2. Submit the Marriage License and request letter to the CMO at least two (2) weeks before the desired date.\n3. Pay the Solemnization Fee at the City Treasurer's Office.\n4. Attend the scheduled wedding at the Mayor's Office.\n\n💰 **Cost:** Solemnization Fee ~₱300.00.\n⏱️ **Processing Time:** Scheduling takes 10-15 mins; subject to the Mayor's availability.",
            "tl": "Maaaring hilingin sa City Mayor na magkasal sa inyo sa pamamagitan ng **Marriage Solemnization**.\n\n---\n### 💍 Proseso ng Kasal sa Mayor\n\n**Steps:**\n1. Kumuha ng Marriage License sa Local Civil Registrar (LCR).\n2. Isumite ang Marriage License at request letter sa CMO, dalawang (2) linggo bago ang kasal.\n3. Magbayad ng Solemnization Fee sa City Treasurer's Office.\n4. Pumunta sa araw ng kasal sa opisina ng Mayor.\n\n💰 **Bayad:** Solemnization Fee ~₱300.00.\n⏱️ **Processing Time:** 10-15 mins para sa scheduling; depende sa schedule ng Mayor.",
            "bis": "Pwede mo magpakasal sa City Mayor pinaagi sa **Marriage Solemnization**.\n\n---\n### 💍 Proseso sa Pagpakasal\n\n**Steps:**\n1. Pagkuha daan og Marriage License sa Local Civil Registrar (LCR).\n2. Isumite ang Marriage License ug request letter sa CMO, duha (2) ka semana sa dili pa ang petsa.\n3. Pagbayad sa Solemnization Fee sa City Treasurer's Office.\n4. Tunga sa naka-schedule nga adlaw sa kasal sa opisina sa Mayor.\n\n💰 **Bayad:** Solemnization Fee ~₱300.00.\n⏱️ **Processing Time:** 10-15 mins ang pag-schedule; depende kung libre ang Mayor."
        },
        "questions": [
            ("en", "How to get married by the Mayor?"),
            ("en", "Process for civil wedding at the Mayor's office"),
            ("en", "Requirements for marriage solemnization"),
            ("tl", "Paano magpakasal sa Mayor?"),
            ("tl", "Ano kailangan sa civil wedding sa city hall?"),
            ("bis", "Unsaon pagpakasal sa Mayor?"),
            ("bis", "Gusto mi magpa civil wedding unsay requirements?"),
            ("bis", "Kasal sa mayor proseso")
        ]
    },
    "cmo_job_recommendation": {
        "department": "City Mayor's Office - PESO",
        "answers": {
            "en": "Job seekers can request an **Endorsement / Recommendation Letter** for local or overseas employment from the CMO/PESO.\n\n---\n### 💼 Recommendation Process\n\n**Steps:**\n1. Prepare your Resume/Bio-data and a cover letter indicating the company you are applying to.\n2. Submit the documents to the Public Employment Service Office (PESO) or the Mayor's Office receiving clerk.\n3. The office will prepare the endorsement letter signed by the Mayor.\n4. Claim the sealed recommendation letter.\n\n💰 **Cost:** Free of charge.\n⏱️ **Processing Time:** Around 15 to 30 minutes.",
            "tl": "Maaaring humingi ng **Recommendation / Endorsement Letter** para sa trabaho mula sa CMO o PESO.\n\n---\n### 💼 Proseso\n\n**Steps:**\n1. Ihanda ang Resume/Bio-data at cover letter kung saan nais mag-apply.\n2. Isumite ito sa Public Employment Service Office (PESO) o sa CMO.\n3. Ipoproseso ng opisina ang endorsement letter na pirmado ng Mayor.\n4. Kunin ang rekomendasyon na nakaselyo.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** Tinatayang 15 hanggang 30 minuto.",
            "bis": "Ang mga nangita og trabaho pwede mangayo og **Recommendation / Endorsement Letter** gikan sa CMO o PESO.\n\n---\n### 💼 Proseso\n\n**Steps:**\n1. Iandam ang imong Resume/Bio-data ug cover letter para sa kumpanya nga imong aplayan.\n2. Isumite ni sa Public Employment Service Office (PESO) o sa CMO.\n3. Buhaton sa opisina ang endorsement letter nga pinirmahan sa Mayor.\n4. Kuhaa ang imong recommendation letter.\n\n💰 **Bayad:** Libre / Walay bayad.\n⏱️ **Processing Time:** Mga 15 hantod 30 minutos."
        },
        "questions": [
            ("en", "How to get a job recommendation from the Mayor?"),
            ("en", "Mayor's endorsement for employment"),
            ("en", "Can I ask for a recommendation letter for work?"),
            ("tl", "Paano makakuha ng recommendation letter sa Mayor para sa trabaho?"),
            ("tl", "Endorsement sa trabaho galing sa mayor"),
            ("bis", "Unsaon pagkuha og recommendation sa Mayor para sa trabaho?"),
            ("bis", "Mangayo ko endorsement para sa applayan nako"),
            ("bis", "Recommendation letter proseso")
        ]
    },
    "cmo_financial_assistance": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "Citizens in crisis can apply for **Medical or Financial Assistance (AICS)** from the City Mayor's Office.\n\n---\n### ❤️ Assistance Process\n\n**Steps:**\n1. Prepare the requirements (e.g., Medical Abstract, Hospital Bill, Barangay Certificate of Indigency, Valid ID).\n2. Submit documents to the CMO Assistance Desk or City Social Welfare and Development Office (CSWDO) for evaluation.\n3. Wait for the social worker's interview and assessment.\n4. Once approved, the releasing of funds or Guarantee Letter will be scheduled.\n\n💰 **Cost:** Free.\n⏱️ **Processing Time:** Evaluation takes 1-2 hours; release of funds varies.",
            "tl": "Ang mga nangangailangan ay maaaring humingi ng **Medical o Financial Assistance** mula sa opisina ng Mayor.\n\n---\n### ❤️ Proseso ng Tulong Pinansyal\n\n**Steps:**\n1. Ihanda ang requirements (Medical Abstract, Reseta, Hospital Bill, Barangay Certificate of Indigency, Valid ID).\n2. Isumite ito sa CMO Assistance Desk o CSWDO para sa evaluation.\n3. Hintayin ang interview ng social worker.\n4. Kapag naaprubahan, bibigyan ka ng Guarantee Letter o i-schedule ang pag-release ng pera.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** Evaluation ay 1-2 oras; ang pag-release ay nakadepende.",
            "bis": "Ang mga nanginahanglan pwede mangayo og **Medical o Financial Assistance** gikan sa opisina sa Mayor.\n\n---\n### ❤️ Proseso sa Pagkuha og Tabang\n\n**Steps:**\n1. Iandam ang requirements (Medical Abstract, Reseta, Hospital Bill, Barangay Certificate of Indigency, Valid ID).\n2. Isumite ni sa CMO Assistance Desk o CSWDO aron ma-evaluate.\n3. Hulata ang interview sa social worker.\n4. Kung ma-aprubahan, hatagan ka og Guarantee Letter o i-schedule ang paghatag sa kwarta.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** 1-2 ka oras ang evaluation; ang pag-release kay magdepende."
        },
        "questions": [
            ("en", "How to ask for medical assistance from the Mayor?"),
            ("en", "Financial assistance requirements"),
            ("en", "Process for hospital bill assistance"),
            ("tl", "Paano humingi ng tulong pinansyal sa Mayor?"),
            ("tl", "Requirements para sa medical assistance"),
            ("bis", "Unsaon pagpangayo og tabang pinansyal sa Mayor?"),
            ("bis", "Unsay requirements sa medical assistance?"),
            ("bis", "Tabang para sa bayranan sa ospital")
        ]
    },
    "cmo_scholarship": {
        "department": "City Mayor's Office",
        "answers": {
            "en": "Students can apply for the **City Educational Scholarship Program**.\n\n---\n### 🎓 Scholarship Process\n\n**Steps:**\n1. Secure an application form from the CMO Scholarship Coordinator.\n2. Submit the completed form along with requirements (Report Card / True Copy of Grades, Certificate of Indigency, Voter's ID of parents, 2x2 ID picture).\n3. Attend the scheduled screening and interview.\n4. Wait for the posting of qualified scholars.\n\n💰 **Cost:** Free.\n⏱️ **Processing Time:** Applications are processed within the specific submission period (usually before the semester starts).",
            "tl": "Maaaring mag-apply ang mga estudyante para sa **City Educational Scholarship Program**.\n\n---\n### 🎓 Proseso ng Scholarship\n\n**Steps:**\n1. Kumuha ng application form sa CMO Scholarship Coordinator.\n2. Isumite ito kasama ang requirements (Report Card / Grades, Certificate of Indigency, Voter's ID ng magulang, 2x2 picture).\n3. Umattend sa naka-schedule na screening at interview.\n4. Hintayin ang anunsyo ng mga nakapasang scholars.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** Pinoproseso ito bago magsimula ang semestre.",
            "bis": "Pwede mag-apply ang mga estudyante para sa **City Educational Scholarship Program**.\n\n---\n### 🎓 Proseso sa Scholarship\n\n**Steps:**\n1. Pagkuha og application form sa CMO Scholarship Coordinator.\n2. Isumite ni uban ang requirements (Report Card / Grades, Certificate of Indigency, Voter's ID sa ginikanan, 2x2 picture).\n3. Mu-attend sa screening ug interview.\n4. Hulata ang anunsyo sa mga nakapasar nga scholars.\n\n💰 **Bayad:** Libre.\n⏱️ **Processing Time:** Ginaproseso ni sa wala pa mag-start ang semester."
        },
        "questions": [
            ("en", "How to apply for Mayor's scholarship?"),
            ("en", "Requirements for educational assistance"),
            ("en", "City scholarship application process"),
            ("tl", "Paano mag-apply ng scholarship sa Mayor?"),
            ("tl", "Ano kailangan para sa educational assistance?"),
            ("bis", "Unsaon pag apply og scholarship sa Mayor?"),
            ("bis", "Unsay requirements sa scholarship?"),
            ("bis", "Gusto ko mo apply sa educational assistance")
        ]
    },
    "cmo_tricycle_dropping": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "If a tricycle unit is no longer operational, the owner must apply for **Dropping of Franchise**.\n\n---\n### 📉 Dropping Process\n\n**Steps:**\n1. Surrender the Original MTOP Franchise, Tricycle Plate, and submit an Affidavit of Dropping to the BPLS.\n2. Secure the Order of Payment.\n3. Pay the Dropping Fee at the City Treasurer's Office.\n4. Claim the Certification of Dropped Franchise.\n\n💰 **Cost:** Dropping Fee is around ~₱150.00.\n⏱️ **Processing Time:** Around 1-2 hours.",
            "tl": "Kung hindi na gagamitin ang tricycle, kailangang mag-apply ng **Dropping of Franchise**.\n\n---\n### 📉 Proseso ng Dropping\n\n**Steps:**\n1. I-surrender ang Original MTOP, Tricycle Plate, at isumite ang Affidavit of Dropping sa BPLS.\n2. Kunin ang Order of Payment.\n3. Magbayad ng Dropping Fee sa City Treasurer's Office.\n4. Kunin ang Certification of Dropped Franchise.\n\n💰 **Bayad:** Dropping Fee ay ~₱150.00.\n⏱️ **Processing Time:** Tinatayang 1-2 oras.",
            "bis": "Kung dili na gamiton ang tricycle, kinahanglan mag-apply og **Dropping of Franchise**.\n\n---\n### 📉 Proseso sa Dropping\n\n**Steps:**\n1. I-surrender ang Original MTOP, Tricycle Plate, ug isumite ang Affidavit of Dropping sa BPLS.\n2. Kuhaa ang Order of Payment.\n3. Pagbayad sa Dropping Fee sa City Treasurer's Office.\n4. Kuhaa ang Certification of Dropped Franchise.\n\n💰 **Bayad:** Dropping Fee kay mga ~₱150.00.\n⏱️ **Processing Time:** Mga 1-2 ka oras."
        },
        "questions": [
            ("en", "How to drop tricycle franchise?"),
            ("en", "Process for dropping of MTOP"),
            ("en", "I want to cancel my tricycle franchise"),
            ("tl", "Paano i-drop ang prangkisa ng tricycle?"),
            ("tl", "Requirements para ipasara ang MTOP"),
            ("bis", "Unsaon pag drop sa prangkisa sa tricycle?"),
            ("bis", "Ipasira nako akong franchise sa tricycle"),
            ("bis", "Dropping of MTOP proseso")
        ]
    },
    "cmo_franchise_renewal": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Tricycle operators must process their **MTOP / Franchise Renewal** annually.\n\n---\n### 🔄 Franchise Renewal\n\n**Steps:**\n1. Present your Previous MTOP, updated LTO CR/OR, and Barangay Clearance to the BPLS.\n2. Have the unit inspected for a Traffic Clearance.\n3. Get the Order of Payment and pay the Renewal Fee at the City Treasurer's Office.\n4. Present the receipt and claim your renewed MTOP Franchise and Sticker.\n\n💰 **Cost:** Mayor's Permit ~₱100.00, Sticker ~₱75.00.\n⏱️ **Processing Time:** Around 2-3 hours.",
            "tl": "Kailangang i-renew ng mga operators ang kanilang **MTOP / Franchise** taon-taon.\n\n---\n### 🔄 Proseso ng Renewal\n\n**Steps:**\n1. Ipakita ang Nakaraang MTOP, updated LTO CR/OR, at Barangay Clearance sa BPLS.\n2. Ipainspeksyon ang tricycle para sa Traffic Clearance.\n3. Kunin ang Order of Payment at magbayad ng Renewal Fee sa City Treasurer's Office.\n4. Ipakita ang resibo at kunin ang na-renew na MTOP at Sticker.\n\n💰 **Bayad:** Mayor's Permit ~₱100.00, Sticker ~₱75.00.\n⏱️ **Processing Time:** Tinatayang 2-3 oras.",
            "bis": "Kinahanglan i-renew sa mga operator ang ilahang **MTOP / Franchise** kada tuig.\n\n---\n### 🔄 Proseso sa Renewal\n\n**Steps:**\n1. Ipakita ang Nakaagi nga MTOP, updated LTO CR/OR, ug Barangay Clearance sa BPLS.\n2. Ipa-inspeksyon ang tricycle para sa Traffic Clearance.\n3. Kuhaa ang Order of Payment ug pagbayad sa Renewal Fee sa City Treasurer's Office.\n4. Ipakita ang resibo ug kuhaa ang na-renew nga MTOP ug Sticker.\n\n💰 **Bayad:** Mayor's Permit ~₱100.00, Sticker ~₱75.00.\n⏱️ **Processing Time:** Mga 2-3 ka oras."
        },
        "questions": [
            ("en", "How to renew tricycle franchise?"),
            ("en", "MTOP renewal requirements"),
            ("en", "Process for renewing my tricycle MTOP"),
            ("tl", "Paano i-renew ang prangkisa ng tricycle?"),
            ("tl", "Requirements sa renewal ng MTOP"),
            ("bis", "Unsaon pag renew sa prangkisa sa tricycle?"),
            ("bis", "Unsay kailangan sa pag renew sa MTOP?"),
            ("bis", "Mag renew ko sa akong tricycle")
        ]
    },
    "cmo_special_business_permit": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Temporary businesses (like carnivals, trade fairs, peryahan, or seasonal stalls) require a **Special Business Permit**.\n\n---\n### 🎪 Special Permit Process\n\n**Steps:**\n1. Submit a letter of intent to the Mayor specifying the duration and type of business.\n2. Secure Barangay Clearance for the specific activity.\n3. BPLS will assess the application and issue an Order of Payment.\n4. Pay the corresponding fees at the City Treasurer's Office.\n5. Claim the Special Business Permit.\n\n💰 **Cost:** Computed per day/week based on the local tax code.\n⏱️ **Processing Time:** 1 to 2 days.",
            "tl": "Ang mga panandaliang negosyo (tulad ng peryahan, trade fair, o seasonal stalls) ay nangangailangan ng **Special Business Permit**.\n\n---\n### 🎪 Proseso\n\n**Steps:**\n1. Isumite ang letter of intent sa Mayor na nagsasaad kung gaano katagal at anong klase ng negosyo.\n2. Kumuha ng Barangay Clearance para sa aktibidad.\n3. I-aassess ng BPLS at bibigyan ka ng Order of Payment.\n4. Magbayad ng fee sa City Treasurer's Office.\n5. Kunin ang Special Business Permit.\n\n💰 **Bayad:** Kinukwenta kada araw/linggo base sa tax code.\n⏱️ **Processing Time:** 1 hanggang 2 araw.",
            "bis": "Ang mga temporaryo nga negosyo (pareha sa peryahan, trade fair, o seasonal stalls) kay nanginahanglan og **Special Business Permit**.\n\n---\n### 🎪 Proseso\n\n**Steps:**\n1. Isumite ang letter of intent sa Mayor kung unsa kadugay ug unsa nga klase sa negosyo.\n2. Pagkuha og Barangay Clearance para sa maong aktibidad.\n3. I-assess sa BPLS ug hatagan ka og Order of Payment.\n4. Pagbayad sa fee didto sa City Treasurer's Office.\n5. Kuhaa ang Special Business Permit.\n\n💰 **Bayad:** Kwentahon kada adlaw/semana base sa tax code.\n⏱️ **Processing Time:** 1 hantod 2 ka adlaw."
        },
        "questions": [
            ("en", "How to get a permit for a trade fair?"),
            ("en", "Special business permit for peryahan"),
            ("en", "Permit for temporary stalls"),
            ("tl", "Paano kumuha ng permit para sa peryahan?"),
            ("tl", "Special permit para sa trade fair"),
            ("bis", "Unsaon pagkuha og permit para sa peryahan?"),
            ("bis", "Permit para sa seasonal stalls"),
            ("bis", "Magbutang mi og temporary stall unsay permit")
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
                    "source": "Citizen Charter (Part 2)",
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
    
    print("CMO Part 2 Population Complete!")

if __name__ == "__main__":
    main()
