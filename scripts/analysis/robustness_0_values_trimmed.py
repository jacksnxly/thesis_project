import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Statsmodels and related imports
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Ensure the results directory exists
os.makedirs('results/robustness_0_values_trimmed', exist_ok=True)

# 1. Load the data
df = pd.read_csv("data/processed/final_h1_data.csv")

# Calculate overall digital presence composite score
df['overall_digital_presence_log'] = df[[
    'twitter_log', 'instagram_log', 'linkedin_log',
    'ceo_connections_log', 'articles_log'
]].mean(axis=1)

# 2. Re-create region and sector clusters
df['region'] = np.select(
    [
        (df['berlin'] == 1) | (df['brandenburg'] == 1),        # East
        (df['baden_wuerttemberg'] == 1) | (df['bayern'] == 1), # South
        (df['hamburg'] == 1) | (df['niedersachsen'] == 1),     # North
        (df['nordrhein_westfalen'] == 1) | (df['hessen'] == 1) # West
    ],
    ['East', 'South', 'North', 'West'],
    default='Other'
)

df['sector'] = np.select(
    [
        (df['information_technology'] == 1) | (df['web3_blockchain'] == 1),
        (df['health_care'] == 1) | (df['consumer_discretionary'] == 1),
        (df['financials'] == 1) | (df['real_estate'] == 1),
        (df['industrials'] == 1) | (df['materials'] == 1)
    ],
    ['Tech', 'Consumer', 'Finance', 'Industrial'],
    default='Other'
)

# 3. Remove companies with total_funding == 0.0
df_nozero = df[df['total_funding'] > 0].copy()

# Make sure we have a 'total_funding_log' column in df_nozero
if 'total_funding_log' not in df_nozero.columns:
    # If not present, create it
    df_nozero['total_funding_log'] = np.log1p(df_nozero['total_funding'])
else:
    # If it already exists, it should match the subset
    pass

# 4. Define and fit the OLS model using the same formula
model_formula = (
    "total_funding_log ~ twitter_log + instagram_log + linkedin_log + "
    "ceo_connections_log + ceo_connections_dummy + articles_log + "
    "overall_digital_presence_log + age_log + startup_stage + "
    "C(region) + C(sector)"
)

try:
    nozero_model = ols(model_formula, data=df_nozero).fit()
except Exception as e:
    print(f"Error fitting model on no-zero-funding subset: {e}")
    raise

# 5. Print or save the summary of the new model
summary_text = nozero_model.summary().as_text()
with open('results/robustness_0_values_trimmed/robust_regression_results_nozero.txt', 'w') as fh:
    fh.write(summary_text)

# 6. Create a coefficient plot for the new model
coefs = nozero_model.params.drop('Intercept')
cis = nozero_model.conf_int().drop('Intercept')

plt.figure(figsize=(10, 6))
sns.pointplot(x=coefs.values, y=coefs.index, join=False, color='#2E86C1')
plt.errorbar(
    x=coefs.values,
    y=coefs.index,
    xerr=[
        coefs.values - cis[0],
        cis[1] - coefs.values
    ],
    fmt='none',
    ecolor='black',
    capsize=3
)

plt.axvline(0, color='gray', linestyle='--')
plt.xlabel("Regression Coefficient (β)")
plt.title(
    "OLS (Excluding 0-Funding Startups)\nDigital Presence vs Funding",
    fontsize=14, pad=20
)
plt.tight_layout()
plt.savefig('results/robustness_0_values_trimmed/multiple_regression_coefficients_nozero.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Optional: Print summary in the console
print(summary_text)
print("\nModel excluding 0.0 funding values completed successfully. Results saved.")