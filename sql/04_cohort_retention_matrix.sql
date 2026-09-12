-- sql/04_cohort_retention_matrix.sql
-- 12-Month Cohort Retention Matrix (Month-by-Month Customer Survival)
-- & Cross-Category Repeat Penetration

-- 1. Triangular Cohort Retention Matrix
WITH first_purchases AS (
    -- Identify the cohort month for each customer
    SELECT 
        cust_id,
        MIN(order_date) AS first_order_date,
        strftime('%Y-%m', MIN(order_date)) AS cohort_month
    FROM fact_orders
    GROUP BY cust_id
),
customer_activities AS (
    -- Map subsequent orders back to cohort and compute month offset
    SELECT 
        fp.cohort_month,
        o.cust_id,
        strftime('%Y-%m', o.order_date) AS order_month,
        (CAST(strftime('%Y', o.order_date) AS INT) - CAST(strftime('%Y', fp.first_order_date) AS INT)) * 12 +
        (CAST(strftime('%m', o.order_date) AS INT) - CAST(strftime('%m', fp.first_order_date) AS INT)) AS month_offset
    FROM fact_orders o
    JOIN first_purchases fp ON o.cust_id = fp.cust_id
),
cohort_sizes AS (
    -- Base size of each cohort
    SELECT 
        cohort_month,
        COUNT(DISTINCT cust_id) AS cohort_size
    FROM first_purchases
    GROUP BY cohort_month
),
retention_counts AS (
    -- Count distinct active users in each month offset
    SELECT 
        ca.cohort_month,
        cs.cohort_size,
        ca.month_offset,
        COUNT(DISTINCT ca.cust_id) AS active_customers,
        ROUND(100.0 * COUNT(DISTINCT ca.cust_id) / cs.cohort_size, 2) AS retention_rate_pct
    FROM customer_activities ca
    JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
    GROUP BY ca.cohort_month, cs.cohort_size, ca.month_offset
)
SELECT 
    cohort_month,
    cohort_size,
    MAX(CASE WHEN month_offset = 0 THEN retention_rate_pct ELSE NULL END) AS m0,
    MAX(CASE WHEN month_offset = 1 THEN retention_rate_pct ELSE NULL END) AS m1,
    MAX(CASE WHEN month_offset = 2 THEN retention_rate_pct ELSE NULL END) AS m2,
    MAX(CASE WHEN month_offset = 3 THEN retention_rate_pct ELSE NULL END) AS m3,
    MAX(CASE WHEN month_offset = 4 THEN retention_rate_pct ELSE NULL END) AS m4,
    MAX(CASE WHEN month_offset = 5 THEN retention_rate_pct ELSE NULL END) AS m5,
    MAX(CASE WHEN month_offset = 6 THEN retention_rate_pct ELSE NULL END) AS m6,
    MAX(CASE WHEN month_offset = 7 THEN retention_rate_pct ELSE NULL END) AS m7,
    MAX(CASE WHEN month_offset = 8 THEN retention_rate_pct ELSE NULL END) AS m8,
    MAX(CASE WHEN month_offset = 9 THEN retention_rate_pct ELSE NULL END) AS m9,
    MAX(CASE WHEN month_offset = 10 THEN retention_rate_pct ELSE NULL END) AS m10,
    MAX(CASE WHEN month_offset = 11 THEN retention_rate_pct ELSE NULL END) AS m11
FROM retention_counts
WHERE cohort_month <= '2025-01'
GROUP BY cohort_month, cohort_size
ORDER BY cohort_month;


-- 2. Cross-Category Repeat Penetration:
-- Did customers who started in Category A purchase in Category B later?
WITH first_cat_orders AS (
    SELECT 
        o.cust_id,
        p.category AS initial_category,
        MIN(o.order_date) AS first_date
    FROM fact_orders o
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_products p ON oi.prod_id = p.prod_id
    GROUP BY o.cust_id
),
subsequent_purchases AS (
    SELECT DISTINCT
        fco.cust_id,
        fco.initial_category,
        p.category AS next_category
    FROM first_cat_orders fco
    JOIN fact_orders o ON fco.cust_id = o.cust_id AND o.order_date > fco.first_date
    JOIN fact_order_items oi ON o.order_id = oi.order_id
    JOIN dim_products p ON oi.prod_id = p.prod_id
)
SELECT 
    fco.initial_category,
    COUNT(DISTINCT fco.cust_id) AS total_initial_customers,
    COUNT(DISTINCT sp.cust_id) AS cross_shopped_customers,
    ROUND(100.0 * COUNT(DISTINCT sp.cust_id) / COUNT(DISTINCT fco.cust_id), 2) AS cross_category_repeat_pct
FROM first_cat_orders fco
LEFT JOIN subsequent_purchases sp ON fco.cust_id = sp.cust_id AND fco.initial_category != sp.next_category
GROUP BY fco.initial_category
ORDER BY cross_category_repeat_pct DESC;
