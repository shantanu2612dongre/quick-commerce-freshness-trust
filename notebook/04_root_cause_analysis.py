# 04_root_cause_analysis.py
# Investigates WHY Zepto's freshness complaint rate is ~4x higher than
# competitors: which themes drive it, whether it's a recent trend, and
# whether other users engage with (upvote) these complaints.
# Run after 03_nmf_topic_model.py in the same session.

import pandas as pd

neg_topics_df = pd.read_csv('negative_freshness_reviews_topics.csv')
all_cleaned_df = pd.read_csv('cleaned_reviews.csv')

# ---- A) Theme distribution by app — where does each app over/under-index? ----
print("="*70)
print("A) THEME DISTRIBUTION BY APP (% within that app's complaints)")
print("="*70)
theme_by_app = pd.crosstab(neg_topics_df['app'], neg_topics_df['theme'], normalize='index') * 100
print(theme_by_app.round(1))
print("\nRaw counts:")
print(pd.crosstab(neg_topics_df['app'], neg_topics_df['theme']))

# ---- B) Time trend — is this recent or long-standing? ----
print("\n" + "="*70)
print("B) TIME TREND — freshness complaint rate by month, per app")
print("="*70)
all_cleaned_df['date'] = pd.to_datetime(all_cleaned_df['date'])
all_cleaned_df['month'] = all_cleaned_df['date'].dt.to_period('M')
neg_topics_df['date'] = pd.to_datetime(neg_topics_df['date'])
neg_topics_df['month'] = neg_topics_df['date'].dt.to_period('M')

total_by_month = all_cleaned_df.groupby(['app', 'month']).size().reset_index(name='total_reviews')
freshness_by_month = neg_topics_df.groupby(['app', 'month']).size().reset_index(name='freshness_complaints')
trend = total_by_month.merge(freshness_by_month, on=['app', 'month'], how='left')
trend['freshness_complaints'] = trend['freshness_complaints'].fillna(0)
trend['complaint_rate_pct'] = (trend['freshness_complaints'] / trend['total_reviews'] * 100).round(2)

# Only show months with a reasonable sample size to avoid noisy tiny-month spikes
trend_clean = trend[trend['total_reviews'] >= 20].sort_values(['app', 'month'])
print(trend_clean.to_string(index=False))

# ---- C) Are these complaints ones other users agree with? ----
print("\n" + "="*70)
print("C) AVG HELPFUL VOTES ON FRESHNESS COMPLAINTS, BY APP")
print("="*70)
print(neg_topics_df.groupby('app')['helpful_votes'].agg(['mean', 'median', 'max']).round(2))

# ---- Recap: overall complaint rate per app ----
print("\n" + "="*70)
print("RECAP: freshness complaint rate per app (of 20,000 scraped each)")
print("="*70)
for app in ['zepto', 'blinkit', 'instamart']:
    count = len(neg_topics_df[neg_topics_df['app'] == app])
    print(f"{app}: {count}/20000 = {count/20000*100:.2f}%")

neg_topics_df.to_csv('freshness_reviews_themed_final.csv', index=False)
print("\nSaved freshness_reviews_themed_final.csv")
