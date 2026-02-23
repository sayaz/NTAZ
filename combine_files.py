import pandas as pd
import os

file_names = ['output_1hr.csv', 'output_2hr.csv']
KEY_COL = 'DIEX_Y'

def hour_suffix_from_filename(fname):
    return '_' + os.path.basename(fname).replace('.csv', '').split('_')[-1]

def generate_summary():

    # Skip rows 2–5 (0-based indexing: skip rows 1,2,3,4)
    dfs = [pd.read_csv(f, skiprows=range(1, 5), dtype={KEY_COL: str})
           for f in file_names]

    # Start with first file (first 5 columns as base)
    summary_df = dfs[0].iloc[:, :5].copy()

    for f, df in zip(file_names, dfs):
        suffix = hour_suffix_from_filename(f)

        param_cols = df.columns[5:]
        temp = df[[KEY_COL] + list(param_cols)].copy()
        temp = temp.rename(columns={c: f"{c}{suffix}" for c in param_cols})

        summary_df = summary_df.merge(temp, on=KEY_COL, how='inner')

    summary_df.to_csv('summary_hour.csv', index=False)
    print("summary_hour.csv created successfully")

if __name__ == "__main__":
    generate_summary()
