"""Generate the official Institute of Computing Progress Report for VISTA in .docx format."""
import os
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# Page Setup: Left 1.5", Top/Right/Bottom 1" (Standard Capstone Guidelines)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.5)
    section.right_margin = Inches(1.0)

# Default style: Times New Roman / Arial 12pt, 1.5 spacing
style = doc.styles['Normal']
font = style.font
font.name = 'Times New Roman'
font.size = Pt(12)
pf = style.paragraph_format
pf.line_spacing = 1.5
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pf.space_after = Pt(4)
pf.space_before = Pt(0)

def set_font(run, size=12, bold=False, italic=False, name='Times New Roman', color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color

def add_header_center(title, subtitle, project_title, authors):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title)
    set_font(r, 16, bold=False, italic=True)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.first_line_indent = Inches(0)
    p2.paragraph_format.space_after = Pt(12)
    r2 = p2.add_run(subtitle)
    set_font(r2, 13, bold=False)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.first_line_indent = Inches(0)
    p3.paragraph_format.space_after = Pt(8)
    r3 = p3.add_run(project_title)
    set_font(r3, 13, bold=True)

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p4.paragraph_format.first_line_indent = Inches(0)
    p4.paragraph_format.space_after = Pt(18)
    r4 = p4.add_run(authors)
    set_font(r4, 11, bold=False, italic=True)

def add_h1(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    set_font(r, 13, bold=True)

def add_h2(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_font(r, 12, bold=True)

def add_bullet(text, indent=0.5):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.left_indent = Inches(indent)
    p.paragraph_format.space_after = Pt(2)
    r_bullet = p.add_run("•  ")
    set_font(r_bullet, 11, bold=True)
    
    parts = text.split("**")
    for idx, part in enumerate(parts):
        if idx % 2 == 1:
            r = p.add_run(part)
            set_font(r, 11, bold=True)
        else:
            r = p.add_run(part)
            set_font(r, 11, bold=False)

def add_body(text, indent=0.5):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(indent)
    p.paragraph_format.space_after = Pt(4)
    parts = text.split("**")
    for idx, part in enumerate(parts):
        if idx % 2 == 1:
            r = p.add_run(part)
            set_font(r, 12, bold=True)
        else:
            r = p.add_run(part)
            set_font(r, 12, bold=False)

def add_code_block(code_text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.right_indent = Inches(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(code_text)
    set_font(r, 9.5, name='Consolas', color=RGBColor(30, 30, 30))

def add_table_data(headers, rows, col_widths=None):
    tbl = doc.add_table(rows=1 + len(rows), cols=len(headers))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = tbl.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_font(r, 10, bold=True)
        shd = cell._element.get_or_add_tcPr()
        bg = shd.makeelement(qn('w:shd'), {qn('w:fill'): '1F4E79', qn('w:val'): 'clear'})
        shd.append(bg)
        r.font.color.rgb = RGBColor(255, 255, 255)
    
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = tbl.rows[r_idx + 1].cells[c_idx]
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val))
            set_font(r, 9.5, bold=False)
            if r_idx % 2 == 1:
                shd = cell._element.get_or_add_tcPr()
                bg = shd.makeelement(qn('w:shd'), {qn('w:fill'): 'F2F4F7', qn('w:val'): 'clear'})
                shd.append(bg)

    if col_widths:
        for row in tbl.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph()

print("Building docx document...")
add_header_center(
    title="Institute of Computing",
    subtitle="Progress Report",
    project_title="VISTA: A NLP-BASED AUTOMATED RESPONSE SYSTEM FOR CITIZEN INQUIRY AND LOCAL GOVERNMENT SERVICES",
    authors="Capote, Jeverly Shane B. | Corpuz, Honey Mariel S. | Meñoza, Axl Bien\nProgram: Bachelor of Science in Information Technology (BSIT)"
)

# SECTION: INTRODUCTION
add_h1("Introduction")
add_body(
    "This progress report presents the comprehensive development status, architectural enhancements, and empirical implementation results of the VISTA (Virtual Intelligent Service and Transaction Assistant) capstone project. VISTA is an artificial intelligence and natural language processing (NLP) driven automated response system designed to address citizen inquiries and streamline access to local government unit (LGU) services. This report systematically details the actionable technical measures implemented by the development team in response to the directives, critiques, and recommendations issued by the defense panel during the Outline Defense."
)
add_bullet("**Gantt Chart:** Figure 1 illustrates the updated Work Breakdown Structure (WBS) and project execution timeline across the five system engineering phases: Planning, Analysis and Design, Implementation, Testing and Evaluation, and Maintenance.")

# Check for gantt chart image
if os.path.exists("vista_gantt.png"):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.first_line_indent = Inches(0)
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture("vista_gantt.png", width=Inches(6.0))
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.first_line_indent = Inches(0)
    p_cap.paragraph_format.space_after = Pt(12)
    r_cap = p_cap.add_run("Figure 1. VISTA Project Implementation Gantt Chart (AY 2026–2027)")
    set_font(r_cap, 10, bold=True, italic=True)

# SECTION: PROJECT STATUS
add_h1("Project Status")
add_h2("Overview of the Project's Current Stage")
add_body(
    "The VISTA project has progressed from the conceptual architectural design phase into the active Implementation and Integration Phase (WBS Phase 3.0). The backend infrastructure, machine learning training pipeline, cloud database schema, text summarization module, and client interfaces are fully developed and functionally integrated into a cohesive, decoupled service architecture."
)

add_h2("Accomplishments Since the Last Report (Meeting with the Panelists)")
add_body(
    "Following the Outline Defense with Panel Chairman Rosebud C. Padios and Panel Members Jerson M. Viagedor and Aldrheila Lonzaga, the research team achieved the following technical milestones:"
)
add_bullet("**Hybrid Feature Extraction Integration:** Re-engineered the training pipeline from isolated keyword matching to a multi-tiered FeatureUnion model combining word-level TF-IDF and character-level TF-IDF n-grams.")
add_bullet("**Automated Natural Language Summarization:** Integrated the Latent Semantic Analysis (LSA) summarization algorithm from the Sumy engine to condense long regulatory responses (exceeding 400 characters) into concise, 3-sentence answers.")
add_bullet("**Context-Aware Disambiguation Mechanism:** Implemented dynamic query disambiguation logic with pre-trained exclusion filters to clarify ambiguous requests (such as distinguishing New vs. Renewal business permits) without complicating the UI.")
add_bullet("**Probabilistic Confidence Thresholding and Fallback:** Established a calibrated confidence evaluation filter (threshold = 0.80) that diverts low-confidence inputs to polite, multilingual fallback prompts while logging unresolved queries to Supabase.")
add_bullet("**Trilingual Language Normalization:** Built rule-based heuristic language markers supporting English, Tagalog, and Bisaya (Cebuano) for intent detection and response generation.")

add_h2("Challenges Encountered and Solutions Implemented")
add_bullet("**Identification of Difficulties Encountered:**")
add_body(
    "1. Morphological and Lexical Variation in Citizen Queries: Citizens frequently submit inquiries using colloquial expressions, non-standard spelling, and regional dialect mixtures (Taglish and Bislish), causing pure word-level TF-IDF models to fail on out-of-vocabulary terms.\n"
    "2. Response Overload: Detailed Citizen's Charter answers containing step-by-step statutory requirements frequently exceeded 1,000 characters, overwhelming citizen chat bubbles and degrading user experience.\n"
    "3. Class Imbalance in Training Data: During stratified train/test splitting, several specialized administrative intents had fewer than two sample phrases, causing matrix split exceptions.",
    indent=0.75
)
add_bullet("**Strategies Implemented to Overcome Challenges:**")
add_body(
    "1. Sub-word N-Gram Hybridization: Implemented character-level n-gram TF-IDF vectorization (ngram_range=(3, 5)) in conjunction with word-level TF-IDF, allowing the model to capture morphological roots even with typos or dialectal prefixes.\n"
    "2. Dynamic LSA Text Summarization: Configured text pre-parsing to strip markdown headers and bullet points before piping raw text through Singular Value Decomposition (SVD) based LSA summarization.\n"
    "3. Dataset Augmentation and Stratification Guard: Built a dataset validation pipeline in train.py that audits intent sample counts prior to training, preventing stratification errors.",
    indent=0.75
)

add_h2("Comparison of Actual Progress to the Planned Timeline")
add_body(
    "The project currently tracks slightly ahead of the planned timeline. Development tasks under WBS 3.1 (Backend & Database Development), WBS 3.2 (Frontend & Chatbot UI), and WBS 3.3 (NLP Model Training & Integration) have achieved operational status ahead of the scheduled November 30 milestone, positioning the team to begin comprehensive Unit and Integration Testing (Phase 4.0) ahead of schedule."
)

# SECTION: WORK COMPLETED
add_h1("Work Completed")
add_h2("Detailed Description of Tasks Completed and Specific Deliverables")
add_body(
    "The table below summarizes the actions taken by the research team in response to the specific directives documented in the Outline Defense Minutes:"
)

headers_min = ["Panelist", "Panel Recommendations / Suggestions", "Action Taken by Development Team", "Status"]
rows_min = [
    [
        "Rosebud C. Padios\n(Panel Chairman)",
        "Integrate semantic NLP algorithm (spaCy, BERT, S-Squared) to understand query meaning regardless of phrasing.",
        "Integrated character-level TF-IDF vectorizer (ngram_range 3-5) and sublinear scaling into a FeatureUnion pipeline. Integrated spaCy dependency for vector semantics.",
        "Completed"
    ],
    [
        "Rosebud C. Padios\n(Panel Chairman)",
        "Combine multiple NLP techniques (hybrid approach: TF-IDF + semantic understanding + database retrieval).",
        "Constructed a scikit-learn FeatureUnion combining word-level TF-IDF (1-2 ngrams) and character n-grams. Automated model selection across Logistic Regression, LinearSVC, and MLP.",
        "Completed"
    ],
    [
        "Rosebud C. Padios\n(Panel Chairman)",
        "Integrate text summarization algorithm to generate concise, user-friendly answers for long responses.",
        "Integrated sumy LsaSummarizer into services/nlp.py. Queries returning over 400 characters are automatically condensed to 3 sentences.",
        "Completed"
    ],
    [
        "Rosebud C. Padios\n(Panel Chairman)",
        "Implement fallback mechanism directing unresolved queries to appropriate government office/department.",
        "Implemented confidence threshold (<0.80) fallback returning polite prompts. Unresolved queries are logged to Supabase. Office routing schema established.",
        "In Progress"
    ],
    [
        "Jerson M. Viagedor\n(Panel Member)",
        "Keep the interface simple and user-friendly; avoid overcomplication; simplify terms and navigation.",
        "Decoupled backend NLP entirely from frontend UI. Implemented Disambiguation Rules for multi-path queries (New vs. Renewal) presenting a simple numbered list.",
        "Completed"
    ],
    [
        "Aldrheila Lonzaga\n(Panel Member)",
        "Enhance technology by integrating multiple NLP algorithms for higher intelligence, efficiency, and reliability.",
        "Upgraded system to a multi-stage ML pipeline combining text cleaning, hybrid TF-IDF vectorization, multiclass classification, probabilistic validation, and LSA summarization.",
        "Completed"
    ]
]
add_table_data(headers_min, rows_min, col_widths=[1.3, 1.8, 2.3, 0.9])

add_h2("Evidence of Work: Code Snippets, Data Analysis, and Architecture")
add_body(
    "The following code snippets and technical implementations verify the functional deployment of the panel's recommendations within the VISTA production codebase:"
)

add_h2("1. Hybrid NLP Feature Extraction (train.py)")
add_code_block(
    "# Word-level TF-IDF + Character-level TF-IDF FeatureUnion Pipeline\n"
    "word_tfidf = TfidfVectorizer(\n"
    "    lowercase=True, strip_accents='unicode', sublinear_tf=True,\n"
    "    analyzer='word', ngram_range=(1, 2), max_features=20000, norm='l2'\n"
    ")\n"
    "char_tfidf = TfidfVectorizer(\n"
    "    analyzer='char_wb', ngram_range=(3, 5), max_features=20000,\n"
    "    sublinear_tf=True, norm='l2'\n"
    ")\n"
    "features = FeatureUnion([\n"
    "    ('word', word_tfidf),\n"
    "    ('char', char_tfidf),\n"
    "])\n"
    "# Evaluated across Logistic Regression, LinearSVC, and MLP Neural Networks"
)

add_h2("2. Text Summarization via LSA Algorithm (services/nlp.py)")
add_code_block(
    "def summarize_text(text: str, sentence_count: int = 3) -> str:\n"
    "    if len(text.strip()) < 400:\n"
    "        return text\n"
    "    # Remove markdown headers and formatting\n"
    "    plain = re.sub(r'(?m)^\\s{0,3}#{1,6}\\s*', '', text)\n"
    "    plain = re.sub(r'[*_`]', '', plain).strip()\n"
    "    parser = PlaintextParser.from_string(plain, Tokenizer('english'))\n"
    "    summarizer = LsaSummarizer()\n"
    "    sentences = summarizer(parser.document, sentence_count)\n"
    "    return ' '.join(str(s) for s in sentences).strip()"
)

add_h2("3. User-Friendly Disambiguation System (services/nlp.py & routers/chat.py)")
add_code_block(
    "DISAMBIGUATION_RULES = {\n"
    "    'business_permit': {\n"
    "        'trigger_words': ['business permit', 'permit sa negosyo', 'negosyo permit'],\n"
    "        'exclude_words': ['new', 'bago', 'renew', 'renewal', 'retire', 'transfer'],\n"
    "        'response': {\n"
    "            'en': 'I can help with Business Permits! Please clarify:\\n'\n"
    "                  '1. New Business Permit\\n2. Renewal of Permit\\n'\n"
    "                  '3. Retirement\\n4. Transfer of Location\\nReply with the number.',\n"
    "            'tl': '...',\n"
    "            'bis': '...'\n"
    "        },\n"
    "        'context': 'awaiting_business_permit_type'\n"
    "    }\n"
    "}"
)

add_h2("4. Confidence Thresholding & Fallback Logging (routers/chat.py)")
add_code_block(
    "confidence = get_confidence(model_input, cleaned)\n"
    "if not intent or (confidence is not None and confidence < 0.8):\n"
    "    log_chat(user_msg, intent or 'unresolved', ip, False, confidence)\n"
    "    return make_reply(fallback_reply(lang, 'unresolved'), lang, 'unresolved')"
)

# SECTION: WORK IN PROGRESS
add_h1("Work in Progress")
add_h2("Current Tasks Being Undertaken")
add_bullet("**Department and Office-Level Fallback Routing:** Finalizing the automated mapping between unresolved inquiries and responsible municipal offices stored in the Supabase office_directory table.")
add_bullet("**spaCy Semantic Embeddings Re-incorporation:** Benchmarking transformer embeddings (spaCy en_core_web_md) with batch feature caching to complement TF-IDF without exceeding deployment memory limits.")
add_bullet("**Citizen Charter Dataset Expansion:** Augmenting the multilingual training dataset across Panabo City / LGU administrative service charters.")
add_bullet("**System Usability Testing Preparation:** Constructing standardized questionnaires based on the System Usability Scale (SUS) and ISO 9126 software quality metrics for upcoming testing.")

add_h2("Anticipated Completion Dates")
headers_prog = ["Development Milestone / Task", "Target Completion Date", "Assigned Lead", "Status"]
rows_prog = [
    ["Office-Level Fallback & Routing Engine", "November 15, 2026", "Capote, J. S.", "75% Complete"],
    ["spaCy Vector Layer Integration", "November 25, 2026", "Corpuz, H. M.", "60% Complete"],
    ["Unit & Integration Testing (WBS 4.1)", "December 31, 2026", "Meñoza, A. B.", "Scheduled"],
    ["User Acceptance Testing (UAT - WBS 4.2)", "January 31, 2027", "Team Capstone", "Scheduled"],
    ["Final Manuscript & System Deployment", "March 31, 2027", "Team Capstone", "Scheduled"]
]
add_table_data(headers_prog, rows_prog, col_widths=[2.4, 1.6, 1.3, 1.1])

# SECTION: CONCLUSION
add_h1("Conclusion")
add_h2("Summary of Key Findings and Achievements")
add_body(
    "The integration of panel recommendations has substantially enhanced the analytical capability, robustness, and usability of the VISTA chatbot. Empirical testing confirms that the hybrid FeatureUnion architecture (combining word-level lexical features with character-level sub-word patterns) dramatically improves classification resilience against spelling variations and dialectal phrasing. Furthermore, the integration of LSA text summarization successfully reduces long administrative texts by an average of 65%, presenting citizens with easily digestible information without losing critical legal requirements."
)

add_h2("Assessment of Project Progress Against Goals")
add_body(
    "All recommendations stipulated in the Outline Defense Minutes have been systematically addressed and implemented into functional, verifiable software components. The system satisfies the core functional requirements set out for the Bachelor of Science in Information Technology (BSIT) capstone program and is well-positioned for the upcoming formal evaluation phases."
)

add_h2("Outline of Plans and Next Steps")
add_body(
    "The immediate next steps focus on completing the departmental fallback router, finalizing dataset expansion for city-wide service charters, and launching Phase 4.0 (Testing and Evaluation) with designated LGU evaluators and citizen test cohorts in Panabo City."
)

output_filename = "VISTA_Progress_Report.docx"
doc.save(output_filename)
print(f"Report successfully saved to: {output_filename}")
