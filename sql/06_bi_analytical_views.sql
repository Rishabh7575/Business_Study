-- sql/06_bi_analytical_views.sql
-- Production Analytical Views for Power BI and Excel Ingestion

-- 1. View: Executive Monthly Commercial Summary
CREATE VIEW IF NOT EXISTS vw_executive_monthly_kpis AS
SELECT 
    d.year,
    d.month,
    d.year_month,
    d.quarter,
    d.is_sale_month,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.gross_gmv), 2) AS gross_mrp_value,
    ROUND(SUM(o.discount_amount), 2) AS total_discounts,
    ROUND(SUM(o.net_gmv), 2) AS booked_gmv,
    
    -- Status counts
    COUNT(CASE WHEN o.order_status = 'Delivered' THEN 1 END) AS delivered_orders,
    COUNT(CASE WHEN o.order_status = 'Returned' THEN 1 END) AS returned_orders,
    COUNT(CASE WHEN o.order_status = 'RTO' THEN 1 END) AS rto_orders,
    COUNT(CASE WHEN o.order_status = 'Cancelled' THEN 1 END) AS cancelled_orders,
    
    -- Realized GMV & Margins
    ROUND(SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv ELSE 0 END), 2) AS realized_gmv,
    ROUND(SUM(CASE WHEN o.order_status = 'Delivered' THEN o.order_cogs ELSE 0 END), 2) AS realized_cogs,
    ROUND(SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv - o.order_cogs ELSE 0 END), 2) AS gross_profit,
    
    -- Rates
    ROUND(100.0 * SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv ELSE 0 END) / NULLIF(SUM(o.net_gmv), 0), 2) AS net_realization_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN o.order_status = 'RTO' THEN 1 END) / COUNT(o.order_id), 2) AS rto_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN o.order_status = 'Returned' THEN 1 END) / COUNT(o.order_id), 2) AS return_rate_pct
FROM fact_orders o
JOIN dim_date d ON o.order_date = d.date_key
GROUP BY d.year, d.month, d.year_month, d.quarter, d.is_sale_month;


-- 2. View: Precomputed Customer RFM Segmentation
CREATE VIEW IF NOT EXISTS vw_customer_rfm_segments AS
WITH ref_date AS (
    SELECT MAX(order_date) AS max_date FROM fact_orders
),
cust_base AS (
    SELECT 
        c.cust_id,
        c.name,
        c.tier,
        c.city,
        c.state,
        c.gender,
        CAST((julianday((SELECT max_date FROM ref_date)) - julianday(MAX(o.order_date))) AS INT) AS recency_days,
        COUNT(o.order_id) AS total_orders,
        COUNT(CASE WHEN o.order_status = 'Delivered' THEN 1 END) AS delivered_orders,
        COUNT(CASE WHEN o.order_status IN ('Returned', 'RTO') THEN 1 END) AS friction_orders,
        ROUND(COALESCE(SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv ELSE 0 END), 0), 2) AS realized_spend,
        ROUND(100.0 * COUNT(CASE WHEN o.order_status IN ('Returned', 'RTO') THEN 1 END) / NULLIF(COUNT(o.order_id), 0), 2) AS return_rate_pct
    FROM dim_customers c
    JOIN fact_orders o ON c.cust_id = o.cust_id
    GROUP BY c.cust_id, c.name, c.tier, c.city, c.state, c.gender
),
scored AS (
    SELECT 
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY realized_spend ASC) AS m_score
    FROM cust_base
)
SELECT 
    *,
    r_score || f_score || m_score AS rfm_cell,
    CASE 
        WHEN total_orders >= 3 AND return_rate_pct >= 40.0 THEN 'Serial Returner'
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalists'
        WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score BETWEEN 1 AND 2 THEN 'Hibernating / Lost'
        ELSE 'Promising / Regular'
    END AS segment_name
FROM scored;


-- 3. View: RTO and COD Performance by City Tier
CREATE VIEW IF NOT EXISTS vw_rto_by_city_tier AS
SELECT 
    c.tier,
    o.payment_mode,
    COUNT(o.order_id) AS total_orders,
    ROUND(SUM(o.net_gmv), 2) AS booked_gmv,
    COUNT(CASE WHEN o.order_status = 'RTO' THEN 1 END) AS rto_orders,
    ROUND(100.0 * COUNT(CASE WHEN o.order_status = 'RTO' THEN 1 END) / COUNT(o.order_id), 2) AS rto_rate_pct,
    ROUND(SUM(CASE WHEN o.order_status = 'RTO' THEN o.net_gmv ELSE 0 END), 2) AS lost_rto_gmv
FROM fact_orders o
JOIN dim_customers c ON o.cust_id = c.cust_id
GROUP BY c.tier, o.payment_mode;
