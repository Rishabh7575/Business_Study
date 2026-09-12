# Executive Commercial Insights Report: Unit Economics, RTO Mitigation & Customer Lifetime Value

**To:** Leadership Team & VP of Commercial Operations, Myntra  
**From:** Business Data Analyst  
**Date:** FY 2024–2025 Retrospective  
**Subject:** Commercial Health Audit, GMV Realization Leakage, and 90-Day Retention Action Plan  

---

## Executive Summary

An exhaustive analysis of **52,000+ transaction records** across 12,000 active customer accounts reveals that while **Gross Booked GMV reached ₹12.4 Cr**, only **₹8.1 Cr (65.3%) was successfully realized** as net delivered revenue. The remaining ₹4.3 Cr is lost to pre-dispatch cancellations (6.2%), Return-to-Origin (RTO, 10.4%), and customer returns (18.1%).

By tackling Cash-on-Delivery (COD) logistics friction, sizing uncertainty in high-return categories, and serial return behavior, Myntra can unlock an estimated **₹1.65 Cr in annual recovered GMV** and **₹46 Lakhs in direct bottom-line margin expansion**.

```
+-----------------------------------------------------------------------------------------+
|                                    GMV WATERFALL OVERVIEW                               |
| Gross Booked GMV: ₹12.40 Cr                                                            |
|  ├── Less: Cancellations (Pre-dispatch)  : -₹0.77 Cr (6.2%)                             |
|  ├── Less: Return-to-Origin (RTO)         : -₹1.29 Cr (10.4% - Driven primarily by COD)  |
|  ├── Less: Customer Returns (Delivered)  : -₹2.24 Cr (18.1% - Driven by Sizing/Fit)     |
|  └── NET REALIZED GMV (NMV)              :  ₹8.10 Cr (65.3% Realization Rate)           |
+-----------------------------------------------------------------------------------------+
```

---

## 5 Key Strategic Findings

### 1. The COD RTO Tax: Cash-on-Delivery Destroys Logistics Economics
* **The Data**: Orders placed via **COD experience a 21.8% RTO rate**, compared to just **4.5% for UPI** and **4.2% for Credit Cards**.
* **Financial Impact**: COD accounts for 32.8% of total orders but generates **68.4% of all RTO occurrences**. Every RTO incurs forward and reverse freight fees with zero revenue offset.
* **Geographic Concentration**: Tier 3 cities display the highest COD dependency (60% COD mix), resulting in an average delivery failure rate of 24.2%.

### 2. Sizing Friction Accounts for 42% of Customer Returns
* **The Data**: Among delivered orders that customers returned, **42.1% cited "Size / Fit Issue"** as the primary reason, followed by "Quality Not as Expected" (22.3%).
* **Category Vulnerability**:
  * **Footwear**: Highest combined friction (19.8% customer return rate, 9.8% RTO).
  * **Women Ethnic Wear**: High sizing variability across unstandardized brand cuts.
  * In contrast, **Beauty & Grooming** and **Accessories** demonstrated superior unit economics with return rates under 9.2%.

### 3. The "Serial Returner" Segment Erodes Category Profits
* **The Data**: Behavioral RFM segmentation identified an active cluster of **706 customers (5.9% of user base)** classified as *Serial Returners* (customers with $\ge$ 3 orders and a return rate exceeding 40%).
* **Commercial Implication**: This group averages a **53.4% return rate**. After factoring reverse logistics and refurbishment costs, their net commercial contribution to Myntra is negative.

### 4. EORS / Mega-Sale Realization Drop
* **The Data**: During flagship sale events (EORS Summer in June, EORS Winter in December, and Festive Big Fashion Festival in October), order volumes surge **1.8x to 1.9x** compared to normal business-as-usual (BAU) months.
* **The Trade-Off**: Discount depth widens from an average of 24% in BAU to **48% in EORS**, while Net Realization Rate drops from 68.2% to **62.1%** due to increased impulse purchases that get cancelled or returned.

### 5. High-Value Cohort Dynamics & Cross-Category LTV
* **The Data**: Cohort retention analysis reveals that after the initial 30-day drop-off, customer cohorts experience predictable re-activation surges during festive and EORS sale months (Months 6 and 10).
* **Cross-Category Multiplier**: Customers whose initial purchase was in Apparel but subsequently purchased in **Footwear or Beauty & Grooming** displayed a **2.3x higher 12-month Customer Lifetime Value (CLV)** than single-category shoppers.

---

## 90-Day Tactical Action Plan

| Phase | Milestone | Expected Impact |
| :--- | :--- | :--- |
| **Day 1–30** | **Prepaid Conversion Incentives**: Introduce instant ₹50 discount / UPI scratchcard incentives on COD orders during checkout. | Reduce COD order share by 8–10%, lowering RTO by ~₹35 Lakhs. |
| **Day 31–60** | **Size & Fit Recommendation Widget**: Deploy fit-prediction prompts based on past purchase history for Footwear and Ethnic Wear. | Reduce sizing-related returns by 12–15%, preserving ~₹30 Lakhs in GMV. |
| **Day 61–90** | **Serial Returner Policy Restructuring**: Temporarily disable COD privileges and require nominal shipping deposits for accounts with >50% return history. | Eliminate negative-margin logistics burn without impacting genuine shoppers. |
| **Ongoing** | **Cross-Category Nudge Campaigns**: Trigger automated category cross-sell discounts (e.g. Ethnic wear buyers receiving a 15% Beauty voucher 14 days post-delivery). | Lift 90-day repeat purchase retention by 3.5 percentage points. |
