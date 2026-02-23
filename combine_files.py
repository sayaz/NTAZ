import pandas as pd
import os

file_names = ['output_1hr.csv', 'output_2hr.csv']

def hour_suffix_from_filename(fname: str) -> str:
    # output_1hr.csv -> _1hr
    base = os.path.basename(fname)
    return '_' + base.replace('.csv', '').split('_')[-1]

def generate_summary():
    dfs = [pd.read_csv(f) for f in file_names]

    # Base info = first 5 columns from first file
    base_info = dfs[0].iloc[:, :5].copy()
    KEY_COLS = list(base_info.columns)   # <-- composite key (most reliable here)

    # Start with base_info
    summary_df = base_info

    # Optional: warn if base key isn't unique in the base file
    if dfs[0].duplicated(subset=KEY_COLS).any():
        dups = dfs[0][dfs[0].duplicated(subset=KEY_COLS, keep=False)][KEY_COLS]
        print("WARNING: Even the composite key (first 5 columns) is NOT unique in output_1hr.csv.")
        print("Here are some duplicate keys (showing up to 10):")
        print(dups.head(10).to_string(index=False))
        print("If this happens, you need to add more columns to the key (e.g., SITE, TIME, etc.).\n")

    # Merge each file's parameter columns onto base using KEY_COLS
    for f, df in zip(file_names, dfs):
        suffix = hour_suffix_from_filename(f)

        # Parameter columns = from index 5 onward (your updated format)
        param_cols = list(df.columns[5:])

        # Build temp = key + params (renamed with suffix)
        temp = df[KEY_COLS + param_cols].copy()
        temp = temp.rename(columns={c: f"{c}{suffix}" for c in param_cols})

        # Merge with left join to preserve base rows
        summary_df = summary_df.merge(temp, on=KEY_COLS, how='left')

    summary_df.to_csv('summary_hour.csv', index=False)
    print("Successfully created 'summary_hour.csv'")

if __name__ == "__main__":
    generate_summary()
