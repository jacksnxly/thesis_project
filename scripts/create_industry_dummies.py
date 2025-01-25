import pandas as pd

industries = ['industrials', 'information_technology', 'communication_services', 'real_estate', 'financials', 'consumer_discretionary', 'web3_blockchain', 'health_care', 'materials', 'consumer_staples', 'other', 'utilities', 'energy']

def create_industry_dummies(input_path):
    # Read CSV
    df = pd.read_csv(input_path)
    
    # Normalize industry names and create dummies
    df['industry_clean'] = df['industry'].str.lower()\
        .str.replace('[ /-]', '_', regex=True)
        
    # Create dummies using pandas' built-in function
    dummies = df['industry_clean'].str.get_dummies().add_prefix('industry_')
    
    # Filter only our target industries
    target_cols = [f'industry_{ind.lower().replace(" ", "_")}' for ind in industries]
    dummies = dummies.reindex(columns=target_cols, fill_value=0)
    
    # Rename columns to match original industry names
    dummies.columns = industries
    
    # Merge with original dataframe
    df = pd.concat([df, dummies], axis=1)
    
    # Reorder columns to insert dummies after industry
    cols = list(df.columns)
    hq_index = cols.index('industry')
    new_cols = cols[:hq_index+1] + industries + [c for c in cols[hq_index+1:] if c not in industries]
    df = df[new_cols]
    
    return df

if __name__ == "__main__":
    input_file = "data/wip/cleaned_funding.csv"
    output_file = "data/wip/cleaned_funding_with_dummies.csv"
    
    updated_df = create_industry_dummies(input_file)
    
    # Save updated CSV
    updated_df.to_csv(output_file, index=False)
    print(f"Successfully added industry dummy columns to {output_file}")
