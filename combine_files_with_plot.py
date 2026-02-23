import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import numpy as np

file_names = ["500_hours.csv", "168_hours.csv"]
KEY_COL = "DIEX_Y"

def suffix_from_filename(fname: str) -> str:
    return "_" + os.path.splitext(os.path.basename(fname))[0]

def read_clean_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=range(1, 5), dtype={KEY_COL: str})

    df[KEY_COL] = df[KEY_COL].astype(str).str.strip()
    df.loc[df[KEY_COL].isin(["", "nan", "NaN", "None"]), KEY_COL] = pd.NA
    df = df[df[KEY_COL].notna()]

    if "Parameter" in df.columns:
        junk = {"Tests#", "Patterns", "Unit", "HighL", "LowL"}
        df = df[~df["Parameter"].astype(str).str.strip().isin(junk)]

    return df

def generate_heatmap():

    dfs = [read_clean_csv(f) for f in file_names]
    summary_df = dfs[0].iloc[:, :5].copy()

    param_cols = list(dfs[0].columns[5:])

    for param in param_cols:
        for f, df in zip(file_names, dfs):
            suf = suffix_from_filename(f)
            temp = df[[KEY_COL, param]].copy()
            temp = temp.rename(columns={param: f"{param}{suf}"})
            summary_df = summary_df.merge(temp, on=KEY_COL, how="inner")

    # Find paired columns automatically
    pattern_500 = re.compile(r"^(.*)_500_hours$")
    pattern_168 = re.compile(r"^(.*)_168_hours$")

    base_cols_500 = {pattern_500.match(c).group(1): c for c in summary_df.columns if pattern_500.match(c)}
    base_cols_168 = {pattern_168.match(c).group(1): c for c in summary_df.columns if pattern_168.match(c)}

    common_params = sorted(set(base_cols_500).intersection(base_cols_168))

    # Build difference matrix
    diff_matrix = []

    for param in common_params:
        col_500 = base_cols_500[param]
        col_168 = base_cols_168[param]

        diff = (
            pd.to_numeric(summary_df[col_500], errors="coerce")
            - pd.to_numeric(summary_df[col_168], errors="coerce")
        )

        diff_matrix.append(diff.values)

    diff_matrix = np.array(diff_matrix).T  # shape: DIEX_Y x parameters

    # Plot heatmap
    plt.figure(figsize=(12,6))
    im = plt.imshow(diff_matrix, aspect="auto", cmap="bwr")

    plt.colorbar(im, label="500h - 168h")

    plt.xticks(range(len(common_params)), common_params, rotation=45, ha="right")
    plt.yticks(range(len(summary_df[KEY_COL])), summary_df[KEY_COL])

    plt.xlabel("Parameters")
    plt.ylabel("DIEX_Y")
    plt.title("Drift Heatmap (500h - 168h)")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    generate_heatmap()
