import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency, spearmanr

# Load the questionnaire data
df = pd.read_csv("data/raw/vc_questionaire.csv")

# ==================================================================
# 1. DEFINE ALL QUESTION MAPPINGS (ADDED NEW QUESTIONS HERE)
# ==================================================================

question_mappings = {
    # Existing Likert-scale questions
    "Likert": {
        "Rate the importance of an entrepreneur’s digital presence when making early-stage investment decisions (Pre-seed to Series A).": "Digital Presence Importance",
        "Professional Networks (e.g., LinkedIn connections, endorsements)": "Professional Networks",
        "Online Reputation (e.g., press coverage, testimonials, Glassdoor reviews)": "Online Reputation",
        "Social Media Engagement (e.g., Twitter, Instagram, YouTube activity)": "Social Media Engagement",
        "Digital Thought Leadership (e.g., blog posts, podcast appearances, conference talks shared online)": "Digital Thought Leadership",
        "On a scale from 1 (Not at all) to 5 (Very much), how much do you believe German cultural factors (e.g., risk aversion, traditional networking norms) influence your evaluation of an entrepreneur’s digital presence?": "Cultural Factors Influence"
    },
    
    # New ordinal questions (ADDED)
    "Ordinal": {
        "In your opinion, how has the importance of digital presence changed over the last 5 years for early-stage funding?": {
            "name": "5yr Digital Change",
            "mapping": {
                "Decreased Significantly": 1,
                "Decreased Slightly": 2,
                "Remained the Same": 3,
                "Increased Slightly": 4,
                "Increased Significantly": 5
            }
        },
        "To what extent do you analyze or verify an entrepreneur’s online footprint (e.g., checking profiles, reading articles, viewing social media) before deciding to invest?": {
            "name": "Verification Frequency",
            "mapping": {
                "Not at all": 1,
                "Occasionally": 2,
                "Often": 3,
                "Extensively": 4
            }
        },
        "How do traditional in-person networking and references compare to an entrepreneur’s digital presence when evaluating them in the German VC scene?": {
            "name": "In-person vs Digital",
            "mapping": {
                "In-person/network-based references are far more important": 1,
                "In-person/network-based references are somewhat more important": 2,
                "Both are equally important": 3,
                "Digital presence is somewhat more important": 4,
                "Digital presence is far more important": 5
            }
        },
        "Looking ahead 3–5 years, how do you see the importance of an entrepreneur’s digital presence evolving for pre-seed to Series A funding decisions in Germany?": {
            "name": "Future Importance",
            "mapping": {
                "It will decrease significantly": 1,
                "It will decrease slightly": 2,
                "It will stay about the same": 3,
                "It will increase slightly": 4,
                "It will increase significantly": 5
            }
        }
    },
    
    # New categorical questions (ADDED)
    "Categorical": {
        "Based on your experience, do you believe German VCs place a different level of importance on entrepreneurs’ digital presence than international VCs do?": {
            "name": "German vs Intl VCs",
            "mapping": {
                "Yes, German VCs place MORE importance": 1,
                "Yes, German VCs place LESS importance": 2,
                "No, it’s about the same": 3
            }
        },
        "Do you foresee a convergence of German VC evaluation criteria with global standards regarding digital presence in the near future?": {
            "name": "Convergence Forecast",
            "mapping": {
                "Definitely not": 1,
                "Probably not": 2,
                "Neutral/Uncertain": 3,
                "Probably yes": 4,
                "Definitely yes": 5
            }
        },
        "Overall, do you think an entrepreneur’s digital presence can compensate for limited in-person connections in the German VC ecosystem?": {
            "name": "Digital Compensation",
            "mapping": {
                "Strongly disagree": 1,
                "Disagree": 2,
                "Neutral": 3,
                "Agree": 4,
                "Strongly agree": 5
            }
        }
    }
}

# ==================================================================
# 2. DATA CLEANING (UPDATED)
# ==================================================================

# Process all question types
df = df.rename(columns=question_mappings["Likert"])

# Process ordinal questions
for q, config in question_mappings["Ordinal"].items():
    df[config["name"]] = df[q].map(config["mapping"])

# Process categorical questions
for q, config in question_mappings["Categorical"].items():
    df[config["name"]] = df[q].map(config["mapping"])

# Get all analysis columns
analysis_cols = (
    list(question_mappings["Likert"].values()) +
    [v["name"] for v in question_mappings["Ordinal"].values()] +
    [v["name"] for v in question_mappings["Categorical"].values()]
)

# Clean numerical data
df[analysis_cols] = df[analysis_cols].apply(pd.to_numeric, errors='coerce')
df = df.dropna(subset=analysis_cols, how='all')

# ==================================================================
# 3. ANALYSIS (UPDATED)
# ==================================================================

# 1. Descriptive Statistics (EXPANDED)
desc_stats = df[analysis_cols].describe().T
desc_stats['mode'] = df[analysis_cols].mode().iloc[0].values
print("Descriptive Statistics:\n", desc_stats)

# 2. Visualizations (EXPANDED)
plt.figure(figsize=(18, 20))
rows, cols = 5, 4  # Adjusted grid for more questions

for i, col in enumerate(analysis_cols, 1):
    plt.subplot(rows, cols, i)
    ax = sns.countplot(x=col, data=df, hue=col, palette="viridis", legend=False)  # Modified line
    plt.title(col, fontsize=12, pad=10)
    plt.xlabel("")
    plt.xticks(ha='right')
    
plt.tight_layout(pad=3.0)
plt.savefig("results/qualitative_analysis/full_distributions.png", dpi=600)
plt.show()

# 3. Correlation Analysis (NEW)
corr_matrix = df[analysis_cols].corr(method='spearman')
plt.figure(figsize=(20, 15))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Spearman Correlation Matrix")
plt.savefig("results/qualitative_analysis/correlation_matrix.png", dpi=600)

# 4. Advanced Analysis (UPDATED)
# Example: Relationship between verification and cultural factors
cross_tab = pd.crosstab(
    df["Verification Frequency"],
    df["Cultural Factors Influence"]
)
chi2, p, dof, expected = chi2_contingency(cross_tab)
print(f"\nVerification vs Cultural Factors: χ²={chi2:.2f}, p={p:.4f}")

# 5. Markdown Reports (UPDATED)
desc_stats.to_markdown("results/qualitative_analysis/full_descriptives.md")

# Frequency tables
with open("results/qualitative_analysis/full_frequencies.md", "w") as f:
    for col in analysis_cols:
        freq = df[col].value_counts(normalize=True).sort_index() * 100
        f.write(f"### {col}\n")
        f.write(freq.round(2).to_markdown() + "\n\n")