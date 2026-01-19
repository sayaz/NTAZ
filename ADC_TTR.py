import re
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# USER EDIT SECTION (no prompts, no arguments)
# ============================================================

# Global AND constraints: every selected column must contain ALL of these
BASE_REQUIRED = [
    "MXS22LPPASS_ADC_HS_RFE0_REFVDDA_NOMV"
]

# OR-of-AND groups: OR between groups, AND inside each group
# Example:
#   (ADC AND CHANNEL AND inl) OR (ADC AND CHANNEL AND bc)
FILTER_GROUPS = [
    ["ADC", "CHANNEL", "inl"],
    # ["ADC", "CHANNEL", "bc"],
]

# Global NOT: columns containing ANY of these keywords will be excluded
EXCLUDE_KEYWORDS = []  # e.g., ["TEMP", "DEBUG"]

CSV_PATH = "/mnt/data/output.csv"

# CSV structure: row 0 = column names; rows 1..4 are extra header rows
SKIP_EXTRA_HEADER_ROWS = [1, 2, 3, 4]

# First N columns are metadata/header-like; do not consider them for filtering
HEADER_LIKE_FIRST_N_COLS = 10

# ============================================================


def build_filter_title(base_required, filter_groups, exclude_keys, max_len=140):
    """
    Build a figure title that describes the applied filter logic.
    Truncates if it becomes too long.
    """
    parts = []

    if base_required:
        parts.append(" AND ".join(base_required))

    if filter_groups:
        group_strs = []
        for g in filter_groups:
            group_strs.append("(" + " AND ".join(g) + ")")
        parts.append(" OR ".join(group_strs))

    title = "Filter: " + " AND ".join(parts) if parts else "Filter: (none)"

    if exclude_keys:
        title += " | EXCLUDE: " + ", ".join(exclude_keys)

    # Avoid ridiculously long titles on plots
    if len(title) > max_len:
        title = title[: max_len - 3] + "..."

    return title


# ---------------------------------------------------------------------
# Load CSV
# ---------------------------------------------------------------------
df = pd.read_csv(CSV_PATH, header=0, skiprows=SKIP_EXTRA_HEADER_ROWS)

# Validate DIE_X / DIE_Y (used to label each row)
if ("DIE_X" not in df.columns) or ("DIE_Y" not in df.columns):
    raise ValueError("Expected columns 'DIE_X' and 'DIE_Y' were not found in the CSV.")

# ---------------------------------------------------------------------
# Normalize config to case-insensitive matching
# ---------------------------------------------------------------------
base_required = [str(k).strip().upper() for k in BASE_REQUIRED if str(k).strip()]
filter_groups = [[str(k).strip().upper() for k in g if str(k).strip()] for g in FILTER_GROUPS]
exclude_keys = [str(k).strip().upper() for k in EXCLUDE_KEYWORDS if str(k).strip()]

if not filter_groups or all(len(g) == 0 for g in filter_groups):
    raise ValueError("FILTER_GROUPS is empty. Put at least one group like ['ADC','CHANNEL','inl'].")

def col_matches(colname: str) -> bool:
    cu = str(colname).upper()

    # Global exclusion: if any excluded keyword appears, reject
    for ek in exclude_keys:
        if ek in cu:
            return False

    # Global AND: must contain all base-required tokens
    for bk in base_required:
        if bk not in cu:
            return False

    # OR-of-AND: match if any group matches completely
    for group in filter_groups:
        if all(k in cu for k in group):
            return True

    return False

# ---------------------------------------------------------------------
# Filter columns (excluding first HEADER_LIKE_FIRST_N_COLS)
# ---------------------------------------------------------------------
first_n_cols = list(df.columns[:HEADER_LIKE_FIRST_N_COLS])
search_space_cols = [c for c in df.columns if c not in first_n_cols]

filtered_cols = [c for c in search_space_cols if col_matches(c)]

if not filtered_cols:
    raise ValueError(
        "No columns matched.\n"
        f"BASE_REQUIRED={BASE_REQUIRED}\n"
        f"FILTER_GROUPS={FILTER_GROUPS}\n"
        f"EXCLUDE_KEYWORDS={EXCLUDE_KEYWORDS}\n"
        "Tip: verify exact substrings in column names, or relax FILTER_GROUPS."
    )

# ---------------------------------------------------------------------
# Sort columns: odd CHANNELs first, then even CHANNELs
# Non-channel columns go last
# ---------------------------------------------------------------------
chan_re = re.compile(r"CHANNEL\s*(\d+)", re.IGNORECASE)

def channel_sort_key(colname: str):
    s = str(colname)
    m = chan_re.search(s)
    if not m:
        return (2, 0, s.upper())  # non-channel last
    ch = int(m.group(1))
    parity_group = 0 if (ch % 2 == 1) else 1  # odd first
    return (parity_group, ch, s.upper())

filtered_cols_sorted = sorted(filtered_cols, key=channel_sort_key)

print(f"Matched {len(filtered_cols_sorted)} columns.")
print("First 12 columns in plot order:", filtered_cols_sorted[:12])

# ---------------------------------------------------------------------
# Plot: one line per row, labeled by (DIE_X, DIE_Y)
# ---------------------------------------------------------------------
title = build_filter_title(base_required, filter_groups, exclude_keys)

x_labels = filtered_cols_sorted
plt.figure(figsize=(max(10, 0.35 * len(x_labels)), 6))

for _, row in df.iterrows():
    die_x = row["DIE_X"]
    die_y = row["DIE_Y"]
    y = pd.to_numeric(row[filtered_cols_sorted], errors="coerce")
    plt.plot(x_labels, y.values, marker="o", linewidth=1, label=f"({die_x},{die_y})")

plt.title(title, fontsize=11)
plt.ylabel("Value")
plt.xticks(rotation=60, ha="right")
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
plt.legend(title="DIE_X, DIE_Y", fontsize=8, ncols=2)
plt.tight_layout()
plt.show()
# plt.savefig("adc_filtered_plot.png", dpi=200, bbox_inches="tight")
