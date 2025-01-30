import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Statsmodels and related imports
import statsmodels.api as sm
from statsmodels.formula.api import ols

# Ensure the results directory exists
os.makedirs('results/robistness', exist_ok=True)

# 1. Load the data
df = pd.read_csv("data/processed/final_h1_data.csv")

# Calculate overall digital presence composite score
df['overall_digital_presence_log'] = df[[
    'twitter_log', 'instagram_log', 'linkedin_log',
    'ceo_connections_log', 'articles_log'
]].mean(axis=1)

# 2. Re-create region and sector clusters as in the original script
df['region'] = np.select(
    [
        (df['berlin'] == 1) | (df['brandenburg'] == 1),       # East
        (df['baden_wuerttemberg'] == 1) | (df['bayern'] == 1),# South
        (df['hamburg'] == 1) | (df['niedersachsen'] == 1),    # North
        (df['nordrhein_westfalen'] == 1) | (df['hessen'] == 1)# West
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

# 3. Trim the top 5% of total_funding outliers
threshold_95 = df['total_funding'].quantile(0.95)
df_trimmed = df[df['total_funding'] < threshold_95].copy()

# (Re-run or confirm the log transform on the trimmed dataset if needed)
# Make sure 'total_funding_log' is consistent within df_trimmed
if 'total_funding_trimmed_log' not in df_trimmed.columns:
    # If for some reason total_funding_log wasn't in the data, define it
    df_trimmed['total_funding_trimmed_log'] = np.log1p(df_trimmed['total_funding'])  # or np.log(...) if no zero values
else:
    # Otherwise, just keep the existing log column
    pass

# 4. Define and fit the OLS model using the same formula
model_formula = (
    "total_funding_trimmed_log ~ twitter_log + instagram_log + linkedin_log + "
    "ceo_connections_log + ceo_connections_dummy + articles_log + "
    "overall_digital_presence_log + age_log + startup_stage + "
    "C(region) + C(sector)"
)

try:
    trimmed_model = ols(model_formula, data=df_trimmed).fit()
except Exception as e:
    print(f"Error fitting trimmed model: {e}")
    raise

# 5. Print or save the summary of the trimmed model
summary_text = trimmed_model.summary().as_text()
with open('results/robustness/robust_regression_results_trimmed.txt', 'w') as fh:
    fh.write(summary_text)

# 6. Create a coefficient plot for the trimmed model
coefs = trimmed_model.params.drop('Intercept')
cis = trimmed_model.conf_int().drop('Intercept')

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
    "OLS (Top 5% Funding Outliers Trimmed)\nDigital Presence vs Funding",
    fontsize=14, pad=20
)
plt.tight_layout()
plt.savefig('results/robustness/multiple_regression_coefficients_trimmed.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Optional: Print summary in the console
print(summary_text)
print("\nTrimmed model completed successfully. Results saved.")