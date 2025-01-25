import csv

STATE_COLUMNS = [
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

def find_zero_state_rows(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Verify all state columns exist
        missing = [col for col in STATE_COLUMNS if col not in reader.fieldnames]
        if missing:
            print(f"Error: Missing columns - {', '.join(missing)}")
            return []
            
        zero_rows = []
        
        for idx, row in enumerate(reader, start=2):  # Line numbers start at 2 (1-based + header)
            state_values = [int(row[col]) for col in STATE_COLUMNS]
            if sum(state_values) == 0:
                zero_rows.append({
                    'line_number': idx,
                    'organization': row.get('Organization Name', ''),
                    'state': row.get('Headquarters State', '')
                })
                
        return zero_rows

if __name__ == '__main__':
    results = find_zero_state_rows('data/wip/cleaned_funding.csv')
    
    if results:
        print(f"Found {len(results)} rows with all state dummies set to 0:")
        for r in results:
            print(f"Line {r['line_number']}: {r['organization']} | State: {r['state']}")
    else:
        print("No rows found with all state dummies set to 0")
