import pandas as pd
from pandas.tseries.offsets import MonthEnd

def calculate_time_to_funding(file_path):
    # Read CSV with date parsing
    df = pd.read_csv(file_path, parse_dates=['Founded Date', 'Last Funding Date'])
    
    # Calculate month difference
    df['funding_time_months'] = (
        (df['Last Funding Date'] - df['Founded Date']) / pd.Timedelta(days=30.44)
    ).astype(int)
    
    # Truncate negative values to 0
    df['funding_time_months'] = df['funding_time_months'].clip(lower=0)
    
    # Save updated CSV
    df.to_csv(file_path, index=False)

if __name__ == "__main__":
    input_file = "data/wip/cleaned_funding.csv"
    calculate_time_to_funding(input_file)
    print(f"Updated {input_file} with funding_time_months column")
