# Myntra Business Data Analyst (BDA) Interview Preparation Guide

This cheat sheet covers the exact behavioral, business case, Root Cause Analysis (RCA), and technical questions you will be asked during interviews at **Myntra, Flipkart, Amazon, and top retail/tech companies**.

---

## 1. The 2-Minute Project Elevator Pitch ("Walk Me Through This Project")

> **Interview Answer Framework:**  
> *"In e-commerce, gross revenue is often a vanity metric—especially in Indian fashion where return rates and COD delivery failures can easily destroy unit economics. I built an end-to-end commercial analytics platform to diagnose where revenue leaks between checkout and customer retention.*  
> 
> *Working with 52,000+ fashion transactions across 12,000 customers, I first designed a normalized Star Schema in SQLite and built a SQL GMV-to-NMV waterfall. This revealed that while Booked GMV reached ₹12.4 Cr, only 65.3% was realized as net delivered revenue. The biggest driver was COD Return-to-Origin (RTO), which ran at 21.8% compared to just 4.5% for prepaid UPI orders.*  
> 
> *To solve this from both customer and category lenses, I wrote SQL window functions using `NTILE(5)` to segment users into 8 RFM personas—including a distinct 'Serial Returner' segment—and tracked 12-month customer survival through cohort retention heatmaps. Finally, I translated these findings into an executive Power BI data model with 25+ DAX measures and an interactive Streamlit simulation tool that showed leadership how a 4% reduction in COD RTO coupled with size-recommendation interventions would expand annual net profit by ₹46 Lakhs."*

---

## 2. Root Cause Analysis (RCA) Case Study

### Question: *"Suppose Myntra's return rate jumps from 18% to 24% in a single week. How would you diagnose the root cause?"*

**Step-by-Step Diagnostic Framework:**
1. **Verify Data Integrity & Scope**:
   * Check whether the spike is platform-wide or concentrated in specific dates, regions, or app versions.
   * Rule out telemetry / logging anomalies (e.g., duplicate webhook events).
2. **Deconstruct by Channel & Payment Mode**:
   * Did the COD mix increase? (COD always has higher return/refusal rates).
   * Check if there was a promotional campaign attracting low-intent, coupon-hunting traffic.
3. **Drill Down by Category & Brand**:
   * Isolate return rates by category: Did Footwear or Ethnic Wear return rates surge?
   * Inspect SKU-level issues: Did a top-selling brand update its sizing chart or switch vendors, causing systematic fit errors?
4. **Analyze Return Reasons**:
   * Query the `fact_returns` table: Did "Size / Fit Issue" spike, or did "Defective / Damaged Item" or "Late Delivery" increase? (Late deliveries often cause doorstep refusals during festive courier congestion).
5. **Formulate Actionable Mitigation**:
   * If sizing: Add a temporary size warning or fit advisory banner on the offending SKUs.
   * If logistics delays: Re-route shipments through alternative courier partners.

---

## 3. Commercial & Business Metrics Defense

### Q: *"Why is Net Realized GMV (NMV) more important than Gross GMV?"*
* **Answer**: *"Gross GMV represents order intent at the checkout page. In fashion retail, 20% to 35% of booked value disappears through pre-dispatch cancellations, courier RTOs, and customer returns. Basing marketing or inventory decisions on Gross GMV creates false optimism, overstates margins, and leads to working capital crunches. NMV reflects true retained cash flow."*

### Q: *"What is the difference between RTO and Customer Return?"*
* **Answer**:
  * **RTO (Return to Origin)**: The shipment was dispatched, but the customer refused delivery at the doorstep or the courier failed to reach them. The customer never unboxed the product. It is 4–5x higher in COD orders.
  * **Customer Return**: The customer received, unboxed, and tried the product, but requested a reverse pickup within the return window (typically due to sizing, quality, or defect).

---

## 4. Technical SQL Deep-Dive Questions

### Q: *"How did you assign RFM scores in SQL without hardcoding arbitrary ranges?"*
* **Answer**:
  * *"Instead of hardcoding arbitrary thresholds, I used the SQL window function `NTILE(5) OVER (ORDER BY recency_days DESC)` for Recency, and `NTILE(5)` ordered ascending for Frequency and Monetary value.*
  * *This dynamically partitions customers into quintiles (1 to 5), ensuring equal 20% bucket distribution across the active customer base, making the segmentation mathematically robust and adaptive as the business grows."*

### Q: *"How does your SQL query compute the month offset in the Cohort Retention Matrix?"*
* **Answer**:
  * *"First, a CTE identifies each customer's `MIN(order_date)` as their cohort month. Then, in the subsequent activity CTE, I join orders back to their cohort and compute the month offset using the formula:*
    ```sql
    (strftime('%Y', order_date) - strftime('%Y', first_order_date)) * 12 +
    (strftime('%m', order_date) - strftime('%m', first_order_date))
    ```
  * *This maps the purchase month offset (0 for acquisition month, 1 for next month, etc.) regardless of whether the order crosses calendar years."*

---

## 5. Power BI & DAX Technical Questions

### Q: *"Why did you use a Star Schema instead of a single flattened table?"*
* **Answer**:
  * *"A Star Schema separates high-cardinality transactional events (`fact_orders`, `fact_order_items`) from low-cardinality business entities (`dim_customers`, `dim_products`, `dim_date`).*
  * *This optimizes Power BI's VertiPaq engine compression (Run-Length Encoding and Dictionary Encoding), prevents double-counting errors across line-items, and ensures single-direction `1:*` filtering with zero ambiguity in DAX time-intelligence calculations."*

### Q: *"Explain how your DAX YoY measure works."*
* **Answer**:
  * *"The `[Realized GMV YoY Growth %]` measure utilizes `CALCULATE([Net Realized GMV], SAMEPERIODLASTYEAR(dim_date[date_key]))`.*
  * *The `SAMEPERIODLASTYEAR` function modifies the current date filter context, shifting it back exactly 365 days along the designated date dimension. We then wrap the difference in a safe `DIVIDE()` statement to handle zero-denominator edge cases without throwing calculation errors."*
