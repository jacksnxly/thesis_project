import pandas as pd
from deep_translator import GoogleTranslator
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

# Download NLTK resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt_tab')

# Initialize components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def load_data(filepath):
    """Load and preprocess questionnaire data with robust cleaning"""
    df = pd.read_csv(filepath)
    
    # Identify text columns using flexible matching
    text_columns = [
        col for col in df.columns 
        if any(keyword in col for keyword in [
            'digital presence', 'change has occurred', 'example',
            'German context', 'in-person networking', 'discounted',
            'perspective', 'elaborate', 'factors will drive'
        ])
    ]
    
    # Convert to string and clean
    df = df[text_columns].fillna('').astype(str)
    
    # Remove residual non-text characters
    df = df.map(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x) if isinstance(x, str) else '')
    
    return df

def translate_text(text):
    """Translate German text to English"""
    try:
        text = str(text)
        if GoogleTranslator(source='auto').detect(text) == 'german':
            return GoogleTranslator(source='de', target='en').translate(text)
        return text
    except:
        return str(text)

def clean_text(text):
    """Enhanced cleaning pipeline"""
    text = str(text).lower()
    text = re.sub(r'\d+', '', text)  # Remove numbers
    tokens = nltk.word_tokenize(text)
    tokens = [lemmatizer.lemmatize(token) 
              for token in tokens 
              if token not in stop_words and len(token) > 2]
    return ' '.join(tokens)

def analyze_sentiment(text):
    """Get sentiment polarity score"""
    return TextBlob(text).sentiment.polarity

def generate_wordcloud(texts):
    """Create visualization of frequent terms"""
    wordcloud = WordCloud(width=800, height=400).generate(' '.join(texts))
    plt.figure(figsize=(15,8))
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig('wordcloud.png')

def topic_modeling(texts, n_topics=3):
    """Automatically detect themes using LDA"""
    vectorizer = CountVectorizer(max_df=0.95, min_df=2)
    dtm = vectorizer.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=n_topics)
    lda.fit(dtm)
    return lda, vectorizer

def main():
    # Load and prepare data
    df = load_data("data/raw/vc_questionaire.csv")
    
    # Convert all values to strings and handle NaNs
    df = df.fillna('').astype(str)
    df = df.map(translate_text).map(clean_text)
    
    # Sentiment Analysis 
    df['sentiment'] = df.map(analyze_sentiment).mean(axis=1)
    sentiment_dist = df['sentiment'].apply(
        lambda x: 'positive' if x > 0.1 else 'negative' if x < -0.1 else 'neutral'
    ).value_counts()
    
    # Word Cloud - Use only text columns
    text_df = df.drop(columns=['sentiment'], errors='ignore')
    all_text = text_df.apply(lambda col: ' '.join(col.astype(str)), axis=0).str.cat(sep=' ')
    generate_wordcloud([all_text])
    
    # Topic Modeling
    lda_model, vectorizer = topic_modeling(text_df.values.flatten())
    feature_names = vectorizer.get_feature_names_out()
    
    # Save Results
    with open("analysis_results.txt", "w") as f:
        f.write("=== Sentiment Distribution ===\n")
        f.write(str(sentiment_dist) + "\n\n")
        
        f.write("=== Key Themes ===\n")
        for idx, topic in enumerate(lda_model.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-10:-1]]
            f.write(f"Theme {idx+1}: {', '.join(top_words)}\n")
        
        f.write("\n=== Example Quotes ===")
        for col in df.columns:
            if col != 'sentiment':  # Exclude sentiment column from quotes
                f.write(f"\n\nColumn: {col}\n")
                f.write('\n\n'.join(df[col].sample(3).astype(str).tolist()))

if __name__ == "__main__":
    main()