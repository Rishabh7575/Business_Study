-- sql/05_category_returns_deepdive.sql
-- Category & Brand Margin, Sizing Friction & Return Root-Cause Analysis

-- 1. Category-Level Performance & Return Leakage
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.qty) AS units_sold,
    ROUND(SUM(oi.selling_price), 2) AS gross_sales_value,
    ROUND(SUM(oi.cogs), 2) AS total_cogs,
    
    -- Delivered vs Returned
    COUNT(DISTINCT CASE WHEN o.order_status = 'Delivered' THEN o.order_id END) AS delivered_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END) AS customer_returns,
    COUNT(DISTINCT CASE WHEN o.order_status = 'RTO' THEN o.order_id END) AS rto_orders,
    
    -- Rates
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS return_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'RTO' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS rto_rate_pct,
    
    -- Realized Margin %
    ROUND(100.0 * (SUM(CASE WHEN o.order_status = 'Delivered' THEN oi.selling_price - oi.cogs ELSE 0 END)) / 
          NULLIF(SUM(CASE WHEN o.order_status = 'Delivered' THEN oi.selling_price ELSE 0 END), 0), 2) AS delivered_margin_pct
FROM fact_order_items oi
JOIN dim_products p ON oi.prod_id = p.prod_id
JOIN fact_orders o ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;


-- 2. Return Reason Breakdown by Category (Highlighting Sizing Friction)
SELECT 
    p.category,
    r.return_reason,
    COUNT(r.order_id) AS return_count,
    ROUND(100.0 * COUNT(r.order_id) / SUM(COUNT(r.order_id)) OVER(PARTITION BY p.category), 2) AS pct_of_category_returns
FROM fact_returns r
JOIN fact_orders o ON r.order_id = o.order_id
JOIN fact_order_items oi ON o.order_id = oi.order_id
JOIN dim_products p ON oi.prod_id = p.prod_id
WHERE r.return_type = 'Customer Return'
GROUP BY p.category, r.return_reason
ORDER BY p.category, return_count DESC;


-- 3. Brand Scorecard (GMV, Return Rate, and Net Realization)
SELECT 
    p.brand,
    p.category,
    COUNT(DISTINCT o.order_id) AS orders_count,
    ROUND(SUM(oi.selling_price), 2) AS brand_gmv,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS brand_return_rate_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'Delivered' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS net_realization_rate_pct
FROM fact_order_items oi
JOIN dim_products p ON oi.prod_id = p.prod_id
JOIN fact_orders o ON oi.order_id = o.order_id
GROUP BY p.brand, p.category
ORDER BY brand_gmv DESC
LIMIT 15;
