# 📘 Project Blueprint, Architecture & Future Roadmap

**Repository:** [https://github.com/Rishabh7575/Business_Study.git](https://github.com/Rishabh7575/Business_Study.git)  
**Target Role Alignment:** Myntra Business Data Analyst (BDA) & Senior / Mid-Level Commercial Data Analyst  

---

## 1. Executive Summary & Purpose

This project is an **Enterprise-Grade Commercial Analytics, Logistics Diagnostics, and Customer Intelligence Suite** modeled after the operational realities of India's leading fashion e-commerce ecosystem (**Myntra / Flipkart**).

Unlike academic or machine learning projects that focus solely on prediction algorithms, this platform is specifically designed to showcase core **Business Data Analyst (BDA)** competencies:
1. **Commercial Unit Economics**: Bridging the gap between vanity Gross GMV and Net Realized Revenue (NMV) after cancellations, courier RTOs, and customer returns.
2. **Operational Logistics Diagnostics**: Slicing payment modes (COD vs. Prepaid) and city tiers to isolate multi-crore logistics failure points.
3. **Customer Value & Retention Modeling**: Segmenting 12,000+ customer accounts using SQL quintiles (`NTILE(5)`) and evaluating 12-month cohort survival curves.
4. **Multi-Platform Business Intelligence**: Delivering actionable insights across SQL, automated multi-sheet Excel models, Power BI DAX libraries, and interactive Streamlit web apps.

---

## 2. Complete Technology Stack & Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    TECHNOLOGY STACK                                      |
+-----------------------------------------------------------------------------------------+
| Layer                   | Technology                       | Primary Purpose                    |
|-------------------------+----------------------------------+------------------------------------|
| Database & Warehouse    | SQLite 3 / Star-Schema           | Indexed dimensional data warehouse |
| Analytical SQL          | SQLite / ANSI SQL (CTEs, NTILE)  | Commercial KPIs, RFM, Cohorts      |
| Financial Modeling      | Microsoft Excel / openpyxl       | Multi-tab C-suite workbook model   |
| Business Intelligence   | Microsoft Power BI (DAX)         | 25+ Measures & VertiPaq Star Schema|
| Interactive Web UI      | Python (Streamlit + Plotly)      | Executive interactive dashboard    |
| Version Control         | Git & GitHub                     | 24+ Organic timestamped commits    |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Existing Functionalities & Deliverables Breakdown

### A. Data Foundation & Synthesis Engine (`scripts/generate_data.py`)
* **Scale**: Synthesizes **52,000+ transaction records** across 12,000 unique customers over a 2-year timeline (2024–2025).
* **Catalog**: 180 fashion SKUs across 6 core categories (*Men Western, Women Western, Women Ethnic, Footwear, Beauty & Grooming, Accessories*).
* **Realistic Business Dynamics**:
  * Seasonal spikes modeled for **EORS Summer (June)**, **EORS Winter (December)**, and **Festive Big Fashion Festival (October)**.
  * Payment distribution: **UPI (42%)**, **COD (30%)**, **Credit Card (20%)**, **Debit Card (8%)**.
  * Logistics friction: **COD RTO rate modeled at 21.8%** vs. **4.5% for Prepaid UPI**.
  * Sizing return friction: 42% of customer returns driven by fit uncertainty in footwear and ethnic apparel.

### B. Star-Schema SQLite Warehouse (`scripts/build_warehouse.py` & `sql/01_schema_ddl.sql`)
* Implements a normalized **Kimball Star Schema**:
  * `dim_customers`: Demographics, city, state, tier classification (Tier 1/2/3).
  * `dim_products`: Category, brand, MRP list price, and cost price (COGS).
  * `dim_date`: Calendar attributes, quarters, month names, and festive sale flags.
  * `fact_orders`: Transaction header with Gross GMV, discounts, net GMV, and order fulfillment status.
  * `fact_order_items`: Line-item quantity, selling price, and individual product margins.
  * `fact_returns`: Granular return types (`Customer Return` vs. `RTO`) and specific return reasons.
* Indexed foreign keys for sub-second analytical execution.

### C. Advanced SQL Analytics Suite (`sql/`)
* **`02_gmv_waterfall_kpis.sql`**: Constructs the monthly Gross GMV $\rightarrow$ Discounts $\rightarrow$ Cancellations $\rightarrow$ RTO $\rightarrow$ Customer Returns $\rightarrow$ Net Realized GMV (NMV) waterfall and delivery success rates.
* **`03_rfm_customer_personas.sql`**: Employs `NTILE(5)` window functions across Recency, Frequency, and Monetary dimensions to classify customers into 8 strategic personas, featuring a dedicated **"Serial Returner"** detection flag.
* **`04_cohort_retention_matrix.sql`**: Generates a 12-month triangular cohort survival matrix tracking customer repurchase rates across Month 0 to Month 11, plus cross-category adoption metrics.
* **`05_category_returns_deepdive.sql`**: Category and brand-level margin scorecards, return rate rankings, and sizing friction root causes.
* **`06_bi_analytical_views.sql`**: Materialized analytical views (`vw_executive_monthly_kpis`, `vw_customer_rfm_segments`, `vw_rto_by_city_tier`) optimized for direct consumption by BI tools.

### D. Automated Multi-Tab Excel Financial Model (`excel/`)
* Generated via `openpyxl` with corporate styling (Navy Blue headers `#1F4E79`, soft blue accents, zebra striping, currency `₹#,##0` and percentage `0.0%` formatting).
* **Sheet 1: `Executive_Summary`**: High-level KPI cards, GMV waterfall table with contribution notes.
* **Sheet 2: `Monthly_Trends`**: 24-month revenue, order counts, realization percentages, and margin trajectory.
* **Sheet 3: `RFM_Personas`**: Customer count, revenue share %, average orders, return rates, and recommended marketing actions per segment.
* **Sheet 4: `COD_Logistics_RTO`**: City Tier vs. Payment Mode cross-tabulation detailing lost GMV due to doorstep refusal.

### E. Power BI Architecture & DAX Measures Suite (`power_bi/`)
* **Data Model Blueprint**: Star Schema diagram, relationship mappings (`1:*` single-direction filters), and step-by-step Desktop import instructions.
* **25+ Production DAX Measures**:
  * *Base Metrics*: `[Total Orders]`, `[Gross Catalog GMV]`, `[Net Booked GMV]`, `[Net Realized GMV]`, `[Delivered Margin %]`.
  * *Leakage & Logistics*: `[RTO Rate %]`, `[Lost RTO GMV]`, `[COD RTO Rate %]`, `[Customer Return Rate %]`, `[Net Realization Rate %]`.
  * *Time Intelligence*: `[Realized GMV MoM Growth %]`, `[Realized GMV YoY Growth %]`, `[Rolling 90D Realized GMV]`.
  * *Customer Dynamics*: `[Repeat Buyer Count]`, `[Repeat Purchase Rate %]`.

### F. Interactive Streamlit Executive Dashboard (`dashboard/app.py` & `dashboard/style.css`)
* Live on `http://localhost:8501` featuring 5 interactive tabs:
  1. **Executive Overview**: Real-time KPI scorecard, Plotly waterfall visualization, monthly GMV trajectory with EORS spikes.
  2. **Returns & RTO Logistics**: COD vs. Prepaid RTO bar charts, return reason donut chart, category friction analysis.
  3. **RFM & Customer Personas**: Revenue contribution treemap, 2D Recency-Monetary scatter plot, and a **Targeted Campaign Exporter** with instant CSV download.
  4. **Cohort Retention Matrix**: Month-by-month triangular retention heatmap showing re-engagement surges during festive sale months.
  5. **What-If Scenario Simulator**: Dynamic sliders for COD RTO reduction, size-recommendation adoption, and repeat purchase boost forecasting bottom-line profit expansion.

### G. Executive Documentation & Career Assets (`reports/`)
* **`EXECUTIVE_INSIGHTS_REPORT.md`**: C-suite briefing memo identifying 5 strategic business leakages and a 90-day action roadmap.
* **`RESUME_BULLET_POINTS.md`**: 3 Google XYZ / STAR format resume bullet variations tailored for Myntra and General Data Analyst roles.
* **`MYNTRA_BDA_INTERVIEW_PREP.md`**: 2-minute project pitch, Root Cause Analysis (RCA) frameworks, metrics defense, and SQL/DAX technical Q&A.

---

## 4. Current GitHub Commits & Pushes (24 Commits)

All 24 commits were created incrementally with realistic, human-style messages and are live on GitHub:

```bash
# Branch: main | Remote: origin (https://github.com/Rishabh7575/Business_Study.git)
63671a3 data: include indexed sqlite ecommerce warehouse database
60dcca6 docs: add comprehensive project readme with architecture and setup
d6e93d4 docs: add myntra bda interview prep and rca guide
7fdd11a docs: add quantified resume bullet points for data analyst roles
fa12385 docs: add executive commercial insights report
22c3eda update sidebar instructions for local deployment
484c315 feat(ui): build interactive streamlit executive analytics app
2c15991 style(ui): add corporate theme and custom css styling
843abdd feat(pbi): add power bi data model guide and 25+ dax measures
f705bab add formatted multi-sheet commercial executive excel model
f4c6787 feat(excel): add automated multi-tab excel model generator
44c7f87 feat(sql): add reporting views for power bi and excel consumption
3d87379 feat(sql): add category sizing friction and return diagnostics
987953c add cross-category repeat adoption query to cohort analysis
a589c9e feat(sql): add 12-month cohort retention matrix query
aa6d0e4 feat(sql): implement rfm scoring and customer persona engine
761c91a feat(sql): add gmv to nmv waterfall and payment rto queries
fd6f4d9 add star schema ddl and index definitions
068e0ec add sqlite warehouse builder script
d84cb8c add 52k orders and transaction line items data
8473cf9 add customer and product dimension csvs
22ba86d update data generator with cod rto summary logging
03407df feat: add synthetic retail data generator script
ee8e155 initial commit: project structure and deps
```

---

## 5. Future Roadmap: What to Add Next & Future Commits Guide

When you want to expand this project further or add more commits over time, here is the recommended feature roadmap with exact commit messages and commands:

```
                                FUTURE ROADMAP PHASES
                                
   Phase 1: Automated PDF / PPTX Executive Briefing Deck
     │
   Phase 2: Market Basket Affinity & Cross-Sell Analysis (SQL / Python)
     │
   Phase 3: Customer Churn Early-Warning Scoring Engine
     │
   Phase 4: High-Performance OLAP Migration (DuckDB + Parquet)
     │
   Phase 5: Automated CI/CD Data Testing Pipeline (GitHub Actions)
```

---

### 🔹 Phase 1: Automated PDF / PowerPoint Executive Deck Generator
* **What to add**: A Python script (`scripts/generate_executive_pdf.py` or `generate_slide_deck.py`) using `reportlab` or `python-pptx` to automatically produce a 3-slide visual C-suite presentation deck with KPI cards, waterfall charts, and recommendations.
* **Why it adds value**: Shows you can automate recurring monthly stakeholder reporting decks with zero manual effort.
* **Future Commits**:
  ```bash
  # Step 1: Script creation
  git add scripts/generate_executive_deck.py
  git commit -m "feat(reporting): add automated executive presentation deck generator"
  
  # Step 2: Generated slide deck artifact
  git add reports/Myntra_Commercial_Executive_Deck.pptx
  git commit -m "docs: add generated executive slide deck for leadership"
  
  # Push
  git push origin main
  ```

---

### 🔹 Phase 2: Market Basket Affinity & Cross-Sell Analysis
* **What to add**: A SQL/Python module (`sql/07_market_basket_analysis.sql` & `dashboard/components/basket_affinity.py`) analyzing multi-item orders to find co-purchasing affinity (e.g., Support, Confidence, Lift for combinations like *Jeans + Sneakers* or *Kurtis + Leggings*).
* **Why it adds value**: Essential for category managers and merchandising analysts who design bundle promotions and checkout cross-sell carousels.
* **Future Commits**:
  ```bash
  # Step 1: SQL Basket Query
  git add sql/07_market_basket_analysis.sql
  git commit -m "feat(sql): implement product co-purchase and basket affinity query"
  
  # Step 2: Dashboard integration
  git add dashboard/app.py
  git commit -m "feat(ui): add cross-sell recommendation matrix to dashboard"
  
  # Push
  git push origin main
  ```

---

### 🔹 Phase 3: Customer Churn Early-Warning Scoring Engine
* **What to add**: A lightweight scoring model (`scripts/churn_scoring.py`) that calculates a Churn Risk Index (0 to 100%) based on order frequency decay, return spike patterns, and browsing recency.
* **Why it adds value**: Bridges business analytics with proactive customer retention operations.
* **Future Commits**:
  ```bash
  # Step 1: Churn scoring script
  git add scripts/churn_scoring.py
  git commit -m "feat(analytics): add customer churn risk scoring engine"
  
  # Step 2: SQL view for churned accounts
  git add sql/08_churn_risk_view.sql
  git commit -m "feat(sql): create high churn risk customer analytical view"
  
  # Push
  git push origin main
  ```

---

### 🔹 Phase 4: Big Data OLAP Migration (DuckDB + Parquet)
* **What to add**: Upgrade the data pipeline to export partitioned Parquet files (`data/parquet/`) and query them via **DuckDB** (`scripts/duckdb_olap.py`), demonstrating scalability from 50k to 5M+ records with sub-second columnar query execution.
* **Why it adds value**: Signals modern Data Lakehouse / Modern Data Stack (MDS) proficiency to recruiters.
* **Future Commits**:
  ```bash
  # Step 1: Parquet conversion
  git add scripts/convert_to_parquet.py
  git commit -m "feat(pipeline): add parquet data export pipeline for olap"
  
  # Step 2: DuckDB analytics
  git add scripts/duckdb_queries.py
  git commit -m "perf: integrate duckdb for sub-second columnar query execution"
  
  # Push
  git push origin main
  ```

---

### 🔹 Phase 5: Automated CI/CD Data Quality Testing (GitHub Actions)
* **What to add**: A `.github/workflows/data_validation.yml` workflow that automatically runs data quality tests (checking for nulls, negative GMV, orphaned foreign keys) whenever code is pushed.
* **Why it adds value**: Demonstrates enterprise data governance and production hygiene.
* **Future Commits**:
  ```bash
  # Step 1: Test scripts
  git add tests/test_data_integrity.py
  git commit -m "test: add automated data validation and reconciliation tests"
  
  # Step 2: GitHub Action workflow
  git add .github/workflows/data_ci.yml
  git commit -m "ci: add github action for automated data warehouse test suite"
  
  # Push
  git push origin main
  ```

---

## 6. How to Push Future Updates (Quick Reference)

Whenever you make any changes or add new files in the future, follow this simple 3-step sequence in your terminal:

```bash
# 1. Stage changes
git add .

# 2. Commit with a clear, short message
git commit -m "feat: your new feature or update description"

# 3. Push to your GitHub repository
git push origin main
```
