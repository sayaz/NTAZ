import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np

# Put files in the order you want to appear in the output
file_names = ["0_hours.csv", "48_hours.csv", "168_hours.csv", "500_hours.csv"]

KEY_COL = "DIEX_Y"   # ID column used for matching across files


def suffix_from_filename(fname: str) -> str:
    # "500_hours.csv" -> "_500_hours"
    return "_" + os.path.splitext(os.path.basename(fname))[0]


def read_clean_csv(path: str) -> pd.DataFrame:
    """
    Assumptions:
      - Row 1 is the column header
      - Rows 2–5 are non-data header/metadata rows
    Fixes:
      - Skip rows 2–5
      - Strip DIEX_Y
      - Drop rows where DIEX_Y is blank/NaN
      - Drop common extra header-like rows in "Parameter" column
    """
    df = pd.read_csv(path, skiprows=range(1, 5), dtype={KEY_COL: str})

    df[KEY_COL] = df[KEY_COL].astype(str).str.strip()
    df.loc[df[KEY_COL].isin(["", "nan", "NaN", "None"]), KEY_COL] = pd.NA
    df = df[df[KEY_COL].notna()]

    if "Parameter" in df.columns:
        junk = {"Tests#", "Patterns", "Unit", "HighL", "LowL"}
        df = df[~df["Parameter"].astype(str).str.strip().isin(junk)]

    return df


def generate_summary_with_delta_ordered_and_plot():
    # Read + clean all files
    dfs = [read_clean_csv(f) for f in file_names]

    # Base columns: first 5 columns from the first file
    base_cols = list(dfs[0].columns[:5])
    if KEY_COL not in base_cols:
        raise ValueError(
            f"'{KEY_COL}' must be within the first 5 columns. "
            f"First 5 columns: {base_cols}"
        )

    summary_df = dfs[0][base_cols].copy()

    # Parameter columns (everything after first 5)
    param_cols = list(dfs[0].columns[5:])

    # Merge all time points into summary_df
    for param in param_cols:
        for f, df in zip(file_names, dfs):
            suf = suffix_from_filename(f)
            temp = df[[KEY_COL, param]].copy()
            temp = temp.rename(columns={param: f"{param}{suf}"})
            summary_df = summary_df.merge(temp, on=KEY_COL, how="inner")

    # Compute Delta columns (500h - 0h) and convert to mV (x1000)
    delta_cols = []
    for param in param_cols:
        col_0 = f"{param}_0_hours"
        col_500 = f"{param}_500_hours"

        if col_0 not in summary_df.columns or col_500 not in summary_df.columns:
            raise ValueError(f"Missing columns for Delta: {col_0} or {col_500}")

        v0 = pd.to_numeric(summary_df[col_0], errors="coerce")
        v500 = pd.to_numeric(summary_df[col_500], errors="coerce")

        delta_col = f"{param}_Delta_mV"  # clearer name since it is now in mV
        summary_df[delta_col] = (v0 - v500) * 1000.0
        delta_cols.append(delta_col)

    # ---------------------------------------------------
    # Reorder columns: for each param -> 4 hours + Delta
    # ---------------------------------------------------
    ordered_cols = base_cols.copy()

    hour_suffixes = [suffix_from_filename(f) for f in file_names]  # [_0_hours, _48_hours, _168_hours, _500_hours]

    for param in param_cols:
        for suf in hour_suffixes:
            ordered_cols.append(f"{param}{suf}")
        ordered_cols.append(f"{param}_Delta_mV")

    summary_df = summary_df[ordered_cols]

    # Save updated CSV
    summary_df.to_csv("summary_hour.csv", index=False)
    print("Successfully created 'summary_hour.csv' with ordered Delta columns in mV.")

    # -----------------------------
    # PLOT: Delta heatmap (best view)
    # -----------------------------
    # Matrix: rows = DIEX_Y, cols = parameters, values = delta_mV
    heat_df = summary_df[[KEY_COL] + delta_cols].copy()
    heat_df = heat_df.set_index(KEY_COL)

    data = heat_df.to_numpy(dtype=float)

    plt.figure(figsize=(12, 6))
    im = plt.imshow(data, aspect="auto")  # default colormap (no manual colors)
    plt.colorbar(im, label="Delta (500h - 0h) [mV]")

    # X labels: parameter names without suffix
    x_labels = [c.replace("_Delta_mV", "") for c in delta_cols]
    plt.xticks(range(len(x_labels)), x_labels, rotation=45, ha="right")
    plt.yticks(range(len(heat_df.index)), heat_df.index)

    plt.xlabel("Parameter")
    plt.ylabel("DIEX_Y")
    plt.title("Delta Heatmap (500h - 0h) in mV")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    generate_summary_with_delta_ordered_and_plot()
