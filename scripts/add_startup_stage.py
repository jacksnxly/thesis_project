import csv
from datetime import datetime

def add_startup_stage_column(input_path, output_path):
    # Read CSV and add new column
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['startup_stage']
        
        rows = []
        for row in reader:
            # Map funding type to numeric code
            funding_type = row['Last Funding Type']
            if funding_type == 'Pre-Seed':
                row['startup_stage'] = '1'
            elif funding_type == 'Seed':
                row['startup_stage'] = '2'
            elif funding_type == 'Series A':
                row['startup_stage'] = '3'
            else:
                row['startup_stage'] = ''
            rows.append(row)

    # Write updated CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == '__main__':
    input_csv = 'data/wip/cleaned_funding.csv'
    output_csv = 'data/wip/cleaned_funding.csv'
    
    print(f"Processing {input_csv}")
    add_startup_stage_column(input_csv, output_csv)
    print(f"Updated file saved to {output_csv} with startup_stage column")
