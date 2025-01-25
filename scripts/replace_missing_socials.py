import pandas as pd
import random

def main():
    # Read CSV file
    df = pd.read_csv('data/processed/cleaned_funding_20250124003849.csv')
    
    # Create backup with timestamp
    backup_path = f"data/backup/cleaned_funding_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv"
    df.to_csv(backup_path, index=False)
    
    # Convert social columns to numeric and fill missing with 0.0
    social_cols = ['Twitter Followers', 'Instagram Followers', 'Linkedin Followers', 'CEO Connections']
    for col in social_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df[social_cols] = df[social_cols].fillna(0.0)
    
    # Save updated data
    df.to_csv('data/wip/cleaned_funding_20250124003849.csv', index=False)

if __name__ == "__main__":
    main()
