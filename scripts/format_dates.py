import pandas as pd
import re
from datetime import datetime

def parse_flex_date(date_str):
    """Parse dates with flexible formats"""
    if pd.isna(date_str) or str(date_str).strip() == '':
        return pd.NaT
    
    date_str = str(date_str).strip()
    
    # Try different patterns
    patterns = [
        (r'\b[A-Za-z]{3} \d{1,2}, \d{4}\b', '%b %d, %Y'),      # "Feb 13, 2024"
        (r'\b[A-Za-z]{3} \d{4}\b', '%b %Y'),                   # "Jul 2023"
        (r'\b\d{4}\b', '%Y')                                   # "2023"
    ]
    
    for pattern, fmt in patterns:
        if re.fullmatch(pattern, date_str, re.IGNORECASE):
            try:
                dt = datetime.strptime(date_str, fmt)
                # Add missing day/month if needed
                if fmt == '%b %Y':
                    return dt.replace(day=1)
                elif fmt == '%Y':
                    return dt.replace(month=1, day=1)
                return dt
            except ValueError:
                continue
                
    # If no patterns match, return NaT and warn
    print(f"Warning: Could not parse date '{date_str}'")
    return pd.NaT

def clean_dates(input_path, output_path):
    """Main cleaning function"""
    df = pd.read_csv(input_path)
    
    df = df.drop(["LinkedIn Followers"], axis=1)
    # Convert date columns
    date_cols = ['Founded Date', 'Last Funding Date']
    
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(parse_flex_date)
            # Format to desired string format
            # Format day without leading zero and ensure comma
            df[col] = df[col].apply(lambda x: x.strftime('%b ') + str(x.day) + ', ' + x.strftime('%Y') if not pd.isnull(x) else x)
    
    # Save cleaned data
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")
    print("\nSample transformed dates:")
    print(df[date_cols].head())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean date formats in CSV')
    parser.add_argument('--input', default='data/wip/merged_raw_data.csv',
                       help='Input CSV path')
    parser.add_argument('--output', default='data/wip/merged_raw_data_clean.csv',
                      help='Output CSV path')
    
    args = parser.parse_args()
    
    clean_dates(args.input, args.output)
