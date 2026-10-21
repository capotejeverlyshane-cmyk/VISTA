"""Convert VISTA_Final_Document.md to a formatted .docx following capstone guidelines."""
import re, os
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# --- Page Setup: Left 1.5", Top/Right/Bottom 1" ---
for section in doc.sections:
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1.5)
    section.right_margin = Inches(1)

# --- Default style: Arial 12pt, 1.5 spacing, justified ---
style = doc.styles['Normal']
font = style.font
font.name = 'Arial'
font.size = Pt(12)
pf = style.paragraph_format
pf.line_spacing = 1.5
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pf.first_line_indent = Inches(0.5)
pf.space_after = Pt(0)
pf.space_before = Pt(0)

def set_font(run, size=12, bold=False, name='Arial'):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold

def add_heading_centered(text, size=14, bold=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text.upper())
    set_font(r, size, bold)

def add_heading_left(text, size=12, bold=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_font(r, size, bold)

def add_body(text):
    p = doc.add_paragraph()
    # Handle bold markers **text**
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            r = p.add_run(part[2:-2])
            set_font(r, 12, True)
        else:
            r = p.add_run(part)
            set_font(r, 12, False)

def add_numbered(num, text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.left_indent = Inches(0.5)
    parts = re.split(r'(\*\*[^*]+\*\*)', text)
    r = p.add_run(f"{num}. ")
    set_font(r, 12, False)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            r = p.add_run(part[2:-2])
            set_font(r, 12, True)
        else:
            r = p.add_run(part)
            set_font(r, 12, False)

def add_figure_caption(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run(text)
    set_font(r, 12, True)

def add_image(img_path, caption, width=5.5):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        r = p.add_run()
        r.add_picture(img_path, width=Inches(width))
        add_figure_caption(caption)
    else:
        add_figure_caption(f"{caption} [Image file not found: {img_path}]")

def add_table(headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_font(r, 10, True)
        # Shade header
        shading = cell._element.get_or_add_tcPr()
        bg = shading.makeelement(qn('w:shd'), {qn('w:fill'): '2F5597', qn('w:val'): 'clear'})
        shading.append(bg)
        r.font.color.rgb = RGBColor(255, 255, 255)
    # Data rows
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ''
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val))
            set_font(r, 10, False)
    doc.add_paragraph()  # spacing after table

# ============================================================
# COVER PAGE
# ============================================================
for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Inches(0)
r = p.add_run("VISTA: AN NLP-BASED CHATBOT FOR CITIZEN INQUIRY\nAND LOCAL GOVERNMENT SERVICES")
set_font(r, 16, True)

doc.add_paragraph()

for line in ["DAVAO DEL NORTE STATE COLLEGE", "Institute of Computing", "New Visayas, Panabo City"]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    r = p.add_run(line)
    set_font(r, 12, False)

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Inches(0)
r = p.add_run("A Capstone Project Presented by:")
set_font(r, 12, False)

doc.add_paragraph()

for name in ["JEVERLY SHANE B. CAPOTE", "HONEY MARIEL S. CORPUZ", "AXL BIEN MEÑOZA"]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    r = p.add_run(name)
    set_font(r, 12, True)

for _ in range(2):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.first_line_indent = Inches(0)
r = p.add_run("MAY 2026")
set_font(r, 12, True)

doc.add_page_break()

# ============================================================
# READ MARKDOWN AND PARSE
# ============================================================
with open("VISTA_Final_Document.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Clean up - skip the cover page section in MD (first ~17 lines)
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == "# CHAPTER 1":
        break
    i += 1

# Process from Chapter 1 onward
md_text = "".join(lines[i:])

# Split into sections and process
current_lines = md_text.split('\n')

fig_counter = 0
table_counter = 0
in_table = False
table_headers = []
table_rows = []
in_json = False
json_lines = []
skip_figure_refs = False

j = 0
while j < len(current_lines):
    line = current_lines[j]
    stripped = line.strip()
    
    # Skip empty lines
    if not stripped:
        j += 1
        continue
    
    # Skip markdown HRs
    if stripped == '---':
        if j > 5:  # Not the first HR
            doc.add_page_break()
        j += 1
        continue
    
    # Skip lines that are just image/figure references we handle separately
    if stripped.startswith('*(Please refer to'):
        j += 1
        continue

    # JSON code block
    if stripped.startswith('```json'):
        in_json = True
        json_lines = []
        j += 1
        continue
    if stripped == '```' and in_json:
        in_json = False
        # Add JSON as formatted text
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.left_indent = Inches(0.5)
        r = p.add_run('\n'.join(json_lines))
        r.font.name = 'Consolas'
        r.font.size = Pt(9)
        j += 1
        continue
    if in_json:
        json_lines.append(stripped)
        j += 1
        continue
    
    # Table detection
    if '|' in stripped and stripped.startswith('|'):
        cells = [c.strip() for c in stripped.split('|')[1:-1]]
        # Check if separator row
        if all(re.match(r'^:?-+:?$', c) for c in cells):
            j += 1
            continue
        if not in_table:
            in_table = True
            table_headers = cells
            table_rows = []
        else:
            table_rows.append(cells)
        j += 1
        continue
    elif in_table:
        # End of table
        # Clean bold markers from cells
        clean_h = [re.sub(r'\*\*([^*]+)\*\*', r'\1', h) for h in table_headers]
        clean_r = [[re.sub(r'\*\*([^*]+)\*\*', r'\1', c) for c in row] for row in table_rows]
        add_table(clean_h, clean_r)
        in_table = False
        table_headers = []
        table_rows = []
        # Don't increment - process current line
        continue
    
    # H1 headings (# CHAPTER...)
    if stripped.startswith('# ') and not stripped.startswith('## '):
        text = stripped[2:].strip()
        add_heading_centered(text, 14, True)
        j += 1
        continue
    
    # H2 headings (## Section)
    if stripped.startswith('## ') and not stripped.startswith('### '):
        text = stripped[3:].strip()
        add_heading_left(text, 12, True)
        j += 1
        continue
    
    # H3 headings (### Subsection)
    if stripped.startswith('### '):
        text = stripped[4:].strip()
        add_heading_left(text, 12, True)
        j += 1
        continue
    
    # H4 headings (#### Sub-subsection)
    if stripped.startswith('#### '):
        text = stripped[5:].strip()
        add_heading_left(text, 12, True)
        j += 1
        continue

    # Figure captions (*Figure X.*)
    if stripped.startswith('*Figure ') and stripped.endswith('*'):
        fig_text = stripped[1:-1]
        fig_counter += 1
        # Try to find matching image
        img_map = {
            'PADIM': 'vista_padim.png',
            'Team': 'vista_team_org.png',
            'WBS': 'vista_wbs.png', 
            'Work Breakdown': 'vista_wbs.png',
            'Gantt': 'vista_gantt.png',
            'System Architecture': 'vista_system_architecture.png',
            'Use Case': 'vista_use_case.png',
            'Context Flow': 'vista_dfd_level0.png',
            'Level 0': 'vista_dfd_level0.png',
            'Level 1': 'vista_dfd_level1.png',
            'ERD': 'vista_erd.png',
            'Entity Relationship': 'vista_erd.png',
            'Problem Tree': 'vista_problem_tree.png',
            'Objective Tree': 'vista_objective_tree.png',
        }
        img_file = None
        for key, val in img_map.items():
            if key.lower() in fig_text.lower():
                img_file = val
                break
        if img_file:
            add_image(img_file, fig_text)
        else:
            add_figure_caption(fig_text)
        j += 1
        continue
    
    # Numbered list items
    m = re.match(r'^(\d+)\.\s+(.+)', stripped)
    if m:
        add_numbered(m.group(1), m.group(2))
        j += 1
        continue
    
    # Bullet definitions (- **Term**: Definition)
    if stripped.startswith('- '):
        text = stripped[2:]
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.left_indent = Inches(0.5)
        parts = re.split(r'(\*\*[^*]+\*\*)', text)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                r = p.add_run(part[2:-2])
                set_font(r, 12, True)
            else:
                r = p.add_run(part)
                set_font(r, 12, False)
        j += 1
        continue
    
    # References [X]
    if re.match(r'^\[\d+\]', stripped):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)
        # Clean italic markers
        text = re.sub(r'\*([^*]+)\*', r'\1', stripped)
        r = p.add_run(text)
        set_font(r, 12, False)
        j += 1
        continue
    
    # Regular paragraph
    if stripped.startswith('&nbsp;'):
        doc.add_paragraph()
        j += 1
        continue
        
    add_body(stripped)
    j += 1

# Flush any remaining table
if in_table:
    clean_h = [re.sub(r'\*\*([^*]+)\*\*', r'\1', h) for h in table_headers]
    clean_r = [[re.sub(r'\*\*([^*]+)\*\*', r'\1', c) for c in row] for row in table_rows]
    add_table(clean_h, clean_r)

# Save
output = "VISTA_Chapter1_and_2_FINAL.docx"
doc.save(output)
print(f"Successfully saved: {output}")
print(f"File size: {os.path.getsize(output):,} bytes")
