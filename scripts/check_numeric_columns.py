import pandas as pd
import sys

def check_numeric_columns(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found")
        return

    columns_to_check = [
        'Twitter Followers',
        'Instagram Followers', 
        'Linkedin Followers',
        'CEO Connections'
    ]
    
    # Check for missing columns
    missing_cols = [col for col in columns_to_check if col not in df.columns]
    if missing_cols:
        print(f"Error: Columns missing from CSV: {', '.join(missing_cols)}")
        return
    
    invalid_entries = {}
    
    for col in columns_to_check:
        # Attempt to convert to numeric, coercing errors to NaN
        converted = pd.to_numeric(df[col], errors='coerce')
        
        # Find rows with invalid values
        invalid_mask = converted.isna() & df[col].notna()
        invalid_rows = df[invalid_mask]
        
        if not invalid_rows.empty:
            invalid_entries[col] = invalid_rows[['Company Name', col]]
    
    if invalid_entries:
        print("Non-numeric values found:")
        for col, entries in invalid_entries.items():
            print(f"\nColumn: {col}")
            print(entries.to_string(index=False))
    else:
        print("All checked columns contain valid numeric values")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_numeric_columns.py <path_to_csv>")
        sys.exit(1)
        
    check_numeric_columns(sys.argv[1])
