import json
import pandas as pd
import shutil

ANSWERS_FILE = 'data/answers.json'
INTENTS_FILE = 'data/intents.csv'

# Backup files
shutil.copy(ANSWERS_FILE, ANSWERS_FILE + '.bak')
shutil.copy(INTENTS_FILE, INTENTS_FILE + '.bak')

NEW_DATA = {
    "cmo_new_business_permit_requirements": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Based on the Citizen's Charter, here are the **Requirements** for a New Business Permit:\n\n1. **DTI / SEC / CDA Registration**\n2. **Location plan or sketch**\n3. **Proof of right to use location** (Title, Lease Contract, etc.)\n4. **Barangay Clearance for Business**\n\nPlease ensure all documents are complete before submitting them to the BPLS.",
            "tl": "Ayon sa Citizen's Charter, narito ang mga **Kailangan** para sa Bagong Business Permit:\n\n1. **DTI / SEC / CDA Registration**\n2. **Location plan o sketch**\n3. **Katibayan ng pagmamay-ari o Lease Contract** ng pwesto\n4. **Barangay Clearance**\n\nSiguraduhing kumpleto ang mga dokumento bago pumunta sa BPLS.",
            "bis": "Base sa Citizen's Charter, mao ni ang mga **Kinahanglanon** para sa Bag-ong Business Permit:\n\n1. **DTI / SEC / CDA Registration**\n2. **Location plan o sketch**\n3. **Katibayan sa pagpanag-iya o Lease Contract** sa pwesto\n4. **Barangay Clearance**\n\nSiguraduha nga kumpleto ang mga dokumento usa moadto sa BPLS."
        },
        "questions": [
            ("en", "What are the requirements for a new business permit?"),
            ("en", "What documents do I need to bring for a new business permit?"),
            ("tl", "Ano ang mga kailangan para sa bagong business permit?"),
            ("tl", "Anong dokumento ang kailangan dalhin sa BPLS para sa bagong negosyo?"),
            ("bis", "Unsa ang requirements sa pagkuha og bag-ong business permit?"),
            ("bis", "Unsa nga mga papeles ang dad-on para sa new business permit?")
        ]
    },
    "cmo_new_business_permit_process": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Based on the Citizen's Charter, here is the **Step-by-Step Process** for a New Business Permit:\n\n1. **Submit** complete documentary requirements to the BPLS.\n2. **Wait** for assessment and secure the Order of Payment.\n3. **Pay** the assigned fees at the City Treasurer's Office and get the Official Receipt.\n4. **Present O.R. and claim** your Business Permit, Plate, and Clearances.\n\n⏱️ *Processing Time: Around 2 hours if requirements are complete.*",
            "tl": "Ayon sa Citizen's Charter, narito ang **Proseso** para sa Bagong Business Permit:\n\n1. **Isumite** ang kumpletong requirements sa BPLS.\n2. **Hintayin** ang assessment at kunin ang Order of Payment.\n3. **Magbayad** sa City Treasurer's Office at kunin ang Official Receipt.\n4. **Ipakita ang O.R.** at kunin ang inyong Business Permit, Plate, at Clearances.\n\n⏱️ *Processing Time: Tinatayang 2 oras kung kumpleto ang requirements.*",
            "bis": "Base sa Citizen's Charter, mao ni ang **Proseso** para sa Bag-ong Business Permit:\n\n1. **Isumite** ang kumpletong requirements sa BPLS.\n2. **Hulata** ang assessment ug kuhaa ang Order of Payment.\n3. **Pagbayad** sa City Treasurer's Office ug kuhaa ang Official Receipt.\n4. **Ipakita ang O.R.** ug kuhaa ang imong Business Permit, Plate, ug Clearances.\n\n⏱️ *Processing Time: Mga 2 ka oras kung kumpleto ang requirements.*"
        },
        "questions": [
            ("en", "How to apply for a new business permit?"),
            ("en", "What is the process of getting a new business permit?"),
            ("en", "Steps for new business permit application"),
            ("tl", "Paano kumuha ng bagong business permit?"),
            ("tl", "Ano ang proseso ng pagkuha ng business permit?"),
            ("bis", "Unsaon pag apply og bag-ong business permit?"),
            ("bis", "Unsay proseso pagkuha og business permit?")
        ]
    },
    "cmo_new_business_permit_fee": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Based on the Citizen's Charter, the **Cost or Fee** for a New Business Permit depends on the capitalization and classification of your business. \n\nPlease proceed to the BPLS for an official assessment and secure the Order of Payment.",
            "tl": "Ayon sa Citizen's Charter, ang **Bayad** para sa Bagong Business Permit ay depende sa kapital at klase ng inyong negosyo. \n\nPumunta sa BPLS upang ipa-assess ito at makakuha ng Order of Payment.",
            "bis": "Base sa Citizen's Charter, ang **Bayad** para sa Bag-ong Business Permit kay magdepende sa kapital ug klase sa inyong negosyo. \n\nAdto sa BPLS para mapa-assess kini ug makakuha og Order of Payment."
        },
        "questions": [
            ("en", "How much is a new business permit?"),
            ("en", "What is the fee for a new business permit?"),
            ("en", "Cost of new business permit"),
            ("tl", "Magkano ang bagong business permit?"),
            ("tl", "Magkano babayaran sa pagkuha ng business permit?"),
            ("bis", "Pila ang bayad sa bag-ong business permit?"),
            ("bis", "Pila ang magasto para sa business permit?")
        ]
    },
    "cmo_new_business_permit_location": {
        "department": "City Mayor's Office - BPLS",
        "answers": {
            "en": "Based on the Citizen's Charter, to apply and pay for a New Business Permit, you need to go to two offices:\n\n1. **BPLS (Business Permit and Licensing Section)** - For submission of documents and assessment.\n2. **City Treasurer's Office** - For payment of assessed fees.",
            "tl": "Ayon sa Citizen's Charter, para sa Bagong Business Permit, kailangan mong pumunta sa dalawang opisina:\n\n1. **BPLS (Business Permit and Licensing Section)** - Para sa pagpasa ng requirements at assessment.\n2. **City Treasurer's Office** - Para sa pagbabayad ng fees.",
            "bis": "Base sa Citizen's Charter, para sa Bag-ong Business Permit, kinahanglan ka moadto sa duha ka opisina:\n\n1. **BPLS (Business Permit and Licensing Section)** - Para sa pagpasa sa requirements ug assessment.\n2. **City Treasurer's Office** - Para sa pagbayad sa fees."
        },
        "questions": [
            ("en", "Where do I apply for a new business permit?"),
            ("en", "Where is the office for new business permit payment?"),
            ("en", "Which office issues the business permit?"),
            ("tl", "Saan kukuha ng bagong business permit?"),
            ("tl", "Saang opisina magbabayad ng business permit?"),
            ("bis", "Asa mokuha og bag-ong business permit?"),
            ("bis", "Asa nga opisina magbayad para sa business permit?")
        ]
    }
}

def main():
    print("Loading existing answers.json...")
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        answers_data = json.load(f)
    
    print("Loading existing intents.csv...")
    intents_df = pd.read_csv(INTENTS_FILE)
    
    # Remove old cmo_new_business_permit intent
    if "cmo_new_business_permit" in answers_data:
        del answers_data["cmo_new_business_permit"]
        print("Removed old 'cmo_new_business_permit' from answers.json")
        
    initial_len = len(intents_df)
    intents_df = intents_df[intents_df['intent'] != "cmo_new_business_permit"]
    print(f"Removed {initial_len - len(intents_df)} rows for 'cmo_new_business_permit' from intents.csv")
    
    next_id = intents_df['id'].max() + 1 if not intents_df.empty else 1
    new_rows = []
    
    for intent, data in NEW_DATA.items():
        if intent not in answers_data:
            print(f"Adding new sub-intent: {intent}")
            answers_data[intent] = {
                "department": data["department"],
                "answers": data["answers"]
            }
            
            for lang, question in data["questions"]:
                answer_text = data["answers"].get(lang, "")
                tags = "new, business, permit, " + intent.split('_')[-1]
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
    
    print("Done restructuring intents!")

if __name__ == "__main__":
    main()
