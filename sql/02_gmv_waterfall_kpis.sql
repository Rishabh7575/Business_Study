-- sql/02_gmv_waterfall_kpis.sql
-- Executive GMV to Net Realized GMV (NMV) Waterfall and Core Commercial KPIs

-- 1. High-level waterfall: Gross GMV -> Discounts -> Cancellations -> RTO -> Returns -> Net Realized GMV
WITH order_base AS (
    SELECT 
        strftime('%Y-%m', order_date) AS order_month,
        COUNT(order_id) AS total_orders,
        SUM(gross_gmv) AS total_gross_mrp,
        SUM(discount_amount) AS total_discounts,
        SUM(net_gmv) AS total_booked_gmv,
        
        -- Cancellations (pre-dispatch)
        SUM(CASE WHEN order_status = 'Cancelled' THEN net_gmv ELSE 0 END) AS cancelled_gmv,
        COUNT(CASE WHEN order_status = 'Cancelled' THEN 1 END) AS cancelled_orders,
        
        -- RTO (undelivered courier return - high in COD)
        SUM(CASE WHEN order_status = 'RTO' THEN net_gmv ELSE 0 END) AS rto_gmv,
        COUNT(CASE WHEN order_status = 'RTO' THEN 1 END) AS rto_orders,
        
        -- Customer returns (after delivery)
        SUM(CASE WHEN order_status = 'Returned' THEN net_gmv ELSE 0 END) AS returned_gmv,
        COUNT(CASE WHEN order_status = 'Returned' THEN 1 END) AS returned_orders,
        
        -- Net Realized (Delivered successfully and retained)
        SUM(CASE WHEN order_status = 'Delivered' THEN net_gmv ELSE 0 END) AS net_realized_gmv,
        COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) AS delivered_orders,
        
        -- Cost of goods for delivered items
        SUM(CASE WHEN order_status = 'Delivered' THEN order_cogs ELSE 0 END) AS delivered_cogs
    FROM fact_orders
    GROUP BY strftime('%Y-%m', order_date)
)
SELECT 
    order_month,
    total_orders,
    ROUND(total_booked_gmv, 2) AS booked_gmv,
    ROUND(cancelled_gmv, 2) AS cancelled_gmv,
    ROUND(rto_gmv, 2) AS rto_gmv,
    ROUND(returned_gmv, 2) AS returned_gmv,
    ROUND(net_realized_gmv, 2) AS net_realized_gmv,
    
    -- Realization & Leakage percentages
    ROUND(100.0 * net_realized_gmv / total_booked_gmv, 2) AS net_realization_pct,
    ROUND(100.0 * rto_gmv / total_booked_gmv, 2) AS rto_leakage_pct,
    ROUND(100.0 * returned_gmv / total_booked_gmv, 2) AS return_leakage_pct,
    
    -- Commercial KPIs
    ROUND(total_booked_gmv / total_orders, 2) AS booked_aov,
    ROUND(net_realized_gmv / NULLIF(delivered_orders, 0), 2) AS realized_aov,
    ROUND(100.0 * (net_realized_gmv - delivered_cogs) / NULLIF(net_realized_gmv, 0), 2) AS gross_margin_pct
FROM order_base
ORDER BY order_month;


-- 2. COD vs Prepaid RTO comparison (Crucial for Myntra Logistics)
SELECT 
    payment_mode,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(net_gmv), 2) AS total_gmv,
    COUNT(CASE WHEN order_status = 'RTO' THEN 1 END) AS rto_count,
    ROUND(100.0 * COUNT(CASE WHEN order_status = 'RTO' THEN 1 END) / COUNT(order_id), 2) AS rto_rate_pct,
    ROUND(SUM(CASE WHEN order_status = 'RTO' THEN net_gmv ELSE 0 END), 2) AS lost_rto_gmv,
    COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) AS delivered_count,
    ROUND(100.0 * COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) / COUNT(order_id), 2) AS delivery_success_pct
FROM fact_orders
GROUP BY payment_mode
ORDER BY rto_rate_pct DESC;
