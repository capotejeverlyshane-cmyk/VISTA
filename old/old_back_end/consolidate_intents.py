import os
import sys

# Ensure imports work from backend directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from supabase_client import supabase

def consolidate_intents():
    print("Fetching intents from Supabase...")
    res = supabase.table("intents").select("*").execute()
    all_intents = res.data

    print(f"Total original intents: {len(all_intents)}")

    # Group intents by base name
    # We look for suffixes: _requirements, _process, _fee, _location
    suffixes = ['_requirements', '_process', '_fee', '_location']
    
    # Map of base_intent_name -> {
    #   'department': '',
    #   'sub_intents': {
    #       'requirements': {...intent_row...},
    #       'process': {...},
    #       ...
    #   }
    # }
    groups = {}
    
    # Track intents that are NOT sub-intents to leave them alone
    master_intents = {}
    
    for intent in all_intents:
        name = intent['intent_name']
        is_sub = False
        for suffix in suffixes:
            if name.endswith(suffix):
                is_sub = True
                base_name = name[: -len(suffix)]
                category = suffix.replace('_', '')
                
                if base_name not in groups:
                    groups[base_name] = {
                        'department': intent.get('department', 'General'),
                        'sub_intents': {}
                    }
                groups[base_name]['sub_intents'][category] = intent
                break
        
        if not is_sub:
            master_intents[name] = intent
            
    print(f"Found {len(groups)} distinct services to consolidate.")

    # Now we build the merged master intents
    for base_name, data in groups.items():
        print(f"Consolidating: {base_name}")
        
        merged_en = []
        merged_tl = []
        merged_bis = []
        
        # Order matters: Requirements -> Process -> Fee -> Location
        order = [
            ('requirements', 'Requirements', 'Mga Kailangan', 'Mga Kinahanglanon'),
            ('process', 'Process', 'Proseso', 'Proseso'),
            ('fee', 'Fees', 'Bayarin', 'Bayad'),
            ('location', 'Location', 'Lokasyon', 'Lokasyon')
        ]
        
        for cat, en_header, tl_header, bis_header in order:
            if cat in data['sub_intents']:
                row = data['sub_intents'][cat]
                
                en_ans = row.get('en_answer') or ""
                tl_ans = row.get('tl_answer') or ""
                bis_ans = row.get('bis_answer') or ""
                
                if en_ans.strip(): merged_en.append(f"### {en_header}\n{en_ans.strip()}")
                if tl_ans.strip(): merged_tl.append(f"### {tl_header}\n{tl_ans.strip()}")
                if bis_ans.strip(): merged_bis.append(f"### {bis_header}\n{bis_ans.strip()}")
                
        final_en = "\n\n".join(merged_en)
        final_tl = "\n\n".join(merged_tl)
        final_bis = "\n\n".join(merged_bis)
        
        # 1. Check if the master intent already exists in the database
        master_id = None
        if base_name in master_intents:
            master_id = master_intents[base_name]['id']
            # Update the existing master intent with the new merged text
            print(f" -> Updating existing master intent: {base_name}")
            supabase.table("intents").update({
                "en_answer": final_en,
                "tl_answer": final_tl,
                "bis_answer": final_bis
            }).eq("id", master_id).execute()
        else:
            # Create a new master intent
            print(f" -> Creating new master intent: {base_name}")
            new_res = supabase.table("intents").insert({
                "intent_name": base_name,
                "department": data['department'],
                "en_answer": final_en,
                "tl_answer": final_tl,
                "bis_answer": final_bis
            }).execute()
            master_id = new_res.data[0]['id']
            
        # 2. Remap training phrases from sub-intents to master intent
        for cat, row in data['sub_intents'].items():
            old_id = row['id']
            print(f"   -> Remapping phrases from {row['intent_name']} (ID {old_id}) to {base_name} (ID {master_id})")
            supabase.table("training_phrases").update({
                "intent_id": master_id
            }).eq("intent_id", old_id).execute()
            
            # 3. Delete the old sub-intent
            supabase.table("intents").delete().eq("id", old_id).execute()
            
    print("Done consolidating! You should now run train.py to retrain the ML model.")

if __name__ == "__main__":
    consolidate_intents()
