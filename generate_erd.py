"""
VISTA - Entity-Relationship Diagram Generator (Crow's Foot Notation)
Generates a complete ERD as a high-resolution PNG image.

Entity names and attributes are aligned with the actual VISTA system:
  - SQLite tables:  chat_logs, feedback, unresolved_queries  (database.py)
  - CSV data:       intents.csv
  - JSON stores:    answers.json, articles.json, offices.json
  - ML artifacts:   best_model.pkl, metrics.json
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ========================== CONFIG ==========================
FIG_W, FIG_H = 42, 42
BG_COLOR = "#ffffff"
CARD_BG = "#ffffff"
CARD_BORDER = "#333333"
CARD_HEADER_BG = "#333333"
CARD_HEADER_TEXT = "#ffffff"
ATTR_TEXT = "#222222"
PK_COLOR = "#000000"
FK_COLOR = "#555555"
LINE_COLOR = "#444444"
TITLE_COLOR = "#111111"
SUBTITLE_COLOR = "#555555"
LEGEND_BG = "#f5f5f5"
TYPE_COLOR = "#666666"
SEPARATOR_COLOR = "#999999"

# ========================== ENTITIES ==========================
X1, X2, X3 = 1, 16.5, 32
Y1, Y2, Y3, Y4 = 38, 28, 18, 8

entities = {
    "chat_logs": {
        "pos": (X1, Y1),
        "attrs": [
            ("PK", "id", "INTEGER"),
            ("", "question", "TEXT"),
            ("FK", "intent", "TEXT"),
            ("", "language", "TEXT"),
            ("", "confidence", "REAL"),
            ("", "created_at", "TIMESTAMP"),
        ]
    },
    "feedback": {
        "pos": (X1, Y2),
        "attrs": [
            ("PK", "id", "INTEGER"),
            ("", "question", "TEXT"),
            ("", "answer", "TEXT"),
            ("FK", "intent", "TEXT"),
            ("", "helpful", "BOOLEAN"),
            ("", "language", "TEXT"),
            ("", "comment", "TEXT"),
            ("", "created_at", "TIMESTAMP"),
        ]
    },
    "unresolved_queries": {
        "pos": (X1, Y3),
        "attrs": [
            ("PK", "id", "INTEGER"),
            ("", "question", "TEXT"),
            ("FK", "predicted_intent", "TEXT"),
            ("", "confidence", "REAL"),
            ("", "created_at", "TIMESTAMP"),
        ]
    },
    "intents": {
        "pos": (X2, Y1),
        "attrs": [
            ("PK", "id", "INTEGER"),
            ("FK", "department", "TEXT"),
            ("FK", "intent", "TEXT"),
            ("", "language", "TEXT"),
            ("", "question", "TEXT"),
            ("", "answer", "TEXT"),
            ("", "source", "TEXT"),
            ("", "tags", "TEXT"),
        ]
    },
    "answers": {
        "pos": (X2, Y2),
        "attrs": [
            ("PK", "intent_key", "TEXT"),
            ("FK", "department", "TEXT"),
            ("", "en_answer", "TEXT"),
            ("", "tl_answer", "TEXT"),
            ("", "bis_answer", "TEXT"),
        ]
    },
    "articles": {
        "pos": (X2, Y3),
        "attrs": [
            ("PK", "id", "INTEGER"),
            ("", "title", "TEXT"),
            ("FK", "department", "TEXT"),
            ("", "content", "TEXT"),
        ]
    },
    "office_directory": {
        "pos": (X2, Y4),
        "attrs": [
            ("PK", "office_id", "TEXT"),
            ("", "name", "TEXT"),
            ("", "head_of_office", "JSON"),
            ("", "contact", "JSON"),
            ("", "location", "JSON"),
            ("", "operating_hours", "JSON"),
        ]
    },
    "nlp_model": {
        "pos": (X3, Y1),
        "attrs": [
            ("PK", "model_name", "TEXT"),
            ("", "model_file", "TEXT"),
            ("", "accuracy", "REAL"),
            ("", "best_model", "TEXT"),
            ("", "trained_at", "TIMESTAMP"),
        ]
    },
    "training_metrics": {
        "pos": (X3, Y2),
        "attrs": [
            ("PK", "metric_id", "INTEGER"),
            ("FK", "model_name", "TEXT"),
            ("", "intent_name", "TEXT"),
            ("", "precision", "REAL"),
            ("", "recall", "REAL"),
            ("", "f1_score", "REAL"),
            ("", "support", "INTEGER"),
        ]
    },
}

# Card dimensions
CARD_W = 7.5
HEADER_H = 0.9
ROW_H = 0.50
CARD_RADIUS = 0.12

def get_card_height(entity):
    return HEADER_H + len(entity["attrs"]) * ROW_H + 0.25

def get_card_edge(entity, side):
    x, y = entity["pos"]
    h = get_card_height(entity)
    cx, cy = x + CARD_W / 2, y - h / 2
    if side == "left":
        return (x, cy)
    elif side == "right":
        return (x + CARD_W, cy)
    elif side == "top":
        return (cx, y)
    elif side == "bottom":
        return (cx, y - h)

# ==================== DRAW FUNCTIONS ====================

def draw_entity(ax, name, entity):
    x, y = entity["pos"]
    attrs = entity["attrs"]
    h = get_card_height(entity)

    body = FancyBboxPatch(
        (x, y - h), CARD_W, h,
        boxstyle=f"round,pad={CARD_RADIUS}",
        facecolor=CARD_BG, edgecolor=CARD_BORDER, linewidth=1.8, zorder=2
    )
    ax.add_patch(body)

    header = FancyBboxPatch(
        (x, y - HEADER_H), CARD_W, HEADER_H,
        boxstyle=f"round,pad={CARD_RADIUS}",
        facecolor=CARD_HEADER_BG, edgecolor=CARD_HEADER_BG, linewidth=0, zorder=3
    )
    ax.add_patch(header)

    mask = plt.Rectangle((x, y - HEADER_H), CARD_W, HEADER_H * 0.5,
                          facecolor=CARD_HEADER_BG, edgecolor="none", zorder=3)
    ax.add_patch(mask)

    ax.text(x + CARD_W / 2, y - HEADER_H / 2, name,
            fontsize=10, fontweight="bold", color=CARD_HEADER_TEXT,
            ha="center", va="center", zorder=4, fontfamily="monospace")

    sep_y = y - HEADER_H - 0.04
    ax.plot([x + 0.25, x + CARD_W - 0.25], [sep_y, sep_y],
            color=SEPARATOR_COLOR, linewidth=0.7, zorder=4)

    for i, (key_type, attr_name, attr_type) in enumerate(attrs):
        ay = y - HEADER_H - 0.32 - i * ROW_H

        if key_type == "PK":
            ax.text(x + 0.35, ay, "PK", fontsize=6.5, fontweight="bold",
                    color=PK_COLOR, ha="left", va="center", zorder=4,
                    fontfamily="monospace",
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="#e8e8e8",
                              edgecolor=PK_COLOR, linewidth=0.6))
        elif key_type == "FK":
            ax.text(x + 0.35, ay, "FK", fontsize=6.5, fontweight="bold",
                    color=FK_COLOR, ha="left", va="center", zorder=4,
                    fontfamily="monospace",
                    bbox=dict(boxstyle="round,pad=0.12", facecolor="#eeeeee",
                              edgecolor=FK_COLOR, linewidth=0.6))

        name_x = x + 1.2 if key_type else x + 0.45
        ax.text(name_x, ay, attr_name, fontsize=8, color=ATTR_TEXT,
                ha="left", va="center", zorder=4, fontfamily="monospace")

        ax.text(x + CARD_W - 0.35, ay, attr_type, fontsize=7,
                color=TYPE_COLOR, ha="right", va="center", zorder=4,
                fontfamily="monospace", style="italic")

def draw_crow_foot(ax, x, y, direction, cardinality):
    size = 0.22
    lw = 1.5

    if direction == "right": dx, dy = 1, 0
    elif direction == "left": dx, dy = -1, 0
    elif direction == "up": dx, dy = 0, 1
    elif direction == "down": dx, dy = 0, -1

    perp_x, perp_y = -dy, dx
    back_x, back_y = -dx, -dy

    if "many" in cardinality:
        ax.plot([x, x + back_x * size], [y, y + back_y * size],
                color=LINE_COLOR, linewidth=lw, zorder=5, solid_capstyle="round")
        ax.plot([x, x + back_x * size + perp_x * size * 0.7], 
                [y, y + back_y * size + perp_y * size * 0.7],
                color=LINE_COLOR, linewidth=lw, zorder=5, solid_capstyle="round")
        ax.plot([x, x + back_x * size - perp_x * size * 0.7], 
                [y, y + back_y * size - perp_y * size * 0.7],
                color=LINE_COLOR, linewidth=lw, zorder=5, solid_capstyle="round")
                
        bar_offset = size * 1.15
        bx, by = x + back_x * bar_offset, y + back_y * bar_offset
        ax.plot([bx + perp_x * size * 0.6, bx - perp_x * size * 0.6],
                [by + perp_y * size * 0.6, by - perp_y * size * 0.6],
                color=LINE_COLOR, linewidth=lw, zorder=5, solid_capstyle="round")

    if "one" in cardinality and "many" not in cardinality:
        for offset in [size * 0.4, size * 0.85]:
            bx, by = x + back_x * offset, y + back_y * offset
            ax.plot([bx + perp_x * size * 0.5, bx - perp_x * size * 0.5],
                    [by + perp_y * size * 0.5, by - perp_y * size * 0.5],
                    color=LINE_COLOR, linewidth=lw, zorder=5, solid_capstyle="round")

    if "zero" in cardinality:
        circle_offset = size * 1.6
        cx, cy = x + back_x * circle_offset, y + back_y * circle_offset
        circle = plt.Circle((cx, cy), size * 0.22, fill=False,
                             edgecolor=LINE_COLOR, linewidth=lw, zorder=5)
        ax.add_patch(circle)

def draw_relationship(ax, e1_name, e1_card, e1_side,
                      e2_name, e2_card, e2_side,
                      label="", waypoints=None, label_offset_y=0.30):
    p1 = get_card_edge(entities[e1_name], e1_side)
    p2 = get_card_edge(entities[e2_name], e2_side)
    all_points = [p1] + (waypoints or []) + [p2]

    for i in range(len(all_points) - 1):
        ax.plot([all_points[i][0], all_points[i + 1][0]],
                [all_points[i][1], all_points[i + 1][1]],
                color=LINE_COLOR, linewidth=1.2, zorder=1, solid_capstyle="round")

    def get_approach_direction(from_pt, to_pt):
        dx, dy = to_pt[0] - from_pt[0], to_pt[1] - from_pt[1]
        if abs(dx) > abs(dy): return "right" if dx > 0 else "left"
        else: return "up" if dy > 0 else "down"

    dir1 = get_approach_direction(all_points[1] if waypoints else p2, p1)
    draw_crow_foot(ax, p1[0], p1[1], dir1, e1_card)

    dir2 = get_approach_direction(all_points[-2] if waypoints else p1, p2)
    draw_crow_foot(ax, p2[0], p2[1], dir2, e2_card)

    if label:
        mid_idx = len(all_points) // 2
        if len(all_points) % 2 == 0:
            mx = (all_points[mid_idx - 1][0] + all_points[mid_idx][0]) / 2
            my = (all_points[mid_idx - 1][1] + all_points[mid_idx][1]) / 2
        else:
            mx, my = all_points[mid_idx]

        ax.text(mx, my + label_offset_y, label, fontsize=7.5, color="#333333",
                ha="center", va="center", zorder=6, style="italic",
                fontfamily="sans-serif",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=BG_COLOR,
                          edgecolor="none", alpha=0.95))

# ==================== MAIN RENDER ====================

fig, ax = plt.subplots(1, 1, figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)
ax.set_xlim(-1, FIG_W + 1)
ax.set_ylim(-1, FIG_H)
ax.set_aspect("equal")
ax.axis("off")

ax.text(FIG_W / 2, FIG_H - 1.0, "VISTA -- Entity-Relationship Diagram",
        fontsize=22, fontweight="bold", color=TITLE_COLOR,
        ha="center", va="center", fontfamily="serif")
ax.text(FIG_W / 2, FIG_H - 2.0,
        "Virtual Intelligent Services and Transactions Assistant  |  Crow's Foot Notation",
        fontsize=12, color=SUBTITLE_COLOR,
        ha="center", va="center", fontfamily="serif")

for name, entity in entities.items():
    draw_entity(ax, name, entity)

# ==================== RELATIONSHIPS ====================

# 1) answers ||--o{ intents : "defines training data for"
draw_relationship(ax, "answers", "one", "top",
                  "intents", "zero_or_many", "bottom",
                  label="defines training data for")

# 2) answers ||--o{ chat_logs : "provides response to"
draw_relationship(ax, "answers", "one", "left",
                  "chat_logs", "zero_or_many", "right",
                  waypoints=[(13.0, get_card_edge(entities["answers"], "left")[1]), 
                             (13.0, get_card_edge(entities["chat_logs"], "right")[1])],
                  label="provides response to", label_offset_y=0.35)

# 3) answers ||--o{ feedback : "receives feedback on"
draw_relationship(ax, "answers", "one", "left",
                  "feedback", "zero_or_many", "right",
                  waypoints=[(14.0, get_card_edge(entities["answers"], "left")[1]), 
                             (14.0, get_card_edge(entities["feedback"], "right")[1])],
                  label="receives feedback on")

# 4) answers ||--o{ unresolved_queries : "fails to match"
draw_relationship(ax, "answers", "one", "left",
                  "unresolved_queries", "zero_or_many", "right",
                  waypoints=[(12.0, get_card_edge(entities["answers"], "left")[1]), 
                             (12.0, get_card_edge(entities["unresolved_queries"], "right")[1])],
                  label="fails to match", label_offset_y=0.35)

# 5) answers ||--o{ articles : "relates to"
draw_relationship(ax, "answers", "one", "bottom",
                  "articles", "zero_or_many", "top",
                  label="relates to")

# 6) intents }o--|| nlp_model : "trains"
draw_relationship(ax, "intents", "zero_or_many", "right",
                  "nlp_model", "one", "left",
                  waypoints=[(28.0, get_card_edge(entities["intents"], "right")[1]), 
                             (28.0, get_card_edge(entities["nlp_model"], "left")[1])],
                  label="trains")

# 7) nlp_model ||--o{ training_metrics : "produces"
draw_relationship(ax, "nlp_model", "one", "bottom",
                  "training_metrics", "zero_or_many", "top",
                  label="produces")

# 8) nlp_model ||--o{ chat_logs : "classifies into"
draw_relationship(ax, "nlp_model", "one", "top",
                  "chat_logs", "zero_or_many", "top",
                  waypoints=[(get_card_edge(entities["nlp_model"], "top")[0], 40.0), 
                             (get_card_edge(entities["chat_logs"], "top")[0], 40.0)],
                  label="classifies into", label_offset_y=0.35)

# 9) office_directory ||--o{ articles : "categorizes"
draw_relationship(ax, "office_directory", "one", "top",
                  "articles", "zero_or_many", "bottom",
                  label="categorizes")

# 10) office_directory ||--o{ answers : "manages knowledge"
draw_relationship(ax, "office_directory", "one", "right",
                  "answers", "zero_or_many", "right",
                  waypoints=[(25.5, get_card_edge(entities["office_directory"], "right")[1]), 
                             (25.5, get_card_edge(entities["answers"], "right")[1])],
                  label="manages knowledge", label_offset_y=0.35)

# 11) office_directory ||--o{ intents : "handles inquiries"
draw_relationship(ax, "office_directory", "one", "right",
                  "intents", "zero_or_many", "right",
                  waypoints=[(26.5, get_card_edge(entities["office_directory"], "right")[1]), 
                             (26.5, get_card_edge(entities["intents"], "right")[1])],
                  label="handles inquiries", label_offset_y=0.35)

# ==================== LEGEND ====================
legend_x, legend_y = X1, Y4
legend_w, legend_h = CARD_W, 4.2

legend_box = FancyBboxPatch(
    (legend_x, legend_y - legend_h), legend_w, legend_h,
    boxstyle=f"round,pad={CARD_RADIUS}",
    facecolor=LEGEND_BG, edgecolor=CARD_BORDER, linewidth=1.2, zorder=2
)
ax.add_patch(legend_box)

ax.text(legend_x + legend_w / 2, legend_y - 0.35, "LEGEND",
        fontsize=10, fontweight="bold", color=TITLE_COLOR,
        ha="center", va="center", zorder=4, fontfamily="monospace")

legend_items = [
    (1.0, "----||----", "Exactly One (1)"),
    (1.7, "----o{----", "Zero or Many (0..*)"),
    (2.4, "  PK  ", "Primary Key"),
    (3.1, "  FK  ", "Foreign Key"),
]

for dy, symbol, desc in legend_items:
    ax.text(legend_x + 0.5, legend_y - dy - 0.15, symbol,
            fontsize=8.5, fontweight="bold", color=TITLE_COLOR,
            ha="left", va="center", zorder=4, fontfamily="monospace")
    ax.text(legend_x + 3.0, legend_y - dy - 0.15, desc,
            fontsize=8.5, color=ATTR_TEXT,
            ha="left", va="center", zorder=4, fontfamily="sans-serif")

# ==================== SAVE ====================
output_path = "vista_erd.png"
plt.savefig(output_path, dpi=200, bbox_inches="tight",
            facecolor=BG_COLOR, edgecolor="none", pad_inches=0.5)
plt.close()
print(f"[OK] ERD saved to: {output_path}")
