import pandas as pd
import numpy as np
from datetime import datetime

def clean_currency_symbols(df):
    """Extract and clean currency symbols from amount columns"""
    # Total Funding Amount processing
    df['Total Funding Currency'] = df['Total Funding Amount'].str.extract(r'([€$])')
    df['Total Funding Amount Clean'] = (
        df['Total Funding Amount']
        .str.replace(r'[^\d.]', '', regex=True)
        .replace('', np.nan)
        .astype(float)
    )
    
    # Last Funding Amount processing  
    df['Last Funding Currency'] = df['Last Funding Amount'].str.extract(r'([€$])')
    df['Last Funding Amount Clean'] = (
        df['Last Funding Amount']
        .str.replace(r'[^\d.]', '', regex=True)
        .replace('', np.nan)
        .astype(float)
    )
    
    return df

def load_fx_data():
    """Load and prepare FX rate data with forward filling"""
    fx = pd.read_csv('data/processed/yahoo_finance_fx_iso.csv', parse_dates=['date'])
    fx = fx.sort_values('date').ffill()  # Forward fill missing rates
    avg_rate = fx['fx'].mean()  # Calculate overall average rate
    return fx, avg_rate

def convert_currencies(df, fx, avg_rate):
    """Perform currency conversions with date matching"""
    # Convert funding dates to datetime
    df['Last Funding Date'] = pd.to_datetime(df['Last Funding Date'], errors='coerce')
    
    # Merge FX rates using nearest valid date
    merged = pd.merge_asof(
        df.sort_values('Last Funding Date'),
        fx.rename(columns={'date': 'Last Funding Date'}),
        on='Last Funding Date',
        direction='forward'
    )
    
    # Create conversion flag and handle missing dates
    merged['fx_source'] = np.where(
        merged['Last Funding Date'].isna(),
        'average',
        'historical'
    )
    merged['fx_rate'] = np.where(
        merged['fx_source'] == 'average',
        avg_rate,
        merged['fx']
    )
    
    # Perform conversions
    merged['Total Funding Amount (converted)'] = np.where(
        merged['Total Funding Currency'] == '$',
        merged['Total Funding Amount Clean'] * merged['fx_rate'],
        merged['Total Funding Amount Clean']  # Assume EUR if no symbol
    )
    
    merged['Last Funding Amount (converted)'] = np.where(
        merged['Last Funding Currency'] == '$',
        merged['Last Funding Amount Clean'] * merged['fx_rate'],
        merged['Last Funding Amount Clean']
    )
    
    return merged

def main():
    # Load and clean data
    df = pd.read_csv('data/wip/merged_raw_data.csv')
    df = clean_currency_symbols(df)
    
    # Prepare FX data
    fx, avg_rate = load_fx_data()
    
    # Perform conversions
    converted_df = convert_currencies(df, fx, avg_rate)
    
    # Save cleaned data with timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    converted_df.to_csv(f'data/processed/cleaned_funding_{timestamp}.csv', index=False)
    print(f"Saved cleaned data with currency conversions to data/processed/cleaned_funding_{timestamp}.csv")

if __name__ == '__main__':
    main()
