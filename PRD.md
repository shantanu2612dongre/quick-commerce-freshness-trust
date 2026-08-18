# Product Requirements Document

## Dark-Store Freshness Quality Score

| | |
|---|---|
| **Product** | Quick-commerce grocery platform — Zepto (case study modeled on public review data) |
| **Author** | Shantanu Dongre |
| **Status** | Draft v1 |
| **Owner** | Product |

---

## 1. Problem Statement

Analysis of 60,000 Play Store reviews across Zepto, Blinkit, and Instamart (May–Aug 2026) found that Zepto's freshness/quality complaint rate is 4x higher than competitors (8.3% vs 1.8–2.0%), and has grown approximately 50% over 4 months (12.4% → 18.9%). Complaints are disproportionately concentrated in produce and perishable spoilage, not order-fulfillment errors — wrong or missing items are actually below competitor rates — indicating the root cause sits upstream in sourcing and dark-store inventory handling, not last-mile logistics.

Today, dark stores are treated as interchangeable fulfillment nodes. There is no mechanism that tracks spoilage or freshness complaint rates back to the specific dark store or vendor that sourced and packed the item, so underperforming nodes keep shipping the same categories at the same volume with no visibility or consequence.

## 2. Goal

Give the platform a way to detect, score, and act on dark-store and vendor-level freshness failures before they compound into a systemic quality problem — using data the platform already has (complaint text, return/refund data, order origin) rather than new infrastructure.

## 3. Success Metrics

| Metric | Current (est.) | Target (6 months post-launch) |
|---|---|---|
| Freshness complaint rate (produce/perishables) | 8.3% | ≤4% |
| Time to flag an underperforming dark store | Not tracked today | <7 days of sustained signal |
| % of produce complaints traced to a scored dark store | 0% (no attribution today) | 90%+ |
| Repeat freshness complaints from same dark store | Unknown | -50% within 60 days of flagging |

## 4. Solution Overview

A **Dark-Store Quality Score**: a rolling, category-specific spoilage and freshness score computed per dark store (and per vendor where produce is externally sourced), used to:

- Surface underperforming nodes to ops for intervention (audit, vendor swap, cold-chain fix)
- Automatically reduce sourcing weight and inventory allocation for chronically low-scoring nodes in the affected category
- Feed a lightweight early-warning signal to ops before a node's problem shows up as a customer-facing pattern

This is an internal ops and product tool, not a customer-facing feature — it fixes the supply side rather than compensating customers after the fact, which a customer-facing freshness-guarantee refund flow would do instead.

## 5. How It Works

**Inputs**

- Order-level data: which dark store fulfilled each order, which vendor supplied each SKU
- Return and refund reason codes, filtered to freshness/quality reasons
- Review or in-app complaint text, classified using the same NLP-based approach (NMF topic modeling) used in this analysis
- Category (produce, dairy, packaged goods) — spoilage tolerance and shelf life differ by category

**Score computation**

*Computed per dark store, per category, on a rolling 7- and 30-day window:*

```
Quality Score = 1 − (freshness-related complaints ÷ total orders fulfilled by that node, that category)
```

Normalized against category-specific peer average — produce naturally carries higher spoilage risk than packaged goods, so raw comparison across categories isn't fair.

**Action tiers**

- **Green** (within 1 std dev of category peer average): no action, monitored
- **Yellow** (1–2 std dev worse): flagged to regional ops lead, triggers manual audit within 7 days
- **Red** (2+ std dev worse, sustained 2+ weeks): automatic sourcing-weight reduction for that category at that node, escalated to category/vendor management for root-cause review

*Figure 1: Dark-store quality score dashboard — overview table with tier flags, and drill-down into a flagged store's complaint theme breakdown.*

![Dark-store quality score dashboard](./assets/dashboard.png)

## 6. User Stories

- *As a regional ops lead*, I want to see which dark stores in my region are trending Yellow or Red on freshness so I can prioritize audits instead of reacting to complaints one at a time.
- *As a category manager*, I want to see if a specific vendor's produce is driving spoilage across multiple dark stores, so I can address it at the vendor level instead of per-store.
- *As a platform*, I want inventory allocation to automatically deprioritize chronically underperforming nodes in a category, so customer exposure to bad produce drops without waiting for manual intervention.

## 7. Rollout Plan

- **Phase 1 (4 weeks):** Build scoring pipeline on historical data, validate against known problem stores
- **Phase 2 (4 weeks):** Ops-facing dashboard (Yellow/Red flagging), human-in-the-loop only — no automated action yet
- **Phase 3 (ongoing):** Enable automated sourcing-weight reduction for sustained Red-tier nodes; monitor for unintended effects such as reduced availability driving customers to competitors

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Score penalizes stores in genuinely hard categories (e.g. leafy greens spoil faster everywhere) | Score against category-specific peer baseline, not an absolute threshold |
| Automated sourcing cuts reduce availability and hurt revenue short-term | Automated action only after Phase 2 validates scoring accuracy; starts conservative (partial weight reduction, not full cutoff) |
| Complaint-text classification (NLP) misclassifies some reviews | Acceptable at aggregate/trend level for flagging; not used for single-order decisions |

## 9. Out of Scope (v1)

- Customer-facing freshness guarantee or refund automation (separate initiative)
- Predictive shelf-life flagging before shipment (a v2 extension once the scoring foundation exists)
- Cross-platform vendor scoring — this scores only the platform's own dark stores and vendors

## 10. Business Impact Estimate

*Estimated, not measured — for illustration of the business case.*

Even a conservative assumption that freshness complaints correlate with reduced reorder rate and support/refund cost suggests that halving the produce-spoilage complaint rate (8.3% → approximately 4%) could plausibly reduce refund costs and improve retention in the affected category.

Directionally: if freshness complaints represent a meaningful share of support and refund costs in the produce category, and this initiative reduces that by half, the cost savings plus retained order value would form the basis for a full ROI case. Precise sizing would require internal cost-per-refund and churn-elasticity data not available from public review data.
