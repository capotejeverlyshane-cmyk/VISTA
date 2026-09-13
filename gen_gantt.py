"""Generate AGRISENSE-style Gantt chart with table + colored bars."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import numpy as np

# Task data: (WBS ID, Task Name, Start, End, Phase)
tasks = [
    ("1.0", "Planning Phase",                       "2026-04-01", "2026-05-30", "planning"),
    ("1.1", "Project Initiation & Scoping",         "2026-04-01", "2026-04-30", "planning"),
    ("1.2", "Resource & Timeline Planning",          "2026-05-01", "2026-05-30", "planning"),
    ("2.0", "Analysis & Design Phase",               "2026-06-01", "2026-09-30", "analysis"),
    ("2.1", "Literature Review & Gap Analysis",      "2026-06-01", "2026-07-15", "analysis"),
    ("2.2", "System Architecture & DFD Design",      "2026-07-01", "2026-08-15", "analysis"),
    ("2.3", "ERD, Schema & UI/UX Prototyping",       "2026-08-01", "2026-09-30", "analysis"),
    ("3.0", "Implementation Phase (Agile Sprints)",  "2026-09-01", "2026-11-30", "implementation"),
    ("3.1", "Backend & Database Development",        "2026-09-01", "2026-09-30", "implementation"),
    ("3.2", "Frontend & Chatbot UI Development",     "2026-10-01", "2026-10-31", "implementation"),
    ("3.3", "NLP Model Training & Integration",      "2026-10-15", "2026-11-30", "implementation"),
    ("4.0", "Testing & Evaluation Phase",            "2026-12-01", "2027-01-31", "testing"),
    ("4.1", "Unit & Integration Testing",            "2026-12-01", "2026-12-31", "testing"),
    ("4.2", "User Acceptance Testing (UAT)",         "2027-01-01", "2027-01-31", "testing"),
    ("5.0", "Maintenance & Final Documentation",     "2027-02-01", "2027-03-31", "maintenance"),
    ("5.1", "System Calibration & Bug Fixing",       "2027-02-01", "2027-02-28", "maintenance"),
    ("5.2", "Final Report Writing & Submission",     "2027-03-01", "2027-03-31", "maintenance"),
]

phase_colors = {
    "planning": "#4472C4",
    "analysis": "#70AD47",
    "implementation": "#ED7D31",
    "testing": "#7030A0",
    "maintenance": "#C00000",
}

fig, (ax_table, ax_gantt) = plt.subplots(1, 2, figsize=(18, 9),
    gridspec_kw={'width_ratios': [3.5, 6.5], 'wspace': 0.02})

# --- Left side: Table ---
ax_table.axis('off')

col_labels = ["WBS ID", "Task Name", "Start Date", "End Date"]
cell_text = []
row_colors_list = []

for wbs, name, start, end, phase in tasks:
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    cell_text.append([wbs, name, s.strftime("%b %d, %Y"), e.strftime("%b %d, %Y")])
    if '.' in wbs and wbs.split('.')[1] == '0':
        row_colors_list.append('#D6E4F0')
    else:
        row_colors_list.append('white')

table = ax_table.table(
    cellText=cell_text,
    colLabels=col_labels,
    loc='center',
    cellLoc='left',
    colWidths=[0.12, 0.52, 0.18, 0.18],
)
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1, 1.35)

# Style header
for j in range(len(col_labels)):
    cell = table[0, j]
    cell.set_facecolor('#2F5597')
    cell.set_text_props(color='white', fontweight='bold', fontsize=8)
    cell.set_edgecolor('#1F3864')

# Style data rows
for i in range(len(tasks)):
    for j in range(len(col_labels)):
        cell = table[i + 1, j]
        cell.set_facecolor(row_colors_list[i])
        cell.set_edgecolor('#B4C6E7')
        wbs = tasks[i][0]
        if '.' in wbs and wbs.split('.')[1] == '0':
            cell.set_text_props(fontweight='bold', fontsize=8)
        else:
            cell.set_text_props(fontsize=7.5)

# --- Right side: Gantt bars ---
project_start = datetime(2026, 4, 1)
project_end = datetime(2027, 4, 1)
total_days = (project_end - project_start).days

ax_gantt.set_xlim(0, total_days)
ax_gantt.set_ylim(-0.5, len(tasks) - 0.5)
ax_gantt.invert_yaxis()

# Month grid lines and labels
months = []
d = project_start
while d <= project_end:
    months.append(d)
    if d.month == 12:
        d = datetime(d.year + 1, 1, 1)
    else:
        d = datetime(d.year, d.month + 1, 1)

for m in months:
    x = (m - project_start).days
    ax_gantt.axvline(x=x, color='#D9D9D9', linewidth=0.5, zorder=0)

# Top axis month labels
month_labels = []
month_positions = []
for m in months:
    if m < project_end:
        x = (m - project_start).days
        label = m.strftime("%b '%y") if m.month in [1, 4, 7, 10] else m.strftime("%b")
        month_labels.append(label)
        month_positions.append(x)

ax_gantt.set_xticks(month_positions)
ax_gantt.set_xticklabels(month_labels, fontsize=7, rotation=45, ha='right')
ax_gantt.xaxis.tick_top()
ax_gantt.set_yticks([])

# Draw bars
for i, (wbs, name, start, end, phase) in enumerate(tasks):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    x_start = (s - project_start).days
    duration = (e - s).days
    color = phase_colors[phase]
    
    is_parent = '.' in wbs and wbs.split('.')[1] == '0'
    bar_height = 0.55 if is_parent else 0.45
    
    # Draw bar with gradient effect
    bar = ax_gantt.barh(i, duration, left=x_start, height=bar_height,
                        color=color, edgecolor='white', linewidth=0.5, zorder=2,
                        alpha=0.95 if is_parent else 0.85)
    
    # Add arrow tip for visual style
    arrow_x = x_start + duration
    ax_gantt.plot([arrow_x - 3, arrow_x, arrow_x - 3],
                  [i - bar_height/3, i, i + bar_height/3],
                  color=color, linewidth=1.5, zorder=3)

# Horizontal grid
for i in range(len(tasks)):
    ax_gantt.axhline(y=i + 0.5, color='#E8E8E8', linewidth=0.3, zorder=0)

ax_gantt.set_facecolor('#FAFAFA')
ax_gantt.spines['bottom'].set_visible(False)
ax_gantt.spines['right'].set_visible(False)
ax_gantt.spines['left'].set_visible(False)

# Year headers
for year in [2026, 2027]:
    yr_start = max(datetime(year, 1, 1), project_start)
    yr_end = min(datetime(year, 12, 31), project_end)
    x_s = (yr_start - project_start).days
    x_e = (yr_end - project_start).days
    ax_gantt.text((x_s + x_e) / 2, -1.5, str(year), ha='center', fontsize=10,
                  fontweight='bold', color='#2F5597')

# Legend
legend_patches = [
    mpatches.Patch(color=phase_colors["planning"], label="Planning"),
    mpatches.Patch(color=phase_colors["analysis"], label="Analysis & Design"),
    mpatches.Patch(color=phase_colors["implementation"], label="Implementation"),
    mpatches.Patch(color=phase_colors["testing"], label="Testing & Evaluation"),
    mpatches.Patch(color=phase_colors["maintenance"], label="Maintenance"),
]
fig.legend(handles=legend_patches, loc='lower center', ncol=5, fontsize=8,
           frameon=True, facecolor='white', edgecolor='#D9D9D9')

plt.suptitle("", y=0.98)
plt.tight_layout(rect=[0, 0.04, 1, 0.96])
plt.savefig("vista_gantt.png", dpi=200, bbox_inches='tight', facecolor='white')
print("Saved vista_gantt.png")
plt.close()
