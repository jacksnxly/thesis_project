import pandas as pd
import numpy as np  # Added numpy import
from scipy.stats import spearmanr
from sklearn.utils import resample
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create directory for results
os.makedirs('results/stage_specific_analysis', exist_ok=True)

# Load data
df = pd.read_csv("data/processed/final_h1_data.csv")

# Create digital presence composite
df['overall_digital_presence'] = df[[
    'twitter_log', 'instagram_log', 'linkedin_log',
    'ceo_connections_log', 'articles_log'
]].mean(axis=1)

# Define stages (1=Pre-Seed, 3=Series A)
stages = {
    1: 'Pre-Seed',
    3: 'Series A'
}

# Define metrics
digital_metrics = ['overall_digital_presence']
business_metrics = ['age_log', 'articles_log', 'ceo_connections_log', 'ceo_connections_dummy']

def bootstrap_correlation(data, metric, target='total_funding_log', n_boot=1000):
    """Calculate bootstrapped correlation with CI"""
    correlations = []
    for _ in range(n_boot):
        sample = resample(data, replace=True)
        corr = spearmanr(sample[metric], sample[target]).correlation
        if not np.isnan(corr):
            correlations.append(corr)
    return np.mean(correlations), np.percentile(correlations, [2.5, 97.5])

def bootstrap_correlation_difference(data1, data2, metric):
    """Bootstrap difference in correlations between two groups"""
    diffs = []
    for _ in range(1000):
        sample1 = resample(data1, replace=True)
        sample2 = resample(data2, replace=True)
        corr1 = spearmanr(sample1[metric], sample1['total_funding_log']).correlation
        corr2 = spearmanr(sample2[metric], sample2['total_funding_log']).correlation
        diffs.append(corr1 - corr2)
    return np.mean(diffs), np.percentile(diffs, [2.5, 97.5])

def plot_stage_comparisons(results, metric_name):
    """Visualize stage-specific correlations with CIs"""
    plt.figure(figsize=(10, 6))
    
    # Prepare data for plotting
    stage_labels = list(results.keys())
    x_pos = np.arange(len(stage_labels))
    means = np.array([results[stage]['mean'] for stage in stage_labels])
    lowers = np.array([results[stage]['ci'][0] for stage in stage_labels])
    uppers = np.array([results[stage]['ci'][1] for stage in stage_labels])
    
    # Create error bars
    plt.errorbar(x=x_pos, y=means, 
                 yerr=[means - lowers, uppers - means],
                 fmt='o', markersize=8, capsize=5,
                 color='#2E86C1')
    
    # Format plot
    plt.xticks(ticks=x_pos, 
               labels=[f"{stage}\n(n={results[stage]['n']})" for stage in stage_labels])
    plt.axhline(0, color='gray', linestyle='--')
    plt.ylabel('Spearman Correlation (ρ)')
    plt.title(f'Stage-Specific Correlations: {metric_name} vs Funding')
    plt.tight_layout()
    plt.savefig(f'results/stage_specific_analysis/{metric_name}_stage_comparison.png', dpi=300)
    plt.close()

# Analyze H7a: Digital presence strength by stage
h7a_results = {}
for stage_num, stage_name in stages.items():
    stage_data = df[df['startup_stage'] == stage_num]
    if len(stage_data) < 20:
        print(f"Warning: Insufficient data for {stage_name} (n={len(stage_data)})")
        continue
    
    corr_mean, corr_ci = bootstrap_correlation(stage_data, 'overall_digital_presence')
    h7a_results[stage_name] = {
        'mean': corr_mean,
        'ci': corr_ci,
        'n': len(stage_data)
    }

# Save H7a results
h7a_df = pd.DataFrame(h7a_results).T
h7a_df.to_csv('results/stage_specific_analysis/h7a_digital_presence_comparison.csv')

# Plot H7a results
if h7a_results:
    plot_stage_comparisons(h7a_results, 'Digital_Presence')

# Analyze H7b: Business vs digital metrics across stages
h7b_results = []

for stage_num, stage_name in stages.items():
    stage_data = df[df['startup_stage'] == stage_num]
    if len(stage_data) < 20:
        continue
    
    for business_metric in business_metrics:
        b_mean, b_ci = bootstrap_correlation(stage_data, business_metric)
        d_mean, d_ci = bootstrap_correlation(stage_data, 'overall_digital_presence')
        
        h7b_results.append({
            'stage': stage_name,
            'metric': business_metric,
            'business_corr': b_mean,
            'business_ci': b_ci,
            'digital_corr': d_mean,
            'digital_ci': d_ci,
            'n': len(stage_data)
        })

# Convert to DataFrame and calculate differences
if h7b_results:
    h7b_df = pd.DataFrame(h7b_results)
    h7b_df['difference'] = h7b_df['business_corr'] - h7b_df['digital_corr']
    
    # Calculate significance using array operations
    business_ci_lower = np.array([ci[0] for ci in h7b_df['business_ci']])
    digital_ci_upper = np.array([ci[1] for ci in h7b_df['digital_ci']])
    h7b_df['sig_better'] = (business_ci_lower > digital_ci_upper)
    
    h7b_df.to_csv('results/stage_specific_analysis/h7b_business_vs_digital.csv', index=False)

    # Plot H7b results
    plt.figure(figsize=(12, 8))
    sns.barplot(x='metric', y='difference', hue='stage', data=h7b_df,
                palette={'Pre-Seed': '#4B8BBE', 'Series A': '#FF7A59'})
    plt.axhline(0, color='gray', linestyle='--')
    plt.ylabel('Business Metric Advantage\n(Business ρ - Digital ρ)')
    plt.xlabel('Business Metric')
    plt.title('Relative Importance: Business Metrics vs Digital Presence')
    plt.legend(title='Funding Stage')
    plt.tight_layout()
    plt.savefig('results/stage_specific_analysis/h7b_metric_comparison.png', dpi=300)
    plt.close()

# Calculate statistical significance of differences
print("\nH7a: Digital Presence Correlation Differences:")
if 1 in df['startup_stage'].values and 3 in df['startup_stage'].values:
    pre_seed_data = df[df['startup_stage'] == 1]
    series_a_data = df[df['startup_stage'] == 3]
    
    diff_mean, diff_ci = bootstrap_correlation_difference(
        pre_seed_data, series_a_data, 'overall_digital_presence'
    )
    print(f"Pre-Seed vs Series A difference: {diff_mean:.2f} (95% CI: {diff_ci})")

print("\nH7b: Significant Business Metric Advantages:")
if 'h7b_df' in locals():
    print(h7b_df[['stage', 'metric', 'difference', 'sig_better']].to_markdown(index=False))

# Generate detailed report
with open('results/stage_specific_analysis/stage_analysis_report.txt', 'w') as f:
    f.write("Hypothesis H7a Results:\n")
    f.write("Digital Presence vs Funding Correlation by Stage:\n")
    f.write(h7a_df.to_string() + "\n\n")
    
    if 'h7b_df' in locals():
        f.write("Hypothesis H7b Results:\n")
        f.write("Business Metrics vs Digital Presence Comparison:\n")
        f.write(h7b_df.to_string() + "\n\n")
    
    if 'diff_mean' in locals():
        f.write(f"H7a Difference Test: {diff_mean:.2f} (95% CI: {diff_ci})\n")
    
    if 'h7b_df' in locals():
        f.write("H7b Significant Advantages (business > digital):\n")
        f.write(h7b_df[h7b_df['sig_better']].to_string())