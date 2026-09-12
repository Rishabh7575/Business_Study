# scripts/build_warehouse.py
# loads raw csvs into sqlite star schema warehouse with indexes

import sqlite3
import pandas as pd
import os

db_path = "data/ecommerce_warehouse.db"

# remove existing if re-running
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("reading raw csv files...")
df_cust = pd.read_csv("data/raw/customers.csv")
df_prod = pd.read_csv("data/raw/products.csv")
df_orders = pd.read_csv("data/raw/orders.csv")
df_items = pd.read_csv("data/raw/order_items.csv")
df_returns = pd.read_csv("data/raw/return_cancellations.csv")

print("creating tables in sqlite...")
df_cust.to_sql("dim_customers", conn, if_exists="replace", index=False)
df_prod.to_sql("dim_products", conn, if_exists="replace", index=False)
df_orders.to_sql("fact_orders", conn, if_exists="replace", index=False)
df_items.to_sql("fact_order_items", conn, if_exists="replace", index=False)
df_returns.to_sql("fact_returns", conn, if_exists="replace", index=False)

# build date dimension
print("building dim_date...")
df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
min_dt = df_orders['order_date'].min()
max_dt = df_orders['order_date'].max()

date_series = pd.date_range(min_dt, max_dt)
df_date = pd.DataFrame({
    "date_key": date_series.strftime("%Y-%m-%d"),
    "year": date_series.year,
    "quarter": "Q" + date_series.quarter.astype(str),
    "month": date_series.month,
    "month_name": date_series.strftime("%B"),
    "year_month": date_series.strftime("%Y-%m"),
    "day_of_week": date_series.strftime("%A"),
    "is_weekend": date_series.dayofweek.isin([5, 6]).astype(int),
    "is_sale_month": date_series.month.isin([6, 10, 12]).astype(int)
})
df_date.to_sql("dim_date", conn, if_exists="replace", index=False)

# create indexes for fast queries
print("creating indexes...")
cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_cust ON fact_orders(cust_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON fact_orders(order_date);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON fact_orders(order_status);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_payment ON fact_orders(payment_mode);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_items_order ON fact_order_items(order_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_items_prod ON fact_order_items(prod_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_cust_tier ON dim_customers(tier);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_prod_cat ON dim_products(category);")

conn.commit()
conn.close()

print(f"warehouse built successfully at {db_path}!")
