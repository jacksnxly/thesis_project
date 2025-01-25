import pandas as pd

def merge_csv_files(file1, file2, output_file):
    """Merge two CSV files with identical columns vertically"""
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    # Concatenate vertically
    merged_df = pd.concat([df1, df2], ignore_index=True)
    
    # Save to output file
    merged_df.to_csv(output_file, index=False)
    print(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    # Define file paths relative to project root
    file1 = "data/wip/merged_raw_data1.csv"
    file2 = "data/raw/15.csv"
    output_file = "data/wip/merged_raw_data.csv"
    
    # Merge files
    merge_csv_files(file1, file2, output_file)
