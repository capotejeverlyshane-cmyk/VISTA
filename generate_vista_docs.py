import os
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_heading(doc, text, level=1):
    heading = doc.add_heading(text, level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in heading.runs:
        run.font.color.rgb = docx.shared.RGBColor(0, 0, 0)
    return heading

def add_paragraph(doc, text, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    return p

def add_image_if_exists(doc, filename, width_inches=6.0):
    if os.path.exists(filename):
        doc.add_picture(filename, width=Inches(width_inches))
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Figure: {filename.replace('.png', '').replace('_', ' ').title()}")
        run.italic = True
    else:
        add_paragraph(doc, f"[Missing Image: {filename}]", italic=True, align=WD_ALIGN_PARAGRAPH.CENTER)

def create_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
    for row_data in rows:
        row_cells = table.add_row().cells
        for i, data in enumerate(row_data):
            row_cells[i].text = str(data)

def main():
    doc = docx.Document()
    
    # Title Page
    add_paragraph(doc, "VISTA: A NLP-BASED CHATBOT FOR CITIZEN INQUIRY AND LOCAL GOVERNMENT SERVICES", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph(); doc.add_paragraph()
    add_paragraph(doc, "DAVAO DEL NORTE STATE COLLEGE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "Institute of Computing", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "New Visayas, Panabo City", align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph(); doc.add_paragraph()
    add_paragraph(doc, "A Capstone Project Presented by:", align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph(); doc.add_paragraph()
    add_paragraph(doc, "JEVERLY SHANE B. CAPOTE", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "HONEY MARIEL S. CORPUZ", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "AXL BIEN MEÑOZA", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph(); doc.add_paragraph()
    add_paragraph(doc, "MAY 2026", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_page_break()

    # CHAPTER 1 (Simplified for script length, focus on Chapter 2 expansion)
    add_paragraph(doc, "CHAPTER 1", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "INTRODUCTION", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()
    add_heading(doc, "Background of Study", level=2)
    add_paragraph(doc, "The global landscape of public administration is under increasing pressure to digitalize as citizens expect faster, more accessible, and transparent governance [1]. According to the United Nations, digital government initiatives are critical in strengthening institutional transparency and delivering efficient services. In Panabo City, the volume of inquiries regarding the Citizen's Charter accelerates frontline workload, yet most local offices still rely on physical front-desk assistance.")
    add_heading(doc, "Objectives of the Study", level=2)
    add_paragraph(doc, "The main objective of this project is to design and develop VISTA, an NLP-Based Chatbot for Citizen Inquiry and Local Government Services. Specifically, the project aims to:")
    add_paragraph(doc, "1. Develop a structured and multilingual dataset (English, Filipino/Tagalog, and Cebuano/Bisaya).")
    add_paragraph(doc, "2. Implement a text preprocessing pipeline and feature extraction through TF-IDF [2].")
    add_paragraph(doc, "3. Train and evaluate selected machine learning algorithms (Neural Network, Support Vector Machine, and Logistic Regression) [3][4].")
    add_paragraph(doc, "4. Implement a controlled improvement mechanism.")
    add_paragraph(doc, "5. Develop a web-based chatbot interface.")
    add_heading(doc, "Problem Tree and Objective Tree Discussion", level=2)
    add_paragraph(doc, "The Problem Tree Diagram maps the causes (reliance on manual replies), core problem (inefficient handling), and effects (frustrated citizens).")
    add_image_if_exists(doc, "vista_problem_tree.png")
    add_paragraph(doc, "The Objective Tree Diagram converts these into positive solutions, centered on automated NLP chatbot responses.")
    add_image_if_exists(doc, "vista_objective_tree.png")
    doc.add_page_break()

    # CHAPTER 2
    add_paragraph(doc, "CHAPTER 2", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_paragraph(doc, "METHODOLOGY", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    doc.add_paragraph()

    add_paragraph(doc, "The methodology used in the development of VISTA dictates the overall workflow. This chapter discusses the development process, including the chosen System Development Life Cycle (SDLC) model—the PADIM framework—and outlines the specific tools, diagrams, and algorithms involved.")
    
    add_heading(doc, "The PADIM Framework", level=2)
    add_paragraph(doc, "VISTA adopts the PADIM (Planning, Analysis, Design, Implementation, Maintenance) SDLC model, which is essential for NLP-based systems that require continuous data structuring and iterative model training. The Planning phase defines the scope. Analysis gathers requirements from the Citizen's Charter. Design translates these into a structured database and UI architecture. Implementation integrates the machine learning models with the web backend. Finally, Maintenance ensures the chatbot adapts via the controlled retraining loop.")
    add_image_if_exists(doc, "vista_padim.png", width_inches=6.5)

    add_heading(doc, "System Planning", level=2)
    add_heading(doc, "Work Breakdown Structure (WBS)", level=3)
    add_paragraph(doc, "The Work Breakdown Structure (WBS) of the project presents a hierarchical decomposition of the entire system development process into manageable phases that align with the PADIM framework.")
    add_image_if_exists(doc, "vista_wbs.png", width_inches=6.5)

    add_heading(doc, "Gantt Chart", level=3)
    add_paragraph(doc, "The Gantt chart presents the timeline and planned schedule for the activities, starting from April 2026 to March 2027.")
    add_image_if_exists(doc, "vista_gantt.png", width_inches=6.5)

    add_heading(doc, "System Analysis", level=2)
    add_heading(doc, "System Architecture", level=3)
    add_paragraph(doc, "The system architecture illustrates how components interact. An SQLite database stores logs, while a Python FastAPI backend utilizes Scikit-learn models to process natural language input.")
    add_image_if_exists(doc, "vista_system_architecture.png", width_inches=6.0)

    add_heading(doc, "Use Case Diagram", level=3)
    add_paragraph(doc, "The Use Case diagram identifies the Citizen and Admin as primary actors interacting with the system.")
    add_image_if_exists(doc, "vista_use_case.png", width_inches=5.5)

    add_heading(doc, "Data Flow Diagrams (DFD)", level=3)
    add_paragraph(doc, "The Context Flow Diagram (Level 0 DFD) defines the system boundary.")
    add_image_if_exists(doc, "vista_dfd_level0.png", width_inches=6.0)
    add_paragraph(doc, "The Level 1 DFD decomposes this into strict sub-processes, ensuring no direct function-to-function or database-to-database connections, enforcing data flow rules.")
    add_image_if_exists(doc, "vista_dfd_level1.png", width_inches=6.5)

    add_heading(doc, "System Design", level=2)
    add_heading(doc, "Entity Relationship Diagram (ERD)", level=3)
    add_paragraph(doc, "The ERD utilizes Crow's Foot Notation to define the relational database structure.")
    add_image_if_exists(doc, "vista_erd.png", width_inches=6.5)

    add_heading(doc, "Data Dictionary", level=3)
    add_paragraph(doc, "The Data Dictionary explicitly defines the schema of the SQLite database utilized by the VISTA backend.")
    
    add_paragraph(doc, "Table 1: chat_logs", bold=True)
    create_table(doc, ["Field Name", "Data Type", "Description"], [
        ("id", "INTEGER", "Primary Key (Auto-increment)."),
        ("question", "TEXT", "The raw text inquiry submitted by the citizen."),
        ("intent", "TEXT", "The NLP-predicted intent classification."),
        ("language", "TEXT", "The detected language of the query."),
        ("confidence", "REAL", "The confidence score (0.0 to 1.0) of the prediction."),
        ("created_at", "TIMESTAMP", "The exact date and time the query was processed.")
    ])
    doc.add_paragraph()

    add_paragraph(doc, "Table 2: feedback", bold=True)
    create_table(doc, ["Field Name", "Data Type", "Description"], [
        ("id", "INTEGER", "Primary Key (Auto-increment)."),
        ("question", "TEXT", "The inquiry the feedback belongs to."),
        ("answer", "TEXT", "The AI-generated response provided to the user."),
        ("intent", "TEXT", "The intent the query was mapped to."),
        ("helpful", "BOOLEAN", "True if the user found it helpful, False otherwise."),
        ("language", "TEXT", "The language used during the interaction."),
        ("comment", "TEXT", "Optional text comment provided by the user."),
        ("created_at", "TIMESTAMP", "The timestamp of the feedback submission.")
    ])
    doc.add_paragraph()

    add_paragraph(doc, "Table 3: unresolved_queries", bold=True)
    create_table(doc, ["Field Name", "Data Type", "Description"], [
        ("id", "INTEGER", "Primary Key (Auto-increment)."),
        ("question", "TEXT", "The user's query that failed to match a high-confidence intent."),
        ("predicted_intent", "TEXT", "The best-guess intent below the threshold."),
        ("confidence", "REAL", "The sub-threshold confidence score."),
        ("created_at", "TIMESTAMP", "The timestamp the query failed to resolve.")
    ])

    add_heading(doc, "JSON Knowledge Base Schema", level=3)
    add_paragraph(doc, "In addition to the relational database, VISTA utilizes structured JSON and CSV files to load its conversational knowledge base into memory for fast NLP training. The system relies on 'intents.csv' (containing intent names and associated training phrases) and 'answers.json'. The JSON schema for the answers is designed as a dictionary where the top-level keys represent the intent identifiers. Inside each intent object, there are nested keys for 'en' (English), 'tl' (Tagalog), and 'bis' (Bisaya), containing the verified responses. This structured schema ensures O(1) retrieval time after the classifier predicts the intent [2].")

    add_heading(doc, "Technologies, Concepts, and Theories", level=3)
    add_paragraph(doc, "Natural Language Processing (NLP): NLP is a subfield of artificial intelligence focused on enabling computers to understand and process human language [1]. In VISTA, NLP techniques are used to clean, tokenize, and normalize raw text inquiries.")
    add_paragraph(doc, "TF-IDF (Term Frequency-Inverse Document Frequency): TF-IDF is a statistical measure used to evaluate how important a word is to a document within a collection or corpus [2]. VISTA utilizes Scikit-learn's TfidfVectorizer to convert qualitative text into quantitative numerical vectors suitable for machine learning.")
    add_paragraph(doc, "Support Vector Machine (LinearSVC): SVM is a supervised learning algorithm that determines the optimal hyperplane to separate data classes [3]. It is highly effective for text classification in high-dimensional spaces.")
    add_paragraph(doc, "Artificial Neural Networks (MLPClassifier): Multi-Layer Perceptrons are feedforward neural networks that learn non-linear functions [4]. VISTA evaluates MLPs to handle complex linguistic patterns across its multilingual datasets.")
    add_paragraph(doc, "FastAPI & Python: FastAPI is a modern, high-performance web framework for building APIs with Python [5]. VISTA relies on FastAPI to bridge the frontend user interface with the backend NLP engine asynchronously.")
    add_paragraph(doc, "SQLite: A C-language library that implements a small, fast, self-contained SQL database engine [6]. It is used as the primary logging database for VISTA.")

    doc.add_page_break()
    add_heading(doc, "References", level=2)
    add_paragraph(doc, "[1] D. Jurafsky and J. H. Martin, Speech and Language Processing. 3rd ed. draft. Stanford, CA: Stanford University, 2023.")
    add_paragraph(doc, "[2] C. D. Manning, P. Raghavan, and H. Schütze, Introduction to Information Retrieval. Cambridge, U.K.: Cambridge University Press, 2008.")
    add_paragraph(doc, "[3] C. Cortes and V. Vapnik, \"Support-vector networks,\" Machine Learning, vol. 20, no. 3, pp. 273-297, 1995.")
    add_paragraph(doc, "[4] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge, MA: MIT Press, 2016.")
    add_paragraph(doc, "[5] S. Ramirez, \"FastAPI: High performance, easy to learn, fast to code, ready for production,\" FastAPI Documentation, 2023.")
    add_paragraph(doc, "[6] R. Owens, SQLite: The Definitive Guide. Sebastopol, CA: O'Reilly Media, 2006.")

    doc.save("VISTA_Chapter_1_and_2_Complete.docx")
    print("VISTA_Chapter_1_and_2_Complete.docx generated successfully with all expanded content.")

if __name__ == "__main__":
    main()
