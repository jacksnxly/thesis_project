# Import necessary libraries
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Download required NLTK data files (only need to run once)
nltk.download('punkt')
nltk.download('stopwords')

# -------------------------------
# 1. Define Modesty Constructs
# -------------------------------

# List of modesty-related single-word keywords
modesty_single_words = {
    'humble', 'understatement', 'modest', 'showmanship',
    'overpromotional', 'reticence', 'boasting', 'posturing',
    'noisy', 'authenticity', 'substance', 'hype', 'avoid',
    'focus', 'proven', 'results', 'overhyped', 'hyped',
    'modesty'  # Include the word itself
}

# List of modesty-related phrases
modesty_phrases = {
    'avoid overhyped claims',
    'no showmanship',
    'focus on substance',
    'avoid overpromotional',
    'avoid hype',
    'proven results',
    'avoid overhyped',
    'avoid hype',
    'avoid over-promotional',
    'no over promotional',
    'focus on substance'
}

# -------------------------------
# 2. Load Survey Data
# -------------------------------

# Specify the path to your CSV file
# Replace 'data/raw/vc_questionaire.csv' with your actual file path if different
data_path = 'data/raw/vc_questionaire.csv'

# Load the data into a pandas DataFrame
df = pd.read_csv(data_path)

# Display the first few rows to verify
print("Initial Data Sample:")
print(df.head())

# -------------------------------
# 3. Text Preprocessing
# -------------------------------

# Specify the columns containing open-ended responses
# Replace these with your actual column names
open_ended_columns = [
    'In your own words, how would you define “digital presence” for an entrepreneur?',
    "Why do you think this change has occurred?",
    "Which single component of an entrepreneur’s digital presence do you believe most strongly correlates with successful VC funding outcomes in Germany?",
    'Please share an example (if any) of when an entrepreneur’s digital presence influenced your decision positively or negatively',
    'In the German context, which cultural factors do you find most critical when evaluating an entrepreneur’s credibility online?',
    "From your perspective, what are the key differences (if any) in evaluating digital presence between German VCs and international VCs?",
    'Is there anything else you’d like to share about how you evaluate an entrepreneur’s digital presence in the German market?',
    "Please elaborate."
    # Add more columns if necessary
]

# Function to preprocess text: lowercase, remove punctuation, tokenize, remove stopwords
def preprocess_text(text):
    if pd.isna(text):
        return []
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

# Apply preprocessing to all open-ended response columns
for col in open_ended_columns:
    df[f'tokens_{col}'] = df[col].apply(preprocess_text)

# -------------------------------
# 4. Modesty Mention Counting
# -------------------------------

# Function to count modesty mentions across multiple token and text columns
def count_modesty_mentions(row, token_cols, text_cols):
    count = 0
    for token_col, text_col in zip(token_cols, text_cols):
        tokens = row[token_col]
        text = row[text_col]
        
        # Check if text is a string before processing
        if isinstance(text, str):
            text = text.lower()
            
            # Count single-word keyword mentions
            count += sum(1 for word in tokens if word in modesty_single_words)
            
            # Count phrase mentions
            for phrase in modesty_phrases:
                if phrase in text:
                    count += 1
        else:
            # If text is not a string (e.g., NaN), skip processing
            continue
    return count

# Define corresponding token and text columns
token_cols = [f'tokens_{col}' for col in open_ended_columns]
text_cols = open_ended_columns

# Apply the counting function to each row
df['modesty_mentions'] = df.apply(lambda row: count_modesty_mentions(row, token_cols, text_cols), axis=1)

# -------------------------------
# 5. Modesty Score Calculation
# -------------------------------

# Calculate the total number of tokens across all open-ended responses for each row
df['total_tokens'] = df[token_cols].apply(lambda row: sum(len(tokens) for tokens in row), axis=1)

# Avoid division by zero by setting total_tokens to 1 where it's 0
df['total_tokens'] = df['total_tokens'].replace(0, 1)

# Calculate the Modesty Score as the proportion of modesty mentions
df['modesty_score'] = df['modesty_mentions'] / df['total_tokens']

# Optional: Scale the Modesty Score to a 0-5 range
# df['modesty_score_scaled'] = df['modesty_score'] * 5

# -------------------------------
# 6. Integration and Saving
# -------------------------------

# Define the output directory
output_dir = 'results/qualitative_analysis/'

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Display the calculated Modesty Scores
print("\nModesty Scores:")
print(df[['modesty_mentions', 'total_tokens', 'modesty_score']])

# Save the updated DataFrame with Modesty Scores to a new CSV in the specified directory
output_csv_path = os.path.join(output_dir, 'survey_data_with_modesty_scores.csv')
df.to_csv(output_csv_path, index=False)
print(f"\nModesty scores have been saved to '{output_csv_path}'.")

# -------------------------------
# 7. Save Overall Modesty Scores Separately
# -------------------------------

# Identify a unique identifier for each response
# Common choices: 'Email Address', 'Timestamp', or any unique ID column
# Replace 'Email Address' with your actual identifier column name if different
identifier_column = 'Email Address'  # Adjust as needed

# Check if the identifier column exists
if identifier_column in df.columns:
    # Select the identifier and Modesty Score
    modesty_scores = df[[identifier_column, 'modesty_score']]
else:
    # If no identifier, use the DataFrame index
    print(f"Identifier column '{identifier_column}' not found. Using DataFrame index as identifier.")
    modesty_scores = df[['modesty_score']].reset_index()
    modesty_scores.rename(columns={'index': 'Response_ID'}, inplace=True)

# Save the Modesty Scores to a separate CSV
modesty_scores_csv_path = os.path.join(output_dir, 'overall_modesty_scores.csv')
modesty_scores.to_csv(modesty_scores_csv_path, index=False)
print(f"Overall Modesty Scores have been saved to '{modesty_scores_csv_path}'.")

# -------------------------------
# 8. Visualization and Validation
# -------------------------------

# Histogram of Modesty Scores
plt.figure(figsize=(8,6))
sns.histplot(df['modesty_score'], bins=10, kde=True, color='skyblue')
plt.title('Distribution of Modesty Scores')
plt.xlabel('Modesty Score')
plt.ylabel('Frequency')
plt.tight_layout()
hist_path = os.path.join(output_dir, 'modesty_score_distribution.png')
plt.savefig(hist_path, dpi=300)
plt.show()
print(f"Histogram saved to '{hist_path}'.")

# Boxplot of Modesty Scores
plt.figure(figsize=(8,6))
sns.boxplot(x=df['modesty_score'], color='lightgreen')
plt.title('Boxplot of Modesty Scores')
plt.xlabel('Modesty Score')
plt.tight_layout()
boxplot_path = os.path.join(output_dir, 'modesty_score_boxplot.png')
plt.savefig(boxplot_path, dpi=300)
plt.show()
print(f"Boxplot saved to '{boxplot_path}'.")

# -------------------------------
# 9. Summary Statistics (Optional)
# -------------------------------

# Display summary statistics for the Modesty Score
print("\nModesty Score Summary Statistics:")
print(df['modesty_score'].describe())

# -------------------------------
# 10. Example Outputs (Optional)
# -------------------------------

# Display example responses with their Modesty Scores
print("\nExample Responses with Modesty Scores:")
for index, row in df.iterrows():
    print(f"\nResponse {index + 1}:")
    for col in open_ended_columns:
        response = row[col]
        if pd.isna(response):
            response = "No response."
        print(f" - {col}: {response}")
    print(f" - Modesty Mentions: {row['modesty_mentions']}")
    print(f" - Total Tokens: {row['total_tokens']}")
    print(f" - Modesty Score: {row['modesty_score']:.4f}")