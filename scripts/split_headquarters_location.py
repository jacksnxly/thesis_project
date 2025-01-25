import csv
from pathlib import Path

def split_location(location):
    """Split location into city and state components"""
    if not location:
        return ('', '')
    
    parts = [part.strip() for part in location.split(',')]
    
    # Get city from first part
    city = parts[0] if len(parts) > 0 else ''
    
    # Get state from second part (ignore country if present)
    state = parts[1] if len(parts) > 1 else ''
    
    return (city, state)

def process_csv(input_path):
    output_path = input_path  # Overwrite original file
    temp_path = input_path.with_suffix('.tmp')
    
    with open(input_path, 'r', newline='', encoding='utf-8') as infile, \
         open(temp_path, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Insert new columns after Headquarters Location
        loc_index = fieldnames.index('Headquarters Location')
        new_fields = fieldnames[:loc_index+1] + ['Headquarters City', 'Headquarters State'] + fieldnames[loc_index+1:]
        
        writer = csv.DictWriter(outfile, fieldnames=new_fields)
        writer.writeheader()
        
        for row in reader:
            location = row['Headquarters Location']
            city, state = split_location(location)
            
            # Add new columns while preserving existing data
            row['Headquarters City'] = city
            row['Headquarters State'] = state
            writer.writerow(row)
    
    # Replace original file with processed version
    temp_path.replace(output_path)

if __name__ == '__main__':
    csv_path = Path('data/processed/cleaned_funding_20250124003849.csv')
    process_csv(csv_path)
    print(f"Successfully updated {csv_path} with new location columns")
