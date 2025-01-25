import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('data/processed/final_h1_data.csv')

# Select columns to analyze
columns = ['twitter', 'instagram', 'linkedin', 'ceo_connections', 'total_funding', 'Number of Articles', 'funding_time_months', 'age']

# Set up visualization
plt.figure(figsize=(15, 15))
sns.set(style="whitegrid")

# Create subplots
for i, col in enumerate(columns, 1):
    plt.subplot(3, 3, i)
    
    # Drop NA values for this column
    data = df[col].dropna()
    
    # Calculate skewness using pandas
    skewness = data.skew()
    
    # Plot histogram with KDE
    sns.histplot(data, kde=True, bins=30)
    plt.title(f'{col}\nSkew: {skewness:.2f}')
    plt.xlabel('Value')
    plt.ylabel('Frequency')

plt.tight_layout()
plt.savefig('data/processed/skewness_histograms.png')
plt.show()
