import pandas as pd

df1 = pd.read_csv('data/intents_backup_original.csv')

dept_map = {
    'General': "City Mayor's Office",
    'Civil Registrar': "City Civil Registrar's Office",
    'Treasurer': "City Treasurer's Office",
    'BPLO': "City Mayor's Office",
    "City Mayor's Office - BPLS / Barangay Level": "City Mayor's Office",
    "City Mayor's Office - BPLS": "City Mayor's Office",
    "City Mayor's Office - TMDS": "City Mayor's Office",
    "City Mayor's Office - Building Official": "City Mayor's Office",
    "City Mayor's Office": "City Mayor's Office",
    "City Mayor's Office - PESO": "City Mayor's Office",
    "City Economic Enterprise": "City Mayor's Office",
    "City Mayor's Office - CENRO": "City Mayor's Office",
    "City Mayor's Office - Engineering": "City Mayor's Office",
    "City Mayor's Office - Permits & Inspections": "City Mayor's Office"
}

df1['department'] = df1['department'].map(dept_map)

df2 = pd.read_csv('data/intents.csv.bak')
target_depts = ["City Assessor's Office", "City Social Welfare & Development Office"]
df2_filtered = df2[df2['department'].isin(target_depts)]

merged = pd.concat([df1, df2_filtered], ignore_index=True)
merged['id'] = range(1, len(merged) + 1)

merged.to_csv('data/intents.csv', index=False)

print(f"Merged successfully. Total rows: {len(merged)}")
print(merged['department'].value_counts())
