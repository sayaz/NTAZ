import pandas as pd
import os

# List of files to process
file_names = ['output_1hr.csv', 'output_2hr.csv']

KEY_COL = 'DIEX_Y'   # <-- the ID you want to align on
BASE_COLS = None     # we'll take "first 5 columns from first file" as your base

def hour_suffix_from_filename(fname: str) -> str:
    # output_1hr.csv -> _1hr
    base = os.path.basename(fname)
    return '_' + base.replace('.csv', '').split('_')[-1]

def generate_summary():
    # Read all files
    dfs = [pd.read_csv(f) for f in file_names]

    # --- sanity checks ---
    for f, df in zip(file_names, dfs):
        if KEY_COL not in df.columns:
            raise ValueError(f"'{KEY_COL}' not found in {f}. Columns are: {list(df.columns)}")

    # Base info = first 5 columns from the first file (as you currently do)
    base_info = dfs[0].iloc[:, :5].copy()
    base_cols = list(base_info.columns)

    # Make sure KEY_COL is included in the base (required for merging)
    if KEY_COL not in base_cols:
        raise ValueError(
            f"Your base_info (first 5 cols) does NOT include '{KEY_COL}'. "
            f"Either move '{KEY_COL}' into the first 5 columns in the CSV, "
            f"or explicitly include it in base_info."
        )

    # Start the merged df as the base info
    summary_df = base_info

    # Parameter columns are everything after the first 5 columns in each file
    # (same logic you used, but applied per file)
    for f, df in zip(file_names, dfs):
        suffix = hour_suffix_from_filename(f)

        param_cols = list(df.columns[5:])  # columns after first 5
        # Build a temp df: KEY + renamed params
        temp = df[[KEY_COL] + param_cols].copy()
        temp = temp.rename(columns={c: f"{c}{suffix}" for c in param_cols})

        # Merge by KEY_COL so rows align by DIEX_Y, not by row number
        summary_df = summary_df.merge(temp, on=KEY_COL, how='left', validate='one_to_one')

    # Optional: detect keys missing in some files (helpful debugging)
    # If a die exists in base but not in another file, you'll see NaNs in that hour's columns.
    summary_df.to_csv('summary_hour.csv', index=False)
    print("Successfully created 'summary_hour.csv'")

if __name__ == "__main__":
    generate_summary()
