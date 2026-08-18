# 01_scrape.py
# Scrapes Play Store reviews for Blinkit, Zepto, and Swiggy Instamart.
# Run in Google Colab. Mounts Google Drive first so output persists
# across sessions (Colab's local disk is wiped on disconnect).

# ---- Install (run once, in its own cell, before this script) ----
# !pip install google-play-scraper pandas

from google.colab import drive
drive.mount('/content/drive')

import os
PROJECT_DIR = '/content/drive/MyDrive/freshness-trust'
os.makedirs(PROJECT_DIR, exist_ok=True)
os.chdir(PROJECT_DIR)
print(f"Working directory: {PROJECT_DIR}")

from google_play_scraper import reviews, Sort
import pandas as pd
import time

# Verified correct Play Store package IDs for each app's customer-facing app.
# Note: Instamart's customer app is a separate package from Swiggy's
# delivery-partner app (in.swiggy.deliveryapp) — verify before scraping any
# new app by sampling a few reviews and confirming they're customer reviews,
# not gig-worker/rider reviews.
APPS = {
    "blinkit": "com.grofers.customerapp",
    "zepto": "com.zeptoconsumerapp",
    "instamart": "in.swiggy.android.instamart"
}

def scrape_app_reviews(app_name, package_id, target_count=20000, batch_size=200):
    print(f"\nScraping {app_name} ({package_id})...")
    all_reviews = []
    continuation_token = None
    while len(all_reviews) < target_count:
        result, continuation_token = reviews(
            package_id, lang='en', country='in', sort=Sort.NEWEST,
            count=batch_size, continuation_token=continuation_token
        )
        if not result:
            print(f"  No more reviews available. Stopped at {len(all_reviews)}.")
            break
        all_reviews.extend(result)
        print(f"  Collected: {len(all_reviews)}")
        if continuation_token is None:
            break
        time.sleep(1)  # be polite to the server, avoid rate limits
    df = pd.DataFrame(all_reviews)
    df['app'] = app_name
    return df

all_dfs = []
for app_name, package_id in APPS.items():
    try:
        df = scrape_app_reviews(app_name, package_id, target_count=20000)
        all_dfs.append(df)
    except Exception as e:
        print(f"Failed on {app_name}: {e}")

final_df = pd.concat(all_dfs, ignore_index=True)
final_df = final_df[['app', 'userName', 'content', 'score', 'at', 'thumbsUpCount']]
final_df.columns = ['app', 'user', 'review_text', 'rating', 'date', 'helpful_votes']

print(f"\nTotal reviews collected: {len(final_df)}")
print(final_df['app'].value_counts())

final_df.to_csv('raw_reviews.csv', index=False)
print("\nSaved to raw_reviews.csv in Google Drive (freshness-trust/).")
