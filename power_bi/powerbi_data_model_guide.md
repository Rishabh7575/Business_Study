# Power BI Star Schema Data Model & Implementation Guide

## 1. Overview & Architecture

This guide details the dimensional data model designed for the **Myntra Commercial & Customer Analytics Dashboard** in Power BI Desktop.

The architecture strictly adheres to **Kimball Dimensional Modeling** best practices using a **Star Schema** with a single centralized Fact table, surrounded by clean Dimension tables. This eliminates bidirectional cross-filtering pitfalls and ensures sub-second DAX calculation speed.

```
       +-----------------------+
       |     dim_customers     |
       |-----------------------|
       | * cust_id (PK)        |
       |   name                |
       |   gender              |
       |   tier (Tier 1/2/3)   |
       |   city, state         |
       +-----------+-----------+
                   |
                   | 1:N (Single)
                   v
+------------------+------------------+         +-----------------------+
|                 fact_orders         |  1:N    |     dim_products      |
|-------------------------------------|<--------|-----------------------|
| * order_id (PK)                     |         | * prod_id (PK)        |
|   cust_id (FK)                      |         |   prod_name           |
|   order_date (FK)                   |         |   category            |
|   order_status (Delivered/RTO/Ret)  |         |   brand               |
|   payment_mode (COD/UPI/Card)       |         |   mrp, cost_price     |
|   gross_gmv, discount_amount        |         +-----------------------+
|   net_gmv, order_cogs               |
+------------------+------------------+
                   ^
                   | 1:N (Single)
       +-----------+-----------+
       |       dim_date        |
       |-----------------------|
       | * date_key (PK)       |
       |   year, quarter       |
       |   month, month_name   |
       |   is_sale_month       |
       +-----------------------+
```

---

## 2. Table Relationships & Cardinality

| From Table (Dimension) | To Table (Fact) | Join Column | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :--- |
| `dim_customers` | `fact_orders` | `cust_id` | One-to-Many (`1:*`) | Single (`dim_customers` filters `fact_orders`) |
| `dim_date` | `fact_orders` | `date_key` -> `order_date` | One-to-Many (`1:*`) | Single (`dim_date` filters `fact_orders`) |
| `fact_orders` | `fact_order_items` | `order_id` | One-to-Many (`1:*`) | Single (`fact_orders` filters `fact_order_items`) |
| `dim_products` | `fact_order_items` | `prod_id` | One-to-Many (`1:*`) | Single (`dim_products` filters `fact_order_items`) |
| `fact_orders` | `fact_returns` | `order_id` | One-to-One / Many | Single (`fact_orders` filters `fact_returns`) |

---

## 3. Power BI Desktop Step-by-Step Setup

1. **Import Data**:
   - Open Power BI Desktop.
   - Click **Get Data** -> **Text/CSV** and select files from `data/raw/`:
     - `customers.csv` (rename query to `dim_customers`)
     - `products.csv` (rename query to `dim_products`)
     - `orders.csv` (rename query to `fact_orders`)
     - `order_items.csv` (rename query to `fact_order_items`)
     - `return_cancellations.csv` (rename query to `fact_returns`)
2. **Date Table Creation**:
   - In Power BI, navigate to the **Modeling** tab -> **New Table** and paste:
     ```dax
     dim_date = 
     CALENDAR(DATE(2024, 1, 1), DATE(2025, 12, 31))
     ```
   - Mark `dim_date` as the official Date Table.
3. **Establish Relationships**:
   - Switch to **Model View** and connect the primary and foreign keys as outlined in the table above.
4. **Create a Dedicated Measure Table**:
   - In Power BI, click **Enter Data** -> create an empty table named `_Measures`.
   - Store all DAX measures from `dax_measures_library.md` inside this folder for organized corporate reporting.
