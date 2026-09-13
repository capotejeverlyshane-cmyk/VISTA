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

problem_tree = """
@startuml
skinparam handwritten false
skinparam linetype ortho

rectangle "EFFECTS" {
  [Frustrated Citizens] as E1
  [Delayed Dissemination of Info] as E2
  [Overwhelmed Frontline Staff] as E3
}

rectangle "CORE PROBLEM" #FFCCCC {
  [Inefficient Citizen Inquiry Handling in LGU] as Core
}

rectangle "CAUSES" {
  [Reliance on Manual / Social Media Replies] as C1
  [Limited Personnel During Peak Hours] as C2
  [Lack of Automated 24/7 Response System] as C3
}

E1 <-- Core
E2 <-- Core
E3 <-- Core

Core <-- C1
Core <-- C2
Core <-- C3

@enduml
"""

objective_tree = """
@startuml
skinparam handwritten false
skinparam linetype ortho

rectangle "BENEFITS" {
  [High Citizen Satisfaction] as B1
  [Immediate Access to Official Info] as B2
  [Reduced Workload for Staff] as B3
}

rectangle "GOAL" #CCFFCC {
  [Efficient Citizen Inquiry Handling in LGU] as Goal
}

rectangle "SOLUTIONS" {
  [Automated NLP Chatbot Responses] as S1
  [24/7 Accessible Web Interface] as S2
  [Intelligent Intent Classification System] as S3
}

B1 <-- Goal
B2 <-- Goal
B3 <-- Goal

Goal <-- S1
Goal <-- S2
Goal <-- S3

@enduml
"""

if __name__ == "__main__":
    generate_diagram("vista_problem_tree", "plantuml", problem_tree)
    generate_diagram("vista_objective_tree", "plantuml", objective_tree)
