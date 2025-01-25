import csv
import os

input_path = 'data/raw/fx_data.csv'
output_path = 'data/processed/fx_data_formatted.csv'

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(input_path, 'r') as infile, open(output_path, 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile, delimiter=';')
    
    for row in reader:
        if len(row) >= 2:
            # Remove quotes from date and format
            date = row[0].strip('"')
            
            # Convert and format FX value
            try:
                fx_value = round(float(row[1]), 2)
                fx_formatted = f"{fx_value:.2f}".replace('.', ',')
            except ValueError:
                fx_formatted = row[1]  # Fallback to original if conversion fails
                
            writer.writerow([date, fx_formatted])
