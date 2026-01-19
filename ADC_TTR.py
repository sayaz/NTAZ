import re
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================
# USER EDIT SECTION (edit these lists only; no prompts used)
# ============================================================
# Columns must contain ALL of these keywords (case-insensitive).
# Examples:
#   ["ADC", "CHANNEL", "inl"]
#   ["ADC", "inl"]                     # does NOT require CHANNEL
#   ["ADC_CHANNEL", "inl"]             # if your naming uses combined tokens
REQUIRED_KEYWORDS = ["ADC", "CHANNEL", "inl"]

# Optional: columns containing ANY of these keywords will be excluded
EXCLUDE_KEYWORDS = []  # e.g., ["TEMP", "DEBUG"]

# Path to your CSV
CSV_PATH = "output.csv"

# Skip first 4 rows after the header row (your extra header lines)
SKIP_EXTRA_HEADER_ROWS = [1, 2, 3, 4]

# First N columns are "header-like" and should not be considered for filtering
HEADER_LIKE_FIRST_N_COLS = 10
# ============================================================


# ---------------------------------------------------------------------
# Load CSV
# ---------------------------------------------------------------------
df = pd.read_csv(CSV_PATH, header=0, skiprows=SKIP_EXTRA_HEADER_ROWS)

# Validate DIE_X / DIE_Y
if ("DIE_X" not in df.columns) or ("DIE_Y" not in df.columns):
    raise ValueError("Expected columns 'DIE_X' and 'DIE_Y' were not found in the CSV.")

# ---------------------------------------------------------------------
# Filter columns based on REQUIRED_KEYWORDS / EXCLUDE_KEYWORDS
# ---------------------------------------------------------------------
first_n_cols = list(df.columns[:HEADER_LIKE_FIRST_N_COLS])
search_space_cols = [c for c in df.columns if c not in first_n_cols]

req = [k.strip().upper() for k in REQUIRED_KEYWORDS if str(k).strip()]
exc = [k.strip().upper() for k in EXCLUDE_KEYWORDS if str(k).strip()]

if not req:
    raise ValueError("REQUIRED_KEYWORDS is empty. Put at least one keyword (e.g., 'ADC').")

def col_matches(colname: str) -> bool:
    cu = str(colname).upper()
    # Must contain all required keywords
    for k in req:
        if k not in cu:
            return False
    # Must contain none of the excluded keywords
    for k in exc:
        if k in cu:
            return False
    return True

filtered_cols = [c for c in search_space_cols if col_matches(c)]

if not filtered_cols:
    raise ValueError(
        "No columns matched your filter.\n"
        f"REQUIRED_KEYWORDS={REQUIRED_KEYWORDS}, EXCLUDE_KEYWORDS={EXCLUDE_KEYWORDS}\n"
        "Tip: relax the filter (remove 'CHANNEL' or adjust 'inl' token)."
    )

# ---------------------------------------------------------------------
# Sort columns: odd CHANNELs first, then even CHANNELs
# CHANNEL<number> is detected anywhere inside the column name.
# Non-channel columns go last.
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
print("First 12 columns (plot order):", filtered_cols_sorted[:12])

# ---------------------------------------------------------------------
# Plot: one line per row, label by (DIE_X, DIE_Y)
# ---------------------------------------------------------------------
x_labels = filtered_cols_sorted

plt.figure(figsize=(max(10, 0.35 * len(x_labels)), 6))

for _, row in df.iterrows():
    die_x = row["DIE_X"]
    die_y = row["DIE_Y"]
    y = pd.to_numeric(row[filtered_cols_sorted], errors="coerce")
    plt.plot(x_labels, y.values, marker="o", linewidth=1, label=f"({die_x},{die_y})")

plt.xlabel("Filtered Columns (odd CHANNELs first, then even)")
plt.ylabel("Value")
plt.xticks(rotation=60, ha="right")
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
plt.legend(title="DIE_X, DIE_Y", fontsize=8, ncols=2)
plt.tight_layout()
plt.show()
# plt.savefig("adc_filtered_plot.png", dpi=200, bbox_inches="tight")
