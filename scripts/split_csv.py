import csv
import os
from pathlib import Path

def split_csv(input_file, output_dir, chunk_size=50):
    try:
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        with open(input_file, 'r', newline='') as infile:
            reader = csv.reader(infile)
            header = next(reader)
            
            file_count = 1
            rows = []
            
            for row in reader:
                rows.append(row)
                if len(rows) == chunk_size:
                    output_file = os.path.join(output_dir, f'part{file_count}.csv')
                    write_chunk(output_file, header, rows)
                    file_count += 1
                    rows = []
            
            # Write remaining rows if any
            if rows:
                output_file = os.path.join(output_dir, f'part{file_count}.csv')
                write_chunk(output_file, header, rows)
                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def write_chunk(output_file, header, rows):
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(rows)

if __name__ == "__main__":
    input_csv = "data/crunchbase_data.csv"
    output_dir = "data"
    split_csv(input_csv, output_dir)
