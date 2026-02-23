import pandas as pd
import os

file_names = ['500_hours.csv', '168_hours.csv']
KEY_COL = 'DIEX_Y'

def hour_suffix_from_filename(fname):
    return '_' + os.path.splitext(os.path.basename(fname))[0]

def generate_summary():

    dfs = [pd.read_csv(f, skiprows=range(1, 5), dtype={KEY_COL: str})
           for f in file_names]

    # Base columns (first 5)
    summary_df = dfs[0].iloc[:, :5].copy()

    # Parameter columns (same structure assumed in both files)
    param_cols = dfs[0].columns[5:]

    for param in param_cols:
        for f, df in zip(file_names, dfs):
            suffix = hour_suffix_from_filename(f)

            temp = df[[KEY_COL, param]].copy()
            temp = temp.rename(columns={param: f"{param}{suffix}"})

            summary_df = summary_df.merge(temp, on=KEY_COL, how='inner')

    summary_df.to_csv('summary_hour.csv', index=False)
    print("summary_hour.csv created successfully")

if __name__ == "__main__":
    generate_summary()
