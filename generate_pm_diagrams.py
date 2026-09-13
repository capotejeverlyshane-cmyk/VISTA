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
        with urllib.request.urlopen(req) as response:
            with open(f"{name}.png", "wb") as f:
                f.write(response.read())
        print(f"Successfully saved {name}.png")
    except Exception as e:
        print(f"Failed to generate {name}.png: {e}")

padim_cycle = """
@startuml
skinparam state {
  BackgroundColor #4A90E2
  FontColor white
  BorderColor #2C3E50
  FontSize 16
}

state "1. PLANNING" as P
state "2. ANALYSIS" as A
state "3. DESIGN" as D
state "4. IMPLEMENTATION" as I
state "5. MAINTENANCE" as M

P --> A : Requirements & Scope
A --> D : System Specs & Logic
D --> I : Architecture & Blueprints
I --> M : Deployed System
M --> P : Feedback & Iteration (Controlled Retraining)
@enduml
"""

wbs_diagram = """
@startwbs
<style>
wbsDiagram {
  BackgroundColor white
  node {
    BackgroundColor #E2EFDA
    BorderColor #548235
    FontColor black
  }
  rootNode {
    BackgroundColor #2F5597
    FontColor white
    FontSize 14
  }
}
</style>
* VISTA: NLP-BASED CHATBOT FOR CITIZEN INQUIRY
** PLANNING
*** Identify Problems
*** Define Objectives
*** Determine Scope
*** Assign Team Roles
*** Select PADIM Model
** ANALYSIS
*** Review of Related Literature
*** Analyze Existing LGU Systems
*** Identify System Requirements
*** Define System Limitations
** DESIGN
*** Design System Architecture
*** Create Use Case Diagram
*** Create ERD & DFD
*** Create UI/UX Wireframing
*** Database Schema Design
** IMPLEMENTATION
*** Setup Web Hosting & Firebase
*** Develop Web Frontend
*** Train NLP Machine Learning Models
*** Develop Backend API (FastAPI)
*** Integrate Frontend & Backend
** MAINTENANCE
*** Monitor Intent Classification
*** Review Unresolved Queries
*** Retrain Models with New Data
*** Fix System Bugs
@endwbs
"""

gantt_chart = """
@startgantt
<style>
ganttDiagram {
  task {
    BackGroundColor #4472C4
    LineColor #2F528F
    FontColor white
  }
  closed {
    BackGroundColor #D9D9D9
  }
}
</style>
project starts 2026-04-01

[Planning Phase] requires 30 days
[Project Initiation & Scoping] requires 15 days
[Resource Planning] requires 15 days
[Project Initiation & Scoping] starts 2026-04-01
[Resource Planning] starts at [Project Initiation & Scoping]'s end

[Analysis & Design Phase] requires 61 days
[Literature Review] requires 30 days
[System Architecture & UI/UX Wireframing] requires 31 days
[Analysis & Design Phase] starts 2026-05-01
[Literature Review] starts 2026-05-01
[System Architecture & UI/UX Wireframing] starts at [Literature Review]'s end

[Implementation Phase] requires 153 days
[Backend Database Setup] requires 31 days
[Web Frontend Development] requires 61 days
[NLP Model Training & Backend API] requires 61 days
[System Integration] requires 30 days
[Implementation Phase] starts 2026-07-01
[Backend Database Setup] starts 2026-07-01
[Web Frontend Development] starts 2026-08-01
[NLP Model Training & Backend API] starts 2026-09-01
[System Integration] starts 2026-11-01

[Testing & Evaluation Phase] requires 62 days
[Unit & Integration Testing] requires 31 days
[User Acceptance Testing] requires 31 days
[Testing & Evaluation Phase] starts 2026-12-01
[Unit & Integration Testing] starts 2026-12-01
[User Acceptance Testing] starts 2027-01-01

[Maintenance & Documentation] requires 59 days
[System Calibration & Bug Fixing] requires 28 days
[Final Report Writing & Submission] requires 31 days
[Maintenance & Documentation] starts 2027-02-01
[System Calibration & Bug Fixing] starts 2027-02-01
[Final Report Writing & Submission] starts 2027-03-01
@endgantt
"""

if __name__ == "__main__":
    generate_diagram("vista_padim", "plantuml", padim_cycle)
    generate_diagram("vista_wbs", "plantuml", wbs_diagram)
    generate_diagram("vista_gantt", "plantuml", gantt_chart)
