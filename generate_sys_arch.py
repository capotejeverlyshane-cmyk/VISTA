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

sys_arch_diagram = """
@startuml
skinparam componentStyle uml2
skinparam linetype ortho

package "Client Tier (Frontend Interface)" {
    [Citizen Chat Interface] as ChatUI
    [LGU Admin Dashboard] as AdminUI
}

package "Application Tier (Backend Server)" {
    [Python Web Server (Flask/FastAPI)] as Server
    
    package "Machine Learning & NLP Pipeline" {
        [Text Preprocessor (Tokenization, Stop Words)] as Preprocessor
        [TF-IDF Feature Extractor] as Extractor
        [Intent Classifier (SVM/LR/MLP)] as Classifier
    }
    
    Server --> Preprocessor : Raw User Text
    Preprocessor --> Extractor : Cleaned Text
    Extractor --> Classifier : Vectorized Features
    Classifier --> Server : Predicted Intent
}

package "Data Tier" {
    database "SQLite Relational Database" as SQLite {
        [Knowledge Base (Intents/Answers)]
        [Chat Logs & Analytics Data]
        [Unmatched Queries Log]
    }
    database "Firebase Auth" as Firebase
}

ChatUI <--> Server : HTTP/REST
AdminUI <--> Server : HTTP/REST
AdminUI <--> Firebase : Authentication

Server <--> SQLite : Read/Write Database
@enduml
"""

if __name__ == "__main__":
    generate_diagram("vista_system_architecture", "plantuml", sys_arch_diagram)
