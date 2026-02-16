"""
Fix NLTK SSL Certificate Issue
================================

This script downloads required NLTK data by temporarily disabling SSL verification.
Run this once to set up NLTK for sentiment analysis.
"""

import ssl
import nltk

print("=" * 60)
print("NLTK DATA DOWNLOADER - SSL FIX")
print("=" * 60)

# Disable SSL certificate verification (temporary fix for macOS)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

print("\n📦 Downloading NLTK data packages...")

# Download required packages
packages = [
    ('vader_lexicon', 'Sentiment analyzer'),
    ('punkt', 'Tokenizer'),
    ('punkt_tab', 'Tokenizer tables (NLTK 3.9+)'),
    ('stopwords', 'Stopword filter'),
    ('wordnet', 'Lemmatizer'),
]

for package, description in packages:
    print(f"\n⬇️  Downloading {package} ({description})...")
    try:
        nltk.download(package, quiet=False)
        print(f"✅ {package} downloaded successfully")
    except Exception as e:
        print(f"❌ Failed to download {package}: {e}")

print("\n" + "=" * 60)
print("✅ NLTK DATA DOWNLOAD COMPLETE")
print("=" * 60)

# Test that everything works
print("\n🧪 Testing sentiment analyzer...")
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    
    test_text = "This event was excellent and very informative!"
    scores = sia.polarity_scores(test_text)
    
    print(f"\nTest text: '{test_text}'")
    print(f"Sentiment scores:")
    print(f"  - Compound: {scores['compound']:.3f}")
    print(f"  - Positive: {scores['pos']:.3f}")
    print(f"  - Neutral: {scores['neu']:.3f}")
    print(f"  - Negative: {scores['neg']:.3f}")
    
    print("\n✅ Sentiment analysis is working correctly!")
    print("\nYou can now run:")
    print("  python3 test_sentiment_analysis.py")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    print("\nPlease try running the script again.")
