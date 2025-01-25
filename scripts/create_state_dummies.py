import pandas as pd

# Define all German states (Bundesländer) in required order
states = [
    'baden_wuerttemberg',
    'bayern', 
    'berlin',
    'brandenburg',
    'bremen',
    'hamburg',
    'hessen',
    'mecklenburg_vorpommern',
    'niedersachsen',
    'nordrhein_westfalen',
    'rheinland_pfalz',
    'saarland',
    'sachsen',
    'sachsen_anhalt',
    'schleswig_holstein',
    'thueringen'
]

def create_state_dummies(input_path):
    # Read CSV
    df = pd.read_csv(input_path)
    
    # Create new columns initialized with 0
    for state in states:
        df[state] = 0
    
    # Map headquarters state to dummy columns
    for idx, row in df.iterrows():
        state = str(row['Headquarters State']).lower().replace(' ', '_').replace('-', '_')
        
        # Handle special cases and normalize names
        if state == 'baden_wurttemberg':
            state = 'baden_wuerttemberg'
        elif state == 'nordrhein_westfalen':
            state = 'nordrhein_westfalen'  # already correct
        elif state == 'thuringen':
            state = 'thueringen'
            
        if state in states:
            df.at[idx, state] = 1
    
    # Reorder columns to insert dummies after Headquarters State
    cols = list(df.columns)
    hq_index = cols.index('Headquarters State')
    
    # Insert new columns after Headquarters State
    new_cols = cols[:hq_index+1] + states + cols[hq_index+1:-len(states)]
    df = df[new_cols]
    
    return df

if __name__ == "__main__":
    input_file = "data/wip/cleaned_funding.csv"
    output_file = "data/wip/cleaned_funding.csv"
    
    updated_df = create_state_dummies(input_file)
    
    # Save updated CSV
    updated_df.to_csv(output_file, index=False)
    print(f"Successfully added state dummy columns to {output_file}")
