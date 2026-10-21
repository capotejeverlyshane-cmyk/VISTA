"""
VISTA - DFD Level 1 Generator (Single Database - Academic Black & White Style)
Matches Level 0 exactly. Strict DFD rules:
  - No Process-to-Process
  - No External-to-Database
  - No Database-to-Database
  - Every Process has an input and an output
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ===================== THEME =====================
BG = "#ffffff"
BLACK = "#000000"
GRAY = "#e0e0e0"
FONT = "Arial"

# ===================== DRAWING HELPERS =====================

def entity(ax, cx, cy, w, h, label):
    rect = plt.Rectangle((cx - w/2, cy - h/2), w, h,
                          fc=BG, ec=BLACK, lw=2.5, zorder=5)
    ax.add_patch(rect)
    ax.text(cx, cy, label, fontsize=11, fontweight="bold", color=BLACK,
            ha="center", va="center", zorder=6, fontfamily=FONT,
            linespacing=1.4)

def process_box(ax, cx, cy, w, h, pid, label):
    rect = plt.Rectangle((cx - w/2, cy - h/2), w, h,
                          fc=BG, ec=BLACK, lw=2, zorder=5)
    ax.add_patch(rect)
    bar_h = h * 0.30
    bar = plt.Rectangle((cx - w/2, cy + h/2 - bar_h), w, bar_h,
                          fc=GRAY, ec=BLACK, lw=1.5, zorder=6)
    ax.add_patch(bar)
    ax.text(cx, cy + h/2 - bar_h/2, str(pid),
            fontsize=12, fontweight="bold", color=BLACK,
            ha="center", va="center", zorder=7, fontfamily=FONT)
    ax.text(cx, cy - bar_h/2 - 0.05, label,
            fontsize=10, color=BLACK, ha="center", va="center",
            zorder=7, fontfamily=FONT, linespacing=1.3, fontweight="bold")

def datastore(ax, cx, cy, w, h, label):
    """Open-ended rectangle: top, bottom, left lines only (right open)."""
    ax.plot([cx - w/2, cx + w/2], [cy + h/2, cy + h/2],
            color=BLACK, lw=2.5, zorder=5)
    ax.plot([cx - w/2, cx + w/2], [cy - h/2, cy - h/2],
            color=BLACK, lw=2.5, zorder=5)
    ax.plot([cx - w/2, cx - w/2], [cy - h/2, cy + h/2],
            color=BLACK, lw=2.5, zorder=5)
    ax.text(cx, cy, label, fontsize=12, color=BLACK, fontweight="bold",
            ha="center", va="center", zorder=6, fontfamily=FONT,
            linespacing=1.2)

def arrow(ax, x1, y1, x2, y2, label="", fontsize=8,
          label_side="above", label_offset=0.22, label_pos=0.5,
          ha="center", rotation=None):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=BLACK, lw=1.2,
                                shrinkA=2, shrinkB=2),
                zorder=4)
    if not label:
        return
    dx, dy = x2 - x1, y2 - y1
    length = (dx**2 + dy**2) ** 0.5
    mx = x1 + dx * label_pos
    my = y1 + dy * label_pos
    if length == 0: return
    px, py = -dy/length, dx/length
    off = label_offset if label_side == "above" else -label_offset
    lx = mx + px * off
    ly = my + py * off

    if rotation is None:
        angle = np.degrees(np.arctan2(dy, dx))
        if angle > 90: angle -= 180
        if angle < -90: angle += 180
        if abs(angle) > 70:
            angle = 90 if dy > 0 else -90
    else:
        angle = rotation

    ax.text(lx, ly, label, fontsize=fontsize, color=BLACK,
            ha=ha, va="center", zorder=8, fontfamily=FONT,
            rotation=angle, rotation_mode="anchor",
            bbox=dict(boxstyle="round,pad=0.12", facecolor=BG, edgecolor="none", alpha=0.92))


# ================================================================
#                    LEVEL 1 — SINGLE DB DFD
# ================================================================
fig1, ax1 = plt.subplots(figsize=(32, 44))
fig1.patch.set_facecolor(BG)
ax1.set_facecolor(BG)
ax1.set_xlim(-4, 32)
ax1.set_ylim(-4, 44)
ax1.set_aspect("equal")
ax1.axis("off")

# ===================== EXTERNAL ENTITIES =====================
EX_W, EX_H = 3.4, 1.5

# Firebase Auth — top-left
FB_CX, FB_CY = 1.5, 38
entity(ax1, FB_CX, FB_CY, EX_W, EX_H, "Firebase\nAuth")
FB_R = FB_CX + EX_W/2

# Citizen — middle-left
CIT_CX, CIT_CY = 1.5, 27
entity(ax1, CIT_CX, CIT_CY, EX_W, EX_H, "Citizen\n(User)")
CIT_R = CIT_CX + EX_W/2

# LGU Admin — bottom-left
ADM_CX, ADM_CY = 1.5, 12
entity(ax1, ADM_CX, ADM_CY, EX_W, EX_H, "LGU Admin")
ADM_R = ADM_CX + EX_W/2

# ===================== PROCESSES (center column) =====================
PW1, PH1 = 5.5, 2.2
pcx = 14
PL1 = pcx - PW1/2   # left edge
PR1 = pcx + PW1/2   # right edge

procs = [
    (pcx, 39,   "1.0", "User\nAuthentication"),
    (pcx, 34.5, "2.0", "Chat Query\nProcessing"),
    (pcx, 30,   "3.0", "Feedback\nManagement"),
    (pcx, 25.5, "4.0", "Content &\nService Display"),
    (pcx, 21,   "5.0", "Knowledge Base\nManagement"),
    (pcx, 16.5, "6.0", "Model\nRetraining"),
    (pcx, 12,   "7.0", "Analytics &\nReporting"),
    (pcx, 7.5,  "8.0", "Directory\nManagement"),
]
for cx, cy, pid, lab in procs:
    process_box(ax1, cx, cy, PW1, PH1, pid, lab)

# ===================== SINGLE DATABASE (right column) =====================
DB_W, DB_H = 5.0, 2.0
DB_CX = 26
DB_CY = 23.5  # centered vertically among the 8 processes
DSL = DB_CX - DB_W/2  # left edge of DB

datastore(ax1, DB_CX, DB_CY, DB_W, DB_H, "DB   Vista Database")


# ===================== ARROWS =====================

# ===================================================================
#  1.0 USER AUTHENTICATION
# ===================================================================
# 1.0 → Firebase: Auth Token Request
arrow(ax1, PL1, 39.6, FB_R, 38.6, "Auth Token Request", fontsize=8)
# Firebase → 1.0: Auth Token / User Profile
arrow(ax1, FB_R, 37.6, PL1, 38.6, "Auth Token / User Profile", fontsize=8)
# Citizen → 1.0: User Credentials
arrow(ax1, CIT_R, 27.8, PL1, 39.4, "User Credentials", fontsize=8,
      label_pos=0.3, label_offset=0.4)
# 1.0 → Citizen: User Account Information
arrow(ax1, PL1, 38.4, CIT_R, 27.6, "User Account Information", fontsize=8,
      label_pos=0.7, label_offset=0.4)
# Admin → 1.0: Admin Credentials
arrow(ax1, ADM_R, 12.8, PL1, 38.0, "Admin Credentials", fontsize=8,
      label_pos=0.08, label_offset=0.5)
# 1.0 ↔ DB: User Record / User Data
arrow(ax1, PR1, 39.4, DSL, 24.2, "User Record", fontsize=7.5,
      label_pos=0.2, label_offset=0.35)
arrow(ax1, DSL, 24.4, PR1, 39.6, "User Data", fontsize=7.5,
      label_pos=0.2, label_offset=-0.35)

# ===================================================================
#  2.0 CHAT QUERY PROCESSING
# ===================================================================
# Citizen → 2.0: User Query + Language
arrow(ax1, CIT_R, 27.4, PL1, 35.0, "User Query + Language", fontsize=8,
      label_pos=0.35, label_offset=0.4)
# 2.0 → Citizen: AI Response
arrow(ax1, PL1, 34.2, CIT_R, 27.2, "AI Response", fontsize=8,
      label_pos=0.45, label_offset=0.4)
# 2.0 → Citizen: Related Articles
arrow(ax1, PL1, 33.8, CIT_R, 26.9, "Related Articles", fontsize=8,
      label_pos=0.7, label_offset=0.35)
# 2.0 ↔ DB
arrow(ax1, PR1, 34.8, DSL, 24.0, "Intent + Answer Data", fontsize=7.5,
      label_side="below", label_pos=0.35, label_offset=0.35)
arrow(ax1, PR1, 34.2, DSL, 23.8, "Chat Log +\nUnresolved Entry", fontsize=7.5,
      label_pos=0.6, label_offset=-0.5)

# ===================================================================
#  3.0 FEEDBACK MANAGEMENT
# ===================================================================
# Citizen → 3.0: Feedback
arrow(ax1, CIT_R, 26.6, PL1, 30.2, "Feedback", fontsize=8,
      label_pos=0.45, label_offset=0.3)
# 3.0 → Admin: Citizen Feedbacks
arrow(ax1, PL1, 29.4, ADM_R, 12.6, "Citizen Feedbacks", fontsize=8,
      label_pos=0.6, label_offset=-0.5)
# 3.0 ↔ DB
arrow(ax1, PR1, 30.4, DSL, 23.6, "Feedback Record", fontsize=7.5,
      label_pos=0.4, label_offset=0.35)
arrow(ax1, DSL, 23.4, PR1, 29.6, "Feedback Data", fontsize=7.5,
      label_pos=0.4, label_offset=-0.35)

# ===================================================================
#  4.0 CONTENT & SERVICE DISPLAY
# ===================================================================
# 4.0 → Citizen: LGU Services
arrow(ax1, PL1, 26.4, CIT_R, 27.8, "LGU Services", fontsize=7.5,
      label_pos=0.55, label_offset=0.4)
# 4.0 → Citizen: Office Directory
arrow(ax1, PL1, 26.0, CIT_R, 26.4, "Office Directory", fontsize=7.5,
      label_pos=0.45, label_offset=0.4)
# 4.0 → Citizen: Chat History
arrow(ax1, PL1, 25.6, CIT_R, 26.2, "Chat History", fontsize=7.5,
      label_pos=0.7, label_offset=-0.3)
# 4.0 → Citizen: Settings Detail
arrow(ax1, PL1, 25.2, CIT_R, 26.0, "Settings Detail", fontsize=7.5,
      label_pos=0.5, label_offset=-0.4)
# 4.0 → Citizen: Help Center Details
arrow(ax1, PL1, 24.8, CIT_R, 25.8, "Help Center Details", fontsize=7.5,
      label_pos=0.3, label_offset=-0.5)
# DB → 4.0: Content Data (read-only)
arrow(ax1, DSL, 23.2, PR1, 25.5, "Content Data", fontsize=7.5,
      label_pos=0.5, label_offset=0.35)

# ===================================================================
#  5.0 KNOWLEDGE BASE MANAGEMENT
# ===================================================================
# Admin → 5.0: New Intent Data
arrow(ax1, ADM_R, 12.4, PL1, 21.4, "New Intent Data", fontsize=8,
      label_pos=0.4, label_offset=0.4)
# Admin → 5.0: Query Review Actions
arrow(ax1, ADM_R, 12.2, PL1, 20.6, "Query Review Actions", fontsize=8,
      label_pos=0.5, label_offset=-0.4)
# 5.0 → Admin: Knowledge Base Details
arrow(ax1, PL1, 21.0, ADM_R, 13.0, "Knowledge Base Details", fontsize=8,
      label_pos=0.65, label_offset=0.5)
# 5.0 → Admin: Unmatched Queries
arrow(ax1, PL1, 20.4, ADM_R, 12.0, "Unmatched Queries", fontsize=8,
      label_pos=0.7, label_offset=-0.4)
# 5.0 ↔ DB
arrow(ax1, DSL, 23.0, PR1, 21.4, "KB + Unresolved Data", fontsize=7.5,
      label_pos=0.5, label_offset=0.35)
arrow(ax1, PR1, 20.6, DSL, 22.8, "Updated KB Data", fontsize=7.5,
      label_pos=0.5, label_offset=-0.35)

# ===================================================================
#  6.0 MODEL RETRAINING
# ===================================================================
# Admin → 6.0: Retrain Command
arrow(ax1, ADM_R, 11.8, PL1, 16.8, "Retrain Command", fontsize=8,
      label_pos=0.4, label_offset=0.35)
# 6.0 → Admin: System Health
arrow(ax1, PL1, 16.2, ADM_R, 11.6, "System Health", fontsize=8,
      label_pos=0.55, label_offset=-0.35)
# 6.0 ↔ DB
arrow(ax1, DSL, 22.6, PR1, 16.8, "Training Data", fontsize=7.5,
      label_pos=0.5, label_offset=0.4)
arrow(ax1, PR1, 16.2, DSL, 22.4, "Updated Model", fontsize=7.5,
      label_pos=0.5, label_offset=-0.4)

# ===================================================================
#  7.0 ANALYTICS & REPORTING
# ===================================================================
# 7.0 → Admin: System Analytics
arrow(ax1, PL1, 12.6, ADM_R, 11.4, "System Analytics", fontsize=8,
      label_pos=0.55, label_offset=0.35)
# 7.0 → Admin: Total Queries
arrow(ax1, PL1, 12.2, ADM_R, 11.2, "Total Queries", fontsize=8,
      label_pos=0.4, label_offset=0.3)
# 7.0 → Admin: Chat Logs
arrow(ax1, PL1, 11.6, ADM_R, 11.0, "Chat Logs", fontsize=8,
      label_pos=0.3, label_offset=-0.35)
# DB → 7.0: Analytics Source Data (read-only)
arrow(ax1, DSL, 22.2, PR1, 12.2, "Analytics Source Data", fontsize=7.5,
      label_pos=0.55, label_offset=0.45)

# ===================================================================
#  8.0 DIRECTORY MANAGEMENT
# ===================================================================
# Admin → 8.0: Manage Directory Data
arrow(ax1, ADM_R, 10.8, PL1, 7.8, "Manage Directory Data", fontsize=8,
      label_pos=0.4, label_offset=0.4)
# 8.0 → Admin: Current Directory Details
arrow(ax1, PL1, 7.2, ADM_R, 10.6, "Current Directory Details", fontsize=8,
      label_pos=0.6, label_offset=-0.5)
# 8.0 ↔ DB
arrow(ax1, DSL, 22.0, PR1, 7.8, "Directory Data", fontsize=7.5,
      label_pos=0.55, label_offset=0.45)
arrow(ax1, PR1, 7.2, DSL, 22.2, "Updated Directory\nRecord", fontsize=7.5,
      label_pos=0.45, label_offset=-0.5)


# === FIGURE LABEL ===
ax1.text(14, -3, "Figure 2: Level 1 — Detailed Data Flow Diagram",
         fontsize=16, fontweight="bold", color=BLACK,
         ha="center", va="center", fontfamily=FONT)

fig1.savefig("vista_dfd_level1_single_db.png", dpi=200, bbox_inches="tight",
             facecolor=BG, pad_inches=0.3)
plt.close(fig1)
print("Saved: vista_dfd_level1_single_db.png")
