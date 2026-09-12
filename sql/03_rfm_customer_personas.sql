-- sql/03_rfm_customer_personas.sql
-- RFM Customer Segmentation & Fashion Behavioral Persona Modeling
-- Uses NTILE(5) window functions and flags Serial Returners

WITH reference_date AS (
    -- Reference date is maximum order date in the dataset
    SELECT MAX(order_date) AS max_date FROM fact_orders
),
customer_metrics AS (
    SELECT 
        c.cust_id,
        c.name,
        c.tier,
        c.gender,
        c.city,
        
        -- Recency: Days since last order
        CAST((julianday((SELECT max_date FROM reference_date)) - julianday(MAX(o.order_date))) AS INT) AS recency_days,
        
        -- Frequency: Total orders placed
        COUNT(o.order_id) AS total_orders,
        COUNT(CASE WHEN o.order_status = 'Delivered' THEN 1 END) AS delivered_orders,
        COUNT(CASE WHEN o.order_status IN ('Returned', 'RTO') THEN 1 END) AS returned_orders,
        
        -- Monetary: Total net realized spend (Delivered GMV)
        ROUND(COALESCE(SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv ELSE 0 END), 0), 2) AS monetary_val,
        
        -- Customer return rate
        ROUND(100.0 * COUNT(CASE WHEN o.order_status IN ('Returned', 'RTO') THEN 1 END) / NULLIF(COUNT(o.order_id), 0), 2) AS return_rate_pct
    FROM dim_customers c
    JOIN fact_orders o ON c.cust_id = o.cust_id
    GROUP BY c.cust_id, c.name, c.tier, c.gender, c.city
),
rfm_scores AS (
    SELECT 
        *,
        -- R score: 5 is most recent (lowest recency_days)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- F score: 5 is highest order frequency
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,
        -- M score: 5 is highest spend
        NTILE(5) OVER (ORDER BY monetary_val ASC) AS m_score
    FROM customer_metrics
),
customer_personas AS (
    SELECT 
        *,
        r_score || f_score || m_score AS rfm_cell,
        CASE 
            -- Flag high-return friction customers (vital for fashion unit economics)
            WHEN total_orders >= 3 AND return_rate_pct >= 40.0 THEN 'Serial Returner'
            
            -- Standard RFM Segments
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalists'
            WHEN r_score >= 4 AND f_score = 1 THEN 'New Customers'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score BETWEEN 1 AND 2 THEN 'Hibernating / Lost'
            ELSE 'Promising / Regular'
        END AS persona_segment
    FROM rfm_scores
)
-- 1. Summary by Customer Persona
SELECT 
    persona_segment,
    COUNT(cust_id) AS customer_count,
    ROUND(100.0 * COUNT(cust_id) / (SELECT COUNT(*) FROM customer_personas), 2) AS customer_share_pct,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(total_orders), 1) AS avg_orders,
    ROUND(AVG(monetary_val), 2) AS avg_spend,
    ROUND(SUM(monetary_val), 2) AS total_segment_revenue,
    ROUND(100.0 * SUM(monetary_val) / (SELECT SUM(monetary_val) FROM customer_personas), 2) AS revenue_share_pct,
    ROUND(AVG(return_rate_pct), 2) AS avg_return_rate_pct
FROM customer_personas
GROUP BY persona_segment
ORDER BY total_segment_revenue DESC;
