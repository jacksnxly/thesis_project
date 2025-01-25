import csv
import datetime
from pathlib import Path
import shutil
import sys

def is_date(value, formats):
    """Check if a value matches any date format"""
    for fmt in formats:
        try:
            datetime.datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False

def convert_date(date_str, formats):
    """Convert date string to ISO format"""
    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str  # Return original if no format matches

def main():
    # Define potential date formats
    date_formats = [
        "%b %d, %Y",    # Jan 1, 2023
        "%b %d, %Y",    # January 1, 2023 (same format works for full month names)
        "%d-%b-%y",     # 01-Jan-23
        "%m/%d/%Y",     # 01/01/2023
        "%Y-%m-%d",     # 2023-01-01 (already correct)
        "%d.%m.%Y"      # 01.01.2023
    ]
    
    if len(sys.argv) != 2:
        print("Usage: python date_converter.py <input_file>")
        sys.exit(1)
        
    input_path = Path(sys.argv[1])
    backup_path = Path(f"data/backup/{input_path.stem}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{input_path.suffix}")
    
    # Create backup
    shutil.copy(input_path, backup_path)
    print(f"Created backup at: {backup_path}")

    with open(input_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        # Identify date columns by header and sample values
        date_columns = set()
        date_keywords = ['date', 'funded', 'created', 'founded']
        sample_row = next(reader)
        
        for i, (col_name, value) in enumerate(zip(header, sample_row)):
            value = value.strip()
            if any(kw in col_name.lower() for kw in date_keywords) or is_date(value, date_formats):
                date_columns.add(i)
        
        # Reset file pointer
        infile.seek(0)
        reader = csv.reader(infile)
        header = next(reader)

        # Process data
        rows = []
        for row in reader:
            modified = False
            for i in date_columns:
                if i < len(row):
                    original = row[i].strip()
                    converted = convert_date(original, date_formats)
                    if converted != original:
                        row[i] = converted
                        modified = True
            rows.append(row)
    
    # Write converted data
    with open(input_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"Successfully converted dates in {input_path}")

if __name__ == "__main__":
    main()
