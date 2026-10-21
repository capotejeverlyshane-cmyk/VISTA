"""
Apply RRL edit: Insert low-resource language dataset gap paragraph
after "...or code-switching." in the research gap section.
"""
import copy
from docx import Document

DOCX_PATH = r"VISTA_Chapter1_and_2_FINAL.docx"

# The sentence fragment we're looking for
TARGET_PHRASE = "or code-switching."

# The new text to insert as a NEW paragraph right after the one containing the target
NEW_TEXT = (
    "Moreover, Filipino and Cebuano are classified as low-resource languages in NLP research, "
    "meaning there is a critical scarcity of publicly available, labeled datasets for tasks such "
    "as intent classification and text categorization in these languages [16]. This absence is "
    "even more pronounced in the government services domain, where no pre-built training corpus "
    "exists for Philippine LGU citizen inquiries — forcing system developers to construct their "
    "own datasets from primary documents such as the Citizen's Charter."
)

def main():
    doc = Document(DOCX_PATH)
    
    # Find the paragraph that contains the target phrase
    target_para_idx = None
    for i, para in enumerate(doc.paragraphs):
        if TARGET_PHRASE in para.text:
            target_para_idx = i
            print(f"[FOUND] Target phrase in paragraph {i}:")
            print(f"  \"{para.text[:120]}...\"")
            break
    
    if target_para_idx is None:
        print("[ERROR] Could not find the target phrase in the document!")
        print(f"  Looking for: '{TARGET_PHRASE}'")
        return

    # Strategy: We need to split the paragraph at "or code-switching."
    # and insert the new sentence WITHIN the same paragraph (not as a new paragraph)
    # because the research gap section is one continuous paragraph.
    
    target_para = doc.paragraphs[target_para_idx]
    
    # Check if the target phrase ends a sentence within a larger paragraph
    full_text = target_para.text
    split_point = full_text.find(TARGET_PHRASE)
    
    if split_point == -1:
        print("[ERROR] Could not find split point!")
        return
    
    end_of_target = split_point + len(TARGET_PHRASE)
    
    # Text before and after the insertion point
    text_before = full_text[:end_of_target]
    text_after = full_text[end_of_target:]
    
    print(f"\n[INFO] Text BEFORE insertion point ends with:")
    print(f"  ...{text_before[-80:]}")
    print(f"\n[INFO] Text AFTER insertion point starts with:")
    print(f"  {text_after[:80]}...")
    
    # Preserve the formatting of the first run
    if target_para.runs:
        reference_run = target_para.runs[0]
        font_name = reference_run.font.name
        font_size = reference_run.font.size
        font_bold = reference_run.font.bold
        font_italic = reference_run.font.italic
        print(f"\n[INFO] Reference formatting: font={font_name}, size={font_size}, bold={font_bold}")
    else:
        font_name = None
        font_size = None
        font_bold = None
        font_italic = None
    
    # Clear all existing runs
    for run in target_para.runs:
        run.text = ""
    
    # If there were runs, set the first one to the combined text
    if target_para.runs:
        target_para.runs[0].text = text_before + " " + NEW_TEXT + text_after
        # Ensure formatting is preserved
        if font_name:
            target_para.runs[0].font.name = font_name
        if font_size:
            target_para.runs[0].font.size = font_size
        target_para.runs[0].font.bold = font_bold
        target_para.runs[0].font.italic = font_italic
    else:
        run = target_para.add_run(text_before + " " + NEW_TEXT + text_after)
        if font_name:
            run.font.name = font_name
        if font_size:
            run.font.size = font_size

    print(f"\n[SUCCESS] Inserted low-resource language dataset gap text.")
    
    # Save
    output_path = "VISTA_Chapter1_and_2_FINAL_UPDATED.docx"
    doc.save(output_path)
    print(f"[SAVED] {DOCX_PATH}")

if __name__ == "__main__":
    main()
