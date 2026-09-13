import zlib
import base64
import urllib.request
import os

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

use_case_diagram = """
@startuml
left to right direction
skinparam packageStyle rectangle
actor "Citizen/Resident" as Citizen
actor "LGU Administrator" as Admin
database "Firebase Auth" as Firebase

package "VISTA Chatbot System" {
  usecase "Account Authentication" as UCAuth
  usecase "View / Manage Account" as UCAcct
  usecase "Send Multilingual Inquiry" as UC1
  usecase "View Official Service Info" as UC3
  usecase "Process NLP & Classify Intent" as UCNLP
  usecase "Trigger Fallback & Log Query" as UCFallback
  
  usecase "View Analytics and Metrics" as UC5
  usecase "Manage Knowledge Base" as UC6
  usecase "Add New Intent" as UCAddIntent
  usecase "Review Unmatched Queries" as UC7
  usecase "Trigger NLP Model Training" as UC8
  usecase "Count Total Queries" as UCCount
}

Citizen --> UCAuth
Citizen --> UCAcct
Citizen --> UC3
Citizen --> UC1

Admin --> UCAuth
Admin --> UC5
Admin --> UC6
Admin --> UC7
Admin --> UC8
Admin --> UCCount

UCAuth --> Firebase

UC1 .> UCNLP : <<include>>
UCNLP .> UCFallback : <<extend>>
UC6 .> UCAddIntent : <<include>>

note right of UC1 : Generalization for the specific language

@enduml
"""

activity_chat = """
@startuml
skinparam conditionStyle inside
|Citizen|
start
:Type and Send Message;
|VISTA Backend|
:Run NLP Intent Classification;
if (Is Intent\nConfidence\nHigh?) then (Yes)
  fork
    :Query Knowledge Base for Match;
  fork again
    :Retrieve Department Data;
  end fork
  :Format Response;
else (No)
  fork
    :Log to 'Unmatched Queries';
  fork again
    :Generate Fallback Message;
  end fork
endif
|Citizen|
:Receive Chatbot Response;
stop
@enduml
"""

activity_auth = """
@startuml
skinparam conditionStyle inside
|LGU Admin|
start
:Navigate to Admin Login Page;
:Enter Username and Password;
:Click 'Login' Button;
|Authentication Service|
:Validate Credentials against DB;
if (Are\nCredentials\nValid?) then (Yes)
  :Generate Session Token;
  |Admin Dashboard|
  :Redirect to Admin Dashboard;
  stop
else (No)
  |Authentication Service|
  :Reject Login Attempt;
  |Admin Dashboard|
  :Display 'Invalid Credentials' Error;
  |LGU Admin|
  :Enter Username and Password;
  detach
endif
@enduml
"""

activity_knowledge = """
@startuml
skinparam conditionStyle inside
|LGU Admin|
start
:Open Knowledge Base Panel;
:Add or Edit Intent & Response Data;
:Click 'Save Changes';
|Model Training Service|
fork
  :Update SQLite Database Records;
fork again
  :Send 'Data Saved' Notification;
end fork
|LGU Admin|
:Review Saved Confirmation;
:Click 'Retrain Model';
|Model Training Service|
fork
  :Execute train.py Script;
  :Rebuild SVM NLP Pipeline;
fork again
  :Generate Training Logs;
end fork
:Save New Model Files;
:Send 'Training Complete' Alert;
|LGU Admin|
:Wait for Retraining to Complete;
stop
@enduml
"""

activity_unmatched = """
@startuml
skinparam conditionStyle inside
|LGU Admin|
start
:View 'Unmatched Queries' Table;
:Select a specific query;
if (Map to\nExisting or\nNew Intent?) then (Existing)
  :Assign Query to Existing Intent;
else (New)
  :Create New Intent Category;
endif
:Submit Update;
|Database & Logic|
fork
  :Remove entry from Unmatched Log;
fork again
  :Update Knowledge Base DB;
end fork
:Prompt Admin to Retrain Model;
stop
@enduml
"""

if __name__ == "__main__":
    generate_diagram("vista_use_case", "plantuml", use_case_diagram)
    generate_diagram("vista_activity_chat", "plantuml", activity_chat)
    generate_diagram("vista_activity_auth", "plantuml", activity_auth)
    generate_diagram("vista_activity_knowledge", "plantuml", activity_knowledge)
    generate_diagram("vista_activity_unmatched", "plantuml", activity_unmatched)
    print("All diagrams regenerated successfully.")
