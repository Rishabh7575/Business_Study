# 🛍️ Myntra Commercial Sales, Logistics & Customer Analytics Suite
### Enterprise-Grade Business Intelligence & Data Analytics Portfolio Project

[![SQL](https://img.shields.io/badge/SQL-Advanced%20Analytics-blue?logo=sqlite)](sql/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Star%20Schema%20%26%20DAX-yellow?logo=powerbi)](power_bi/)
[![Excel](https://img.shields.io/badge/Microsoft%20Excel-Financial%20Modeling-green?logo=microsoftexcel)](excel/)
[![Python](https://img.shields.io/badge/Python-Streamlit%20%26%20Plotly-red?logo=python)](dashboard/)
[![Domain](https://img.shields.io/badge/Industry-Fashion%20E--Commerce-purple)]()

---

## 📌 Executive Overview

In fashion e-commerce, gross revenue is often a vanity metric. Because fashion apparel and footwear suffer high return rates (20%–35%) and Cash-on-Delivery (COD) orders frequently fail at the doorstep, real commercial profitability hinges on **Net Realized GMV (NMV)** and reverse logistics control.

This project delivers an end-to-end commercial analytics platform auditing **52,000+ fashion transactions** across 12,000 customers for **Myntra** (and modern retail platforms). It models unit economics, diagnoses Return-to-Origin (RTO) leakage, executes dynamic RFM customer segmentation, and builds 12-month cohort retention matrices.

```
+-----------------------------------------------------------------------------------------+
|                                    GMV REALIZATION WATERFALL                            |
| Gross Booked GMV: ₹12.40 Cr                                                            |
|  ├── Less: Cancellations (Pre-dispatch)  : -₹0.77 Cr (6.2%)                             |
|  ├── Less: Return-to-Origin (RTO)         : -₹1.29 Cr (10.4% - Driven primarily by COD)  |
|  ├── Less: Customer Returns (Delivered)  : -₹2.24 Cr (18.1% - Driven by Sizing/Fit)     |
|  └── NET REALIZED GMV (NMV)              :  ₹8.10 Cr (65.3% Realization Rate)           |
+-----------------------------------------------------------------------------------------+
```

---

## 🎯 Key Business Findings & Quantified Impact

1. **COD vs. Prepaid RTO Disparity**: COD orders suffer a **21.8% RTO rate** compared to just **4.5% for UPI** and 4.2% for Credit Cards. COD drives 68.4% of all logistics failure volume.
2. **Sizing Uncertainty Friction**: **42.1% of customer returns** cite "Size / Fit Issue" as the root cause, heavily concentrated in Footwear and Women's Ethnic Wear.
3. **The "Serial Returner" Segment**: Identified an active cluster of **706 customers with a 53.4% return rate**, generating net negative contribution margin after reverse logistics.
4. **EORS Surge vs. Realization**: Mega-sales (EORS / BFF) lift transaction volume by 1.8x, but net realization drops by 4.2% due to impulse buying and return friction.
5. **Cross-Category Multiplier**: Customers who expand from Apparel into Footwear or Beauty exhibit a **2.3x higher 12-month Customer Lifetime Value (CLV)**.

---

## 🏗️ Technical Architecture & Data Model

The data warehouse follows a **Kimball Star Schema** implemented in SQLite with indexed primary/foreign key relationships:

```
       +-----------------------+
       |     dim_customers     |
       |-----------------------|
       | * cust_id (PK)        |
       |   name, gender, tier  |
       |   city, state         |
       +-----------+-----------+
                   |
                   | 1:N
                   v
+------------------+------------------+         +-----------------------+
|                 fact_orders         |  1:N    |     dim_products      |
|-------------------------------------|<--------|-----------------------|
| * order_id (PK)                     |         | * prod_id (PK)        |
|   cust_id (FK), order_date (FK)     |         |   prod_name, brand    |
|   order_status, payment_mode        |         |   category, mrp       |
|   gross_gmv, net_gmv, order_cogs    |         +-----------------------+
+------------------+------------------+
                   ^
                   | 1:N
       +-----------+-----------+
       |       dim_date        |
       |-----------------------|
       | * date_key (PK)       |
       |   year, month, sale   |
       +-----------------------+
```

---

## 📂 Repository Structure

```
├── data/
│   ├── raw/                         # 52,000+ orders, customers, items, returns CSVs
│   └── ecommerce_warehouse.db       # Star-Schema SQLite database with indexes
├── sql/
│   ├── 01_schema_ddl.sql            # Star schema DDL & index definitions
│   ├── 02_gmv_waterfall_kpis.sql    # GMV to Net Realized GMV waterfall & payment RTO
│   ├── 03_rfm_customer_personas.sql # NTILE(5) RFM scoring & persona classification
│   ├── 04_cohort_retention_matrix.sql # 12-month cohort retention & cross-category repeat
│   ├── 05_category_returns_deepdive.sql # Sizing friction & category return diagnostics
│   └── 06_bi_analytical_views.sql   # Reusable analytical views for BI tools
├── dashboard/
│   ├── app.py                       # Interactive Streamlit Executive Web Application
│   └── style.css                    # Corporate executive styling & Myntra accents
├── excel/
│   ├── generate_excel_model.py      # Automated openpyxl generation pipeline
│   └── Myntra_Commercial_Executive_Model.xlsx # Multi-tab formatted financial model
├── power_bi/
│   ├── powerbi_data_model_guide.md  # Star-Schema architecture & relationship setup
│   └── dax_measures_library.md      # 25+ Production DAX Measures with Time Intelligence
├── reports/
│   ├── EXECUTIVE_INSIGHTS_REPORT.md # C-Suite strategic memo & 90-day action plan
│   ├── RESUME_BULLET_POINTS.md      # Quantified STAR-format resume bullet options
│   └── MYNTRA_BDA_INTERVIEW_PREP.md # Interview cheat sheet (RCA, metrics, SQL/DAX)
├── scripts/
│   ├── generate_data.py             # 52k synthetic e-commerce transaction generator
│   └── build_warehouse.py           # Database ingestion & indexing pipeline
├── requirements.txt                 # Project dependencies
└── README.md                        # Documentation & project showcase
```

---

## 🚀 Quickstart & How to Run

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Rishabh7575/Business_Study.git
cd Business_Study
pip install -r requirements.txt
```

### 2. Launch Interactive Executive Dashboard
```bash
streamlit run dashboard/app.py
```
*The interactive dashboard will launch at `http://localhost:8501` featuring executive KPI cards, Plotly waterfall charts, RFM customer explorers, cohort retention heatmaps, and a What-If scenario modeler.*

### 3. Generate Formatted Excel Financial Model
```bash
python excel/generate_excel_model.py
```
*Outputs `excel/Myntra_Commercial_Executive_Model.xlsx` styled with corporate palette, KPI summary cards, and dynamic formulas.*

### 4. Execute SQL Queries
You can run any script in `sql/` directly against `data/ecommerce_warehouse.db` using any SQLite client (or Python `sqlite3`).

---

## 💼 Skills & Competencies Demonstrated

* **Business Commercial Acumen**: GMV vs. NMV, Net Realization Rate %, RTO mitigation, Unit Economics, Sizing Return Analysis.
* **Database & SQL Engineering**: Star Schema dimensional modeling, CTEs, Window Functions (`NTILE`, `OVER PARTITION BY`), Self-Joins, Materialized Views.
* **BI & Data Modeling**: Power BI VertiPaq optimization, 25+ DAX measures (Time-Intelligence, YoY%, MoM%, Rolling 90D).
* **Financial & Spreadsheet Modeling**: Automated Excel workbook engineering (`openpyxl`), structured KPI cards, dynamic lookup structures.
* **Executive Storytelling**: Root Cause Analysis (RCA), scenario sensitivity simulation, C-suite executive briefing.
