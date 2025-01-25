import csv
from datetime import datetime

# Input file path from environment details
input_csv = 'data/processed/cleaned_funding_20250124003849.csv'
reference_date = datetime(2025, 1, 24)  # From environment's current time

# Read and process the CSV
with open(input_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames + ['Organization Age']
    rows = list(reader)

for row in rows:
    founded_date = row.get('Founded Date', '')
    if not founded_date:
        row['Organization Age'] = ''
        continue
        
    try:
        # Parse date and calculate year difference
        dt = datetime.strptime(founded_date, '%Y-%m-%d')
        age = reference_date.year - dt.year
        
        # Subtract 1 if anniversary hasn't occurred yet this year
        if (reference_date.month, reference_date.day) < (dt.month, dt.day):
            age -= 1
            
        row['Organization Age'] = max(0, age)  # Ensure non-negative
    except ValueError:
        row['Organization Age'] = ''

# Write updated data back to CSV
with open(input_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
