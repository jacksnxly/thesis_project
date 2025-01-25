import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr, pointbiserialr
from sklearn.utils import resample
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multitest import multipletests

df = pd.read_csv("data/processed/final_h1_data.csv")

# Calculate overall digital presence composite score
df['overall_digital_presence'] = df[[
    'twitter_log', 'instagram_log', 'linkedin_log',
    'ceo_connections_log', 'articles_log'
]].mean(axis=1)

numeric_cols = [
    'twitter_log', 'instagram_log', 'linkedin_log',
    'ceo_connections_log', 'ceo_connections_dummy',
    'total_funding_log', 'articles_log', 'age_log',
    'overall_digital_presence'
]
numeric_df = df[numeric_cols]

def compute_correlations(df, method='pearson'):
    cols = df.columns
    corr_matrix = pd.DataFrame(index=cols, columns=cols)
    pval_matrix = pd.DataFrame(index=cols, columns=cols)
    
    for col1 in cols:
        for col2 in cols:
            if col1 == col2:
                corr_matrix.loc[col1, col2] = 1.0
                pval_matrix.loc[col1, col2] = 0.0
            else:
                if method == 'pearson':
                    corr, pval = pearsonr(df[col1], df[col2])
                elif method == 'pointbiserial':
                    corr, pval = pointbiserialr(df[col1], df[col2])
                corr_matrix.loc[col1, col2] = corr
                pval_matrix.loc[col1, col2] = pval
    return corr_matrix.astype(float), pval_matrix.astype(float)

# Calculate correlations for different variable types
pearson_corr_matrix, pearson_pval_matrix = compute_correlations(numeric_df, method='pearson')
pointbiserial_corr_matrix, pointbiserial_pval_matrix = compute_correlations(
    numeric_df[['ceo_connections_dummy', 'total_funding_log']], 
    method='pointbiserial'
)

# Calculate Spearman correlations
spearman_corr_matrix = numeric_df.corr(method='spearman')
spearman_pval_matrix = numeric_df.apply(lambda x: numeric_df.apply(
    lambda y: spearmanr(x, y).pvalue))

# Platform-specific analysis
platforms = {
    'twitter_log': 'Twitter Followers',
    'instagram_log': 'Instagram Followers', 
    'linkedin_log': 'LinkedIn Followers',
    'overall_digital_presence': 'Overall Digital Presence'
}

platform_results = []
for platform, label in platforms.items():
    # Pearson for continuous variables
    pearson_corr = pearson_corr_matrix.loc[platform, 'total_funding_log']
    pearson_p = pearson_pval_matrix.loc[platform, 'total_funding_log']
    
    # Spearman for non-linear relationships
    spearman_corr, spearman_p = spearmanr(numeric_df[platform], numeric_df['total_funding_log'])
    
    platform_results.append({
        'Platform': label,
        'Pearson r': f"{pearson_corr:.2f}",
        'Pearson p': f"{pearson_p:.3f}",
        'Spearman ρ': f"{spearman_corr:.2f}",
        'Spearman p': f"{spearman_p:.3f}"
    })

# Add CEO connections dummy results
platform_results.append({
    'Platform': 'CEO Connections (500+ dummy)',
    'Pearson r': f"{pointbiserial_corr_matrix.loc['ceo_connections_dummy', 'total_funding_log']:.2f}",
    'Pearson p': f"{pointbiserial_pval_matrix.loc['ceo_connections_dummy', 'total_funding_log']:.3f}",
    'Spearman ρ': '-',
    'Spearman p': '-'
})

results_df = pd.DataFrame(platform_results)

alpha = 0.05

# FDR correction for Pearson correlations
pvals = pearson_pval_matrix.values[np.triu_indices_from(pearson_pval_matrix, k=1)]
reject, pvals_corrected, _, _ = multipletests(pvals, alpha=alpha, method='fdr_bh')

pval_corrected_matrix = pd.DataFrame(np.nan, index=pearson_pval_matrix.index, columns=pearson_pval_matrix.columns)
upper_tri_indices = np.triu_indices_from(pval_corrected_matrix, k=1)
pval_corrected_matrix.values[upper_tri_indices] = pvals_corrected

significant_mask_corrected = pval_corrected_matrix < alpha
significant_corr_corrected = pearson_corr_matrix.where(significant_mask_corrected)

# Save corrected results
significant_corr_corrected.to_csv('results/h1/significant_pearson_correlations_fdr.csv')

# Create subplots for comparison
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# Plot Spearman correlations
sns.heatmap(
    spearman_corr_matrix,
    annot=True,
    fmt=".2f",
    cmap='viridis',
    vmax=1,
    vmin=-1,
    center=0,
    square=True,
    linewidths=.5,
    cbar_kws={"shrink": .5, "label": "Correlation Coefficient"},
    ax=axes[0],
    annot_kws={"size": 9}
)
axes[0].set_title('A) Spearman Rank Correlations', pad=20, fontsize=14, weight='bold')
axes[0].tick_params(axis='both', which='major', labelsize=9)

# Plot Pearson correlations with FDR correction
heatmap = sns.heatmap(
    significant_corr_corrected,
    annot=True,
    fmt=".2f",
    cmap='viridis',
    vmax=1,
    vmin=-1,
    center=0,
    square=True,
    linewidths=.5,
    cbar_kws={"shrink": .5, "label": "Correlation Coefficient"},
    ax=axes[1],
    annot_kws={"size": 9}
)
axes[1].set_title('B) Pearson Correlations (FDR Corrected)', pad=20, fontsize=14, weight='bold')
axes[1].tick_params(axis='both', which='major', labelsize=9)

# Add figure labels
plt.figtext(0.5, 1.02, 'Digital Presence Metrics vs Funding Success', 
           ha='center', va='top', fontsize=16, weight='bold')

plt.tight_layout()
plt.savefig('correlation_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Format and save results
print("\nPlatform-Specific Funding Correlations:")
print(results_df.to_markdown(index=False))

results_df.to_csv('results/h1/platform_correlations.csv', index=False)
pearson_corr_matrix.to_csv('results/h1/full_pearson_matrix.csv')

# Platform-specific analysis
from sklearn.inspection import PartialDependenceDisplay, partial_dependence
from scipy.stats import pointbiserialr

platforms = {
    'continuous': ['twitter', 'instagram', 'linkedin', 'ceo_connections', 'articles', 'overall_digital_presence'],
    'binary': ['ceo_connections_dummy']
}

# Analyze continuous platforms
for platform in platforms['continuous']:
    platform_var = f'{platform}_log' if platform != 'overall_digital_presence' else platform
    pdp_feature = platform_var  # Set PDP feature dynamically based on current platform
    xlabel = f'{platform.capitalize()} Presence (log scale)' if platform != 'overall_digital_presence' else 'Overall Digital Presence Score'
    
    # Scatterplot with regression line and density
    plt.figure(figsize=(10,6))
    
    # Calculate correlations
    if platform == 'overall_digital_presence':
        corr = spearmanr(df[platform_var], df['total_funding_log']).correlation
        corr_label = f'Overall ρ = {corr:.2f}'
    else:
        corr = spearmanr(df[platform_var], df['total_funding_log']).correlation
        corr_label = f'ρ = {corr:.2f}'
    
    g = sns.jointplot(x=platform_var, y='total_funding_log', 
                    data=df, kind='reg',
                    joint_kws={
                        'scatter_kws': {'alpha':0.4, 'color':'#4B8BBE'}
                    },
                    marginal_kws={
                        'color': '#306998',
                        'kde': True
                    },
                    height=6)
    
    g.ax_joint.set_xlabel(xlabel, fontsize=12, labelpad=10)
    g.ax_joint.set_ylabel('Funding Amount (log EUR)', fontsize=12, labelpad=10)
    g.ax_joint.tick_params(axis='both', which='major', labelsize=10)
    
    # Add annotation
    g.ax_joint.text(0.05, 0.95, 
                   corr_label,
                   transform=g.ax_joint.transAxes,
                   fontsize=12,
                   verticalalignment='top',
                   bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
    
    plt.suptitle(f'{platform.capitalize()} vs Funding Success', 
                y=1.02, fontsize=14, weight='bold')
    plt.tight_layout()
    plt.savefig(f'{platform}_funding_jointplot.png', dpi=300)
    plt.close()
    
    # Partial dependence plot with bootstrap CI
    digital_metrics = ['twitter_log', 'instagram_log', 'linkedin_log', 
                      'ceo_connections_log', 'ceo_connections_dummy', 'articles_log',
                      'overall_digital_presence']
    
    fig, ax = plt.subplots(figsize=(10,6))
    n_bootstraps = 100
    bootstrap_pdps = []  # Initialize empty list
    # Calculate grid from full dataset to ensure consistent size
    grid_values = np.linspace(
        df[pdp_feature].min(),
        df[pdp_feature].max(),
        50
    )
    
    # Bootstrap loop
    for _ in range(n_bootstraps):
        sample = resample(df, replace=True, random_state=_)
        estimator = RandomForestRegressor(n_estimators=100, random_state=_)
        estimator.fit(sample[digital_metrics], sample['total_funding_log'])
        
        # Calculate PDP with fixed grid range
        avg, _ = partial_dependence(
            estimator=estimator,
            X=sample[digital_metrics],
            features=[pdp_feature],
            grid=[grid_values],  # Use precomputed grid
            kind='average'
        )
        
        # Store results
        bootstrap_pdps.append(avg[0])

    # Calculate statistics - ensure numeric type conversion
    bootstrap_array = np.array(bootstrap_pdps, dtype=np.float64)
    mean_pdp = np.nanmean(bootstrap_array, axis=0)
    ci_lower = np.nanpercentile(bootstrap_array, 2.5, axis=0)
    ci_upper = np.nanpercentile(bootstrap_array, 97.5, axis=0)

    # Plot main PDP with CI
    ax.plot(grid_values, mean_pdp, color='#2E86C1', lw=2.5, label='Mean PDP')
    ax.fill_between(grid_values, ci_lower, ci_upper, 
                   color='#85C1E9', alpha=0.3, label='95% CI')

    # Add original full dataset PDP
    full_estimator = RandomForestRegressor(n_estimators=100, random_state=42)
    full_estimator.fit(df[digital_metrics], df['total_funding_log'])
    PartialDependenceDisplay.from_estimator(
        estimator=full_estimator,
        X=df[digital_metrics],
        features=[pdp_feature],
        grid_resolution=50,
        ax=ax,
        line_kw={'color': '#E74C3C', 'linestyle': '--',
                'label': 'Full Dataset PDP'}
    )
    title_suffix = 'Log-transformed Metric' if platform != 'overall_digital_presence' else 'Composite Score'
    plt.xlabel(title_suffix, fontsize=12, labelpad=10)
    plt.ylabel('Impact on Funding (log EUR)', fontsize=12, labelpad=10)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.title(f'{platform.capitalize()} Impact Analysis\n(PDP: {title_suffix})', 
             fontsize=13, pad=20, weight='bold')
    plt.savefig(f'{platform}_partial_dependence.png', dpi=400, bbox_inches='tight')
    plt.close()
    
# Analyze binary platform (CEO connections dummy)
plt.figure(figsize=(10,6))
sns.boxplot(x='ceo_connections_dummy', y='total_funding_log', data=df,
            palette=['#4B8BBE', '#FF7A59'])
plt.xticks([0, 1], ['<500 Connections', '500+ Connections'])
plt.xlabel('CEO Connections Tier', fontsize=12)
plt.ylabel('Funding Amount (log EUR)', fontsize=12)
plt.title('Funding Distribution by CEO Connections Tier', fontsize=14, pad=15, weight='bold')

# Calculate point-biserial correlation
pb_corr, pb_pval = pointbiserialr(df['ceo_connections_dummy'], df['total_funding_log'])
plt.text(0.05, 0.95, 
        f'r_pb = {pb_corr:.2f}\np = {pb_pval:.3f}',
        transform=plt.gca().transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

plt.savefig('ceo_connections_dummy_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()

# Partial dependence plot for binary feature
fig, ax = plt.subplots(figsize=(10,6))
digital_metrics = ['twitter_log', 'instagram_log', 'linkedin_log', 
                  'ceo_connections_log', 'ceo_connections_dummy', 'articles_log',
                  'overall_digital_presence']

# Fit model on full data
full_estimator = RandomForestRegressor(n_estimators=100, random_state=42)
full_estimator.fit(df[digital_metrics], df['total_funding_log'])

# Calculate PDP for binary feature using feature name
pdp_binary = PartialDependenceDisplay.from_estimator(
    estimator=full_estimator,
    X=df[digital_metrics],
    features=['ceo_connections_dummy'],
    grid_resolution=2,
    ax=ax,
    line_kw={'color': '#E74C3C', 'label': 'PDP'}
)

# Format plot
plt.xticks([0, 1], ['<500 Connections', '500+ Connections'])
plt.xlabel('CEO Connections Tier', fontsize=12, labelpad=10)
plt.ylabel('Impact on Funding (log EUR)', fontsize=12, labelpad=10)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.title('CEO Connections Impact Analysis\n(Partial Dependence Plot)', 
         fontsize=13, pad=20, weight='bold')
plt.savefig('ceo_connections_dummy_partial_dependence.png', dpi=400, bbox_inches='tight')
plt.close()

# Calculate partial correlations controlling for company age
from scipy import stats

digital_metrics = ['overall_digital_presence', 'twitter_log', 'instagram_log', 
                  'linkedin_log', 'ceo_connections_log', 'ceo_connections_dummy', 
                  'articles_log']
funding_metric = 'total_funding_log'
control_var = 'age_log'

partial_corrs = {}
for metric in digital_metrics:
    # Partial correlation formula
    corr_xy = spearman_corr_matrix.loc[metric, funding_metric]
    corr_xz = spearman_corr_matrix.loc[metric, control_var]
    corr_yz = spearman_corr_matrix.loc[funding_metric, control_var]
    
    partial_corr = (corr_xy - corr_xz*corr_yz) / np.sqrt((1 - corr_xz**2)*(1 - corr_yz**2))
    partial_corrs[metric] = partial_corr

# Create enhanced results dataframe
results_df = pd.DataFrame({
    'metric': digital_metrics,
    'type': ['Composite'] + ['Social']*3 + ['Network']*2 + ['Media'],
    'spearman_corr': [spearman_corr_matrix.loc[m, funding_metric] for m in digital_metrics],
    'pearson_corr': [pearson_corr_matrix.loc[m, funding_metric] for m in digital_metrics],
    'partial_corr': [partial_corrs[m] for m in digital_metrics],
    'spearman_p': [spearman_pval_matrix.loc[m, funding_metric] for m in digital_metrics],
    'pearson_p_fdr': [significant_corr_corrected.loc[m, funding_metric] for m in digital_metrics]
})

# Apply FDR correction to Spearman correlations
spearman_pvals = [spearman_pval_matrix.loc[m, funding_metric] for m in digital_metrics]
spearman_reject, spearman_pvals_fdr, _, _ = multipletests(spearman_pvals, alpha=0.05, method='fdr_bh')
results_df['spearman_p_fdr'] = spearman_pvals_fdr

# Add significance stars
def add_stars(row):
    p = row['spearman_p_fdr']  # Use FDR-corrected p-values
    if p < 0.001:
        return f"{row['spearman_corr']:.2f}***"
    elif p < 0.01:
        return f"{row['spearman_corr']:.2f}**"
    elif p < 0.05:
        return f"{row['spearman_corr']:.2f}*"
    return f"{row['spearman_corr']:.2f}"

results_df['formatted'] = results_df.apply(add_stars, axis=1)

print("\nDigital Presence vs Funding Success (FDR-corrected):")
print(results_df[['metric', 'type', 'formatted', 'partial_corr', 'pearson_p_fdr']]
      .rename(columns={
          'formatted': 'spearman_ρ (FDR)',
          'partial_corr': 'partial_ρ',
          'pearson_p_fdr': 'pearson_r (FDR)'
      })
      .to_markdown(index=False, floatfmt=".2f"))

# Create regression plots
plt.figure(figsize=(15, 10))
for i, metric in enumerate(digital_metrics, 1):
    plt.subplot(2, 3, i)
    sns.regplot(x=metric, y=funding_metric, data=df,
                scatter_kws={'alpha':0.4, 'color':'#4B8BBE'})
    plt.title(f"{metric}\nρ={partial_corrs[metric]:.2f}", fontsize=12, pad=15)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xlabel('')
    plt.ylabel('Total Funding (log)' if i == 1 else '')
    
plt.tight_layout()
plt.savefig('funding_regression_plots.png', dpi=300, bbox_inches='tight')
plt.close()

pearson_corr_matrix.to_csv('results/h1/pearson_correlations.csv')
pearson_pval_matrix.to_csv('results/h1/pearson_pvalues.csv')

# Bootstrap confidence intervals for Twitter-Funding correlation
np.random.seed(42)
bootstrap_corrs = []
n_iterations = 1000

for _ in range(n_iterations):
    sample = resample(df, replace=True)
    corr = spearmanr(sample['twitter_log'], sample['total_funding_log']).correlation
    bootstrap_corrs.append(corr)

ci_lower = np.percentile(bootstrap_corrs, 2.5)
ci_upper = np.percentile(bootstrap_corrs, 97.5)

plt.figure(figsize=(10, 6))
sns.histplot(bootstrap_corrs, kde=True)
plt.axvline(ci_lower, color='red', linestyle='--')
plt.axvline(ci_upper, color='red', linestyle='--')
plt.title(f'Bootstrap Correlation Distribution\n95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]')
plt.xlabel('Spearman Correlation Coefficient')
plt.savefig('bootstrap_confidence.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"\nBootstrap 95% Confidence Interval for Twitter-Funding Correlation:")
print(f"[{ci_lower:.2f}, {ci_upper:.2f}]")

# Save corrected results
significant_corr_corrected.to_csv('results/h1/significant_pearson_correlations_fdr.csv')
