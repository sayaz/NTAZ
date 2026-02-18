import pandas as pd

# List of files to process
file_names = ['output_1hr.csv', 'output_2hr.csv', 'output_3hr.csv', 'output_4hr.csv']

def generate_summary():
    # Load all files into DataFrames
    # Since row 1 is the header, pandas will use it for column names automatically.
    # Rows 2, 3, 4, 5 (metadata) will be treated as the first 4 rows of data.
    dfs = [pd.read_csv(f) for f in file_names]
    
    # 1. Extract the first 10 columns from the first file as the base
    # (Parameter, SBIN, HBIN, DIE_X, DIE_Y, SITE, TIME, TOTAL_TESTS, LOT_ID, WAFER_ID)
    base_info = dfs[0].iloc[:, :10]
    
    # 2. Identify the parameter columns (from index 10 onwards)
    param_names = dfs[0].columns[10:]
    
    # 3. Build the list of columns for the final DataFrame
    # Start with the base 10 columns
    final_parts = [base_info]
    
    # 4. For each parameter, collect the data from all 4 files
    for param in param_names:
        for i, df in enumerate(dfs):
            hour_suffix = f'_{i+1}hr'
            # Select the specific column and rename it with the suffix
            # We use [[param]] to keep it as a DataFrame for easy renaming
            col_data = df[[param]].rename(columns={param: f"{param}{hour_suffix}"})
            final_parts.append(col_data)
            
    # 5. Concatenate everything horizontally (axis=1)
    # This aligns rows automatically (including the metadata rows 2-5)
    summary_df = pd.concat(final_parts, axis=1)
    
    # 6. Save the final summary file
    summary_df.to_csv('summary_hour.csv', index=False)
    print("Successfully created 'summary_hour.csv'")

if __name__ == "__main__":
    generate_summary()