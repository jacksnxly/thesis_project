import os

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------------------------------------------------------
# 1. CREATE DIRECTORY FOR RESULTS
# -----------------------------------------------------------------------------
os.makedirs('results/stage_specific_analysis', exist_ok=True)

# -----------------------------------------------------------------------------
# 2. LOAD DATA
# -----------------------------------------------------------------------------
df = pd.read_csv("data/processed/final_h1_data.csv")

# -----------------------------------------------------------------------------
# 3. DATA PREPARATION
# -----------------------------------------------------------------------------
# 3A. CREATE DIGITAL PRESENCE COMPOSITE
df['overall_digital_presence'] = df[[
    'twitter_log', 
    'instagram_log', 
    'linkedin_log',
    'ceo_connections_log', 
    'articles_log'
]].mean(axis=1)

# 3B. CHECK STARTUP STAGE VALUES
#    We expect: 1=Pre-Seed, 2=Seed, 3=Series A
#    If you have different codes, adjust accordingly.
print("Unique stages in the data:", df['startup_stage'].unique())

# 3C. (OPTIONAL) DROP ROWS WITH MISSING DATA IN KEY COLUMNS
#    Adjust this as needed if you prefer imputation or partial usage.
key_cols = [
    'total_funding_log',
    'overall_digital_presence',
    'startup_stage',
    'age_log',
    'articles_log',
    'ceo_connections_log',
    'ceo_connections_dummy'
]
df = df.dropna(subset=key_cols).copy()

# 3D. MAKE SURE startup_stage IS IN {1, 2, 3}
df = df[df['startup_stage'].isin([1, 2, 3])].copy()
df['startup_stage'] = df['startup_stage'].astype(int)

# -----------------------------------------------------------------------------
# 4. DEFINE MODELS
# -----------------------------------------------------------------------------

# --- 4A. H7A-STYLE MODEL ---
# Hypothesis: "The influence of digital presence on funding differs by stage."
#
# We treat 'startup_stage' as a 3-level categorical variable via C(startup_stage).
# The model includes:
#   total_funding_log ~ overall_digital_presence
#                     + C(startup_stage)
#                     + interaction: overall_digital_presence * C(startup_stage)

formula_h7a = """
    total_funding_log 
    ~ overall_digital_presence
    + C(startup_stage)
    + overall_digital_presence:C(startup_stage)
"""

model_h7a = smf.ols(formula=formula_h7a, data=df).fit()
print("=== H7a Model Summary ===")
print(model_h7a.summary())

# Save summary
with open('results/stage_specific_analysis/h7a_regression_summary.txt', 'w') as f:
    f.write(model_h7a.summary().as_text())

# --- 4B. H7B-STYLE MODEL ---
# Hypothesis: "The importance of verifiable business metrics relative to digital presence 
#              changes (increases) from Pre-Seed to Seed to Series A."
#
# We include your known business metrics: age_log, articles_log, ceo_connections_log, ceo_connections_dummy.
# We fully interact them (plus digital presence) with startup_stage to see if their 
# effects differ by stage.

business_metrics = ["age_log", "articles_log", "ceo_connections_log", "ceo_connections_dummy"]

# Build up the formula string for interactions. For example:
# total_funding_log ~ overall_digital_presence + C(startup_stage) 
#                   + overall_digital_presence:C(startup_stage)
#                   + age_log + age_log:C(startup_stage)
#                   + articles_log + articles_log:C(startup_stage)
#                   + ceo_connections_log + ceo_connections_log:C(startup_stage)
#                   + ceo_connections_dummy + ceo_connections_dummy:C(startup_stage)

interaction_parts = []
for bm in business_metrics:
    interaction_parts.append(bm)
    interaction_parts.append(f"{bm}:C(startup_stage)")

# Join them with "+"
business_formula_part = " + ".join(interaction_parts)

formula_h7b = f"""
    total_funding_log
    ~ overall_digital_presence
    + C(startup_stage)
    + overall_digital_presence:C(startup_stage)
    + {business_formula_part}
"""

model_h7b = smf.ols(formula=formula_h7b, data=df).fit()
print("\n=== H7b Model Summary ===")
print(model_h7b.summary())

# Save summary
with open('results/stage_specific_analysis/h7b_regression_summary.txt', 'w') as f:
    f.write(model_h7b.summary().as_text())

# -----------------------------------------------------------------------------
# 5. EXTRACT COEFFICIENTS & CONFIDENCE INTERVALS FOR EASY REVIEW
# -----------------------------------------------------------------------------
h7b_params = model_h7b.params
h7b_conf = model_h7b.conf_int()
h7b_results = pd.DataFrame({
    'variable': h7b_params.index,
    'coef': h7b_params.values,
    'ci_lower': h7b_conf[0].values,
    'ci_upper': h7b_conf[1].values
})
h7b_results.to_csv('results/stage_specific_analysis/h7b_regression_coeffs.csv', index=False)

# -----------------------------------------------------------------------------
# 6. OPTIONAL: PLOTTING PREDICTED FUNDING BY DIGITAL PRESENCE FOR EACH STAGE
# -----------------------------------------------------------------------------
# This helps visualize if digital presence slopes differ for Pre-Seed, Seed, Series A.

# Create a grid of digital_presence values
dp_grid = np.linspace(df['overall_digital_presence'].min(), 
                      df['overall_digital_presence'].max(), 50)

# For each stage in [1=Pre-Seed, 2=Seed, 3=SeriesA], create a data subset 
# with median values for business metrics (if you want to hold them constant)
pred_dfs = []
for stage_val in [1, 2, 3]:
    tmp = pd.DataFrame({
        'overall_digital_presence': dp_grid,
        'startup_stage': stage_val,
        # Provide median (or mean) values for each business metric included in H7b
        'age_log': df['age_log'].median() if 'age_log' in df else 0,
        'articles_log': df['articles_log'].median() if 'articles_log' in df else 0,
        'ceo_connections_log': df['ceo_connections_log'].median() if 'ceo_connections_log' in df else 0,
        'ceo_connections_dummy': df['ceo_connections_dummy'].median() if 'ceo_connections_dummy' in df else 0
    })
    pred_dfs.append(tmp)

pred_data = pd.concat(pred_dfs, ignore_index=True)

# Add predicted log-funding and predicted funding
pred_data['predicted_funding_log'] = model_h7b.predict(pred_data)
pred_data['predicted_funding'] = np.exp(pred_data['predicted_funding_log'])

# Map numeric stage to labels
stage_label_map = {
    1: 'Pre-Seed',
    2: 'Seed',
    3: 'Series A'
}
pred_data['stage_label'] = pred_data['startup_stage'].map(stage_label_map)

# Plot
plt.figure(figsize=(10, 6))
sns.lineplot(data=pred_data,
             x='overall_digital_presence',
             y='predicted_funding',
             hue='stage_label',
             palette=['#4B8BBE', '#FFD43B', '#FF7A59'])  # example palette

plt.title("Predicted Funding vs Digital Presence, by Stage")
plt.xlabel("Overall Digital Presence")
plt.ylabel("Predicted Funding (exp of log)")
plt.legend(title="Stage")
plt.tight_layout()
plt.savefig("results/stage_specific_analysis/h7b_predicted_plot.png", dpi=300)
plt.show()

# -----------------------------------------------------------------------------
# 7. CREATE A TEXT REPORT
# -----------------------------------------------------------------------------
with open('results/stage_specific_analysis/stage_analysis_report.txt', 'w') as f:
    f.write("======= MULTI-STAGE ANALYSIS REPORT =======\n\n")
    f.write("[H7a-Style Model: Digital Presence x Stage (3 levels)]\n")
    f.write(model_h7a.summary().as_text())
    f.write("\n\n")

    f.write("[H7b-Style Model: Business Metrics & Digital Presence x Stage (3 levels)]\n")
    f.write(model_h7b.summary().as_text())
    f.write("\n\n")
    
    f.write("Interpretation Tips:\n")
    f.write("1) For H7a: Look at 'overall_digital_presence:C(startup_stage)[T.x]'.\n")
    f.write("   - If those interaction coefficients are +/- and significant, it indicates\n")
    f.write("     how digital presence differs in effect from the baseline stage.\n\n")
    f.write("2) For H7b: Look at each 'metric:C(startup_stage)[T.x]' term.\n")
    f.write("   - Positive (and significant) => that metric's slope is stronger in stage x\n")
    f.write("     than in the baseline stage (usually Pre-Seed).\n")
    f.write("   - Negative => weaker slope than the baseline.\n")

print("Analysis complete. Check 'results/stage_specific_analysis' for outputs.")