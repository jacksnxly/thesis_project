import pandas as pd
import numpy as np
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def apply_log_transformations(input_path):
    """Apply log(1+x) transformation to specified columns."""
    try:
        # Load data
        df = pd.read_csv(input_path)
        logging.info(f"Loaded data from {input_path} with {len(df)} rows")

        # Columns to transform with their new names
        transform_cols = {
            'twitter': 'twitter_log',
            'instagram': 'instagram_log',
            'linkedin': 'linkedin_log',
            'ceo_connections': 'ceo_connections_log',
            'total_funding': 'total_funding_log',
            'Number of Articles': 'articles_log',
            'funding_time_months': 'funding_time_months_log',
            'age': 'age_log'
        }

        # Check for missing columns
        missing = [col for col in transform_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")

        # Apply transformations
        for orig_col, new_col in transform_cols.items():
            # Copy original data and ensure numeric type
            df[new_col] = pd.to_numeric(df[orig_col], errors='coerce')
            
            # Clip negative values to 0 before transformation
            df[new_col] = df[new_col].clip(lower=0)
            
            # Apply log1p (log(1+x)) transformation
            df[new_col] = np.log1p(df[new_col])
            
            logging.info(f"Applied transformation to {orig_col} -> {new_col}")

        # Save overwriting original file
        df.to_csv(input_path, index=False)
        logging.info(f"Saved transformed data to {input_path}")

    except Exception as e:
        logging.error(f"Error processing file: {str(e)}")
        raise

if __name__ == "__main__":
    input_csv = Path(__file__).parent.parent / 'data/processed/final_h1_data.csv'
    
    if not input_csv.exists():
        logging.error(f"Input file not found: {input_csv}")
        exit(1)
        
    apply_log_transformations(input_csv)
