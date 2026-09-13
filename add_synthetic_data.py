import csv
import json
import os

intents_file = 'backend/data/intents.csv'
answers_file = 'backend/data/answers.json'

# Read current max ID
max_id = 0
with open(intents_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader, None) # skip header
    for row in reader:
        if row and row[0].isdigit():
            max_id = max(max_id, int(row[0]))

cao_services = [
    ('cao_new_tax_declaration', 'New Tax Declaration'),
    ('cao_transfer_tax_declaration', 'Transfer of Tax Declaration'),
    ('cao_certified_true_copy_tax_dec', 'Certified True Copy of Tax Declaration'),
    ('cao_cert_no_improvement', 'Certificate of No Improvement'),
    ('cao_property_assessment', 'Property Assessment'),
    ('cao_cancellation_assessment', 'Cancellation of Assessment'),
    ('cao_revision_assessment', 'Revision of Assessment'),
    ('cao_verification_property', 'Verification of Property Location'),
    ('cao_reassessment_property', 'Reassessment of Real Property'),
    ('cao_consolidation_tax_dec', 'Consolidation of Tax Declaration')
]

cswdo_services = [
    ('cswdo_aics', 'Assistance to Individuals in Crisis Situation (AICS)'),
    ('cswdo_solo_parent_id', 'Solo Parent ID'),
    ('cswdo_pwd_id', 'PWD ID'),
    ('cswdo_senior_citizen_id', 'Senior Citizen ID'),
    ('cswdo_social_case_study', 'Social Case Study Report'),
    ('cswdo_pre_marriage_counseling', 'Pre-Marriage Counseling'),
    ('cswdo_cert_indigency', 'Certificate of Indigency'),
    ('cswdo_relief_assistance', 'Relief Assistance'),
    ('cswdo_day_care_enrollment', 'Day Care Center Enrollment'),
    ('cswdo_livelihood_assistance', 'Livelihood Assistance Program')
]

departments = [
    (cao_services, "City Assessor's Office"),
    (cswdo_services, "City Social Welfare and Development Office")
]

templates = {
    '_requirements': [
        ('en', 'What are the requirements for {name}?'),
        ('en', 'What to bring for {name}?'),
        ('tl', 'Ano ang mga kailangan para sa {name}?'),
        ('bis', 'Unsa ang requirements para sa {name}?')
    ],
    '_process': [
        ('en', 'How to apply for {name}?'),
        ('en', 'What is the process for {name}?'),
        ('tl', 'Paano ang proseso ng {name}?'),
        ('bis', 'Unsaon pag process sa {name}?')
    ],
    '_fee': [
        ('en', 'How much is the fee for {name}?'),
        ('en', 'Cost of {name}'),
        ('tl', 'Magkano ang bayad sa {name}?'),
        ('bis', 'Pila ang bayad para sa {name}?')
    ],
    '_location': [
        ('en', 'Where to go for {name}?'),
        ('en', 'Location of office for {name}'),
        ('tl', 'Saan ang opisina para sa {name}?'),
        ('bis', 'Asa nga opisina moadto para sa {name}?')
    ]
}

new_rows = []
new_answers = {}

curr_id = max_id + 1

for dept_services, dept_name in departments:
    for intent_base, service_name in dept_services:
        for suffix, qs in templates.items():
            full_intent = intent_base + suffix
            
            # Create a placeholder answer for JSON
            if full_intent not in new_answers:
                new_answers[full_intent] = {
                    'department': dept_name,
                    'answers': {
                        'en': f'This is the English answer for {service_name} ({suffix.replace("_", "")}). Please update via Admin Dashboard.',
                        'tl': f'Ito ang Tagalog na sagot para sa {service_name} ({suffix.replace("_", "")}). I-update sa Admin Dashboard.',
                        'bis': f'Kini ang Bisaya nga tubag para sa {service_name} ({suffix.replace("_", "")}). I-update sa Admin Dashboard.'
                    }
                }

            # Generate questions for CSV
            for lang, q_template in qs:
                question = q_template.format(name=service_name)
                tags = f'{service_name.lower()}, {suffix.replace("_", "")}'
                tags = tags.replace(' (aics)', '').replace(' id', '') # clean up tags
                row = [curr_id, dept_name, full_intent, lang, question, 'Synthetic Baseline', tags]
                new_rows.append(row)
                curr_id += 1

# Write to CSV
with open(intents_file, 'a', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for row in new_rows:
        writer.writerow(row)

# Update answers.json
try:
    with open(answers_file, 'r', encoding='utf-8') as f:
        answers_data = json.load(f)
except Exception:
    answers_data = {}

answers_data.update(new_answers)

with open(answers_file, 'w', encoding='utf-8') as f:
    json.dump(answers_data, f, indent=2, ensure_ascii=False)

print(f'Successfully added {len(new_rows)} questions and {len(new_answers)} intents.')
