import pandas as pd
import os

# Files to process (update as needed)
file_names = ["500_hours.csv", "168_hours.csv"]

KEY_COL = "DIEX_Y"   # ID column used for matching across files

def suffix_from_filename(fname: str) -> str:
    # "500_hours.csv" -> "_500_hours"
    return "_" + os.path.splitext(os.path.basename(fname))[0]

def read_clean_csv(path: str) -> pd.DataFrame:
    """
    Assumptions:
      - Row 1 is the column header
      - Rows 2–5 are non-data header/metadata rows (may be blank or not)
    Fixes:
      - Skip rows 2–5
      - Strip DIEX_Y
      - Drop rows where DIEX_Y is blank/NaN
      - Drop common extra header-like rows (e.g., Tests#, Patterns, Unit, HighL, LowL)
    """
    df = pd.read_csv(path, skiprows=range(1, 5), dtype={KEY_COL: str})

    # Normalize key values
    df[KEY_COL] = df[KEY_COL].astype(str).str.strip()
    df.loc[df[KEY_COL].isin(["", "nan", "NaN", "None"]), KEY_COL] = pd.NA
    df = df[df[KEY_COL].notna()]

    # Drop any remaining header-like rows that often appear in "Parameter" column
    if "Parameter" in df.columns:
        junk = {"Tests#", "Patterns", "Unit", "HighL", "LowL"}
        df = df[~df["Parameter"].astype(str).str.strip().isin(junk)]

    return df

def generate_summary():
    # Read + clean all files
    dfs = [read_clean_csv(f) for f in file_names]

    # Base columns: first 5 columns from the first file (as you requested)
    summary_df = dfs[0].iloc[:, :5].copy()

    # Ensure key exists in base
    if KEY_COL not in summary_df.columns:
        raise ValueError(
            f"'{KEY_COL}' must be within the first 5 columns (base_info). "
            f"Current first 5 columns: {list(summary_df.columns)}"
        )

    # Parameter columns (assumed common structure across files)
    param_cols = list(dfs[0].columns[5:])

    # Interleave columns: col1_500_hours, col1_168_hours, col2_500_hours, col2_168_hours, ...
    for param in param_cols:
        for f, df in zip(file_names, dfs):
            suf = suffix_from_filename(f)

            # Keep only key + this param, rename with suffix
            temp = df[[KEY_COL, param]].copy()
            temp = temp.rename(columns={param: f"{param}{suf}"})

            # Merge by DIEX_Y (row order in original files doesn't matter)
            summary_df = summary_df.merge(temp, on=KEY_COL, how="inner")

    summary_df.to_csv("summary_hour.csv", index=False)
    print("Successfully created 'summary_hour.csv'")

if __name__ == "__main__":
    generate_summary()
