import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configure plot style
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = [12, 8]

def plot_skew_comparison(input_path, output_path):
    """Plot comparison histograms of original vs log-transformed features."""
    df = pd.read_csv(input_path)
    
    # Plot pairs - original and transformed columns
    pairs = [
        ('twitter', 'twitter_log'),
        ('instagram', 'instagram_log'), 
        ('linkedin', 'linkedin_log'),
        ('ceo_connections', 'ceo_connections_log'),
        ('total_funding', 'total_funding_log')
    ]
    
    # Create figure with subplots
    fig, axes = plt.subplots(nrows=5, ncols=2, tight_layout=True)
    fig.suptitle('Distribution Comparison: Original vs Log-Transformed Features')
    
    for idx, (orig_col, log_col) in enumerate(pairs):
        # Original distribution
        sns.histplot(df[orig_col], ax=axes[idx,0], kde=True)
        axes[idx,0].set_title(f'Original {orig_col}')
        axes[idx,0].set_xlabel('')
        
        # Transformed distribution
        sns.histplot(df[log_col], ax=axes[idx,1], kde=True)
        axes[idx,1].set_title(f'Transformed {log_col}')
        axes[idx,1].set_xlabel('')
    
    # Save and show
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Saved skewness comparison plot to {output_path}")

if __name__ == "__main__":
    input_csv = Path(__file__).parent.parent / 'data/processed/final_h1_data.csv'
    output_png = Path(__file__).parent.parent / 'data/processed/skew_comparison.png'
    
    if not input_csv.exists():
        raise FileNotFoundError(f"Input file missing: {input_csv}")
        
    if not all(col in pd.read_csv(input_csv).columns for col in ['twitter_log', 'total_funding_log']):
        raise ValueError("Log-transformed columns missing - run apply_log_transform.py first")
    
    plot_skew_comparison(input_csv, output_png)
