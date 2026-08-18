# 02_clean_filter.py
# Cleans raw scraped reviews, then isolates freshness/quality-related
# complaints using a keyword first pass.
# Run after 01_scrape.py in the same (Drive-mounted) Colab session.

import pandas as pd
import re

# ============ CLEAN ============
df = pd.read_csv('raw_reviews.csv')
print(f"Starting: {len(df)} reviews")

df = df.dropna(subset=['review_text'])
df['review_text'] = df['review_text'].astype(str).str.strip()
df = df[df['review_text'] != '']
df = df.drop_duplicates(subset=['review_text'])

# Drop too-short reviews — not enough signal for topic modeling later
df['word_count'] = df['review_text'].apply(lambda x: len(x.split()))
df = df[df['word_count'] >= 5]

# Drop reviews that are just emojis/symbols, no real words
def has_real_words(text):
    return len(re.findall(r'[a-zA-Z]{2,}', text)) >= 3
df = df[df['review_text'].apply(has_real_words)]

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
df['clean_text'] = df['review_text'].apply(clean_text)
df['clean_word_count'] = df['clean_text'].apply(lambda x: len(x.split()))
df = df[df['clean_word_count'] >= 5]

df['date'] = pd.to_datetime(df['date'])
df['rating'] = df['rating'].astype(int)
df = df[['app', 'review_text', 'clean_text', 'rating', 'date', 'helpful_votes', 'word_count']]

df.to_csv('cleaned_reviews.csv', index=False)
print(f"After cleaning: {len(df)}")
print(df['app'].value_counts())

# ============ FILTER FOR FRESHNESS ============
# Keyword pass to isolate freshness/quality complaints from general reviews
# (delivery speed, app bugs, refunds unrelated to product condition, etc).
# \b (word boundary) wrapping prevents false matches like "raw" inside
# "withdraw", or "fresh" inside "refreshing".

FRESHNESS_KEYWORDS = [
    'rotten', 'rotting', 'spoiled', 'spoilt', 'stale', 'smelly',
    'moldy', 'mold', 'fungus', 'worms', 'insect', 'maggot',
    'fresh', 'freshness', 'quality',
    'damaged', 'crushed', 'squashed', 'bruised', 'overripe', 'unripe',
    'old stock', 'expired', 'expiry', 'expiration',
    'vegetable', 'vegetables', 'veggies', 'fruit', 'fruits',
    'tomato', 'onion', 'potato', 'leafy', 'spinach', 'banana', 'apple',
    'packaging', 'leaking', 'leaked', 'torn',
    'wrong item', 'not as described', 'poor condition'
]
pattern = '|'.join([
    r'\b' + re.escape(k) + r'\b' if ' ' not in k else re.escape(k)
    for k in FRESHNESS_KEYWORDS
])
df['is_freshness_related'] = df['clean_text'].str.contains(pattern, case=False, regex=True)

freshness_df = df[df['is_freshness_related']].copy()
freshness_df.to_csv('freshness_reviews.csv', index=False)

print(f"\nFreshness-related reviews: {len(freshness_df)}")
print(freshness_df['app'].value_counts())
print(f"\nBy rating:")
print(freshness_df['rating'].value_counts().sort_index())
print("\nSaved cleaned_reviews.csv and freshness_reviews.csv")
