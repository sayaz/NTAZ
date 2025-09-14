#!/usr/bin/env python3
# Simple CSV checker: hardcoded file names, stop at first fail per row.
# Adds two columns: Failed_TN (Test#) and Failed_Param (header name).

import csv

INPUT  = "NusratTest.csv"              # input file
OUTPUT = "NusratTest_checked.csv"      # output file

with open(INPUT, "r", newline="", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))

# Expected layout:
# row0: names, row1: Test#, row2: Unit, row3: HighL, row4: LowL, row5+: data
names   = rows[0]
testnum = rows[1]
units   = rows[2]
highL   = rows[3]
lowL    = rows[4]

out_rows = []
# Add header rows; append Failed_TN and Failed_Param to the first header line
out_rows.append(names + ["Failed_TN", "Failed_Param"])
out_rows.append(testnum + ["", ""])
out_rows.append(units   + ["", ""])
out_rows.append(highL   + ["", ""])
out_rows.append(lowL    + ["", ""])

# Process data rows (from index 5)
for r in rows[5:]:
    failed_tn = ""
    failed_param = ""
    # Check each Param column (skip the first column = unit/row label)
    for c in range(1, len(names)):
        # Skip columns without numeric limits
        try:
            lo = float(lowL[c]); hi = float(highL[c])
        except Exception:
            continue
        # Skip non-numeric cell
        try:
            val = float(r[c])
        except Exception:
            continue
        # If outside [LowL, HighL], record this column's Test# and header, then STOP for this row
        if not (lo <= val <= hi):
            if c < len(testnum) and testnum[c]:
                failed_tn = str(testnum[c])
            failed_param = names[c] if c < len(names) else ""
            break
    out_rows.append(r + [failed_tn, failed_param])

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(out_rows)

print("Saved:", OUTPUT)
