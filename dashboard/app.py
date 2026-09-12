# dashboard/app.py
# Myntra Executive Commercial & Customer Analytics Dashboard

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Myntra Commercial & Customer Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# load custom css
css_file = "dashboard/style.css"
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

db_path = "data/ecommerce_warehouse.db"

@st.cache_data
def load_data(query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Header section
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.title("🛍️ Myntra Fashion E-Commerce Analytics Suite")
    st.caption("Commercial Unit Economics, COD-RTO Logistics, RFM Personas & Cohort Retention")
with col_badge:
    st.markdown("<br><span class='myntra-badge'>MYNTRA BDA SHOWCASE</span>", unsafe_allow_html=True)

st.markdown("---")

# Sidebar filters
st.sidebar.header("Filter Analytics")
selected_year = st.sidebar.selectbox("Select Financial Year", ["All", "2024", "2025"])
selected_tier = st.sidebar.multiselect("Customer City Tier", ["Tier 1", "Tier 2", "Tier 3"], default=["Tier 1", "Tier 2", "Tier 3"])
selected_payment = st.sidebar.multiselect("Payment Mode", ["UPI", "COD", "Credit Card", "Debit Card"], default=["UPI", "COD", "Credit Card", "Debit Card"])

# Filter condition helper
where_clauses = []
if selected_year != "All":
    where_clauses.append(f"strftime('%Y', o.order_date) = '{selected_year}'")
if selected_tier:
    tiers_str = "', '".join(selected_tier)
    where_clauses.append(f"c.tier IN ('{tiers_str}')")
if selected_payment:
    pay_str = "', '".join(selected_payment)
    where_clauses.append(f"o.payment_mode IN ('{pay_str}')")

filter_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Overview", 
    "🚚 Returns & RTO Logistics", 
    "👥 RFM & Customer Personas", 
    "🔄 Cohort Retention", 
    "🎯 What-If Simulator"
])

# ========================================================
# TAB 1: EXECUTIVE OVERVIEW & WATERFALL
# ========================================================
with tab1:
    st.markdown("<div class='section-header'>Commercial Performance Scorecard</div>", unsafe_allow_html=True)
    
    # Query summary metrics
    q_sum = f"""
        SELECT 
            COUNT(o.order_id) AS total_orders,
            SUM(o.gross_gmv) AS gross_mrp,
            SUM(o.discount_amount) AS total_discounts,
            SUM(o.net_gmv) AS booked_gmv,
            SUM(CASE WHEN o.order_status = 'Cancelled' THEN o.net_gmv ELSE 0 END) AS cancelled_gmv,
            SUM(CASE WHEN o.order_status = 'RTO' THEN o.net_gmv ELSE 0 END) AS rto_gmv,
            SUM(CASE WHEN o.order_status = 'Returned' THEN o.net_gmv ELSE 0 END) AS returned_gmv,
            SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv ELSE 0 END) AS realized_gmv,
            SUM(CASE WHEN o.order_status = 'Delivered' THEN o.order_cogs ELSE 0 END) AS realized_cogs,
            COUNT(CASE WHEN o.order_status = 'Delivered' THEN 1 END) AS delivered_orders
        FROM fact_orders o
        JOIN dim_customers c ON o.cust_id = c.cust_id
        {filter_sql}
    """
    df_kpi = load_data(q_sum).iloc[0]
    
    b_gmv = df_kpi["booked_gmv"] or 1
    r_gmv = df_kpi["realized_gmv"] or 0
    deliv_orders = df_kpi["delivered_orders"] or 1
    cogs = df_kpi["realized_cogs"] or 0
    gross_profit = r_gmv - cogs
    
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Booked GMV", f"₹{b_gmv/1e7:.2f} Cr")
    k2.metric("Realized GMV (NMV)", f"₹{r_gmv/1e7:.2f} Cr", delta=f"{100*r_gmv/b_gmv:.1f}% Realization")
    k3.metric("Delivered Orders", f"{deliv_orders:,}", delta=f"{100*deliv_orders/df_kpi['total_orders']:.1f}% of Total")
    k4.metric("Realized AOV", f"₹{r_gmv/deliv_orders:.0f}")
    k5.metric("Delivered Margin %", f"{100*gross_profit/r_gmv:.1f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_w, col_trend = st.columns([1, 1])
    
    with col_w:
        st.subheader("GMV to Net Realized GMV Waterfall")
        waterfall_x = ["Booked GMV", "Cancellations", "RTO", "Customer Returns", "Net Realized GMV"]
        waterfall_y = [
            b_gmv,
            -df_kpi["cancelled_gmv"],
            -df_kpi["rto_gmv"],
            -df_kpi["returned_gmv"],
            r_gmv
        ]
        
        fig_wf = go.Figure(go.Waterfall(
            name="GMV Waterfall",
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "total"],
            x=waterfall_x,
            textposition="outside",
            text=[f"₹{abs(v)/1e5:.1f}L" for v in waterfall_y],
            y=waterfall_y,
            connector={"line": {"color": "#6C757D"}},
            decreasing={"marker": {"color": "#DC3545"}},
            increasing={"marker": {"color": "#28A745"}},
            totals={"marker": {"color": "#FF3F6C"}}
        ))
        fig_wf.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_wf, use_container_width=True)
        
    with col_trend:
        st.subheader("Monthly Revenue Trajectory (EORS Spikes)")
        q_monthly = f"""
            SELECT 
                strftime('%Y-%m', o.order_date) AS order_month,
                SUM(o.net_gmv) AS booked_gmv,
                SUM(CASE WHEN o.order_status = 'Delivered' THEN o.net_gmv ELSE 0 END) AS realized_gmv,
                MAX(CASE WHEN strftime('%m', o.order_date) IN ('06', '10', '12') THEN 1 ELSE 0 END) AS is_event
            FROM fact_orders o
            JOIN dim_customers c ON o.cust_id = c.cust_id
            {filter_sql}
            GROUP BY strftime('%Y-%m', o.order_date)
            ORDER BY order_month
        """
        df_m = load_data(q_monthly)
        
        fig_m = px.line(df_m, x="order_month", y=["booked_gmv", "realized_gmv"],
                        labels={"value": "GMV (₹)", "order_month": "Month", "variable": "Metric"},
                        color_discrete_map={"booked_gmv": "#9E9E9E", "realized_gmv": "#FF3F6C"})
        fig_m.update_layout(height=400, legend=dict(orientation="h", y=1.1), margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_m, use_container_width=True)

# ========================================================
# TAB 2: RETURNS & RTO LOGISTICS INTELLIGENCE
# ========================================================
with tab2:
    st.markdown("<div class='section-header'>Logistics Friction: COD vs Prepaid RTO & Sizing Analysis</div>", unsafe_allow_html=True)
    
    st.info("💡 **Myntra BDA Key Insight**: Cash on Delivery (COD) orders suffer ~22% RTO (Return to Origin) compared to only ~4.5% in Prepaid orders, leading to significant two-way logistics leakage.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("RTO Rate by Payment Mode")
        q_pay_rto = f"""
            SELECT 
                o.payment_mode,
                COUNT(o.order_id) AS orders,
                ROUND(100.0 * COUNT(CASE WHEN o.order_status = 'RTO' THEN 1 END) / COUNT(o.order_id), 2) AS rto_rate_pct,
                SUM(CASE WHEN o.order_status = 'RTO' THEN o.net_gmv ELSE 0 END) AS lost_gmv
            FROM fact_orders o
            JOIN dim_customers c ON o.cust_id = c.cust_id
            {filter_sql}
            GROUP BY o.payment_mode
            ORDER BY rto_rate_pct DESC
        """
        df_pay_rto = load_data(q_pay_rto)
        fig_pay = px.bar(df_pay_rto, x="payment_mode", y="rto_rate_pct", text="rto_rate_pct",
                         color="payment_mode",
                         color_discrete_map={"COD": "#DC3545", "UPI": "#28A745", "Credit Card": "#007BFF", "Debit Card": "#17A2B8"},
                         labels={"rto_rate_pct": "RTO Rate %", "payment_mode": "Payment Mode"})
        fig_pay.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_pay.update_layout(height=380, showlegend=False, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_pay, use_container_width=True)
        
    with c2:
        st.subheader("Customer Return Reasons (Delivered Orders)")
        q_reasons = """
            SELECT 
                return_reason,
                COUNT(order_id) AS cnt,
                ROUND(100.0 * COUNT(order_id) / (SELECT COUNT(*) FROM fact_returns WHERE return_type = 'Customer Return'), 1) AS pct
            FROM fact_returns
            WHERE return_type = 'Customer Return'
            GROUP BY return_reason
            ORDER BY cnt DESC
        """
        df_reasons = load_data(q_reasons)
        fig_reasons = px.pie(df_reasons, names="return_reason", values="cnt",
                             color_discrete_sequence=px.colors.sequential.RdPu_r,
                             hole=0.45)
        fig_reasons.update_layout(height=380, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_reasons, use_container_width=True)
        
    # Category level return breakdown
    st.subheader("Return & RTO Rate by Fashion Category")
    q_cat_ret = """
        SELECT 
            p.category,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS return_rate_pct,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'RTO' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS rto_rate_pct,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_status = 'Delivered' THEN o.order_id END) / COUNT(DISTINCT o.order_id), 2) AS delivery_rate_pct
        FROM fact_order_items oi
        JOIN dim_products p ON oi.prod_id = p.prod_id
        JOIN fact_orders o ON oi.order_id = o.order_id
        GROUP BY p.category
        ORDER BY return_rate_pct DESC
    """
    df_cat_ret = load_data(q_cat_ret)
    fig_cat = px.bar(df_cat_ret, x="category", y=["return_rate_pct", "rto_rate_pct"],
                     barmode="group",
                     labels={"value": "Rate %", "category": "Product Category", "variable": "Metric"},
                     color_discrete_map={"return_rate_pct": "#FF3F6C", "rto_rate_pct": "#6C757D"})
    fig_cat.update_layout(height=380, margin=dict(t=30, b=30, l=30, r=30))
    st.plotly_chart(fig_cat, use_container_width=True)

# ========================================================
# TAB 3: RFM & CUSTOMER PERSONAS
# ========================================================
with tab3:
    st.markdown("<div class='section-header'>RFM Customer Segmentation & Behavioral Personas</div>", unsafe_allow_html=True)
    
    df_rfm = load_data("SELECT * FROM vw_customer_rfm_segments")
    
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        st.subheader("Revenue Contribution by Persona")
        df_seg_summary = df_rfm.groupby("segment_name").agg(
            cust_count=("cust_id", "count"),
            total_spend=("realized_spend", "sum"),
            avg_return_rate=("return_rate_pct", "mean")
        ).reset_index()
        
        fig_tree = px.treemap(
            df_seg_summary,
            path=["segment_name"],
            values="total_spend",
            color="avg_return_rate",
            color_continuous_scale="Reds",
            labels={"total_spend": "Spend (₹)", "avg_return_rate": "Avg Return %"}
        )
        fig_tree.update_layout(height=380, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_tree, use_container_width=True)
        
    with col_t2:
        st.subheader("Recency vs Monetary Scatter")
        sample_rfm = df_rfm.sample(min(2000, len(df_rfm)), random_state=42)
        fig_scat = px.scatter(
            sample_rfm,
            x="recency_days",
            y="realized_spend",
            color="segment_name",
            size="total_orders",
            hover_data=["name", "city", "return_rate_pct"],
            labels={"recency_days": "Recency (Days Ago)", "realized_spend": "Realized Spend (₹)"}
        )
        fig_scat.update_layout(height=380, margin=dict(t=30, b=30, l=30, r=30))
        st.plotly_chart(fig_scat, use_container_width=True)
        
    # Interactive Customer Lookup and Campaign Exporter
    st.subheader("🎯 Targeted Campaign Audience Generator")
    chosen_persona = st.selectbox("Select Segment to Export Campaign Target List", df_rfm["segment_name"].unique())
    
    df_filtered_cust = df_rfm[df_rfm["segment_name"] == chosen_persona][
        ["cust_id", "name", "tier", "city", "recency_days", "total_orders", "realized_spend", "return_rate_pct"]
    ]
    st.dataframe(df_filtered_cust.head(100), use_container_width=True)
    
    csv_data = df_filtered_cust.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {chosen_persona} Audience List ({len(df_filtered_cust)} Customers)",
        data=csv_data,
        file_name=f"myntra_campaign_{chosen_persona.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

# ========================================================
# TAB 4: COHORT RETENTION MATRIX
# ========================================================
with tab4:
    st.markdown("<div class='section-header'>12-Month Cohort Retention & Repeat Dynamics</div>", unsafe_allow_html=True)
    
    q_cohort = """
        WITH first_purchases AS (
            SELECT cust_id, strftime('%Y-%m', MIN(order_date)) AS cohort_month
            FROM fact_orders GROUP BY cust_id
        ),
        activities AS (
            SELECT 
                fp.cohort_month, o.cust_id,
                (CAST(strftime('%Y', o.order_date) AS INT) - CAST(strftime('%Y', fp.cohort_month || '-01') AS INT)) * 12 +
                (CAST(strftime('%m', o.order_date) AS INT) - CAST(strftime('%m', fp.cohort_month || '-01') AS INT)) AS month_offset
            FROM fact_orders o
            JOIN first_purchases fp ON o.cust_id = fp.cust_id
        ),
        cohort_sizes AS (
            SELECT cohort_month, COUNT(DISTINCT cust_id) AS c_size
            FROM first_purchases GROUP BY cohort_month
        )
        SELECT 
            a.cohort_month, a.month_offset,
            ROUND(100.0 * COUNT(DISTINCT a.cust_id) / cs.c_size, 1) AS retention_pct
        FROM activities a
        JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
        WHERE a.cohort_month <= '2025-01' AND a.month_offset BETWEEN 0 AND 11
        GROUP BY a.cohort_month, a.month_offset
        ORDER BY a.cohort_month, a.month_offset
    """
    df_c = load_data(q_cohort)
    df_pivot = df_c.pivot(index="cohort_month", columns="month_offset", values="retention_pct")
    
    fig_heat = px.imshow(
        df_pivot,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdPu",
        labels=dict(x="Month Offset", y="Cohort Month", color="Retention %"),
        title="Cohort Retention Survival Heatmap (% Active Customers by Month)"
    )
    fig_heat.update_layout(height=450, margin=dict(t=40, b=30, l=30, r=30))
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.markdown("""
    **Cohort Takeaway**:
    * Month 1 retention experiences a normal drop-off to 20-30%.
    * Periodic re-engagement spikes occur during **Month 6 and Month 10/11**, precisely aligning with Myntra's **EORS Summer and Festive Diwali mega-sale events**.
    """)

# ========================================================
# TAB 5: WHAT-IF REVENUE SCENARIO SIMULATOR
# ========================================================
with tab5:
    st.markdown("<div class='section-header'>Strategic What-If Scenario Modeler (Unit Economics)</div>", unsafe_allow_html=True)
    
    st.write("Simulate the bottom-line financial impact of key strategic initiatives proposed to Myntra leadership.")
    
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        cod_rto_reduction = st.slider("Target COD RTO Reduction (% pts)", min_value=0.0, max_value=10.0, value=4.0, step=0.5)
    with s_col2:
        sizing_return_reduction = st.slider("AI Size-Recommendation Impact on Returns (% pts)", min_value=0.0, max_value=8.0, value=3.0, step=0.5)
    with s_col3:
        repeat_boost = st.slider("Retention Campaign Repeat Purchase Lift (%)", min_value=0.0, max_value=15.0, value=5.0, step=1.0)
        
    # Baseline calculations
    base_orders = df_kpi["total_orders"]
    base_rto_gmv = df_kpi["rto_gmv"]
    base_ret_gmv = df_kpi["returned_gmv"]
    base_realized_gmv = df_kpi["realized_gmv"]
    
    # Savings
    cod_recovered = (cod_rto_reduction / 100.0) * base_rto_gmv * 1.5
    sizing_recovered = (sizing_return_reduction / 100.0) * base_ret_gmv
    retention_added = (repeat_boost / 100.0) * base_realized_gmv * 0.40
    
    total_impact = cod_recovered + sizing_recovered + retention_added
    margin_expansion = total_impact * 0.28
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Projected Annual GMV Recovery", f"₹{total_impact/1e5:.1f} Lakhs", delta=f"+₹{total_impact/1e7:.2f} Cr")
    res2.metric("Direct Bottom-Line Profit Expansion", f"₹{margin_expansion/1e5:.1f} Lakhs", delta="Net Margin Boost")
    res3.metric("Logistics Freight Cost Saved", f"₹{(cod_recovered * 0.12)/1e5:.1f} Lakhs", delta="Two-Way Logistics")
    
    st.markdown("""
    <div class='insight-card'>
    <b>Strategic Recommendation for Myntra Commercial Operations:</b><br>
    1. <b>Prepaid Conversion Incentives</b>: Offering a ₹50 instant cashback or UPI scratch card converts 15% of COD buyers to prepaid, immediately reducing RTO losses.<br>
    2. <b>True-Fit Sizing Widget</b>: Addressing footwear & ethnic wear returns with virtual sizing guidance can preserve ₹1.2+ Cr in realized GMV.<br>
    3. <b>VIP Retention Playbook</b>: Nurturing "Champions" and "Potential Loyalists" via customized early-access sales provides 5x ROI compared to acquiring cold users.
    </div>
    """, unsafe_allow_html=True)
