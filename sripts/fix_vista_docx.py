"""
Apply all fixes from analysis_results.md to VISTA_Chapter1_and_2_REVISED_AY25-26.docx

Fixes:
  1-11: Replace default/template text with VISTA-specific content
  12-14: Add missing sections (Conceptual Framework, Security Plan, Maintenance Plan)
  15:    Update "500 questions" references
"""

import copy
import shutil
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

SRC = "VISTA_Chapter1_and_2_REVISED_AY25-26.docx"
BACKUP = "VISTA_Chapter1_and_2_REVISED_AY25-26_BACKUP.docx"
OUT = "VISTA_Chapter1_and_2_REVISED_AY25-26_FIXED.docx"

# --- helpers ---

def clear_paragraph(para):
    """Remove all runs from a paragraph, keeping the paragraph's style."""
    for run in para.runs:
        run.text = ""
    # If the paragraph has no runs, make sure we clear _p text too
    if not para.runs:
        para.text = ""


def set_paragraph_text(para, new_text):
    """Replace ALL text in a paragraph while preserving the paragraph style
    and the formatting of the first run (font name, size, bold, italic)."""
    if para.runs:
        # Store first run's formatting
        first_run = para.runs[0]
        font_name = first_run.font.name
        font_size = first_run.font.size
        bold = first_run.font.bold
        italic = first_run.font.italic

        # Clear all runs
        for run in para.runs:
            run.text = ""
        # Set new text on first run
        para.runs[0].text = new_text
        para.runs[0].font.name = font_name
        para.runs[0].font.size = font_size
        para.runs[0].font.bold = bold
        para.runs[0].font.italic = italic
    else:
        para.text = new_text


def insert_paragraph_after(para, text, style=None):
    """Insert a new paragraph immediately after the given paragraph."""
    new_p = copy.deepcopy(para._element)
    # Clear the copied element
    for child in list(new_p):
        new_p.remove(child)
    para._element.addnext(new_p)
    new_para = type(para)(new_p, para._parent)
    new_para.text = text
    if style:
        new_para.style = style
    return new_para


def add_paragraphs_after(doc, after_index, texts_and_styles):
    """Insert multiple paragraphs after a given paragraph index.
    texts_and_styles: list of (text, style_name_or_None)
    Returns the last inserted paragraph.
    """
    anchor = doc.paragraphs[after_index]
    last = anchor
    for text, style_name in texts_and_styles:
        new_p = copy.deepcopy(anchor._element)
        for child in list(new_p):
            new_p.remove(child)
        last._element.addnext(new_p)
        from docx.text.paragraph import Paragraph
        new_para = Paragraph(new_p, doc)
        new_para.text = text
        if style_name:
            try:
                new_para.style = doc.styles[style_name]
            except KeyError:
                pass  # style not found, use default
        last = new_para
    return last


# --- main ---

def main():
    # backup
    shutil.copy(SRC, BACKUP)
    print(f"Backup created: {BACKUP}")

    doc = Document(SRC)
    paras = doc.paragraphs

    # =========================================================================
    # FIX 1: Definition of Terms (Paragraph 70) — replace guideline instruction
    # =========================================================================
    print("Fix 1: Definition of Terms (P70)")
    set_paragraph_text(paras[70],
        "The following terms are defined operationally as they are used in this study:")

    # Insert definition terms AFTER paragraph 70
    definitions = [
        ("Cebuano/Bisaya \u2013 A Visayan language widely spoken in Panabo City, Davao del Norte, used as one of three supported input languages in the VISTA chatbot.", None),
        ("Citizen\u2019s Charter \u2013 A standardized document mandated by Republic Act No. 11032, listing the services, requirements, processing times, and fees of government frontline offices, serving as the primary data source for VISTA\u2019s knowledge base.", None),
        ("Confidence Threshold \u2013 The minimum probability score (set at 60%) that the machine learning classifier must produce for a predicted intent before the system considers the classification valid and returns a response.", None),
        ("Controlled Retraining \u2013 A supervised learning mechanism in VISTA where new training data is incorporated into the machine learning model only after explicit validation and approval by the LGU Administrator.", None),
        ("Feature Extraction \u2013 The process of converting raw text input into numerical representations (TF-IDF vectors) that can be processed by machine learning algorithms.", None),
        ("Intent \u2013 A predefined category representing a specific citizen service inquiry (e.g., \u201cbusiness_permit_fee\u201d, \u201cbirth_certificate_process\u201d) used by the classifier to route queries to the correct knowledge base response.", None),
        ("Knowledge Base \u2013 The structured repository of validated question-answer pairs organized by intent category and office, sourced from the Citizen\u2019s Charter.", None),
        ("Logistic Regression (LR) \u2013 A probabilistic supervised machine learning algorithm used in VISTA as one of three classifiers for intent prediction.", None),
        ("Multilayer Perceptron (MLP) \u2013 A type of artificial neural network with one or more hidden layers, used in VISTA as one of three classifiers for intent classification.", None),
        ("Natural Language Processing (NLP) \u2013 A branch of artificial intelligence concerned with enabling computers to understand, interpret, and generate human language text.", None),
        ("Support Vector Machine (SVM) \u2013 A supervised machine learning algorithm that finds the optimal hyperplane for classifying text into intent categories.", None),
        ("TF-IDF (Term Frequency\u2013Inverse Document Frequency) \u2013 A statistical measure used to evaluate the importance of a word in a document relative to a corpus, used by VISTA for feature extraction.", None),
        ("Unmatched Query \u2013 A citizen inquiry that the classifier fails to match to any intent with sufficient confidence, logged for administrator review and potential knowledge base expansion.", None),
    ]
    add_paragraphs_after(doc, 70, definitions)
    print("  -> Added 13 definition terms")

    # Re-read paragraphs since we inserted new ones -- indices shift by 13
    SHIFT1 = 13
    paras = doc.paragraphs

    # =========================================================================
    # FIX 2: System Architecture Intro (originally P99, now P99+SHIFT1 = P112)
    # =========================================================================
    idx = 99 + SHIFT1
    print(f"Fix 2: System Architecture intro (P{idx})")
    set_paragraph_text(paras[idx],
        "The system architecture of VISTA presents a structured framework that illustrates how the different components of the system interact to support real-time citizen inquiry classification, multilingual response retrieval, and administrative knowledge base management. The architecture is composed of three main tiers: Client Tier (Frontend Interface), Application Tier (Backend Server), and Data Tier.")

    # =========================================================================
    # FIX 3: System Planning Intro (originally P80, now P80+SHIFT1 = P93)
    # =========================================================================
    idx = 80 + SHIFT1
    print(f"Fix 3: System Planning intro (P{idx})")
    set_paragraph_text(paras[idx],
        "This section discusses the planning phase of the VISTA system development, including how the project team was organized, the identification of scope and objectives, and the breakdown and scheduling of development tasks aligned with the PADIM framework.")

    # =========================================================================
    # FIX 4: System Analysis Intro (originally P97, now P97+SHIFT1 = P110)
    # =========================================================================
    idx = 97 + SHIFT1
    print(f"Fix 4: System Analysis intro (P{idx})")
    set_paragraph_text(paras[idx],
        "This section presents the analysis phase of the VISTA system development. It covers the system architecture, functional and non-functional requirements, use case diagram, context flow diagram, and Level 1 data flow diagram.")

    # =========================================================================
    # FIX 5: Level 1 DFD Intro (originally P152, now P152+SHIFT1 = P165)
    # =========================================================================
    idx = 152 + SHIFT1
    print(f"Fix 5: Level 1 DFD intro (P{idx})")
    set_paragraph_text(paras[idx],
        "The Level 1 Data Flow Diagram decomposes the VISTA system into its constituent sub-processes, providing a more detailed view of how data flows between system modules. The external entities and data flows established in the Context Flow Diagram (Level 0 DFD) are retained and expanded upon in this diagram.")

    # =========================================================================
    # FIX 6: System Design Intro (originally P167, now P167+SHIFT1 = P180)
    # =========================================================================
    idx = 167 + SHIFT1
    print(f"Fix 6: System Design intro (P{idx})")
    set_paragraph_text(paras[idx],
        "This section presents the design phase of the VISTA system development, detailing the database structure through the Entity Relationship Diagram, JSON schema design, data dictionary, and the technologies, concepts, and theories used in developing the system.")

    # =========================================================================
    # FIX 7: ERD Intro (originally P169, now P169+SHIFT1 = P182)
    # =========================================================================
    idx = 169 + SHIFT1
    print(f"Fix 7: ERD intro (P{idx})")
    set_paragraph_text(paras[idx],
        "The Entity Relationship Diagram (ERD) defines the structure of the database for VISTA, showing how data entities are organized and related to one another.")

    # =========================================================================
    # FIX 8: JSON Schema Intro (originally P184, now P184+SHIFT1 = P197)
    # =========================================================================
    idx = 184 + SHIFT1
    print(f"Fix 8: JSON Schema intro (P{idx})")
    set_paragraph_text(paras[idx],
        "Although VISTA uses an SQL-based database (SQLite) as its primary data store, a JSON schema design is also utilized to represent key data components such as intent definitions, training phrases, and API request/response structures. The use of JSON Schema supports interoperability between different system components and external services.")

    # =========================================================================
    # FIX 9: System Dev & Testing Intro (originally P234-236, now +SHIFT1)
    # =========================================================================
    idx234 = 234 + SHIFT1
    idx235 = 235 + SHIFT1
    idx236 = 236 + SHIFT1
    print(f"Fix 9: System Dev & Testing intro (P{idx234}-P{idx236})")
    set_paragraph_text(paras[idx234],
        "This section presents the results of the machine learning model evaluation conducted during the development of VISTA. The evaluation compares the performance of the three candidate classification algorithms \u2014 Support Vector Machine (SVM), Logistic Regression, and Neural Network (Multilayer Perceptron) \u2014 using the custom-built intent classification dataset derived from the Panabo City Citizen\u2019s Charter.")
    # Clear the numbered list items (they are guideline instructions)
    set_paragraph_text(paras[idx235], "")
    set_paragraph_text(paras[idx236], "")

    # =========================================================================
    # FIX 10: Systems Test Plan & Implementation Intro (originally P250, now +SHIFT1)
    # =========================================================================
    idx = 250 + SHIFT1
    print(f"Fix 10: Test Plan intro (P{idx})")
    set_paragraph_text(paras[idx],
        "The following subsections describe the planned testing strategy and implementation approach for deploying VISTA in Panabo City Hall.")

    # =========================================================================
    # FIX 11: System Maintenance Intro (originally P256, now +SHIFT1)
    # =========================================================================
    idx = 256 + SHIFT1
    print(f"Fix 11: System Maintenance intro (P{idx})")
    set_paragraph_text(paras[idx],
        "The maintenance phase describes how the VISTA system will be supported and improved after initial deployment. Because the project has not yet reached this stage, the following plans are written in the future tense.")

    # =========================================================================
    # FIX 12: Add Conceptual Framework after System Architecture
    # (originally after P104, now after P104+SHIFT1 = P117)
    # =========================================================================
    anchor_idx = 104 + SHIFT1  # after the Data Tier paragraph
    print(f"Fix 12: Adding Conceptual Framework (after P{anchor_idx})")

    cf_paragraphs = [
        ("Conceptual Framework", "Heading 2"),
        ("The conceptual framework illustrates how the VISTA system receives citizen text inquiries, processes them through its NLP classification pipeline, and produces automated service responses and administrative analytics. Based on the requirements of Panabo City Hall\u2019s frontline offices and citizen users, the framework ensures that the system provides accurate multilingual inquiry handling, knowledge base management, and data-driven insights through a centralized web-based platform.", None),
        ("Figure XX. Conceptual Framework", None),
        ("Input", "Heading 3"),
        ("The input of the system includes raw natural language text submitted by citizens through the chatbot interface. Inquiries may be in English, Filipino/Tagalog, or Cebuano/Bisaya. The system also receives administrator inputs including knowledge base updates (new intents, edited responses), unmatched query resolutions, and retraining commands through the administrator dashboard. The initial knowledge base content is sourced from the Panabo City Citizen\u2019s Charter, covering five frontline offices: City Mayor\u2019s Office, City Civil Registrar\u2019s Office, City Treasurer\u2019s Office, City Assessor\u2019s Office, and the City Social Welfare and Development Office.", None),
        ("Process", "Heading 3"),
        ("The process begins when a citizen submits a text query through the chatbot interface. The backend server receives the raw text and passes it through the NLP classification pipeline, which consists of three stages: (1) the Text Preprocessor performs tokenization, lowercasing, and stop word removal to clean the raw input; (2) the TF-IDF Feature Extractor converts the cleaned text into numerical feature vectors; and (3) the Intent Classifier \u2014 using the best-performing model among SVM, Logistic Regression, and Neural Network (MLP) \u2014 predicts the most probable service intent. If the classification confidence exceeds the predefined threshold (60%), the system retrieves the corresponding validated response from the knowledge base. If the confidence falls below the threshold, the query is logged as an unmatched query for administrator review. Administrators can also manage the knowledge base, review unmatched queries, and trigger controlled model retraining through the admin dashboard.", None),
        ("Output", "Heading 3"),
        ("The output of the system is a web-based chatbot interface that delivers automated, validated responses to citizen inquiries in real time. The system also provides an administrator dashboard that displays inquiry analytics, including the most frequently asked service categories, peak inquiry periods, and unmatched query logs. Additional outputs include classification performance reports, exportable chat logs, and a continuously improving knowledge base through the controlled retraining mechanism.", None),
    ]
    add_paragraphs_after(doc, anchor_idx, cf_paragraphs)
    SHIFT2 = len(cf_paragraphs)
    print(f"  -> Added {SHIFT2} paragraphs for Conceptual Framework")

    # Total shift is now SHIFT1 + SHIFT2
    TOTAL_SHIFT = SHIFT1 + SHIFT2
    paras = doc.paragraphs

    # =========================================================================
    # FIX 13 & 14: Add Systems Security Plan & Systems Maintenance Plan
    # after the maintenance paragraph (originally P257, now +TOTAL_SHIFT)
    # =========================================================================
    maint_idx = 257 + TOTAL_SHIFT
    print(f"Fix 13-14: Adding Security & Maintenance Plans (after P{maint_idx})")

    sec_maint_paragraphs = [
        ("Systems Security Plan", "Heading 3"),
        ("The VISTA system will implement security measures to protect citizen inquiry data, knowledge base content, and administrator access. Authentication will be required before the administrator can access the dashboard and manage system functions such as knowledge base editing, unmatched query review, and model retraining. Administrator credentials will be protected through Firebase Authentication, which handles password hashing, session token management, and secure credential storage.", None),
        ("Access control will be applied to ensure that only authorized LGU administrators can manage knowledge base intents, view inquiry analytics, review unmatched queries, and trigger model retraining. The system will also protect stored data in the SQLite database, including citizen chat logs, intent definitions, training data, and unmatched query records.", None),
        ("The system will maintain data integrity by storing records properly and preventing unauthorized modification of important system information. Input sanitization will be implemented to prevent injection attacks on the backend API. Rate limiting will be applied to prevent API abuse. The system will also monitor login activity and failed login attempts to help identify possible security issues. These security measures will help ensure that VISTA remains reliable, protected, and suitable for handling citizen inquiries at Panabo City Hall.", None),
        ("Systems Maintenance Plan", "Heading 3"),
        ("The VISTA system will follow a structured maintenance plan to ensure continuous operation, accuracy, and reliability. Regular maintenance will include monthly reviews of the knowledge base to ensure alignment with the current Citizen\u2019s Charter, quarterly model retraining cycles incorporating accumulated administrator-validated queries, and weekly automated backups of the SQLite database to prevent data loss.", None),
        ("The administrator or system maintainer will also monitor classification accuracy trends through the analytics dashboard to determine when the model requires retraining. If a significant drop in accuracy is observed, or if new service categories are added by Panabo City Hall, the administrator will trigger the controlled retraining process to update the machine learning models.", None),
        ("Software maintenance will include updating the web application frontend, improving system functions based on user feedback, reviewing SQLite database records, fixing detected errors, and updating system documentation. The knowledge base responses, intent categories, and office directory information will also be reviewed regularly to ensure that the system remains aligned with actual Panabo City Hall services and processes. Through this maintenance plan, VISTA will continue to support accurate multilingual citizen inquiry classification, knowledge base management, and real-time chatbot response delivery.", None),
    ]
    add_paragraphs_after(doc, maint_idx, sec_maint_paragraphs)
    SHIFT3 = len(sec_maint_paragraphs)
    TOTAL_SHIFT += SHIFT3
    paras = doc.paragraphs
    print(f"  -> Added {SHIFT3} paragraphs for Security & Maintenance Plans")

    # =========================================================================
    # FIX 15: Update "500 questions" references
    # Paragraph 52 (Scope), Paragraph 53 (retraining), Paragraph 254 (Implementation Plan)
    # These are in the ORIGINAL indices, which shifted by SHIFT1 from the definitions
    # But P52 and P53 are BEFORE the definitions insertion (P70), so no shift for those
    # =========================================================================
    print("Fix 15: Updating question counts")

    # P52 - Scope paragraph (before P70 insertion, so no shift)
    p52 = paras[52]
    old_text_52 = p52.text
    new_text_52 = old_text_52.replace(
        "limited to a baseline of 500 pre-defined questions distributed across five (5) selected frontline offices of Panabo City Hall. These five offices and their approximate question allocations are as follows: City Mayor\u2019s Office with approximately 100 questions, City Civil Registrar\u2019s Office with approximately 100 questions, City Treasurer\u2019s Office with approximately 100 questions, City Assessor\u2019s Office with approximately 100 questions, and City Social Welfare and Development Office with approximately 100 questions",
        "limited to a baseline of approximately 1,500 pre-defined question variations distributed across five (5) selected frontline offices of Panabo City Hall. These five offices and their approximate allocations are as follows: City Mayor\u2019s Office with approximately 1,000 question variations covering its extensive range of services, City Civil Registrar\u2019s Office with approximately 100 question variations, City Treasurer\u2019s Office with approximately 100 question variations, City Assessor\u2019s Office with approximately 150 question variations, and City Social Welfare and Development Office with approximately 150 question variations"
    )
    if new_text_52 != old_text_52:
        set_paragraph_text(paras[52], new_text_52)
        print("  -> Updated P52 (Scope)")
    else:
        # Try with straight quotes
        new_text_52 = old_text_52.replace(
            "limited to a baseline of 500 pre-defined questions distributed across five (5) selected frontline offices of Panabo City Hall",
            "limited to a baseline of approximately 1,500 pre-defined question variations distributed across five (5) selected frontline offices of Panabo City Hall"
        )
        if new_text_52 != old_text_52:
            # Also fix the per-office counts
            new_text_52 = new_text_52.replace(
                "City Mayor's Office with approximately 100 questions, City Civil Registrar's Office with approximately 100 questions, City Treasurer's Office with approximately 100 questions, City Assessor's Office with approximately 100 questions, and City Social Welfare and Development Office with approximately 100 questions",
                "City Mayor's Office with approximately 1,000 question variations covering its extensive range of services, City Civil Registrar's Office with approximately 100 question variations, City Treasurer's Office with approximately 100 question variations, City Assessor's Office with approximately 150 question variations, and City Social Welfare and Development Office with approximately 150 question variations"
            )
            set_paragraph_text(paras[52], new_text_52)
            print("  -> Updated P52 (Scope) [straight quotes]")
        else:
            print("  !! Could not match P52 text for replacement. Doing full replacement.")
            set_paragraph_text(paras[52],
                "The initial deployment and testing of the system will be limited to a baseline of approximately 1,500 pre-defined question variations distributed across five (5) selected frontline offices of Panabo City Hall. These five offices and their approximate allocations are as follows: City Mayor\u2019s Office with approximately 1,000 question variations covering its extensive range of services, City Civil Registrar\u2019s Office with approximately 100 question variations, City Treasurer\u2019s Office with approximately 100 question variations, City Assessor\u2019s Office with approximately 150 question variations, and City Social Welfare and Development Office with approximately 150 question variations. The questions for each service consist of the most common frequently asked questions (FAQs) gathered from the Citizen\u2019s Charter and historical citizen inquiries from the LGU\u2019s public communication channels. This 1,500-question baseline exists because it is not feasible to anticipate every possible citizen inquiry phrasing during the initial data gathering phase.")
            print("  -> Full-replaced P52 (Scope)")

    # P53 - Retraining paragraph: "beyond the initial 500 questions"
    p53 = paras[53]
    old_text_53 = p53.text
    new_text_53 = old_text_53.replace("beyond the initial 500 questions", "beyond the initial baseline")
    if new_text_53 != old_text_53:
        set_paragraph_text(paras[53], new_text_53)
        print("  -> Updated P53 (retraining reference)")
    else:
        print("  !! P53: '500 questions' not found, may already be updated")

    # P254 - Implementation Plan (shifted by TOTAL_SHIFT)
    idx254 = 254 + TOTAL_SHIFT
    p254 = paras[idx254]
    old_text_254 = p254.text
    new_text_254 = old_text_254.replace("500 curated questions across five frontline services", "approximately 1,500 curated question variations across five frontline offices")
    if new_text_254 != old_text_254:
        set_paragraph_text(paras[idx254], new_text_254)
        print(f"  -> Updated P{idx254} (Implementation Plan)")
    else:
        # Try with different phrasing
        new_text_254 = old_text_254.replace("500 curated questions", "approximately 1,500 curated question variations")
        if new_text_254 != old_text_254:
            set_paragraph_text(paras[idx254], new_text_254)
            print(f"  -> Updated P{idx254} (Implementation Plan) [alt match]")
        else:
            print(f"  !! P{idx254}: Could not match '500' text, may need manual check")

    # =========================================================================
    # SAVE
    # =========================================================================
    doc.save(OUT)
    print(f"\nAll fixes applied! Saved to: {OUT}")
    print(f"Original backup at: {BACKUP}")
    print(f"Total paragraphs added: {SHIFT1 + SHIFT2 + SHIFT3}")


if __name__ == "__main__":
    main()
