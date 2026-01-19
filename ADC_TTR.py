import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "output.csv"

# ---------------------------------------------------------------------
# Read CSV:
# - Row 0: column names
# - Rows 1..4: extra header rows to skip
# ---------------------------------------------------------------------
df = pd.read_csv(CSV_PATH, header=0, skiprows=[1, 2, 3, 4])

# Validate DIE_X / DIE_Y
if ("DIE_X" not in df.columns) or ("DIE_Y" not in df.columns):
    raise ValueError("Expected columns 'DIE_X' and 'DIE_Y' were not found in the CSV.")

# ---------------------------------------------------------------------
# User inputs
# ---------------------------------------------------------------------
metric_key = input("Enter metric keyword (e.g., inl, bc): ").strip().upper()
if not metric_key:
    raise ValueError("Metric keyword cannot be empty.")

require_channel = input("Require 'CHANNEL' in column name? (y/n) [y]: ").strip().lower()
require_channel = True if require_channel in ("", "y", "yes") else False

extra_key = input(
    "Optional extra filter keyword (press Enter to skip). "
    "If provided, columns may match via this keyword even if 'CHANNEL' is absent: "
).strip().upper()
# extra_key can be empty -> ignored

# ---------------------------------------------------------------------
# Column filtering space:
# first row is column names; first 10 columns are header-like and excluded from filtering
# ---------------------------------------------------------------------
first_10_cols = list(df.columns[:10])
search_space_cols = [c for c in df.columns if c not in first_10_cols]

def norm(s: str) -> str:
    return str(s).upper()

filtered_cols = []
for c in search_space_cols:
    cu = norm(c)

    # Always require ADC + metric
    if ("ADC" not in cu) or (metric_key not in cu):
        continue

    # Two ways a column can qualify:
    # (A) Primary rule: must have CHANNEL (if required) + (optional extra_key if user gave one)
    # (B) Extra rule: if extra_key provided, allow matching that keyword even if CHANNEL is missing
    if require_channel:
        primary_ok = ("CHANNEL" in cu) and ((extra_key in cu) if extra_key else True)
        extra_ok = bool(extra_key) and (extra_key in cu)  # may omit CHANNEL
        if primary_ok or extra_ok:
            filtered_cols.append(c)
    else:
        # If not requiring CHANNEL, then just ADC + metric + (optional extra_key)
        if (extra_key in cu) if extra_key else True:
            filtered_cols.append(c)

# De-duplicate while preserving order
seen = set()
filtered_cols = [c for c in filtered_cols if not (c in seen or seen.add(c))]

if not filtered_cols:
    raise ValueError(
        "No columns matched your filters.\n"
        f"metric_key='{metric_key}', require_channel={require_channel}, extra_key='{extra_key or None}'"
    )

print(f"Selected {len(filtered_cols)} columns.")
print("First few selected columns:", filtered_cols[:10])

# ---------------------------------------------------------------------
# Plot: one line per row, ID by (DIE_X, DIE_Y)
# ---------------------------------------------------------------------
x_labels = filtered_cols

plt.figure(figsize=(max(10, 0.35 * len(x_labels)), 6))

for _, row in df.iterrows():
    die_x = row["DIE_X"]
    die_y = row["DIE_Y"]
    y = pd.to_numeric(row[filtered_cols], errors="coerce")
    plt.plot(x_labels, y.values, marker="o", linewidth=1, label=f"({die_x},{die_y})")

plt.xlabel("Filtered Columns")
plt.ylabel("Value")
plt.xticks(rotation=60, ha="right")
plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.6)
plt.legend(title="DIE_X, DIE_Y", fontsize=8, ncols=2)
plt.tight_layout()
plt.show()
