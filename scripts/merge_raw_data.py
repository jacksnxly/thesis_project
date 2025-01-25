import pandas as pd
from pathlib import Path

def merge_csv_files():
    # Get list of CSV files from 0.csv to 13.csv
    data_dir = Path('data/raw/')
    csv_files = [data_dir / f'{i}.csv' for i in range(16)]
    
    # Read and concatenate all CSV files
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if not dfs:
        print("No valid CSV files found")
        return
    
    # Combine all DataFrames
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Save merged data
    output_file = data_dir / 'merged_raw_data.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"Merged data saved to {output_file}")

if __name__ == '__main__':
    merge_csv_files()
