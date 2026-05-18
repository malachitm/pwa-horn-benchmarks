import csv
import json
import math
import re
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_200708 = os.path.join(DATA_DIR, "benchmark_results_20260428_200708.csv")
OUT_PNG = os.path.join(DATA_DIR, "samples_summary.png")


def extract_stats(result_str):
    """Extract attempt_count and synth_time_seconds stats from the Result JSON."""
    match = re.search(r'\{.*\}', result_str, re.DOTALL)
    if not match:
        return None
    data = json.loads(match.group())
    ac = data["attempt_count"]
    st = data["synth_time_seconds"]
    return {
        "samples":      ac["samples"],
        "ac_mean":      ac["mean"],
        "ac_median":    ac["median"],
        "st_mean":      st["mean"],
        "st_median":    st["median"],
    }


def load_file(path):
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats = extract_stats(row["Result"])
            if stats is not None:
                p1 = float(row["Param_1"])
                p2 = float(row["Param_2"])
                p3 = float(row["Param_3"])
                p4 = float(row["Param_4"])
                rows.append({
                    "filename":  row["Filename"],
                    "param1":    p1,
                    "param2":    p2,
                    "param3":    p3,
                    "param4":    p4,
                    "param5":    float(row["Param_5"]),
                    "diff":      p2 - p1,
                    "diff_diff": (p2 - p1) - (p4 - p3),
                    **stats,
                })
    return rows


def avg(values):
    return sum(values) / len(values) if values else float('nan')


def median(values):
    if not values:
        return float('nan')
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def std(values):
    if len(values) < 2:
        return float('nan')
    m = avg(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def stats_row(label, group):
    samples = [r["samples"] for r in group]
    st_mean = [r["st_mean"] for r in group]
    return (
        label,
        len(group),
        avg(samples),
        median(samples),
        std(samples),
        avg(st_mean),
    )


# ── Load data ─────────────────────────────────────────────────────────────────
rows = load_file(FILE_200708)
diffs      = sorted(set(r["diff"]      for r in rows))
param5s    = sorted(set(r["param5"]    for r in rows))
diff_diffs = sorted(set(r["diff_diff"] for r in rows))

# ── Table 1: overall + grouped by diff ────────────────────────────────────────
t1_cols   = ["Category", "# Problems", "Avg Samples", "Median Samples", "Std Samples", "Avg Synth Time (s)"]
t1_entries = [stats_row("Overall (all problems)", rows)]
for d in diffs:
    g = [r for r in rows if r["diff"] == d]
    t1_entries.append(stats_row(f"Param_2 − Param_1 = {d:g}", g))

t1_data = [
    [lbl, str(n), f"{av:.2f}", f"{med:.2f}", f"{sd:.2f}", f"{st:.4f}"]
    for lbl, n, av, med, sd, st in t1_entries
]

# ── Table 2: (diff × param5) with extra stats ─────────────────────────────────
t2_cols   = ["Param_2−Param_1", "Param_5", "# Problems", "Avg Samples", "Median Samples", "Std Samples", "Avg Synth Time (s)"]
t2_entries = []
for d in diffs:
    for p5 in param5s:
        g = [r for r in rows if r["diff"] == d and r["param5"] == p5]
        if not g:
            continue
        _, n, av, med, sd, st = stats_row("", g)
        t2_entries.append((f"{d:g}", f"{p5:g}", n, av, med, sd, st))

t2_data = [
    [d_str, p5_str, str(n), f"{av:.2f}", f"{med:.2f}", f"{sd:.2f}", f"{st:.4f}"]
    for d_str, p5_str, n, av, med, sd, st in t2_entries
]

# ── Table 3: grouped by (P2-P1) - (P4-P3) ────────────────────────────────────
t3_cols   = ["(P2−P1)−(P4−P3)", "# Problems", "Avg Samples", "Median Samples", "Std Samples", "Avg Synth Time (s)"]
t3_entries = [stats_row("Overall (all problems)", rows)]
for dd in diff_diffs:
    g = [r for r in rows if r["diff_diff"] == dd]
    t3_entries.append(stats_row(f"{dd:g}", g))

t3_data = [
    [lbl, str(n), f"{av:.2f}", f"{med:.2f}", f"{sd:.2f}", f"{st:.4f}"]
    for lbl, n, av, med, sd, st in t3_entries
]

# ── Print to stdout ────────────────────────────────────────────────────────────
W = 110
print("=" * W)
print("TABLE 1 — By (Param_2 − Param_1)")
print("=" * W)
hdr = f"{'Category':<35} {'#':>6} {'Avg Samp':>10} {'Med Samp':>10} {'Std Samp':>10} {'Avg Synth(s)':>14}"
print(hdr)
print("-" * W)
for lbl, n, av, med, sd, st in t1_entries:
    print(f"{lbl:<35} {n:>6} {av:>10.2f} {med:>10.2f} {sd:>10.2f} {st:>14.4f}")

print()
print("=" * W)
print("TABLE 2 — By (Param_2 − Param_1) × Param_5")
print("=" * W)
hdr2 = f"{'P2-P1':>10} {'P5':>8} {'#':>6} {'Avg Samp':>10} {'Med Samp':>10} {'Std Samp':>10} {'Avg Synth(s)':>14}"
print(hdr2)
print("-" * W)
for d_str, p5_str, n, av, med, sd, st in t2_entries:
    print(f"{d_str:>10} {p5_str:>8} {n:>6} {av:>10.2f} {med:>10.2f} {sd:>10.2f} {st:>14.4f}")

print()
print("=" * W)
print("TABLE 3 — By (Param_2−Param_1) − (Param_4−Param_3)")
print("=" * W)
hdr3 = f"{'(P2-P1)-(P4-P3)':>18} {'#':>6} {'Avg Samp':>10} {'Med Samp':>10} {'Std Samp':>10} {'Avg Synth(s)':>14}"
print(hdr3)
print("-" * W)
for lbl, n, av, med, sd, st in t3_entries:
    print(f"{lbl:>18} {n:>6} {av:>10.2f} {med:>10.2f} {sd:>10.2f} {st:>14.4f}")

# ── Render PNG ────────────────────────────────────────────────────────────────
HEADER_COLOR  = "#2c5f8a"
OVERALL_COLOR = "#e8f5e9"
ROW_COLORS    = ["#dce9f5", "#f0f5fb"]

def make_table(ax, data, col_labels, title, overall_row=False):
    ax.axis("off")
    tbl = ax.table(cellText=data, colLabels=col_labels, cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.auto_set_column_width(list(range(len(col_labels))))
    for col in range(len(col_labels)):
        cell = tbl[0, col]
        cell.set_facecolor(HEADER_COLOR)
        cell.set_text_props(color="white", fontweight="bold")
    for row in range(1, len(data) + 1):
        if overall_row and row == 1:
            color = OVERALL_COLOR
        else:
            offset = 2 if overall_row else 1
            color = ROW_COLORS[(row - offset) % 2]
        for col in range(len(col_labels)):
            tbl[row, col].set_facecolor(color)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=6)

n1 = len(t1_data)
n2 = len(t2_data)
n3 = len(t3_data)
fig = plt.figure(figsize=(14, 1.8 + n1 * 0.38 + 1.8 + n2 * 0.38 + 1.8 + n3 * 0.38))
gs  = gridspec.GridSpec(3, 1, figure=fig, hspace=0.6)

ax1 = fig.add_subplot(gs[0])
make_table(ax1, t1_data, t1_cols,
           "Table 1 — Average Samples by (Param_2 − Param_1)", overall_row=True)

ax2 = fig.add_subplot(gs[1])
make_table(ax2, t2_data, t2_cols,
           "Table 2 — Statistics by (Param_2 − Param_1) × Param_5", overall_row=False)

ax3 = fig.add_subplot(gs[2])
make_table(ax3, t3_data, t3_cols,
           "Table 3 — Statistics by (Param_2−Param_1) − (Param_4−Param_3)", overall_row=True)

plt.savefig(OUT_PNG, dpi=150, bbox_inches="tight")
print(f"\nSaved PNG → {OUT_PNG}")
