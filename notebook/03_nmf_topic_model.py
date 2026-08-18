# 03_nmf_topic_model.py
# TF-IDF + NMF topic modeling on negative freshness-related reviews to find
# substantive complaint themes (produce spoilage, dairy spoilage, expired
# goods, etc) rather than generic sentiment ("good quality" / "bad quality").
# Run after 02_clean_filter.py in the same session.

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.decomposition import NMF

df = pd.read_csv('freshness_reviews.csv')

# Restrict to negative reviews (1-2 star) — this is where the actual
# freshness PROBLEMS live. 5-star "good quality" reviews don't help
# identify what's broken.
neg_df = df[df['rating'] <= 2].copy()
print(f"Negative freshness reviews (1-2 star): {len(neg_df)}")
print(neg_df['app'].value_counts())

# Sentiment/generic words are added to the stopword list so NMF clusters on
# WHAT went wrong (rotten, expired, packaging) instead of restating the
# star rating in words (good/bad/quality/best/worst).
CUSTOM_STOPWORDS = [
    'good', 'bad', 'quality', 'best', 'worst', 'poor', 'nice', 'pathetic',
    'great', 'excellent', 'terrible', 'awful', 'horrible', 'worse', 'better',
    'app', 'zepto', 'blinkit', 'instamart', 'swiggy',
    'order', 'ordered', 'orders', 'ordering',
    'delivery', 'delivered', 'deliver',
    'service', 'experience', 'time', 'today', 'just', 'don', 'didn',
    'got', 'get', 'getting', 'received', 'receive'
]
all_stopwords = list(ENGLISH_STOP_WORDS) + CUSTOM_STOPWORDS

vectorizer = TfidfVectorizer(
    stop_words=all_stopwords,
    max_features=800,
    ngram_range=(1, 2),   # capture single words AND two-word phrases
    min_df=4              # word/phrase must appear in at least 4 reviews
)
tfidf_matrix = vectorizer.fit_transform(neg_df['clean_text'])
feature_names = vectorizer.get_feature_names_out()
print(f"\nTF-IDF matrix shape: {tfidf_matrix.shape}  (reviews x vocabulary)")

N_TOPICS = 8
nmf_model = NMF(n_components=N_TOPICS, random_state=42, max_iter=500)
nmf_topics = nmf_model.fit_transform(tfidf_matrix)
nmf_components = nmf_model.components_

print("\n" + "="*70)
print("TOPICS FOUND")
print("="*70)
for topic_idx, topic in enumerate(nmf_components):
    top_word_indices = topic.argsort()[-12:][::-1]
    top_words = [feature_names[i] for i in top_word_indices]
    print(f"\nTopic {topic_idx}: {', '.join(top_words)}")

neg_df['dominant_topic'] = nmf_topics.argmax(axis=1)

print("\n" + "="*70)
print("REVIEW COUNT PER TOPIC")
print("="*70)
print(neg_df['dominant_topic'].value_counts().sort_index())

# Manual topic naming based on reading top words + sample reviews per topic.
# Some NMF topics represent the same real-world theme (e.g. two variants of
# "expired products") and were merged during manual review.
TOPIC_NAMES = {
    0: 'Support/Complaint Friction',
    1: 'Expired Packaged Goods',
    2: 'Damaged + Refund Friction',
    3: 'Wrong/Missing/Rotten Items',
    4: 'Produce Spoilage',
    5: 'Expired/Damaged Products (general)',
    6: 'Wrong Item + Refund',
    7: 'Dairy/Perishable Spoilage'
}
neg_df['theme'] = neg_df['dominant_topic'].map(TOPIC_NAMES)

neg_df.to_csv('negative_freshness_reviews_topics.csv', index=False)
print("\nSaved negative_freshness_reviews_topics.csv")
