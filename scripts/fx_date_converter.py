#!/usr/bin/env python3
import csv
import datetime
import sys

def convert_date(input_file, output_file):
    """Convert dates in CSV from 'MMM D, YYYY' to 'YYYY-MM-DD' format"""
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile, delimiter=';')
            writer = csv.writer(outfile, delimiter=';')
            
            for row in reader:
                if len(row) >= 1:
                    try:
                        # Parse original date format and convert to YYYY-MM-DD
                        original_date = row[0]
                        date_obj = datetime.datetime.strptime(original_date, "%b %d, %Y")
                        row[0] = date_obj.strftime("%Y-%m-%d")
                    except ValueError as e:
                        print(f"Error parsing date {original_date}: {e}")
                        continue
                writer.writerow(row)
        print(f"Successfully converted dates. Output saved to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file {input_file} not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 fx_date_converter.py <input_file> <output_file>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    convert_date(input_path, output_path)
