import pandas as pd

# Read CSV file
df = pd.read_csv('data/wip/cleaned_funding.csv')

# Clean and split industries
industries = (
    df['Industries']
    .dropna()
    .str.split(',')
    .explode()
    .str.strip()
    .str.lower()
    .unique()
)

# Sort alphabetically and print
print("Unique Industries Found:")
for industry in sorted(industries):
    print(f"- {industry.title()}")

# Optional: Save to text file
with open('data/processed/unique_industries.txt', 'w') as f:
    f.write("\n".join(sorted(industry.title() for industry in industries)))
