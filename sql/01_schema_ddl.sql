-- sql/01_schema_ddl.sql
-- Star Schema DDL for Myntra Fashion E-Commerce Warehouse

-- 1. Customer Dimension
CREATE TABLE IF NOT EXISTS dim_customers (
    cust_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender VARCHAR(10),
    city VARCHAR(50),
    state VARCHAR(50),
    tier VARCHAR(20),       -- Tier 1, Tier 2, Tier 3
    signup_date DATE
);

-- 2. Product Dimension
CREATE TABLE IF NOT EXISTS dim_products (
    prod_id VARCHAR(20) PRIMARY KEY,
    prod_name VARCHAR(150) NOT NULL,
    category VARCHAR(50),   -- Men Western, Women Ethnic, Footwear, etc.
    brand VARCHAR(50),      -- Roadster, HRX, Anouk, Biba, etc.
    mrp DECIMAL(10, 2),
    cost_price DECIMAL(10, 2)
);

-- 3. Date Dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key DATE PRIMARY KEY,
    year INT,
    quarter VARCHAR(5),
    month INT,
    month_name VARCHAR(20),
    year_month VARCHAR(10),
    day_of_week VARCHAR(20),
    is_weekend INT,
    is_sale_month INT       -- 1 for EORS (June, Dec) and Festive (Oct)
);

-- 4. Fact Orders (Order level metrics)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id VARCHAR(30) PRIMARY KEY,
    cust_id VARCHAR(20),
    order_date DATE,
    delivery_date DATE,
    order_status VARCHAR(20),  -- Delivered, Returned, Cancelled, RTO
    payment_mode VARCHAR(20),  -- UPI, Credit Card, Debit Card, COD
    sale_event VARCHAR(30),    -- EORS / BFF Event, BAU Regular
    gross_gmv DECIMAL(12, 2),  -- Total MRP value of order
    discount_amount DECIMAL(12, 2),
    net_gmv DECIMAL(12, 2),    -- gross_gmv - discount_amount
    order_cogs DECIMAL(12, 2),
    FOREIGN KEY (cust_id) REFERENCES dim_customers(cust_id),
    FOREIGN KEY (order_date) REFERENCES dim_date(date_key)
);

-- 5. Fact Order Items (Line-item level details)
CREATE TABLE IF NOT EXISTS fact_order_items (
    item_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30),
    prod_id VARCHAR(20),
    qty INT DEFAULT 1,
    mrp DECIMAL(10, 2),
    discount_amount DECIMAL(10, 2),
    selling_price DECIMAL(10, 2),
    cogs DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id),
    FOREIGN KEY (prod_id) REFERENCES dim_products(prod_id)
);

-- 6. Fact Returns (Returns and RTO details)
CREATE TABLE IF NOT EXISTS fact_returns (
    order_id VARCHAR(30),
    return_type VARCHAR(30),    -- Customer Return, RTO (Undelivered)
    return_reason VARCHAR(100), -- Size / Fit Issue, Quality, Doorstep Refusal
    refund_amount DECIMAL(12, 2),
    FOREIGN KEY (order_id) REFERENCES fact_orders(order_id)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_fact_orders_cust ON fact_orders(cust_id);
CREATE INDEX IF NOT EXISTS idx_fact_orders_date ON fact_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_fact_orders_status ON fact_orders(order_status);
CREATE INDEX IF NOT EXISTS idx_fact_orders_pay ON fact_orders(payment_mode);
CREATE INDEX IF NOT EXISTS idx_fact_items_order ON fact_order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_fact_items_prod ON fact_order_items(prod_id);
CREATE INDEX IF NOT EXISTS idx_dim_cust_tier ON dim_customers(tier);
CREATE INDEX IF NOT EXISTS idx_dim_prod_cat ON dim_products(category);
