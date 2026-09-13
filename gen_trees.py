import zlib, base64, urllib.request

def gen(name, text):
    text = text.strip().replace('\r\n', '\n')
    compressed = zlib.compress(text.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    url = f"https://kroki.io/plantuml/png/{encoded}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(f"{name}.png", "wb") as f:
                f.write(resp.read())
        print(f"OK: {name}.png")
    except Exception as e:
        print(f"FAIL: {name}.png - {e}")

gen("vista_problem_tree", """@startwbs
* CORE PROBLEM
** EFFECTS
*** Frustrated Citizens
*** Delayed Info Dissemination
*** Overwhelmed Frontline Staff
*** Reduced Public Trust
** ROOT CAUSES
*** Reliance on Manual Replies
*** Limited Personnel During Peak
*** No Automated 24/7 System
*** No Multilingual Support
@endwbs""")

gen("vista_objective_tree", """@startwbs
* CENTRAL OBJECTIVE
** EXPECTED BENEFITS
*** High Citizen Satisfaction
*** Immediate Info Dissemination
*** Reduced Staff Workload
*** Strengthened Public Trust
** PROPOSED SOLUTIONS
*** Automated NLP Chatbot
*** 24/7 Web Interface
*** Intent Classification (SVM/NB/LR)
*** Multilingual Support (EN/TL/BS)
@endwbs""")
