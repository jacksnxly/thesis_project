import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr, pointbiserialr
from sklearn.utils import resample
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import PartialDependenceDisplay, partial_dependence
from scipy.stats import pointbiserialr
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.multitest import multipletests
from statsmodels.api import OLS, add_constant

# Ensure results directory exists
import os
os.makedirs('results/h1-h4', exist_ok=True)

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
significant_corr_corrected.to_csv('results/h1-h4/significant_pearson_correlations_fdr.csv')

# Create subplots for comparison
fig, axes = plt.subplots(1, 2, figsize=(24, 12))

# Add more padding between subplots
plt.subplots_adjust(wspace=0.3, hspace=0.4)  # Horizontal and vertical spacing

# After plotting, use tight_layout with padding
plt.tight_layout(pad=4)  # Add padding around subplots

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
axes[0].set_title('A) Spearman Rank Correlations', pad=20, fontsize=12, weight='bold')
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
axes[1].set_title('B) Pearson Correlations (FDR Corrected)', pad=20, fontsize=12, weight='bold')
axes[1].tick_params(axis='both', which='major', labelsize=9)

# Add figure labels
plt.figtext(0.5, 1.05, 'Digital Presence Metrics vs Funding Success', 
           ha='center', va='top', fontsize=18, weight='bold')

plt.tight_layout()
plt.savefig('results/h1-h4/correlation_comparison.png', dpi=400, bbox_inches='tight')
plt.close()

# Format and save results
print("\nPlatform-Specific Funding Correlations:")
print(results_df.to_markdown(index=False))

results_df.to_csv('results/h1-h4/platform_correlations.csv', index=False)
pearson_corr_matrix.to_csv('results/h1-h4/full_pearson_matrix.csv')

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

    g = sns.jointplot(
        x=platform_var, y='total_funding_log', 
        data=df, kind='reg',
        joint_kws={
            'scatter_kws': {'alpha':0.4, 'color':'#4B8BBE'}
        },
        marginal_kws={
            'color': '#306998',
            'kde': True
        },
        height=6
    )

    g.ax_joint.set_xlabel(xlabel, fontsize=12, labelpad=10)
    g.ax_joint.set_ylabel('Funding Amount (log EUR)', fontsize=12, labelpad=10)
    g.ax_joint.tick_params(axis='both', which='major', labelsize=10)

    # Add annotation
    g.ax_joint.text(
        0.05, 0.95, 
        corr_label,
        transform=g.ax_joint.transAxes,
        fontsize=12,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none')
    )

    plt.suptitle(f'{platform.capitalize()} vs Funding Success', y=1.02, fontsize=14, weight='bold')
    plt.tight_layout()
    plt.savefig(f'results/h1-h4/{platform}_funding_jointplot.png', dpi=300)
    plt.close()

    # Partial dependence plot with bootstrap CI
    digital_metrics = [
        'twitter_log', 'instagram_log', 'linkedin_log', 
        'ceo_connections_log', 'ceo_connections_dummy', 'articles_log',
        'overall_digital_presence'
    ]

    fig, ax = plt.subplots(figsize=(10,6))
    n_bootstraps = 100
    bootstrap_pdps = []  # Initialize empty list
    grid_values = None  # Initialize grid_values

    # Bootstrap loop for PDPs
    for i in range(n_bootstraps):
        sample = resample(df, replace=True, random_state=i)
        estimator = RandomForestRegressor(n_estimators=100, random_state=i)
        estimator.fit(sample[digital_metrics], sample['total_funding_log'])

        # Calculate PDP
        features_idx = digital_metrics.index(pdp_feature)
        pdp_result = partial_dependence(
            estimator=estimator,
            X=sample[digital_metrics],
            features=[features_idx],
            kind='average',
            grid_resolution=50
        )

        # Handle different return types
        if isinstance(pdp_result, tuple):
            # Old versions: tuple (grid, avg)
            grid = pdp_result[0]
            avg = pdp_result[1]
        else:
            # New versions: Bunch with keys
            grid = pdp_result['grid_values']  # Key changed here
            avg = pdp_result['average']       # Key changed here

        if grid_values is None:
            grid_values = grid[0]
            current_avg = avg[0]
        else:
            pdp_grid = grid[0]
            pdp_avg = avg[0]
            current_avg = np.interp(grid_values, pdp_grid, pdp_avg)

        bootstrap_pdps.append(current_avg)

    # Convert to NumPy array for calculations
    bootstrap_array = np.array(bootstrap_pdps, dtype=np.float64)

    # Calculate mean and confidence intervals
    mean_pdp = np.nanmean(bootstrap_array, axis=0)
    ci_lower = np.nanpercentile(bootstrap_array, 2.5, axis=0)
    ci_upper = np.nanpercentile(bootstrap_array, 97.5, axis=0)

    # Plot main PDP with CI
    ax.plot(grid_values, mean_pdp, color='#2E86C1', lw=2.5, label='Mean PDP')
    ax.fill_between(grid_values, ci_lower, ci_upper, color='#85C1E9', alpha=0.3, label='95% CI')

    # Add original full dataset PDP
    full_estimator = RandomForestRegressor(n_estimators=100, random_state=42)
    full_estimator.fit(df[digital_metrics], df['total_funding_log'])
    PartialDependenceDisplay.from_estimator(
        estimator=full_estimator,
        X=df[digital_metrics],
        features=[pdp_feature],
        grid_resolution=50,
        ax=ax,
        line_kw={'color': '#E74C3C', 'linestyle': '--', 'label': 'Full Dataset PDP'}
    )

    # Formatting the plot
    title_suffix = 'Log-transformed Metric' if platform != 'overall_digital_presence' else 'Composite Score'
    plt.xlabel(title_suffix, fontsize=12, labelpad=10)
    plt.ylabel('Impact on Funding (log EUR)', fontsize=12, labelpad=10)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.title(f'{platform.capitalize()} Impact Analysis\n(PDP: {title_suffix})', fontsize=13, pad=20, weight='bold')
    plt.legend()
    plt.savefig(f'results/h1-h4/{platform}_partial_dependence.png', dpi=400, bbox_inches='tight')
    plt.close()
    
# Analyze binary platform (CEO connections dummy)
plt.figure(figsize=(10,6))
plt.figure(figsize=(10,6))
sns.boxplot(x='ceo_connections_dummy', y='total_funding_log', data=df,
            hue='ceo_connections_dummy',  # Add hue parameter
            palette=['#4B8BBE', '#FF7A59'],
            legend=False)  # Disable legend
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

plt.savefig('results/h1-h4/ceo_connections_dummy_boxplot.png', dpi=300, bbox_inches='tight')
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
plt.savefig('results/h1-h4/ceo_connections_dummy_partial_dependence.png', dpi=400, bbox_inches='tight')
plt.close()

# Calculate partial correlations controlling for company age, industry, stage, and location
industry_dummies = [
    'industrials', 'information_technology', 'communication_services',
    'real_estate', 'financials', 'consumer_discretionary', 
    'web3_blockchain', 'health_care', 'materials', 'consumer_staples',
    'other', 'utilities'  # 'energy' as reference
]

state_dummies = [
    'baden_wuerttemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
    'hamburg', 'hessen', 'mecklenburg_vorpommern', 'niedersachsen',
    'nordrhein_westfalen', 'rheinland_pfalz', 'saarland', 'sachsen',
    'sachsen_anhalt', 'schleswig_holstein'  # 'thueringen' as reference
]

control_vars = ['age_log', 'startup_stage'] + industry_dummies + state_dummies

def compute_partial_correlation(df, x_col, y_col, control_cols):
    """Calculate partial correlation using regression residuals"""
    valid_data = df[[x_col, y_col] + control_cols].dropna()
    if len(valid_data) < 20:  # Minimum sample size check
        return np.nan, np.nan
    
    try:
        X = add_constant(valid_data[control_cols])
        
        # Residualize X
        model_x = OLS(valid_data[x_col], X).fit()
        resid_x = model_x.resid
        
        # Residualize Y
        model_y = OLS(valid_data[y_col], X).fit()
        resid_y = model_y.resid
        
        return pearsonr(resid_x, resid_y)
    except:
        return np.nan, np.nan

# Calculate partial correlations with all controls
partial_corrs_full = {}
partial_pvals_full = {}

digital_metrics = [
    'overall_digital_presence', 'twitter_log', 'instagram_log',
    'linkedin_log', 'ceo_connections_log', 'ceo_connections_dummy',
    'articles_log'
]

for metric in digital_metrics:
    corr, pval = compute_partial_correlation(df, metric, 'total_funding_log', control_vars)
    partial_corrs_full[metric] = corr
    partial_pvals_full[metric] = pval

# Calculate both versions of partial correlations
partial_corrs_age = {}
partial_pvals_age = {}
partial_corrs_full = {}
partial_pvals_full = {}

for metric in digital_metrics:
    # Age-only control
    corr_age, pval_age = compute_partial_correlation(df, metric, 'total_funding_log', ['age_log'])
    partial_corrs_age[metric] = corr_age
    partial_pvals_age[metric] = pval_age
    
    # Full controls
    corr_full, pval_full = compute_partial_correlation(df, metric, 'total_funding_log', control_vars)
    partial_corrs_full[metric] = corr_full
    partial_pvals_full[metric] = pval_full

# Create enhanced results dataframe
results_df = pd.DataFrame({
    'metric': digital_metrics,
    'type': ['Composite'] + ['Social']*3 + ['Network']*2 + ['Media'],
    'spearman_rho': [spearman_corr_matrix.loc[m, 'total_funding_log'] for m in digital_metrics],
    'partial_rho_age': [partial_corrs_age[m] for m in digital_metrics],
    'partial_rho_full_model': [partial_corrs_full[m] for m in digital_metrics],
    'p_value_full': [partial_pvals_full[m] for m in digital_metrics]
})

# Apply FDR correction to new p-values
_, pvals_fdr_full, _, _ = multipletests(results_df['p_value_full'], method='fdr_bh')
results_df['p_value_fdr'] = pvals_fdr_full

# Formatting function with significance stars
def format_results(row):
    if pd.isna(row['partial_rho_full_model']):
        return 'NA'
    
    corr = row['partial_rho_full_model']
    pval = row['p_value_fdr']
    
    stars = ''
    if pval < 0.001: stars = '***'
    elif pval < 0.01: stars = '**'
    elif pval < 0.05: stars = '*'
    
    return f"{corr:.2f}{stars}"

results_df['formatted_result'] = results_df.apply(format_results, axis=1)

# Save updated results
results_df.to_csv('results/h1-h4/controlled_correlations.csv', index=False)

print("\nDigital Presence vs Funding Success (FDR-corrected):")
print(results_df[['metric', 'type', 'formatted_result', 'partial_rho_full_model', 'p_value_fdr']]
      .rename(columns={
          'formatted_result': 'Full Model ρ',
          'partial_rho_full_model': 'Partial ρ',
          'p_value_fdr': 'FDR adj. p-value'
      })
      .to_markdown(index=False, floatfmt=("", "", ".2f", ".2f", ".3f")))

# 1. Sample size check
original_count = len(df)
controlled_count = len(df.dropna(subset=control_vars + ['total_funding_log']))
print(f"Sample size reduction: {original_count} → {controlled_count} "
      f"({controlled_count/original_count:.1%} retained)")

# 2. Variance Inflation Factors
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif_data = pd.DataFrame()
X_vals = add_constant(df[control_vars].dropna()).values

vif_data["feature"] = ['const'] + control_vars
vif_data["VIF"] = [variance_inflation_factor(X_vals, i) 
                  for i in range(len(vif_data["feature"]))]

print("\nVariance Inflation Factors:")
print(vif_data.to_markdown(index=False))

# Create regression plots
plt.figure(figsize=(10,6))
sns.barplot(x='partial_rho_full_model', y='metric', data=results_df,
            palette='viridis', edgecolor='black')

plt.axvline(0, color='gray', linestyle='--')
plt.xlabel("Partial Correlation Coefficient (Controlled for Industry, Stage, Location)")
plt.ylabel("Digital Presence Metric")
plt.title("Adjusted Correlation with Funding Amount\n(Controlling for Key Confounders)",
         fontsize=14, pad=20)

plt.tight_layout()
plt.savefig('results/h1-h4/controlled_correlations_plot.png', dpi=300, bbox_inches='tight')
plt.close()

def bootstrap_spearman_ci(metric, n_iterations=1000):
    """Calculate bootstrap 95% CI for Spearman correlation"""
    bootstrap_corrs = []
    for _ in range(n_iterations):
        sample = resample(df, replace=True)
        corr = spearmanr(sample[metric], sample['total_funding_log']).correlation
        bootstrap_corrs.append(corr)
    return np.nanpercentile(bootstrap_corrs, [2.5, 97.5])

# Metrics to analyze - matches your digital_metrics list
metrics_to_bootstrap = [
    'overall_digital_presence',
    'twitter_log',
    'instagram_log',
    'linkedin_log',
    'ceo_connections_log',
    'ceo_connections_dummy',
    'articles_log'
]

# Calculate bootstrap CIs for all metrics
bootstrap_results = {}
for metric in metrics_to_bootstrap:
    ci = bootstrap_spearman_ci(metric)
    point_estimate = spearmanr(df[metric], df['total_funding_log']).correlation
    bootstrap_results[metric] = {
        'estimate': point_estimate,
        'ci_lower': ci[0],
        'ci_upper': ci[1]
    }

# Save results to CSV
bootstrap_df = pd.DataFrame(bootstrap_results).T
bootstrap_df.to_csv('results/h1-h4/bootstrap_confidence_intervals.csv')

# Create forest plot
plt.figure(figsize=(12, 8))
metric_labels = {
    'overall_digital_presence': 'Overall Digital',
    'twitter_log': 'Twitter',
    'instagram_log': 'Instagram',
    'linkedin_log': 'LinkedIn',
    'ceo_connections_log': 'CEO Connections',
    'ceo_connections_dummy': 'CEO 500+ Dummy',
    'articles_log': 'Media Articles'
}

for i, metric in enumerate(metrics_to_bootstrap):
    res = bootstrap_results[metric]
    
    # Plot main estimate
    plt.plot(res['estimate'], i, 'o', color='#2E86C1', markersize=8)
    
    # Plot confidence interval
    plt.hlines(y=i, xmin=res['ci_lower'], xmax=res['ci_upper'], 
               color='#85C1E9', linewidth=3, alpha=0.7)
    
    # Add text annotation
    ci_text = f"{res['estimate']:.2f} [{res['ci_lower']:.2f}, {res['ci_upper']:.2f}]"
    plt.text(0.95, i, ci_text, 
             ha='right', va='center',
             fontsize=10, 
             transform=plt.gca().get_yaxis_transform())

# Formatting
plt.yticks(range(len(metrics_to_bootstrap)), 
          [metric_labels[m] for m in metrics_to_bootstrap])
plt.axvline(0, color='gray', linestyle='--', alpha=0.7)
plt.xlabel('Spearman Correlation Coefficient (95% CI)', fontsize=12)
plt.title('Bootstrap Confidence Intervals for Digital Presence Metrics', 
         fontsize=14, pad=20, weight='bold')
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)

plt.tight_layout()
plt.savefig('results/h1-h4/bootstrap_forest_plot.png', dpi=300, bbox_inches='tight')
plt.close()

# Print results
print("\nBootstrap 95% Confidence Intervals:")
print(pd.DataFrame(bootstrap_results).T[['estimate', 'ci_lower', 'ci_upper']]
      .rename(columns=lambda x: x.replace('_', ' ').title())
      .rename_axis('Metric')
      .reset_index()
      .to_markdown(index=False, floatfmt=".2f"))

# Save corrected results
significant_corr_corrected.to_csv('results/h1-h4/significant_pearson_correlations_fdr.csv')
