import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime
import pandas as pd
import numpy as np

# Set font styles
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# Complete, fully corrected 5-phase dataset for VISTA
tasks_data = [
    # WBS, Task Name, Start Date, End Date, Phase, is_summary, progress_pct
    # Phase 1: Planning
    ("1.0", "Planning Phase", "2026-04-01", "2026-04-20", "Planning", True, 100),
    ("1.1", "Project Identification", "2026-04-01", "2026-04-05", "Planning", False, 100),
    ("1.2", "Project Scope & Objectives", "2026-04-06", "2026-04-12", "Planning", False, 100),
    ("1.3", "Team Organization", "2026-04-13", "2026-04-16", "Planning", False, 100),
    ("1.4", "Timeline & Gantt Chart", "2026-04-17", "2026-04-20", "Planning", False, 100),
    
    # Phase 2: Analysis
    ("2.0", "Analysis Phase", "2026-04-21", "2026-05-11", "Analysis", True, 100),
    ("2.1", "RRL (Review of Related Literature)", "2026-04-21", "2026-04-27", "Analysis", False, 100),
    ("2.2", "Functional & Non-Functional Req.", "2026-04-28", "2026-05-02", "Analysis", False, 100),
    ("2.3", "Data Gathering (Citizen's Charter)", "2026-05-03", "2026-05-07", "Analysis", False, 100),
    ("2.4", "System Architecture Design", "2026-05-08", "2026-05-11", "Analysis", False, 100),
    
    # Phase 3: Design
    ("3.0", "Design Phase", "2026-05-12", "2026-05-26", "Design", True, 100),
    ("3.1", "ERD & Database Schema", "2026-05-12", "2026-05-16", "Design", False, 100),
    ("3.2", "UI/UX Prototyping", "2026-05-17", "2026-05-19", "Design", False, 100),
    ("3.3", "NLP Pipeline Design", "2026-05-20", "2026-05-23", "Design", False, 100),
    ("3.4", "Use Case & DFD Diagrams", "2026-05-24", "2026-05-26", "Design", False, 100),
    
    # Phase 4: Implementation
    ("4.0", "Implementation Phase", "2026-05-20", "2026-12-15", "Implementation", True, 88),
    ("4.1", "Backend API Dev (FastAPI)", "2026-05-20", "2026-06-01", "Implementation", False, 100),
    ("4.2", "Frontend Dev (100% UI)", "2026-05-20", "2026-06-02", "Implementation", False, 100),
    ("4.3", "Core Backend Logic & Auth", "2026-06-08", "2026-07-17", "Implementation", False, 100),
    ("4.4", "Knowledge Base Population", "2026-07-20", "2026-08-21", "Implementation", False, 100),
    ("4.5", "ML Model Training & Pipeline", "2026-08-24", "2026-10-09", "Implementation", False, 100),
    ("4.6", "Integration & Unit Testing", "2026-10-12", "2026-11-04", "Implementation", False, 100),
    ("4.7", "User Acceptance Testing (UAT)", "2026-11-16", "2026-12-15", "Implementation", False, 0),
    
    # Phase 5: Maintenance
    ("5.0", "Maintenance & Evaluation Phase", "2027-01-05", "2027-03-31", "Maintenance", True, 0),
    ("5.1", "Knowledge Base Monthly Review", "2027-01-05", "2027-01-23", "Maintenance", False, 0),
    ("5.2", "Quarterly Model Retraining", "2027-01-26", "2027-02-15", "Maintenance", False, 0),
    ("5.3", "System Backup & Security Audit", "2027-02-16", "2027-03-05", "Maintenance", False, 0),
    ("5.4", "Bug Fixes & System Updates", "2027-03-08", "2027-03-31", "Maintenance", False, 0),
]

df = pd.DataFrame(tasks_data, columns=["WBS", "TaskName", "Start", "End", "Phase", "IsSummary", "Progress"])
df["StartDate"] = pd.to_datetime(df["Start"])
df["EndDate"] = pd.to_datetime(df["End"])
df["StartStr"] = df["StartDate"].dt.strftime("%b %d, %Y")
df["EndStr"] = df["EndDate"].dt.strftime("%b %d, %Y")

num_tasks = len(df)

# Palette closely matching user's visual identity
theme = {
    "Planning": {"summary": "#eff6ff", "bar_light": "#bfdbfe", "bar_dark": "#2563eb"},
    "Analysis": {"summary": "#f0fdf4", "bar_light": "#bbf7d0", "bar_dark": "#16a34a"},
    "Design": {"summary": "#faf5ff", "bar_light": "#e9d5ff", "bar_dark": "#9333ea"},
    "Implementation": {"summary": "#fff7ed", "bar_light": "#fed7aa", "bar_dark": "#ea580c"},
    "Maintenance": {"summary": "#ecfeff", "bar_light": "#a5f3fc", "bar_dark": "#0891b2"},
}

fig = plt.figure(figsize=(24, 14), dpi=300)
gs = fig.add_gridspec(1, 2, width_ratios=[0.36, 0.64], wspace=0.0)

ax_table = fig.add_subplot(gs[0])
ax_gantt = fig.add_subplot(gs[1])

chart_start = pd.to_datetime("2026-03-25")
chart_end = pd.to_datetime("2027-04-05")

y_max = num_tasks + 2.8
ax_table.set_xlim(0, 100)
ax_table.set_ylim(-1.5, y_max)
ax_table.axis('off')

ax_gantt.set_xlim(chart_start, chart_end)
ax_gantt.set_ylim(-1.5, y_max)

y_positions = list(range(num_tasks - 1, -1, -1))

# Table Header
header_y = num_tasks
ax_table.fill_between([0, 100], header_y - 0.45, header_y + 0.55, color="#0f2942")
ax_table.text(3, header_y + 0.05, "WBS", color="white", weight="bold", fontsize=10, va="center")
ax_table.text(14, header_y + 0.05, "Task Name", color="white", weight="bold", fontsize=10, va="center")
ax_table.text(64, header_y + 0.05, "Start Date", color="white", weight="bold", fontsize=10, va="center")
ax_table.text(84, header_y + 0.05, "End Date", color="white", weight="bold", fontsize=10, va="center")

# Rows and Bars
for idx, row in df.iterrows():
    y = y_positions[idx]
    phase_colors = theme[row["Phase"]]
    
    if row["IsSummary"]:
        ax_table.fill_between([0, 100], y - 0.45, y + 0.45, color=phase_colors["summary"])
        ax_gantt.fill_between([chart_start, chart_end], y - 0.45, y + 0.45, color=phase_colors["summary"], alpha=0.35)
        text_weight = "bold"
        fontsize = 9.8
        text_color = "#0f172a"
    else:
        bg_col = "#ffffff" if idx % 2 == 0 else "#f8fafc"
        ax_table.fill_between([0, 100], y - 0.45, y + 0.45, color=bg_col)
        ax_gantt.fill_between([chart_start, chart_end], y - 0.45, y + 0.45, color=bg_col, alpha=0.5)
        text_weight = "normal"
        fontsize = 9.2
        text_color = "#1e293b"

    # Row text in table
    indent = 14 if row["IsSummary"] else 17
    ax_table.text(3, y, row["WBS"], weight=text_weight, fontsize=fontsize, va="center", color=text_color)
    ax_table.text(indent, y, row["TaskName"], weight=text_weight, fontsize=fontsize, va="center", color=text_color)
    ax_table.text(64, y, row["StartStr"], weight=text_weight, fontsize=8.5, va="center", color="#475569")
    ax_table.text(84, y, row["EndStr"], weight=text_weight, fontsize=8.5, va="center", color="#475569")
    
    # Gantt Bars
    start_num = mdates.date2num(row["StartDate"])
    end_num = mdates.date2num(row["EndDate"])
    bar_width = max(1.2, end_num - start_num + 1)
    bar_height = 0.58 if row["IsSummary"] else 0.42
    
    # Planned bar
    ax_gantt.barh(y, bar_width, left=start_num, height=bar_height, color=phase_colors["bar_light"], edgecolor=phase_colors["bar_dark"], linewidth=0.8, alpha=0.9)
    
    # Progress portion
    prog_pct = row["Progress"] / 100.0
    if prog_pct > 0:
        prog_width = bar_width * prog_pct
        ax_gantt.barh(y, prog_width, left=start_num, height=bar_height, color=phase_colors["bar_dark"], edgecolor=phase_colors["bar_dark"], linewidth=0.8)

# Gantt time axis configuration (on top)
ax_gantt.xaxis.set_major_locator(mdates.MonthLocator())
ax_gantt.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
ax_gantt.xaxis.set_minor_locator(mdates.DayLocator(bymonthday=[15]))

ax_gantt.grid(True, which='major', axis='x', color='#94a3b8', linestyle='-', linewidth=0.8, alpha=0.7)
ax_gantt.grid(True, which='minor', axis='x', color='#cbd5e1', linestyle=':', linewidth=0.6, alpha=0.8)
ax_gantt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True, labelsize=9.2, pad=6)
ax_gantt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)

# DEFENSE 1 MILESTONE (June 3, 2026)
def1_date = mdates.date2num(datetime(2026, 6, 3))
ax_gantt.axvline(def1_date, color="#dc2626", linestyle="--", linewidth=2.2, zorder=6)
ax_gantt.text(
    def1_date, num_tasks + 1.35,
    "1st DEFENSE (Jun 03, 2026)\nStatus: 100% UI, 30% Functionality",
    ha="center", va="center", fontsize=8.6, weight="bold", color="#991b1b",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fee2e2", edgecolor="#ef4444", lw=1.2)
)

# DEFENSE 2 MILESTONE (November 11, 2026)
def2_date = mdates.date2num(datetime(2026, 11, 11))
ax_gantt.axvline(def2_date, color="#b45309", linestyle="--", linewidth=2.2, zorder=6)
ax_gantt.text(
    def2_date, num_tasks + 1.35,
    "2nd DEFENSE (Nov 11, 2026)\nStatus: 100% UI, ~90% Functional Prototype",
    ha="center", va="center", fontsize=8.6, weight="bold", color="#92400e",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef3c7", edgecolor="#f59e0b", lw=1.2)
)

# Border styling
for spine in ax_table.spines.values():
    spine.set_visible(False)
ax_gantt.spines['top'].set_color('#64748b')
ax_gantt.spines['bottom'].set_visible(False)
ax_gantt.spines['left'].set_color('#64748b')
ax_gantt.spines['right'].set_color('#64748b')

# Header & Subtitle
fig.text(0.03, 0.968, "VISTA: PROJECT IMPLEMENTATION GANTT CHART (AY 2026–2027)", fontsize=16, weight="bold", color="#0f2942")
fig.text(0.03, 0.945, "A NLP-Based Automated Response System for Citizen Inquiry and Local Government Services", fontsize=11, fontstyle="italic", color="#475569")

# Bottom Legend with precise color boxes
handles_phases = [
    mpatches.Patch(facecolor="#2563eb", edgecolor="#1d4ed8", label="1.0 Planning"),
    mpatches.Patch(facecolor="#16a34a", edgecolor="#15803d", label="2.0 Analysis"),
    mpatches.Patch(facecolor="#9333ea", edgecolor="#7e22ce", label="3.0 Design"),
    mpatches.Patch(facecolor="#ea580c", edgecolor="#c2410c", label="4.0 Implementation"),
    mpatches.Patch(facecolor="#0891b2", edgecolor="#0e7490", label="5.0 Maintenance"),
]
leg1 = ax_table.legend(handles=handles_phases, loc='lower left', bbox_to_anchor=(0.02, -0.08), ncol=5, frameon=True, fontsize=9.2, title="WBS Phase Categories", title_fontproperties={'weight': 'bold', 'size': 9.8})
leg1.get_frame().set_edgecolor('#cbd5e1')

handles_prog = [
    mpatches.Patch(facecolor="#fed7aa", edgecolor="#c2410c", label="Planned Duration"),
    mpatches.Patch(facecolor="#0f2942", edgecolor="#0f2942", label="Completed Portion (Progress)"),
]
leg2 = ax_gantt.legend(handles=handles_prog, loc='lower right', bbox_to_anchor=(0.98, -0.08), ncol=2, frameon=True, fontsize=9.2, title="Progress Legend", title_fontproperties={'weight': 'bold', 'size': 9.8})
leg2.get_frame().set_edgecolor('#cbd5e1')

plt.subplots_adjust(left=0.03, right=0.97, top=0.86, bottom=0.08)

# Save both as vista_gantt_fixed.png and overwrite vista_gantt.png
fixed_path = r"c:\Users\Jeverly Shane Capote\OneDrive\Desktop\VISTA\vista_gantt_fixed.png"
vista_gantt_path = r"c:\Users\Jeverly Shane Capote\OneDrive\Desktop\VISTA\vista_gantt.png"

plt.savefig(fixed_path, dpi=300, bbox_inches='tight')
plt.savefig(vista_gantt_path, dpi=300, bbox_inches='tight')
print("Successfully generated both vista_gantt_fixed.png and vista_gantt.png")
