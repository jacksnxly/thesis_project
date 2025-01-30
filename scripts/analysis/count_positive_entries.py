import pandas as pd
import os
import sys

def count_positive_entries(file_path, columns):
    """
    Counts the number of entries greater than 0 for specified columns in a CSV file.

    Parameters:
    - file_path (str): Path to the CSV file.
    - columns (list of str): List of column names to evaluate.

    Returns:
    - dict: A dictionary with column names as keys and counts as values.
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        sys.exit(1)
    
    counts = {}
    
    for col in columns:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found in the CSV file.")
            counts[col] = None
            continue
        
        # Ensure the column is numeric
        # Coerce errors to NaN, then drop NaN for accurate counting
        numeric_series = pd.to_numeric(df[col], errors='coerce').dropna()
        
        # Count entries greater than 0
        count = (numeric_series > 0).sum()
        counts[col] = count
    
    return counts

def main():
    # Define the path to the CSV file
    csv_file_path = "data/processed/final_h1_data.csv"
    
    # Define the columns to evaluate
    target_columns = ["twitter", "instagram", "linkedin", "ceo_connections"]
    
    # Get the counts
    result = count_positive_entries(csv_file_path, target_columns)
    
    # Display the results
    print("Count of entries > 0 for each specified column:")
    for col, count in result.items():
        if count is not None:
            print(f"- {col}: {count}")
        else:
            print(f"- {col}: Column not found.")

if __name__ == "__main__":
    main()