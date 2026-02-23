import pandas as pd
import os

# List of files to process
file_names = ['output_1hr.csv', 'output_2hr.csv']

KEY_COL = 'DIEX_Y'  # join key

def hour_suffix_from_filename(fname: str) -> str:
    # output_1hr.csv -> _1hr
    base = os.path.basename(fname)
    return '_' + base.replace('.csv', '').split('_')[-1]

def generate_summary():
    dfs = []
    for f in file_names:
        df = pd.read_csv(f)

        # Sanity: key must exist
        if KEY_COL not in df.columns:
            raise ValueError(f"'{KEY_COL}' not found in {f}. Columns are: {list(df.columns)}")

        # Critical: key must be unique per file for a clean 1-to-1 match
        if df[KEY_COL].duplicated().any():
            dup_vals = df.loc[df[KEY_COL].duplicated(keep=False), KEY_COL].unique()
            raise ValueError(
                f"ERROR: '{KEY_COL}' is NOT unique in {f}. "
                f"Found duplicates (showing up to 20): {dup_vals[:20].tolist()}\n"
                f"Fix: make '{KEY_COL}' unique per row OR use a composite key (e.g., DIEX_Y + SITE)."
            )

        dfs.append(df)

    # Base info = first 5 columns from first file (your updated format)
    base_info = dfs[0].iloc[:, :5].copy()

    # Start summary with base_info; keep ONLY rows that match across ALL files (inner join)
    summary_df = base_info

    for f, df in zip(file_names, dfs):
        suffix = hour_suffix_from_filename(f)

        # Parameters are everything after the first 5 columns
        param_cols = list(df.columns[5:])

        # KEY + params, renamed with hour suffix
        temp = df[[KEY_COL] + param_cols].copy()
        temp = temp.rename(columns={c: f"{c}{suffix}" for c in param_cols})

        # INNER join => only keep DIEX_Y present in both summary_df and this file
        summary_df = summary_df.merge(temp, on=KEY_COL, how='inner', validate='one_to_one')

    summary_df.to_csv('summary_hour.csv', index=False)
    print("Successfully created 'summary_hour.csv' (only DIEX_Y common to all files)")

if __name__ == "__main__":
    generate_summary()
