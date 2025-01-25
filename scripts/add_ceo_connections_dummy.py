import pandas as pd

def main():
    # Read the CSV file
    df = pd.read_csv('data/wip/merged_raw_data.csv')
    
    # Convert CEO Connections to numeric, handling non-numeric values
    df['CEO Connections'] = pd.to_numeric(df['CEO Connections'], errors='coerce')
    
    # Create dummy variable
    df['CEO_Connections_Dummy'] = df['CEO Connections'].apply(
        lambda x: 1 if x >= 500.0 else 0 if pd.notnull(x) else None
    )
    
    # Save back to CSV
    df.to_csv('data/wip/merged_raw_data.csv', index=False)
    print("Successfully added dummy column")

if __name__ == "__main__":
    main()
