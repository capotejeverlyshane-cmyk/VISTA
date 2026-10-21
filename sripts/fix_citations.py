"""
Fix citations in VISTA_Chapter1_and_2_REVISED_AY25-26.docx
1. Add [2] to Background paragraph 1
2. Add [29] to Data Pre-processing section
3. Add [30] to Panabo City paragraph
4. Remove old references [30]-[33]
5. Renumber old [34] to [30]
"""

from docx import Document
import copy
import re

SRC = r"VISTA_Chapter1_and_2_REVISED_AY25-26.docx"
OUT = r"VISTA_Chapter1_and_2_REVISED_AY25-26.docx"  # overwrite

doc = Document(SRC)

changes_made = []

# Helper: replace text in a paragraph while preserving formatting
def replace_in_paragraph(para, old_text, new_text):
    """Replace text in paragraph runs, preserving formatting."""
    full_text = para.text
    if old_text not in full_text:
        return False
    
    # Try simple run-level replacement first
    for run in para.runs:
        if old_text in run.text:
            run.text = run.text.replace(old_text, new_text)
            return True
    
    # If text spans multiple runs, rebuild the paragraph
    # Collect all runs and their formatting
    runs_data = []
    for run in para.runs:
        runs_data.append({
            'text': run.text,
            'bold': run.bold,
            'italic': run.italic,
            'underline': run.underline,
            'font_name': run.font.name,
            'font_size': run.font.size,
            'font_color': run.font.color.rgb if run.font.color and run.font.color.rgb else None,
        })
    
    # Join all text
    joined = ''.join(r['text'] for r in runs_data)
    if old_text not in joined:
        return False
    
    # Find position of old_text
    pos = joined.find(old_text)
    
    # Build new joined text
    new_joined = joined[:pos] + new_text + joined[pos + len(old_text):]
    
    # Now redistribute text across runs (keep first run's formatting for inserted text)
    # Simple approach: put all text in first run, clear others
    # Better approach: preserve run boundaries where possible
    
    char_idx = 0
    new_runs_text = []
    for rd in runs_data:
        run_len = len(rd['text'])
        new_runs_text.append(new_joined[char_idx:char_idx + run_len])
        char_idx += run_len
    
    # If new text is longer, append remainder to last run
    if char_idx < len(new_joined):
        new_runs_text[-1] += new_joined[char_idx:]
    
    # Apply new text to runs
    for i, run in enumerate(para.runs):
        if i < len(new_runs_text):
            run.text = new_runs_text[i]
        else:
            run.text = ""
    
    return True


# ── CHANGE 1: Add [2] to Background paragraph 1 ──────────────────────
# Find the paragraph that contains the [1] citation in Background
for i, para in enumerate(doc.paragraphs):
    target_text = "through information and communication technologies (ICT) [1]. Digital platforms allow citizens to access official information remotely"
    if target_text in para.text:
        old = "through information and communication technologies (ICT) [1]. Digital platforms allow citizens to access official information remotely, reducing the need for physical visits and helping standardize service communication across channels."
        new = "through information and communication technologies (ICT) [1]. These digital transformation efforts are closely tied to the United Nations Sustainable Development Goals, particularly SDG 9 (Industry, Innovation, and Infrastructure) and SDG 16 (Peace, Justice, and Strong Institutions), which call for inclusive, accountable institutions supported by technology [2]. Digital platforms allow citizens to access official information remotely, reducing the need for physical visits and helping standardize service communication across channels."
        if replace_in_paragraph(para, old, new):
            changes_made.append("1. Added [2] citation to Background paragraph 1")
        else:
            # Try a shorter match
            old2 = "(ICT) [1]. Digital platforms"
            new2 = "(ICT) [1]. These digital transformation efforts are closely tied to the United Nations Sustainable Development Goals, particularly SDG 9 (Industry, Innovation, and Infrastructure) and SDG 16 (Peace, Justice, and Strong Institutions), which call for inclusive, accountable institutions supported by technology [2]. Digital platforms"
            if replace_in_paragraph(para, old2, new2):
                changes_made.append("1. Added [2] citation to Background paragraph 1 (short match)")
        break

# ── CHANGE 2: Add [29] to Data Pre-processing ────────────────────────
for i, para in enumerate(doc.paragraphs):
    if "Before classification, the collected text data undergoes pre-processing" in para.text:
        old = "Before classification, the collected text data undergoes pre-processing to improve its quality and reliability."
        new = "Before classification, the collected text data undergoes pre-processing to improve its quality and reliability [29]."
        if replace_in_paragraph(para, old, new):
            changes_made.append("2. Added [29] citation to Data Pre-processing section")
        else:
            old2 = "undergoes pre-processing to improve its quality and reliability. This"
            new2 = "undergoes pre-processing to improve its quality and reliability [29]. This"
            if replace_in_paragraph(para, old2, new2):
                changes_made.append("2. Added [29] citation to Data Pre-processing (alt match)")
        break

# ── CHANGE 3: Add [30] to Panabo City paragraph ──────────────────────
for i, para in enumerate(doc.paragraphs):
    if "In Panabo City specifically, citizen inquiries are still handled" in para.text:
        old = "In Panabo City specifically, citizen inquiries are still handled through manual and fragmented channels"
        new = "In Panabo City, a first-class component city in Davao del Norte with a population of 184,599 as of the 2020 Census [30], citizen inquiries are still handled through manual and fragmented channels"
        if replace_in_paragraph(para, old, new):
            changes_made.append("3. Added [30] citation to Panabo City paragraph")
        else:
            old2 = "In Panabo City specifically,"
            new2 = "In Panabo City, a first-class component city in Davao del Norte with a population of 184,599 as of the 2020 Census [30],"
            if replace_in_paragraph(para, old2, new2):
                changes_made.append("3. Added [30] citation to Panabo City paragraph (alt match)")
        break
    elif "In Panabo City" in para.text and "citizen inquiries" in para.text:
        old = "In Panabo City"
        new = "In Panabo City, a first-class component city in Davao del Norte with a population of 184,599 as of the 2020 Census [30]"
        # Only replace if it's the right paragraph
        if "manual and fragmented" in para.text or "front-desk" in para.text:
            if replace_in_paragraph(para, old, new):
                changes_made.append("3. Added [30] citation to Panabo City paragraph (broad match)")
            break


# ── CHANGE 4: Fix References Section ─────────────────────────────────
# Find and remove references [30]-[33], renumber [34] to [30]
refs_to_remove = []
ref_34_idx = None

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    # Match references [30] through [33] - remove them
    if re.match(r'^\[30\]', text) and ('Zhang' in text or 'sensitivity' in text.lower()):
        refs_to_remove.append(i)
    elif re.match(r'^\[31\]', text) and ('Deng' in text or 'Deep Learning in Natural' in text):
        refs_to_remove.append(i)
    elif re.match(r'^\[32\]', text) and ('Vaswani' in text or 'Attention' in text):
        refs_to_remove.append(i)
    elif re.match(r'^\[33\]', text) and ('Brownlee' in text or 'Deep Learning for Natural' in text):
        refs_to_remove.append(i)
    elif re.match(r'^\[34\]', text) and ('Philippine Statistics' in text or 'PSA' in text or 'Census' in text):
        ref_34_idx = i

# Remove references [30]-[33] by clearing their text
for idx in refs_to_remove:
    # Clear the paragraph (can't easily delete paragraphs in python-docx)
    for run in doc.paragraphs[idx].runs:
        run.text = ""
    changes_made.append(f"4. Cleared old reference at paragraph index {idx}")

# Renumber [34] to [30]
if ref_34_idx is not None:
    para = doc.paragraphs[ref_34_idx]
    if replace_in_paragraph(para, "[34]", "[30]"):
        changes_made.append("5. Renumbered [34] to [30] (PSA Census)")

# ── CHANGE 5: Add [29] reference if not already present ──────────────
# Check if [29] reference already exists
ref_29_exists = False
ref_29_idx = None
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if re.match(r'^\[29\]', text) and 'Feldman' in text:
        ref_29_exists = True
        ref_29_idx = i
        break

if ref_29_exists:
    changes_made.append("6. Reference [29] (Feldman & Sanger) already exists - no change needed")
else:
    changes_made.append("6. WARNING: Reference [29] not found - you may need to add it manually")


# ── Save ──────────────────────────────────────────────────────────────
doc.save(OUT)

print("=" * 60)
print("CITATION FIXES APPLIED")
print("=" * 60)
for c in changes_made:
    print(f"  {c}")
print(f"\nSaved to: {OUT}")
print(f"\nTotal changes: {len(changes_made)}")
