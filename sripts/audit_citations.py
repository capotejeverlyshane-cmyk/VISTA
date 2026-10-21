"""
Audit all citations [N] in the document to find gaps and ordering issues.
"""
import re
from docx import Document

DOCX_PATH = r"VISTA_Chapter1_and_2_FINAL_UPDATED.docx"

def main():
    doc = Document(DOCX_PATH)
    
    all_citations = []  # (para_index, citation_number, context_snippet)
    
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if not text:
            continue
        
        # Find all [N] patterns
        matches = re.finditer(r'\[(\d+)\]', text)
        for m in matches:
            cite_num = int(m.group(1))
            # Get surrounding context
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            snippet = text[start:end]
            all_citations.append((i, cite_num, snippet))
    
    print("=" * 80)
    print("FULL CITATION AUDIT")
    print("=" * 80)
    
    # Print all citations in order of appearance
    print("\n--- All citations in order of appearance ---")
    for para_idx, cite_num, snippet in all_citations:
        print(f"  Para {para_idx:3d} | [{cite_num:2d}] | ...{snippet}...")
    
    # Find unique citation numbers used
    used_nums = sorted(set(c[1] for c in all_citations))
    print(f"\n--- Unique citation numbers used: {used_nums}")
    print(f"--- Total unique: {len(used_nums)}")
    
    # Check for gaps
    if used_nums:
        expected = list(range(1, max(used_nums) + 1))
        missing = [n for n in expected if n not in used_nums]
        if missing:
            print(f"\n[WARNING] Missing citation numbers (gaps): {missing}")
        else:
            print(f"\n[OK] No gaps in citation numbering.")
    
    # Also print the References section if found
    print("\n" + "=" * 80)
    print("REFERENCES SECTION")
    print("=" * 80)
    in_references = False
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if "References" in text and len(text) < 30:
            in_references = True
            print(f"\n[Found References header at para {i}]")
            continue
        if in_references and text:
            print(f"  Para {i}: {text[:150]}")

if __name__ == "__main__":
    main()
