# quick-commerce-freshness-trust
NLP analysis of 60K quick-commerce reviews reveals a 4x freshness-complaint gap — plus the product (PRD + dashboard) designed to fix it.

**PM case study:** Why is Zepto's freshness-complaint rate 4x higher than Blinkit and Instamart — and what should the product do about it?

Analyzed 60,000 Play Store reviews across Zepto, Blinkit, and Swiggy Instamart using NLP topic modeling (NMF) to isolate freshness/quality complaints from generic feedback. Found that Zepto's freshness-complaint rate (8.3%) is ~4x competitors and grew ~50% over 4 months — concentrated specifically in produce/perishable spoilage, not fulfillment errors, pointing to a sourcing/cold-chain root cause rather than a logistics one. Designed a Dark-Store Quality Score system (PRD + dashboard mockup) as the product response.

**Full write-up:** [link to your portfolio case study]

---

## What's in this repo

```
├── notebooks/
│   ├── 01_scrape_reviews.py         # Play Store scraping (google-play-scraper)
│   ├── 02_clean_filter.py           # Cleaning + freshness keyword filtering
│   ├── 03_nmf_topic_model.py        # TF-IDF + NMF topic modeling on negative reviews
│   └── 04_root_cause_analysis.py    # Theme-by-app breakdown, time trend, root-cause checks
├── PRD.md                           # Dark-Store Quality Score — full product requirements doc
├── case_study.md                    # Full narrative write-up
└── README.md
```

## Approach

1. **Scrape** — 20,000 reviews each from Blinkit, Zepto, and Swiggy Instamart via Play Store (no API key required)
2. **Clean** — dedup, filter junk/short reviews, normalize text
3. **Filter** — keyword pass to isolate freshness/quality-related reviews (~3,400 of ~21,000 cleaned reviews)
4. **Topic model** — NMF on the negative (1–2★) subset to find substantive complaint themes (produce spoilage, dairy spoilage, expired goods, wrong items, damaged-in-transit) rather than generic sentiment
5. **Root-cause** — cross-app theme comparison, month-over-month trend, and engagement (helpful-vote) checks to validate the Zepto finding
6. **Solution design** — PRD for an internal ops tool (Dark-Store Quality Score) targeting the diagnosed root cause

## Key finding

| App | Freshness complaint rate (of all reviews) |
|---|---|
| Zepto | 8.3% |
| Instamart | 2.0% |
| Blinkit | 1.8% |

Zepto's rate climbed from 12.4% (May) to 18.9% (August) over the observation window — a ~50% relative increase — concentrated in produce/perishable spoilage rather than order-fulfillment errors.

## Limitations

- Freshness filtering used a keyword-based first pass; some relevant reviews may use language outside the keyword list
- Blinkit's 20,000 reviews were concentrated in a single month due to higher review volume, so a comparable multi-month trend isn't available for Blinkit the way it is for Zepto/Instamart
- Root cause (sourcing vs. dark-store turnover vs. cold-chain) is inferred from complaint patterns, not confirmed against internal operational data
- Business impact figures in the PRD are directional estimates, not measured outcomes

## Stack

Python (pandas, scikit-learn), `google-play-scraper`, NMF topic modeling, Figma (dashboard mockup)
