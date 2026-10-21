"""
Restructure intents.csv for VISTA
- 5 offices, ~100 questions each
- City Mayor's Office (CMO)
- City Civil Registrar's Office (CCR)
- City Treasurer's Office (CTO)
- City Assessor's Office (CAO)
- City Social Welfare & Development Office (CSWDO)
"""

import pandas as pd
import os, shutil

SRC = "backend/data/intents.csv"
BAK = "backend/data/intents_backup_original.csv"
OUT = "backend/data/intents.csv"

# ── 0. Back up original ─────────────────────────────────────────────
shutil.copy2(SRC, BAK)
print(f"✅ Backup saved → {BAK}")

df = pd.read_csv(SRC)

# ── 1. Consolidate City Mayor's Office ──────────────────────────────
cmo_depts = [d for d in df["department"].unique()
             if "Mayor" in str(d) or d == "BPLO"]

cmo_rows = df[df["department"].isin(cmo_depts)].copy()
cmo_rows["department"] = "City Mayor's Office"

# Keep only the most diverse intents (pick top 100 rows, spread across intents)
cmo_intents = cmo_rows["intent"].unique()
# Take up to 4 questions per intent, then trim to ~100
sampled_cmo = cmo_rows.groupby("intent").head(4).head(100)
print(f"📌 CMO: kept {len(sampled_cmo)} rows from {len(cmo_rows)} (across {len(cmo_intents)} intents)")

# ── 2. Keep & Expand Civil Registrar ────────────────────────────────
ccr_rows = df[df["department"] == "Civil Registrar"].copy()
ccr_rows["department"] = "City Civil Registrar's Office"

# Generate additional questions to reach ~100
ccr_extra = []
ccr_services = [
    ("ccr_birth_certificate", "Birth Certificate",
     ["How do I get a birth certificate?", "What are the requirements for birth certificate?",
      "How much is a birth certificate?", "Where do I get a birth certificate?",
      "How long does it take to get a birth certificate?", "Can I get a birth certificate online?",
      "What if my birth was not registered?", "How to get a late registration of birth?",
      "Requirements for late registration of birth?", "How much is the fee for late registration?"]),
    ("ccr_marriage_certificate", "Marriage Certificate",
     ["How do I get a marriage certificate?", "What are the requirements for marriage certificate?",
      "How much is a marriage certificate?", "Where do I get a marriage certificate?",
      "How long does it take to process a marriage certificate?",
      "What documents do I need for marriage certificate?",
      "Can I get a copy of my marriage certificate?",
      "How to request a certified true copy of marriage certificate?",
      "Is there a fee for marriage certificate copy?",
      "Where is the Civil Registrar office located?"]),
    ("ccr_death_certificate", "Death Certificate",
     ["How do I get a death certificate?", "What are the requirements for death certificate?",
      "How much is a death certificate?", "Where do I get a death certificate?",
      "How long does it take to get a death certificate?",
      "What if the death was not registered?", "Late registration of death requirements?",
      "How to request a certified copy of death certificate?",
      "Who can request a death certificate?", "Is there a fee for death certificate?"]),
    ("ccr_cenomar", "CENOMAR / No Marriage Record",
     ["How do I get a CENOMAR?", "What is CENOMAR?",
      "How much is the CENOMAR fee?", "Where do I request CENOMAR?",
      "How long does CENOMAR processing take?", "Requirements for CENOMAR?",
      "Can I get CENOMAR at City Hall?", "What is a certificate of no marriage?",
      "Who needs a CENOMAR?", "Is CENOMAR available locally?"]),
    ("ccr_legitimation", "Legitimation",
     ["What is legitimation?", "How do I file for legitimation?",
      "Requirements for legitimation?", "How much is the legitimation fee?",
      "Where do I file legitimation?", "How long does legitimation take?",
      "Who can file for legitimation?", "What documents are needed for legitimation?",
      "Can legitimation be done at the local civil registrar?",
      "What is the process for legitimation?"]),
    ("ccr_correction_entry", "Correction of Entry",
     ["How do I correct an error in my birth certificate?",
      "What is RA 9048?", "Requirements for correction of clerical error?",
      "How much is the fee for correction of entry?",
      "Where do I file correction of entry?",
      "How long does correction of entry take?",
      "Can I change my first name?", "What is RA 10172?",
      "How to correct gender or date of birth?",
      "Requirements for change of first name?"]),
]

for intent, service, questions in ccr_services:
    for q in questions:
        ccr_extra.append({
            "department": "City Civil Registrar's Office",
            "intent": intent,
            "language": "en",
            "question": q,
            "answer": f"For {service} services, please visit the City Civil Registrar's Office at Panabo City Hall. Please bring the necessary documents and valid ID.",
            "source": "Citizens Charter",
            "tags": f"{intent},civil_registrar"
        })

ccr_extra_df = pd.DataFrame(ccr_extra)
ccr_combined = pd.concat([ccr_rows, ccr_extra_df], ignore_index=True).head(100)
print(f"📌 CCR: {len(ccr_combined)} rows (original {len(ccr_rows)} + generated)")

# ── 3. Keep & Expand Treasurer ──────────────────────────────────────
cto_rows = df[df["department"] == "Treasurer"].copy()
cto_rows["department"] = "City Treasurer's Office"

cto_extra = []
cto_services = [
    ("cto_real_property_tax", "Real Property Tax",
     ["How do I pay real property tax?", "When is the deadline for real property tax?",
      "How much is the real property tax?", "Where do I pay real property tax?",
      "What happens if I don't pay real property tax?", "Is there a discount for early payment?",
      "Can I pay real property tax online?", "How is real property tax computed?",
      "What is the penalty for late payment?", "Who is required to pay real property tax?",
      "What documents do I need to pay real property tax?",
      "Can I pay real property tax in installments?"]),
    ("cto_business_tax", "Business Tax",
     ["How do I pay business tax?", "When is business tax due?",
      "How much is the business tax?", "Where do I pay business tax?",
      "What is the penalty for late business tax payment?",
      "Can I pay business tax quarterly?", "How is business tax computed?",
      "What documents are needed for business tax payment?",
      "Is there a discount for prompt business tax payment?",
      "Who needs to pay business tax?", "Can I pay business tax online?",
      "Where is the Treasurer's Office located?"]),
    ("cto_community_tax", "Community Tax Certificate (Cedula)",
     ["How do I get a community tax certificate?", "What is a cedula?",
      "How much is the cedula?", "Where do I get a cedula?",
      "When is the deadline for cedula?", "Requirements for community tax certificate?",
      "Who needs a community tax certificate?", "Is cedula required for government transactions?",
      "Can I get cedula at the barangay?", "What is the penalty for late cedula?",
      "How is community tax computed?", "Where can I pay for cedula?"]),
    ("cto_tax_clearance", "Tax Clearance",
     ["How do I get a tax clearance?", "What is a tax clearance certificate?",
      "How much is the tax clearance fee?", "Where do I get tax clearance?",
      "Requirements for tax clearance?", "How long does tax clearance processing take?",
      "Who needs a tax clearance?", "Is tax clearance required for business permit?",
      "Can I get tax clearance online?", "What documents are needed for tax clearance?",
      "When do I need to get tax clearance?", "Is there a fee for tax clearance?"]),
    ("cto_transfer_tax", "Transfer Tax",
     ["How do I pay transfer tax?", "What is transfer tax?",
      "How much is the transfer tax rate?", "Where do I pay transfer tax?",
      "Requirements for transfer tax payment?", "When is transfer tax due?",
      "Who pays the transfer tax?", "Is transfer tax required for property sale?",
      "How is transfer tax computed?", "What documents are needed for transfer tax?",
      "Can I pay transfer tax in installments?", "Where is the payment window?"]),
    ("cto_fees_charges", "Fees and Charges",
     ["What fees does the Treasurer collect?", "How do I pay government fees?",
      "Where do I pay fees and charges?", "What payment methods are accepted?",
      "Can I pay fees online?", "What is the schedule of fees?",
      "Are there any discounts on fees?", "How do I get a receipt for payment?",
      "What if I lost my official receipt?", "Can I request a refund?",
      "What time is the Treasurer's office open?", "Is there a payment deadline?"]),
]

for intent, service, questions in cto_services:
    for q in questions:
        cto_extra.append({
            "department": "City Treasurer's Office",
            "intent": intent,
            "language": "en",
            "question": q,
            "answer": f"For {service} inquiries, please visit the City Treasurer's Office at Panabo City Hall Ground Floor. Bring the necessary documents and valid ID.",
            "source": "Citizens Charter",
            "tags": f"{intent},treasurer"
        })

cto_extra_df = pd.DataFrame(cto_extra)
cto_combined = pd.concat([cto_rows, cto_extra_df], ignore_index=True).head(100)
print(f"📌 CTO: {len(cto_combined)} rows (original {len(cto_rows)} + generated)")

# ── 4. Generate City Assessor's Office (NEW) ────────────────────────
cao_data = []
cao_services = [
    ("cao_tax_declaration", "Tax Declaration",
     ["How do I get a tax declaration?", "What is a tax declaration?",
      "Requirements for tax declaration?", "How much is the tax declaration fee?",
      "Where do I get a tax declaration?", "How long does it take to get a tax declaration?",
      "Who needs a tax declaration?", "Can I transfer a tax declaration?",
      "What is the process for new tax declaration?", "Is tax declaration the same as land title?",
      "How to update tax declaration?", "What if I lost my tax declaration?"]),
    ("cao_property_assessment", "Property Assessment",
     ["How is property assessed?", "What is the assessment level for residential property?",
      "How do I know the assessed value of my property?", "Where do I get property assessment?",
      "Requirements for property assessment?", "How much is the assessment fee?",
      "Who does the property assessment?", "How often is property reassessed?",
      "Can I appeal my property assessment?", "What is fair market value?",
      "How is fair market value determined?", "What is the schedule of market values?"]),
    ("cao_transfer_ownership", "Transfer of Ownership",
     ["How do I transfer property ownership?", "Requirements for transfer of ownership?",
      "How much is the transfer fee?", "Where do I file transfer of ownership?",
      "How long does transfer of ownership take?", "What documents are needed for property transfer?",
      "Can I transfer property to a family member?", "Is a deed of sale required?",
      "What is the process for property transfer?", "Do I need a tax clearance for transfer?",
      "Who handles property transfer at City Hall?", "Is there a deadline for property transfer?"]),
    ("cao_certification", "Assessor Certification",
     ["How do I get a certification from the Assessor?", "What certifications does the Assessor issue?",
      "How much is the Assessor certification fee?", "Where do I get Assessor certification?",
      "Requirements for Assessor certification?", "How long does certification processing take?",
      "What is a certification of no property?", "How to get a certification of property holdings?",
      "Is Assessor certification required for loans?", "Can I request certification online?",
      "Who can request Assessor certification?", "What valid IDs are accepted?"]),
    ("cao_reclassification", "Land Reclassification",
     ["How do I reclassify my land?", "What is land reclassification?",
      "Requirements for land reclassification?", "How much is reclassification fee?",
      "Where do I file for reclassification?", "How long does reclassification take?",
      "Can I convert agricultural land to residential?", "Who approves land reclassification?",
      "What is the process for land reclassification?", "Is there a hearing for reclassification?",
      "What documents are needed for reclassification?", "Can reclassification be denied?"]),
    ("cao_new_discovery", "New Discovery of Property",
     ["What is new discovery of property?", "How do I declare newly discovered property?",
      "Requirements for new discovery declaration?", "Is there a fee for new discovery?",
      "Where do I report new discovery?", "What happens after new discovery?",
      "How long does new discovery processing take?", "Who handles new discovery of property?",
      "Is new discovery the same as new tax declaration?", "What documents are needed?",
      "Can I declare improvements as new discovery?", "Is there a penalty for undeclared property?"]),
    ("cao_annotation", "Annotation of Tax Declaration",
     ["What is annotation of tax declaration?", "How do I annotate my tax declaration?",
      "Requirements for annotation?", "How much is annotation fee?",
      "Where do I file for annotation?", "How long does annotation take?",
      "When is annotation required?", "Who can request annotation?",
      "What documents are needed for annotation?", "Is annotation required for mortgage?",
      "Can annotation be cancelled?", "What types of annotation are there?"]),
    ("cao_general", "General Assessor Inquiry",
     ["Where is the City Assessor's Office?", "What are the office hours of the Assessor?",
      "What services does the Assessor's Office offer?", "How do I contact the City Assessor?"]),
]

for intent, service, questions in cao_services:
    for q in questions:
        cao_data.append({
            "department": "City Assessor's Office",
            "intent": intent,
            "language": "en",
            "question": q,
            "answer": f"For {service} services, please visit the City Assessor's Office at Panabo City Hall. Bring the required documents and a valid ID.",
            "source": "Citizens Charter",
            "tags": f"{intent},assessor"
        })

cao_df = pd.DataFrame(cao_data).head(100)
print(f"📌 CAO: {len(cao_df)} rows (all generated)")

# ── 5. Generate CSWDO (NEW) ─────────────────────────────────────────
cswd_data = []
cswd_services = [
    ("cswd_senior_citizen_id", "Senior Citizen ID",
     ["How do I get a senior citizen ID?", "Requirements for senior citizen ID?",
      "How much is the senior citizen ID?", "Where do I get a senior citizen ID?",
      "Who is eligible for senior citizen ID?", "How long does it take to get senior citizen ID?",
      "What benefits come with senior citizen ID?", "Can I renew my senior citizen ID?",
      "What if I lost my senior citizen ID?", "Is senior citizen ID free?",
      "What age qualifies for senior citizen ID?", "Where is the CSWDO office?"]),
    ("cswd_pwd_id", "PWD ID",
     ["How do I get a PWD ID?", "Requirements for PWD ID?",
      "How much is the PWD ID fee?", "Where do I get a PWD ID?",
      "Who is eligible for PWD ID?", "How long does PWD ID processing take?",
      "What benefits come with PWD ID?", "Can I renew my PWD ID?",
      "What if I lost my PWD ID?", "Is PWD ID free?",
      "What disabilities qualify for PWD ID?", "What documents are needed for PWD ID?"]),
    ("cswd_social_pension", "Social Pension",
     ["What is the social pension program?", "Who is eligible for social pension?",
      "How much is the social pension?", "How do I apply for social pension?",
      "Requirements for social pension?", "Where do I claim social pension?",
      "When is the social pension payout schedule?", "Can I get social pension if I have income?",
      "How do I know if I am a social pension beneficiary?",
      "What if I missed the social pension payout?",
      "Is social pension the same as SSS pension?", "How to update social pension records?"]),
    ("cswd_burial_assistance", "Burial Assistance",
     ["How do I apply for burial assistance?", "Requirements for burial assistance?",
      "How much is the burial assistance?", "Where do I apply for burial assistance?",
      "Who is eligible for burial assistance?", "How long does burial assistance processing take?",
      "What documents are needed for burial assistance?",
      "Can I apply for burial assistance after the funeral?",
      "Is burial assistance a cash grant?", "How many times can I avail burial assistance?",
      "Is there a deadline to apply for burial assistance?",
      "Who provides the burial assistance at City Hall?"]),
    ("cswd_medical_assistance", "Medical Assistance",
     ["How do I apply for medical assistance?", "Requirements for medical assistance?",
      "How much medical assistance can I receive?", "Where do I apply for medical assistance?",
      "Who is eligible for medical assistance?", "What illnesses are covered?",
      "Can I apply for hospital bill assistance?", "How long does medical assistance processing take?",
      "Is medical assistance a one-time benefit?", "What documents are needed?",
      "Can I apply for medicine assistance?", "Is there a hotline for emergency assistance?"]),
    ("cswd_solo_parent_id", "Solo Parent ID",
     ["How do I get a solo parent ID?", "Requirements for solo parent ID?",
      "How much is the solo parent ID?", "Where do I get a solo parent ID?",
      "Who qualifies as a solo parent?", "What benefits come with solo parent ID?",
      "How long does solo parent ID processing take?", "Can I renew solo parent ID?",
      "What if I lost my solo parent ID?", "Is solo parent ID free?",
      "What is RA 8972?", "What documents are needed for solo parent ID?"]),
    ("cswd_educational_assistance", "Educational Assistance",
     ["How do I apply for educational assistance?", "Requirements for educational assistance?",
      "How much is the educational assistance?", "Where do I apply for educational assistance?",
      "Who is eligible for educational assistance?", "When is the application period?",
      "Is educational assistance a scholarship?", "Can college students apply?",
      "What documents are needed?", "How many students per family can apply?",
      "Is educational assistance cash or check?", "How long does processing take?"]),
    ("cswd_general", "General CSWD Inquiry",
     ["Where is the CSWDO office?", "What services does CSWDO offer?",
      "What are the office hours of CSWDO?", "How do I contact CSWDO?"]),
]

for intent, service, questions in cswd_services:
    for q in questions:
        cswd_data.append({
            "department": "City Social Welfare & Development Office",
            "intent": intent,
            "language": "en",
            "question": q,
            "answer": f"For {service} services, please visit the City Social Welfare & Development Office (CSWDO) at Panabo City Hall. Bring the required documents and a valid ID.",
            "source": "Citizens Charter",
            "tags": f"{intent},cswdo"
        })

cswd_df = pd.DataFrame(cswd_data).head(100)
print(f"📌 CSWDO: {len(cswd_df)} rows (all generated)")

# ── 6. Combine all 5 offices ───────────────────────────────────────
final_df = pd.concat([sampled_cmo, ccr_combined, cto_combined, cao_df, cswd_df], ignore_index=True)
final_df["id"] = range(1, len(final_df) + 1)

# Ensure column order
final_df = final_df[["id", "department", "intent", "language", "question", "answer", "source", "tags"]]

# ── 7. Save ─────────────────────────────────────────────────────────
final_df.to_csv(OUT, index=False)

# ── 8. Summary ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("✅ RESTRUCTURED intents.csv SAVED!")
print("=" * 60)
print(f"\nTotal questions: {len(final_df)}")
print(f"\nBreakdown by office:")
print(final_df["department"].value_counts().to_string())
print(f"\nTotal unique intents: {final_df['intent'].nunique()}")
print(f"\nBackup of original saved as: {BAK}")
