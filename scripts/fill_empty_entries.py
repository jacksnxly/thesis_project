import pandas as pd

# Read the CSV file
df = pd.read_csv('data/processed/final_h1_data.csv')

# Replace empty strings and NaN values with 0.0
df.replace(r'^\s*$', 0.0, regex=True, inplace=True)
df.fillna(0.0, inplace=True)

# Save the modified DataFrame back to the same file
df.to_csv('data/processed/final_h1_data.csv', index=False)
