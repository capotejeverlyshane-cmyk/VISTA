"""Extract objectives from the document."""
from docx import Document

doc = Document(r"VISTA_Chapter1_and_2_FINAL_v2.docx")

print("SEARCHING FOR OBJECTIVES...")
print("=" * 100)

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    lower = text.lower()
    
    # Look for objective-related headings and content
    if any(keyword in lower for keyword in ['objective', 'aims to', 'specifically']):
        print(f"\nPara {i}: {text}")
    
    # Also catch numbered objectives (1., 2., etc. or a., b.)
    if i > 0:
        prev = doc.paragraphs[i-1].text.strip().lower()
        if 'objective' in prev or 'specifically' in prev:
            if text:
                print(f"  Para {i}: {text}")

# Also do a broader sweep for the section
print("\n\n" + "=" * 100)
print("CONTEXT AROUND 'OBJECTIVES' (10 paragraphs after each match)")
print("=" * 100)

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip().lower()
    if 'objectives of the study' in text or 'specific objectives' in text or 'general objective' in text:
        print(f"\n--- Found at Para {i}: {doc.paragraphs[i].text.strip()} ---")
        for j in range(i, min(i + 15, len(doc.paragraphs))):
            t = doc.paragraphs[j].text.strip()
            if t:
                print(f"  Para {j}: {t}")
