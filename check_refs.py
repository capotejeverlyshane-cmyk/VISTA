"""Extract all references with their full text and any URLs from the fixed document."""
from docx import Document
import re

doc = Document(r"VISTA_Chapter1_and_2_FIXED.docx")

print("=" * 100)
print("FULL REFERENCES - Text and URLs")
print("=" * 100)

refs = []
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if re.match(r'^\[\d+\]', text):
        refs.append((i, text))

for para_idx, text in refs:
    print(f"\n{'-' * 100}")
    print(f"[Para {para_idx}]")
    print(text)
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s\],]+', text)
    if urls:
        for url in urls:
            # Clean trailing punctuation
            url = url.rstrip('.')
            print(f"  URL: {url}")
    else:
        print("  (No URL found)")
