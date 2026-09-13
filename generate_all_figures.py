import zlib
import base64
import urllib.request

def generate_diagram(name, diagram_type, text):
    compressed = zlib.compress(text.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    url = f"https://kroki.io/{diagram_type}/png/{encoded}"
    
    print(f"Generating {name}.png...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(f"{name}.png", "wb") as f:
                f.write(response.read())
        print(f"  -> Saved {name}.png")
    except Exception as e:
        print(f"  -> FAILED {name}.png: {e}")

# ── 1. PADIM / Agile SDLC Cycle ──
padim = """
@startuml
skinparam BackgroundColor white
skinparam handwritten false

skinparam state {
  BackgroundColor<<plan>> #2F5597
  BackgroundColor<<analysis>> #4472C4
  BackgroundColor<<design>> #5B9BD5
  BackgroundColor<<impl>> #70AD47
  BackgroundColor<<maint>> #FFC000
  FontColor white
  BorderColor #1F3864
  FontSize 14
  RoundCorner 20
}

state "1. PLANNING\\n─────────────\\nDefine scope, objectives,\\ntimeline & resources" as P <<plan>>
state "2. ANALYSIS\\n─────────────\\nGather requirements,\\nreview existing systems" as A <<analysis>>
state "3. DESIGN\\n─────────────\\nSystem architecture,\\nERD, DFD, UI/UX" as D <<design>>
state "4. IMPLEMENTATION\\n─────────────\\nDevelop, integrate,\\ntest iteratively" as I <<impl>>
state "5. MAINTENANCE\\n─────────────\\nMonitor, retrain\\nNLP model, fix bugs" as M <<maint>>

P -right-> A : Requirements & Scope
A -right-> D : System Specs
D -down-> I : Blueprints
I -left-> M : Deployed System
M -up-> P : Feedback & Iteration

@enduml
"""

# ── 2. Project Team Organization ──
team_org = """
@startuml
skinparam BackgroundColor white
skinparam handwritten false
skinparam linetype ortho

skinparam rectangle {
  RoundCorner 15
  FontSize 13
  BorderColor #2F5597
}

rectangle "**PROJECT ADVISER**" as Adviser #2F5597;text:white

rectangle "**PROJECT MANAGER &\\nSYSTEMS ANALYST**\\nJeverly Shane B. Capote" as PM #4472C4;text:white
rectangle "**SYSTEM DESIGNER &\\nUI/UX SPECIALIST**\\nHoney Mariel S. Corpuz" as SD #5B9BD5;text:white
rectangle "**SYSTEM DEVELOPER &\\nNLP ENGINEER**\\nAxl Bien Meñoza" as Dev #70AD47;text:white

Adviser -down-> PM
Adviser -down-> SD
Adviser -down-> Dev

@enduml
"""

# ── 3. WBS ──
wbs = """
@startwbs
<style>
wbsDiagram {
  BackgroundColor white
  node {
    BackgroundColor #D6E4F0
    BorderColor #2F5597
    FontColor #1F3864
    RoundCorner 10
    FontSize 12
    Padding 8
    Margin 4
  }
  rootNode {
    BackgroundColor #2F5597
    FontColor white
    FontSize 14
    RoundCorner 10
  }
  :depth(1) {
    BackgroundColor #4472C4
    FontColor white
  }
  :depth(2) {
    BackgroundColor #D6E4F0
    FontColor #1F3864
  }
}
</style>
* VISTA: NLP-Based Chatbot\\nfor Citizen Inquiry
** 1. PLANNING
*** 1.1 Identify Problems & Gaps
*** 1.2 Define Objectives (IPO)
*** 1.3 Determine Scope & Limits
*** 1.4 Assign Team Roles
*** 1.5 Select SDLC Model (PADIM)
** 2. ANALYSIS
*** 2.1 Review Related Literature
*** 2.2 Analyze Existing LGU Systems
*** 2.3 Define Functional Requirements
*** 2.4 Define Non-Functional Requirements
*** 2.5 Create Use Case & DFD
** 3. DESIGN
*** 3.1 System Architecture Design
*** 3.2 ERD & Database Schema
*** 3.3 JSON Schema Design
*** 3.4 UI/UX Wireframing
*** 3.5 NLP Pipeline Design
** 4. IMPLEMENTATION
*** 4.1 Backend API (FastAPI/Python)
*** 4.2 Frontend Development (HTML/JS)
*** 4.3 NLP Model Training (SVM/NB/LR)
*** 4.4 System Integration & Testing
*** 4.5 User Acceptance Testing
** 5. MAINTENANCE
*** 5.1 Monitor Classification Accuracy
*** 5.2 Controlled Retraining Loop
*** 5.3 Knowledge Base Expansion
*** 5.4 Bug Fixes & Updates
@endwbs
"""

# ── 4. Gantt Chart (Month jumps like AGRISENSE) ──
gantt = """
@startgantt
<style>
ganttDiagram {
  BackgroundColor white
  task {
    BackGroundColor #4472C4
    LineColor #2F528F
    FontColor white
    FontSize 11
  }
  milestone {
    BackGroundColor #C00000
    LineColor #C00000
    FontColor #C00000
  }
  separator {
    FontColor #2F5597
    FontSize 13
    BackGroundColor #D6E4F0
  }
  arrow {
    LineColor #2F5597
  }
}
</style>

Project starts 2026-04-26
printscale monthly zoom 2

-- Planning Phase --
[Topic Formulation & Scoping] starts 2026-04-26 and ends 2026-05-26
[Resource & Timeline Planning] starts 2026-05-26 and ends 2026-06-26

-- Analysis & Design Phase --
[Literature Review & Gap Analysis] starts 2026-06-26 and ends 2026-07-26
[System Architecture & DFD Design] starts 2026-07-26 and ends 2026-08-26
[ERD, Schema & UI/UX Prototyping] starts 2026-08-26 and ends 2026-09-26

-- Implementation Phase --
[Backend & Database Development] starts 2026-09-26 and ends 2026-10-26
[Frontend & Chatbot UI Development] starts 2026-10-26 and ends 2026-11-26
[NLP Model Training & Integration] starts 2026-11-26 and ends 2026-12-26

-- Testing & Evaluation Phase --
[Unit & Integration Testing] starts 2026-12-26 and ends 2027-01-26
[User Acceptance Testing (UAT)] starts 2027-01-26 and ends 2027-02-26

-- Maintenance & Documentation --
[System Calibration & Bug Fixing] starts 2027-02-26 and ends 2027-03-26
[Final Documentation & Submission] starts 2027-03-26 and ends 2027-04-26

@endgantt
"""

# ── 5. Problem Tree ──
problem_tree = """
@startwbs
* CORE PROBLEM\nInefficient citizen inquiry\nhandling in Panabo City LGU
** EFFECTS
*** Frustrated Citizens
*** Delayed Info Dissemination
*** Overwhelmed Frontline Staff
*** Reduced Public Trust
** ROOT CAUSES
*** Reliance on Manual\nand Social Media Replies
*** Limited Personnel\nDuring Peak Hours
*** Lack of Automated\n24/7 Response System
*** Absence of Multilingual\nInquiry Support
@endwbs
"""

# ── 6. Objective Tree ──
objective_tree = """
@startwbs
* CENTRAL OBJECTIVE\nEfficient automated citizen\ninquiry via VISTA chatbot
** EXPECTED BENEFITS
*** High Citizen Satisfaction
*** Immediate Info Dissemination
*** Reduced Staff Workload
*** Strengthened Public Trust
** PROPOSED SOLUTIONS
*** Automated NLP Chatbot Responses
*** 24/7 Accessible Web Interface
*** Intelligent Intent Classification
*** Multilingual Support (EN/TL/BS)
@endwbs
"""

# ── 7. Comparison Table (as a diagram) ──
comparison = """
@startuml
skinparam BackgroundColor white

skinparam rectangle {
  RoundCorner 0
  FontSize 11
}

rectangle "**COMPARISON OF EXISTING SYSTEMS AND PROPOSED SYSTEM**" as Title #2F5597;text:white {

  rectangle "**Feature**" as H0 #4472C4;text:white
  rectangle "**eGovPH Portal**" as H1 #4472C4;text:white
  rectangle "**AskGov (SG)**" as H2 #4472C4;text:white
  rectangle "**Bologna Chatbot**" as H3 #4472C4;text:white
  rectangle "**VISTA (Proposed)**" as H4 #70AD47;text:white

  rectangle "NLP Intent Classification" as F1 #F2F2F2
  rectangle "✗" as V1a #FFD7D7
  rectangle "✓ (BERT)" as V1b #E2EFDA
  rectangle "✓ (SVM)" as V1c #E2EFDA
  rectangle "✓ (SVM/NB/LR)" as V1d #E2EFDA

  rectangle "Multilingual Support" as F2 #F2F2F2
  rectangle "✗" as V2a #FFD7D7
  rectangle "✗" as V2b #FFD7D7
  rectangle "✗" as V2c #FFD7D7
  rectangle "✓ (EN/TL/BS)" as V2d #E2EFDA

  rectangle "Verified Knowledge Base" as F3 #F2F2F2
  rectangle "✓" as V3a #E2EFDA
  rectangle "✓" as V3b #E2EFDA
  rectangle "✓" as V3c #E2EFDA
  rectangle "✓ (Citizen's Charter)" as V3d #E2EFDA

  rectangle "Controlled Retraining" as F4 #F2F2F2
  rectangle "✗" as V4a #FFD7D7
  rectangle "✗" as V4b #FFD7D7
  rectangle "✗" as V4c #FFD7D7
  rectangle "✓" as V4d #E2EFDA

  rectangle "Admin Analytics Dashboard" as F5 #F2F2F2
  rectangle "✗" as V5a #FFD7D7
  rectangle "✗" as V5b #FFD7D7
  rectangle "✗" as V5c #FFD7D7
  rectangle "✓" as V5d #E2EFDA
}

@enduml
"""

if __name__ == "__main__":
    print("=" * 50)
    print("VISTA Professional Figure Generator")
    print("=" * 50)
    
    diagrams = [
        ("vista_padim", "plantuml", padim),
        ("vista_team_org", "plantuml", team_org),
        ("vista_wbs", "plantuml", wbs),
        ("vista_gantt", "plantuml", gantt),
        ("vista_problem_tree", "plantuml", problem_tree),
        ("vista_objective_tree", "plantuml", objective_tree),
    ]
    
    for name, dtype, text in diagrams:
        generate_diagram(name, dtype, text)
    
    print("\n" + "=" * 50)
    print("All figures generated!")
    print("=" * 50)
