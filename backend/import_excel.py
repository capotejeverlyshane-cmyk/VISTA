import json
import pandas as pd
import re
import os

ANSWERS_FILE = 'data/answers.json'
INTENTS_FILE = 'data/intents.csv'
CSV_SOURCE = 'data/citizen_chart_cmo - Sheet1.csv'

def clean_intent_name(text):
    # Remove leading numbers like "1. "
    text = re.sub(r'^\d+\.\s*', '', str(text))
    # Replace non-alphanumeric with underscore
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', text.lower()).strip('_')
    return f"cmo_{clean}"

def format_bullet_points(text):
    if pd.isna(text): return ""
    text = str(text).strip()
    if text.startswith('-') or text.startswith('1.'):
        return text # Already formatted
    
    # If it has semicolons, split by semicolon to make bullets
    if ';' in text:
        parts = [p.strip() for p in text.split(';') if p.strip()]
        return '\n'.join([f"- {p}" for p in parts])
    return text

def main():
    print("Loading existing answers.json...")
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        answers_data = json.load(f)
    
    print("Loading existing intents.csv...")
    intents_df = pd.read_csv(INTENTS_FILE)
    next_id = intents_df['id'].max() + 1 if not intents_df.empty else 1
    
    # Backup
    import shutil
    shutil.copy(ANSWERS_FILE, ANSWERS_FILE + '.bak')
    shutil.copy(INTENTS_FILE, INTENTS_FILE + '.bak')
    
    print(f"Reading {CSV_SOURCE}...")
    source_df = pd.read_csv(CSV_SOURCE)
    
    new_rows = []
    processed_count = 0
    
    for index, row in source_df.iterrows():
        service_name = str(row.get('Service Name', ''))
        
        # Stop processing if we hit the tables (doesn't start with a number and dot)
        if not re.match(r'^\d+\.', service_name):
            continue
            
        service_display_name = re.sub(r'^\d+\.\s*', '', service_name)
        base_intent = clean_intent_name(service_name)
        department = str(row.get('Department', "City Mayor's Office"))
        
        # Data
        reqs = format_bullet_points(row.get('Requirements', ''))
        process = format_bullet_points(row.get('Process', ''))
        fee = str(row.get('Fee', ''))
        location = str(row.get('Location', ''))
        
        # Definitions of 4 sub-intents
        sub_intents = {
            "requirements": {
                "suffix": "_requirements",
                "markdown": f"Based on the Citizen's Charter, here are the **Requirements** for {service_display_name}:\n\n{reqs}\n\nPlease ensure all documents are complete.",
                "questions": [
                    ("en", f"What are the requirements for {service_display_name}?"),
                    ("en", f"What to bring for {service_display_name}?"),
                    ("tl", f"Ano ang mga kailangan para sa {service_display_name}?"),
                    ("bis", f"Unsa ang requirements para sa {service_display_name}?")
                ],
                "tags": f"{service_display_name.lower()}, requirements, documents"
            },
            "process": {
                "suffix": "_process",
                "markdown": f"Based on the Citizen's Charter, here is the **Step-by-Step Process** for {service_display_name}:\n\n{process}",
                "questions": [
                    ("en", f"How to apply for {service_display_name}?"),
                    ("en", f"What is the process for {service_display_name}?"),
                    ("tl", f"Paano ang proseso ng {service_display_name}?"),
                    ("bis", f"Unsaon pag process sa {service_display_name}?")
                ],
                "tags": f"{service_display_name.lower()}, process, steps, how to"
            },
            "fee": {
                "suffix": "_fee",
                "markdown": f"Based on the Citizen's Charter, the **Fee or Cost** for {service_display_name} is as follows:\n\n💰 {fee}\n\n*Note: Exact fees may vary depending on assessments.*",
                "questions": [
                    ("en", f"How much is the fee for {service_display_name}?"),
                    ("en", f"Cost of {service_display_name}"),
                    ("tl", f"Magkano ang bayad sa {service_display_name}?"),
                    ("bis", f"Pila ang bayad para sa {service_display_name}?")
                ],
                "tags": f"{service_display_name.lower()}, fee, cost, price, pay"
            },
            "location": {
                "suffix": "_location",
                "markdown": f"Based on the Citizen's Charter, you need to proceed to the following office(s) for {service_display_name}:\n\n📍 **{location}**",
                "questions": [
                    ("en", f"Where to go for {service_display_name}?"),
                    ("en", f"Location of office for {service_display_name}"),
                    ("tl", f"Saan ang opisina para sa {service_display_name}?"),
                    ("bis", f"Asa nga opisina moadto para sa {service_display_name}?")
                ],
                "tags": f"{service_display_name.lower()}, location, where, office"
            }
        }
        
        for key, data in sub_intents.items():
            intent_id = base_intent + data["suffix"]
            
            # Add to answers.json if not exists
            if intent_id not in answers_data:
                answers_data[intent_id] = {
                    "department": department,
                    "answers": {
                        "en": data["markdown"],
                        "tl": data["markdown"].replace("Based on the Citizen's Charter, here are the **Requirements** for", f"Ayon sa Citizen's Charter, narito ang mga **Kailangan** para sa").replace("Based on the Citizen's Charter, here is the **Step-by-Step Process** for", f"Ayon sa Citizen's Charter, narito ang **Proseso** para sa").replace("Based on the Citizen's Charter, the **Fee or Cost** for", f"Ayon sa Citizen's Charter, ang **Bayad** para sa").replace("Based on the Citizen's Charter, you need to proceed to the following office(s) for", f"Ayon sa Citizen's Charter, pumunta sa sumusunod na opisina para sa"),
                        "bis": data["markdown"].replace("Based on the Citizen's Charter, here are the **Requirements** for", f"Base sa Citizen's Charter, mao ni ang mga **Kinahanglanon** para sa").replace("Based on the Citizen's Charter, here is the **Step-by-Step Process** for", f"Base sa Citizen's Charter, mao ni ang **Proseso** para sa").replace("Based on the Citizen's Charter, the **Fee or Cost** for", f"Base sa Citizen's Charter, ang **Bayad** para sa").replace("Based on the Citizen's Charter, you need to proceed to the following office(s) for", f"Base sa Citizen's Charter, adto sa mosunod nga opisina para sa")
                    }
                }
                
                # Add to intents.csv
                for lang, question in data["questions"]:
                    new_rows.append({
                        "id": next_id,
                        "department": department,
                        "intent": intent_id,
                        "language": lang,
                        "question": question,
                        "answer": data["markdown"],
                        "source": "Citizen Charter Automated",
                        "tags": data["tags"]
                    })
                    next_id += 1
                    
        processed_count += 1
        print(f"Processed: {service_display_name}")

    # Save
    if new_rows:
        print(f"Adding {len(new_rows)} new questions to intents.csv...")
        new_df = pd.DataFrame(new_rows)
        intents_df = pd.concat([intents_df, new_df], ignore_index=True)
        intents_df.to_csv(INTENTS_FILE, index=False)
        
        print("Saving updated answers.json...")
        with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
            json.dump(answers_data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully processed {processed_count} services into {processed_count * 4} sub-intents!")
    else:
        print("No new data to add.")

if __name__ == "__main__":
    main()
