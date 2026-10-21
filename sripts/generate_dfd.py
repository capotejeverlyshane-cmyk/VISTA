"""
VISTA - Data Flow Diagram Generator (Academic Black & White Style)
Matches strict DFD rules: No External-to-External, No DB-to-DB, No Process-to-Process.
Every Process has an input and an output.
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
    ax.text(cx, cy, label, fontsize=12, fontweight="bold", color=BLACK,
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
            fontsize=13, fontweight="bold", color=BLACK,
            ha="center", va="center", zorder=7, fontfamily=FONT)
    ax.text(cx, cy - bar_h/2 - 0.05, label,
            fontsize=11, color=BLACK, ha="center", va="center",
            zorder=7, fontfamily=FONT, linespacing=1.3, fontweight="bold")

def context_process(ax, cx, cy, w, h, pid, label):
    rect = plt.Rectangle((cx - w/2, cy - h/2), w, h,
                          fc=BG, ec=BLACK, lw=2.5, zorder=5)
    ax.add_patch(rect)
    bar_h = 0.6
    ax.plot([cx - w/2, cx + w/2], [cy + h/2 - bar_h, cy + h/2 - bar_h],
            color=BLACK, lw=1.5, zorder=6)
    ax.text(cx, cy + h/2 - bar_h/2, str(pid),
            fontsize=16, fontweight="bold", color=BLACK,
            ha="center", va="center", zorder=7, fontfamily=FONT)
    ax.text(cx, cy - 0.3, label,
            fontsize=13, color=BLACK, ha="center", va="center",
            zorder=7, fontfamily=FONT, linespacing=1.5, fontweight="bold")

def datastore(ax, cx, cy, w, h, label):
    ax.plot([cx - w/2, cx + w/2], [cy + h/2, cy + h/2],
            color=BLACK, lw=2, zorder=5)
    ax.plot([cx - w/2, cx + w/2], [cy - h/2, cy - h/2],
            color=BLACK, lw=2, zorder=5)
    ax.plot([cx - w/2, cx - w/2], [cy - h/2, cy + h/2],
            color=BLACK, lw=2, zorder=5)
    ax.text(cx, cy, label, fontsize=9.5, color=BLACK, fontweight="bold",
            ha="center", va="center", zorder=6, fontfamily=FONT,
            linespacing=1.2)

def arrow(ax, x1, y1, x2, y2, label="", fontsize=8.5,
          label_side="above", label_offset=0.2, label_pos=0.5,
          ha="center", rotation=None):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=BLACK, lw=1.3,
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
            bbox=dict(boxstyle="round,pad=0.2", facecolor=BG, edgecolor="none", alpha=0.9))

# ================================================================
#                    LEVEL 0 — CONTEXT DIAGRAM
# ================================================================
fig0, ax0 = plt.subplots(figsize=(30, 18))
fig0.patch.set_facecolor(BG)
ax0.set_facecolor(BG)
ax0.set_xlim(-3, 30)
ax0.set_ylim(0, 18)
ax0.set_aspect("equal")
ax0.axis("off")

# === CENTRAL PROCESS ===
CX, CY = 14, 8.5
PW, PH = 14, 5.5
P_TOP   = CY + PH/2
P_BOT   = CY - PH/2
P_LEFT  = CX - PW/2
P_RIGHT = CX + PW/2

context_process(ax0, CX, CY, PW, PH, "0", "VISTA\nVirtual Intelligent Service\nand Transaction Assistant")

# === EXTERNAL ENTITIES ===
ADMIN_CY = 17; ADMIN_W = 3.5; ADMIN_H = 1.2
CITIZEN_CX = 0.5; CITIZEN_W = 3.5; CITIZEN_H = 1.2
FIREBASE_CX = 27; FIREBASE_W = 3.5; FIREBASE_H = 1.2

entity(ax0, CX, ADMIN_CY, ADMIN_W, ADMIN_H, "LGU Admin")
entity(ax0, CITIZEN_CX, CY, CITIZEN_W, CITIZEN_H, "Citizen\n(User)")
entity(ax0, FIREBASE_CX, CY, FIREBASE_W, FIREBASE_H, "Firebase\nAuth")

# === EDGE COORDINATES ===
ADMIN_BOT    = ADMIN_CY - ADMIN_H/2
CITIZEN_RIGHT = CITIZEN_CX + CITIZEN_W/2
FIREBASE_LEFT = FIREBASE_CX - FIREBASE_W/2

# ======================================================================
#  ADMIN FLOWS (4 inputs down + 7 outputs up = 11 arrows on top edge)
# ======================================================================
admin_in  = ["Admin Credentials", "New Intent Data", "Retrain Command", "Query Review Actions"]
admin_out = ["System Analytics", "Feedbacks", "Unmatched Queries",
             "System Health", "Total Queries", "Knowledge Base Details", "Chat Logs"]

total_admin = len(admin_in) + len(admin_out)
spacing_a = (PW - 2) / (total_admin - 1)
start_ax = P_LEFT + 1

for i, lab in enumerate(admin_in):
    fx = start_ax + i * spacing_a
    arrow(ax0, fx, ADMIN_BOT, fx, P_TOP, lab,
          fontsize=8, label_side="above", rotation=90, label_offset=0)
for i, lab in enumerate(admin_out):
    fx = start_ax + (len(admin_in) + i) * spacing_a
    arrow(ax0, fx, P_TOP, fx, ADMIN_BOT, lab,
          fontsize=8, label_side="above", rotation=90, label_offset=0)

# ======================================================================
#  CITIZEN FLOWS (3 inputs right + 8 outputs left = 11 arrows on left)
# ======================================================================
citizen_in  = ["User Query + Language", "User Credentials", "Feedback"]
citizen_out = ["AI Responses", "Related Articles", "Chat History",
               "User Account Information", "LGU Services",
               "Office Directory", "Settings Detail", "Help Center Details"]

total_citizen = len(citizen_in) + len(citizen_out)
spacing_c = (PH - 0.4) / (total_citizen - 1)
start_cy = P_TOP - 0.2

for i, lab in enumerate(citizen_in):
    fy = start_cy - i * spacing_c
    arrow(ax0, CITIZEN_RIGHT, fy, P_LEFT, fy, lab,
          fontsize=8, label_side="above")
for i, lab in enumerate(citizen_out):
    fy = start_cy - (len(citizen_in) + i) * spacing_c
    arrow(ax0, P_LEFT, fy, CITIZEN_RIGHT, fy, lab,
          fontsize=8, label_side="above")

# ======================================================================
#  FIREBASE FLOWS (2 arrows on right edge)
# ======================================================================
arrow(ax0, P_RIGHT, CY + 0.6, FIREBASE_LEFT, CY + 0.6,
      "Auth Token Request", fontsize=8.5, label_side="above")
arrow(ax0, FIREBASE_LEFT, CY - 0.6, P_RIGHT, CY - 0.6,
      "Auth Token / User Profile", fontsize=8.5, label_side="above")

# === FIGURE LABEL ===
ax0.text(CX, 0.5, "Figure 1: Level 0 \u2014 Context Diagram",
         fontsize=15, fontweight="bold", color=BLACK,
         ha="center", va="center", fontfamily=FONT)

fig0.savefig("vista_dfd_level0.png", dpi=200, bbox_inches="tight",
             facecolor=BG, pad_inches=0.3)
plt.close(fig0)
print("Saved: vista_dfd_level0.png")

# ================================================================
#                    LEVEL 1 — DETAILED DFD
# ================================================================
fig1, ax1 = plt.subplots(figsize=(34, 42))
fig1.patch.set_facecolor(BG)
ax1.set_facecolor(BG)
ax1.set_xlim(-2, 30)
ax1.set_ylim(-3, 40)
ax1.set_aspect("equal")
ax1.axis("off")

# ===================== EXTERNAL ENTITIES =====================
EX_W, EX_H = 3.2, 1.4

# Firebase Auth — top-left
entity(ax1, 2, 36, EX_W, EX_H, "Firebase\nAuth")
FB_R = 2 + EX_W/2   # 3.6

# Citizen — middle-left
entity(ax1, 1.5, 25, EX_W, EX_H, "Citizen\n(User)")
CIT_R = 1.5 + EX_W/2  # 3.1

# LGU Admin — bottom-left
entity(ax1, 1.5, 8, EX_W, EX_H, "LGU Admin")
ADM_R = 1.5 + EX_W/2  # 3.1

# ===================== PROCESSES =====================
PW1, PH1 = 5.2, 2.2
pcx = 13
PL1 = pcx - PW1/2   # 10.4
PR1 = pcx + PW1/2   # 15.6

procs = [
    (pcx, 36,   "1.0", "User\nAuthentication"),
    (pcx, 30.5, "2.0", "Chat Query\nProcessing"),
    (pcx, 25,   "3.0", "Feedback\nCollection"),
    (pcx, 19.5, "4.0", "Service & Help\nDisplay"),
    (pcx, 14,   "5.0", "Knowledge Base\nManagement"),
    (pcx, 8.5,  "6.0", "Model\nRetraining"),
    (pcx, 3,    "7.0", "Analytics &\nReporting"),
]
for cx, cy, pid, lab in procs:
    process_box(ax1, cx, cy, PW1, PH1, pid, lab)

# ===================== DATA STORES =====================
DSW, DSH = 4.5, 1.0
dsx = 24.5
DSL = dsx - DSW/2   # 22.25

stores = [
    (dsx, 38,   "D1 | User Accounts"),
    (dsx, 34,   "D2 | Knowledge Base\n(Intents + Answers)"),
    (dsx, 30.5, "D3 | NLP Models"),
    (dsx, 27,   "D4 | Chat Logs"),
    (dsx, 23.5, "D5 | Article Repository"),
    (dsx, 19.5, "D6 | Unresolved Queries"),
    (dsx, 15.5, "D7 | Feedback Log"),
    (dsx, 11.5, "D8 | Service Directory"),
]
for sx, sy, lab in stores:
    datastore(ax1, sx, sy, DSW, DSH, lab)

# ===================== ARROWS =====================

# ===================================================================
#  1.0 USER AUTHENTICATION
# ===================================================================
# 1.0 → Firebase: Auth Token Request
arrow(ax1, PL1, 36.6, FB_R, 36.6, "Auth Token Request", fontsize=8.5)
# Firebase → 1.0: Auth Token / User Profile
arrow(ax1, FB_R, 35.6, PL1, 35.6, "Auth Token / User Profile", fontsize=8.5)
# Citizen → 1.0: User Credentials
arrow(ax1, CIT_R, 25.6, PL1, 36.2, "User Credentials", fontsize=8.5,
      label_pos=0.25, label_offset=0.4)
# 1.0 → Citizen: User Account Information
arrow(ax1, PL1, 35.4, CIT_R, 25.4, "User Account Information", fontsize=8.5,
      label_pos=0.75, label_offset=0.4)
# Admin → 1.0: Admin Credentials
arrow(ax1, ADM_R, 8.6, PL1, 35.0, "Admin Credentials", fontsize=8.5,
      label_pos=0.12, label_offset=0.5)
# 1.0 → D1: Write User Record
arrow(ax1, PR1, 36.6, DSL, 38.0, "User Record", fontsize=8.5)
# D1 → 1.0: Read User Data
arrow(ax1, DSL, 37.6, PR1, 36.2, "User Data", fontsize=8.5)

# ===================================================================
#  2.0 CHAT QUERY PROCESSING
# ===================================================================
# Citizen → 2.0: User Query + Language
arrow(ax1, CIT_R, 25.2, PL1, 31.0, "User Query + Language", fontsize=8.5,
      label_pos=0.35, label_offset=0.4)
# 2.0 → Citizen: AI Responses + Confidence
arrow(ax1, PL1, 30.0, CIT_R, 24.8, "AI Responses + Confidence", fontsize=8.5,
      label_pos=0.4, label_offset=0.4)
# 2.0 → Citizen: Related Articles
arrow(ax1, PL1, 29.8, CIT_R, 24.6, "Related Articles", fontsize=8.5,
      label_pos=0.7, label_offset=0.4)
# D2 → 2.0: Intent Labels + Answer Data
arrow(ax1, DSL, 33.6, PR1, 31.0, "Intent Labels +\nAnswer Data", fontsize=8.5)
# D3 → 2.0: Trained Model
arrow(ax1, DSL, 30.5, PR1, 30.5, "Trained Model", fontsize=8.5)
# D5 → 2.0: Article Content
arrow(ax1, DSL, 23.8, PR1, 30.0, "Article Content", fontsize=8.5,
      label_pos=0.6, label_offset=0.4)
# 2.0 → D4: Chat Session Data
arrow(ax1, PR1, 31.0, DSL, 27.4, "Chat Session Data", fontsize=8.5,
      label_pos=0.5, label_offset=0.4)
# 2.0 → D6: Unresolved Record
arrow(ax1, PR1, 30.0, DSL, 19.8, "Unresolved Record", fontsize=8.5,
      label_pos=0.35, label_offset=0.5)

# ===================================================================
#  3.0 FEEDBACK COLLECTION
# ===================================================================
# Citizen → 3.0: Feedback
arrow(ax1, CIT_R, 24.4, PL1, 25.0, "Feedback", fontsize=8.5)
# 3.0 → D7: Feedback Record
arrow(ax1, PR1, 25.0, DSL, 15.8, "Feedback Record", fontsize=8.5,
      label_pos=0.5, label_offset=0.5)

# ===================================================================
#  4.0 SERVICE & HELP DISPLAY
# ===================================================================
# 4.0 → Citizen: LGU Services
arrow(ax1, PL1, 20.8, CIT_R, 25.6, "LGU Services", fontsize=8.5,
      label_pos=0.65, label_offset=0.6)
# 4.0 → Citizen: Office Directory
arrow(ax1, PL1, 20.2, CIT_R, 25.3, "Office Directory", fontsize=8.5,
      label_pos=0.45, label_offset=0.6)
# 4.0 → Citizen: Chat History
arrow(ax1, PL1, 19.6, CIT_R, 24.8, "Chat History", fontsize=8.5,
      label_pos=0.75, label_offset=-0.4)
# 4.0 → Citizen: Settings Detail
arrow(ax1, PL1, 19.0, CIT_R, 24.4, "Settings Detail", fontsize=8.5,
      label_pos=0.55, label_offset=-0.6)
# 4.0 → Citizen: Help Center Details
arrow(ax1, PL1, 18.4, CIT_R, 24.0, "Help Center Details", fontsize=8.5,
      label_pos=0.35, label_offset=-0.6)
# D4 → 4.0: Chat History Data
arrow(ax1, DSL, 26.6, PR1, 19.6, "Chat History Data", fontsize=8.5,
      label_pos=0.5, label_offset=0.4)
# D8 → 4.0: Service & Department Data
arrow(ax1, DSL, 11.8, PR1, 18.6, "Service &\nDepartment Data", fontsize=8.5,
      label_pos=0.5, label_offset=0.5)
# D2 → 4.0: KB Display Data
arrow(ax1, DSL, 33.8, PR1, 20.6, "KB Display Data", fontsize=8.5,
      label_pos=0.7, label_offset=0.5)

# ===================================================================
#  5.0 KNOWLEDGE BASE MANAGEMENT
# ===================================================================
# Admin → 5.0: New Intent Data
arrow(ax1, ADM_R, 8.4, PL1, 14.4, "New Intent Data", fontsize=8.5,
      label_pos=0.4, label_offset=0.4)
# Admin → 5.0: Query Review Actions
arrow(ax1, ADM_R, 8.2, PL1, 13.6, "Query Review Actions", fontsize=8.5,
      label_pos=0.5, label_offset=-0.4)
# 5.0 → Admin: Knowledge Base Details
arrow(ax1, PL1, 14.0, ADM_R, 8.8, "Knowledge Base Details", fontsize=8.5,
      label_pos=0.65, label_offset=0.5)
# 5.0 → Admin: Unmatched Queries
arrow(ax1, PL1, 13.4, ADM_R, 8.0, "Unmatched Queries", fontsize=8.5,
      label_pos=0.7, label_offset=-0.4)
# 5.0 → D2: New/Updated Intents
arrow(ax1, PR1, 14.4, DSL, 33.4, "New/Updated Intents", fontsize=8.5,
      label_pos=0.4, label_offset=0.5)
# D6 → 5.0: Unresolved List
arrow(ax1, DSL, 19.2, PR1, 14.2, "Unresolved List", fontsize=8.5,
      label_pos=0.5, label_offset=0.4)
# 5.0 → D6: Dismiss/Link Updates
arrow(ax1, PR1, 13.6, DSL, 19.8, "Dismiss/Link Updates", fontsize=8.5,
      label_pos=0.5, label_offset=-0.4)

# ===================================================================
#  6.0 MODEL RETRAINING
# ===================================================================
# Admin → 6.0: Retrain Command
arrow(ax1, ADM_R, 7.8, PL1, 8.8, "Retrain Command", fontsize=8.5)
# 6.0 → Admin: System Health
arrow(ax1, PL1, 8.2, ADM_R, 7.4, "System Health", fontsize=8.5)
# D2 → 6.0: Training Data
arrow(ax1, DSL, 33.2, PR1, 9.0, "Training Data", fontsize=8.5,
      label_pos=0.7, label_offset=0.6)
# 6.0 → D3: Updated Model
arrow(ax1, PR1, 8.5, DSL, 30.2, "Updated Model", fontsize=8.5,
      label_pos=0.3, label_offset=0.5)

# ===================================================================
#  7.0 ANALYTICS & REPORTING
# ===================================================================
# 7.0 → Admin: System Analytics
arrow(ax1, PL1, 3.6, ADM_R, 7.6, "System Analytics", fontsize=8.5,
      label_pos=0.55, label_offset=0.6)
# 7.0 → Admin: Total Queries
arrow(ax1, PL1, 3.2, ADM_R, 7.3, "Total Queries", fontsize=8.5,
      label_pos=0.4, label_offset=0.5)
# 7.0 → Admin: Feedbacks
arrow(ax1, PL1, 2.8, ADM_R, 7.0, "Feedbacks", fontsize=8.5,
      label_pos=0.5, label_offset=-0.5)
# 7.0 → Admin: Chat Logs
arrow(ax1, PL1, 2.4, ADM_R, 6.7, "Chat Logs", fontsize=8.5,
      label_pos=0.3, label_offset=-0.6)
# D4 → 7.0: Chat Log Data
arrow(ax1, DSL, 26.8, PR1, 3.4, "Chat Log Data", fontsize=8.5,
      label_pos=0.6, label_offset=0.5)
# D7 → 7.0: Feedback Data
arrow(ax1, DSL, 15.2, PR1, 3.0, "Feedback Data", fontsize=8.5,
      label_pos=0.5, label_offset=0.5)
# D6 → 7.0: Unresolved Data
arrow(ax1, DSL, 19.0, PR1, 2.6, "Unresolved Data", fontsize=8.5,
      label_pos=0.4, label_offset=-0.5)

# === FIGURE LABEL ===
ax1.text(14, -2, "Figure 2: Level 1 \u2014 Detailed Data Flow Diagram",
         fontsize=16, fontweight="bold", color=BLACK,
         ha="center", va="center", fontfamily=FONT)

fig1.savefig("vista_dfd_level1.png", dpi=200, bbox_inches="tight",
             facecolor=BG, pad_inches=0.3)
plt.close(fig1)
print("Saved: vista_dfd_level1.png")

