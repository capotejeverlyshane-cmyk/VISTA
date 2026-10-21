"""Fix the author name in reference [16]: 'A. Buber' -> 'A. Budhiraja'"""
from docx import Document
import re

doc = Document(r"VISTA_Chapter1_and_2_FIXED.docx")

fixed = False
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if text.startswith('[16]') and 'Buber' in text:
        print(f"[FOUND] Para {i}: {text[:100]}...")
        for run in para.runs:
            if 'Buber' in run.text:
                run.text = run.text.replace('A. Buber', 'A. Budhiraja')
                fixed = True
                print(f"  -> Fixed 'A. Buber' to 'A. Budhiraja'")
                break
        if not fixed:
            # Try full paragraph approach
            if para.runs:
                full = para.text
                new_full = full.replace('A. Buber', 'A. Budhiraja')
                for run in para.runs:
                    run.text = ""
                para.runs[0].text = new_full
                fixed = True
                print(f"  -> Fixed via full paragraph rebuild")
        break

    # Also check in the RRL body text if "Buber" appears anywhere
    if 'Buber' in text and not text.startswith('['):
        print(f"[BODY] Para {i} also has 'Buber': {text[:80]}...")

if fixed:
    doc.save(r"VISTA_Chapter1_and_2_FINAL_v2.docx")
    print("\n[SAVED] Fixed author name in VISTA_Chapter1_and_2_FIXED.docx")
else:
    print("\n[INFO] 'Buber' not found or already correct.")
