import pandas as pd
import argparse

def find_duplicates(input_file, output_file=None):
    # Read CSV file
    df = pd.read_csv(input_file)
    
    # Check for duplicates based on Organization Name and Founded Date
    duplicates = df[df.duplicated(subset=['Organization Name', 'Founded Date'], keep=False)]
    
    # Sort duplicates for better readability
    duplicates_sorted = duplicates.sort_values(by=['Organization Name', 'Founded Date'])
    
    # Print summary
    print(f"Found {len(duplicates_sorted)} duplicate entries based on Organization Name and Founded Date")
    
    # Save to output file if specified
    if output_file:
        duplicates_sorted.to_csv(output_file, index=False)
        print(f"Duplicate entries saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Identify duplicate entries based on Organization Name and Founded Date')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--output', help='Output CSV file path for duplicates')
    args = parser.parse_args()
    
    find_duplicates(args.input, args.output)
