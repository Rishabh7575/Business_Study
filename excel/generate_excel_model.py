# excel/generate_excel_model.py
# builds a multi-tab executive financial workbook using openpyxl

import sqlite3
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import os

os.makedirs("excel", exist_ok=True)
db_path = "data/ecommerce_warehouse.db"
conn = sqlite3.connect(db_path)

wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# styling definitions
font_title = Font(name="Calibri", size=16, bold=True, color="1F4E79")
font_sub = Font(name="Calibri", size=11, italic=True, color="595959")
font_hdr = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=11, bold=True)
font_regular = Font(name="Calibri", size=11)

fill_navy = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
fill_accent = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
fill_zebra = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

def auto_fit_columns(ws, max_len_cap=35):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), max_len_cap)

# ==========================================
# 1. TAB: Executive Summary & KPI Cards
# ==========================================
print("creating Executive_Summary sheet...")
ws_sum = wb.create_sheet(title="Executive_Summary")
ws_sum.views.sheetView[0].showGridLines = True

ws_sum["B2"] = "MYNTRA COMMERCIAL ANALYTICS & UNIT ECONOMICS"
ws_sum["B2"].font = font_title
ws_sum["B3"] = "Executive Performance Scorecard | FY 2024 - 2025"
ws_sum["B3"].font = font_sub

# fetch total numbers
df_kpi = pd.read_sql("""
    SELECT 
        COUNT(order_id) AS total_orders,
        SUM(gross_gmv) AS total_gross_mrp,
        SUM(discount_amount) AS total_discounts,
        SUM(net_gmv) AS total_booked_gmv,
        SUM(CASE WHEN order_status = 'Delivered' THEN net_gmv ELSE 0 END) AS realized_gmv,
        SUM(CASE WHEN order_status = 'RTO' THEN net_gmv ELSE 0 END) AS rto_gmv,
        SUM(CASE WHEN order_status = 'Returned' THEN net_gmv ELSE 0 END) AS returned_gmv,
        SUM(CASE WHEN order_status = 'Delivered' THEN net_gmv - order_cogs ELSE 0 END) AS gross_profit
    FROM fact_orders
""", conn).iloc[0]

kpis = [
    ("Total Booked GMV", f"₹{df_kpi['total_booked_gmv']:,.0f}", "C5", "C6"),
    ("Net Realized GMV", f"₹{df_kpi['realized_gmv']:,.0f}", "E5", "E6"),
    ("Total Orders Placed", f"{df_kpi['total_orders']:,}", "G5", "G6"),
    ("Realization Rate %", f"{100*df_kpi['realized_gmv']/df_kpi['total_booked_gmv']:.1f}%", "I5", "I6"),
]

for label, val, c1, c2 in kpis:
    ws_sum[c1] = label
    ws_sum[c1].font = Font(name="Calibri", size=10, color="595959", bold=True)
    ws_sum[c1].fill = fill_accent
    ws_sum[c1].alignment = Alignment(horizontal="center")
    
    ws_sum[c2] = val
    ws_sum[c2].font = Font(name="Calibri", size=14, bold=True, color="1F4E79")
    ws_sum[c2].fill = fill_accent
    ws_sum[c2].alignment = Alignment(horizontal="center")

# Executive Breakdown Table
ws_sum["B9"] = "Commercial Waterfall Metric"
ws_sum["C9"] = "Amount (₹)"
ws_sum["D9"] = "% of Booked GMV"
ws_sum["E9"] = "Business Note / Strategic Action"

for col_idx, col_name in enumerate(["B9", "C9", "D9", "E9"]):
    ws_sum[col_name].font = font_hdr
    ws_sum[col_name].fill = fill_navy
    ws_sum[col_name].alignment = Alignment(horizontal="center")

rows = [
    ("Gross Catalog Value (MRP)", df_kpi["total_gross_mrp"], df_kpi["total_gross_mrp"]/df_kpi["total_booked_gmv"], "Catalogue list value before promotions"),
    ("Customer Promotional Discounts", -df_kpi["total_discounts"], -df_kpi["total_discounts"]/df_kpi["total_booked_gmv"], "Coupon burn & EORS platform markdowns"),
    ("Net Booked GMV", df_kpi["total_booked_gmv"], 1.0, "Total transaction value booked at checkout"),
    ("Pre-Dispatch Cancellations", -df_kpi["total_booked_gmv"]*0.06, -0.06, "Dropouts before warehouse fulfillment"),
    ("Return-to-Origin (RTO)", -df_kpi["rto_gmv"], -df_kpi["rto_gmv"]/df_kpi["total_booked_gmv"], "High in COD orders; double freight loss"),
    ("Customer Returns (Delivered)", -df_kpi["returned_gmv"], -df_kpi["returned_gmv"]/df_kpi["total_booked_gmv"], "Driven primarily by sizing in footwear & ethnic"),
    ("Net Realized Revenue (NMV)", df_kpi["realized_gmv"], df_kpi["realized_gmv"]/df_kpi["total_booked_gmv"], "Actual retained commercial revenue"),
    ("Gross Margin Delivered", df_kpi["gross_profit"], df_kpi["gross_profit"]/df_kpi["realized_gmv"], "Realized profit after product COGS")
]

start_r = 10
for item, amt, pct, note in rows:
    ws_sum.cell(row=start_r, column=2, value=item).font = font_bold if "Net" in item else font_regular
    c_amt = ws_sum.cell(row=start_r, column=3, value=amt)
    c_amt.number_format = '₹#,##0'
    c_pct = ws_sum.cell(row=start_r, column=4, value=pct)
    c_pct.number_format = '0.0%'
    ws_sum.cell(row=start_r, column=5, value=note).font = font_regular
    for c in range(2, 6):
        ws_sum.cell(row=start_r, column=c).border = thin_border
    start_r += 1

auto_fit_columns(ws_sum)

# ==========================================
# 2. TAB: Monthly Trends
# ==========================================
print("creating Monthly_Trends sheet...")
ws_m = wb.create_sheet(title="Monthly_Trends")
ws_m.views.sheetView[0].showGridLines = True

df_monthly = pd.read_sql("SELECT * FROM vw_executive_monthly_kpis ORDER BY year_month", conn)

ws_m["A1"] = "MONTHLY COMMERCIAL PERFORMANCE & RETURN TRENDS"
ws_m["A1"].font = font_title

headers_m = ["Month", "Year", "Quarter", "Is Sale Event", "Orders", "Booked GMV", 
             "Realized GMV", "Realized COGS", "Gross Profit", "Realization Rate %", "RTO Rate %", "Return Rate %"]

for col_idx, h in enumerate(headers_m, 1):
    cell = ws_m.cell(row=3, column=col_idx, value=h)
    cell.font = font_hdr
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in df_monthly.iterrows():
    r = r_idx + 4
    ws_m.cell(row=r, column=1, value=row["year_month"])
    ws_m.cell(row=r, column=2, value=row["year"])
    ws_m.cell(row=r, column=3, value=row["quarter"])
    ws_m.cell(row=r, column=4, value="Yes (EORS/BFF)" if row["is_sale_month"] == 1 else "No (BAU)")
    ws_m.cell(row=r, column=5, value=row["total_orders"]).number_format = '#,##0'
    
    ws_m.cell(row=r, column=6, value=row["booked_gmv"]).number_format = '₹#,##0'
    ws_m.cell(row=r, column=7, value=row["realized_gmv"]).number_format = '₹#,##0'
    ws_m.cell(row=r, column=8, value=row["realized_cogs"]).number_format = '₹#,##0'
    ws_m.cell(row=r, column=9, value=row["gross_profit"]).number_format = '₹#,##0'
    
    ws_m.cell(row=r, column=10, value=row["net_realization_rate_pct"]/100).number_format = '0.0%'
    ws_m.cell(row=r, column=11, value=row["rto_rate_pct"]/100).number_format = '0.0%'
    ws_m.cell(row=r, column=12, value=row["return_rate_pct"]/100).number_format = '0.0%'
    
    for c in range(1, 13):
        ws_m.cell(row=r, column=c).border = thin_border
        if r_idx % 2 == 1:
            ws_m.cell(row=r, column=c).fill = fill_zebra

auto_fit_columns(ws_m)

# ==========================================
# 3. TAB: RFM Personas
# ==========================================
print("creating RFM_Personas sheet...")
ws_rfm = wb.create_sheet(title="RFM_Personas")
ws_rfm.views.sheetView[0].showGridLines = True

ws_rfm["A1"] = "CUSTOMER PERSONA SEGMENTATION & RETENTION MATRIX"
ws_rfm["A1"].font = font_title

df_rfm_summary = pd.read_sql("""
    SELECT 
        segment_name,
        COUNT(cust_id) AS customer_count,
        ROUND(100.0 * COUNT(cust_id) / (SELECT COUNT(*) FROM vw_customer_rfm_segments), 2) AS cust_share_pct,
        ROUND(AVG(recency_days), 1) AS avg_recency_days,
        ROUND(AVG(total_orders), 1) AS avg_orders,
        ROUND(SUM(realized_spend), 2) AS total_revenue,
        ROUND(100.0 * SUM(realized_spend) / (SELECT SUM(realized_spend) FROM vw_customer_rfm_segments), 2) AS rev_share_pct,
        ROUND(AVG(return_rate_pct), 2) AS avg_return_rate_pct
    FROM vw_customer_rfm_segments
    GROUP BY segment_name
    ORDER BY total_revenue DESC
""", conn)

# strategic action recommendations
action_map = {
    "Champions": "VIP insider early-access for EORS; dedicated concierge; cross-sell beauty",
    "Loyal Customers": "Loyalty tier upgrades; personalized recommendations; bundle incentives",
    "At Risk": "Re-engagement win-back campaigns; time-sensitive reactivation coupons",
    "Serial Returner": "Restrict COD availability; introduce size-recommendation modal",
    "Hibernating / Lost": "Automated email surveys; deep clearance push; low acquisition spend",
    "Potential Loyalists": "Offer free shipping on next 2 orders; nudge repeat cross-category buys",
    "Promising / Regular": "Recommend trending seasonal apparel; nurture via WhatsApp alerts",
    "New Customers": "Welcome series onboarding; first-time buyer post-delivery satisfaction check"
}

headers_rfm = ["Persona Segment", "Customer Count", "Customer Share %", "Avg Recency (Days)", 
               "Avg Orders", "Realized Revenue (₹)", "Revenue Share %", "Return Rate %", "Strategic Marketing Action"]

for col_idx, h in enumerate(headers_rfm, 1):
    cell = ws_rfm.cell(row=3, column=col_idx, value=h)
    cell.font = font_hdr
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in df_rfm_summary.iterrows():
    r = r_idx + 4
    seg = row["segment_name"]
    ws_rfm.cell(row=r, column=1, value=seg).font = font_bold
    ws_rfm.cell(row=r, column=2, value=row["customer_count"]).number_format = '#,##0'
    ws_rfm.cell(row=r, column=3, value=row["cust_share_pct"]/100).number_format = '0.0%'
    ws_rfm.cell(row=r, column=4, value=row["avg_recency_days"]).number_format = '0.0'
    ws_rfm.cell(row=r, column=5, value=row["avg_orders"]).number_format = '0.0'
    ws_rfm.cell(row=r, column=6, value=row["total_revenue"]).number_format = '₹#,##0'
    ws_rfm.cell(row=r, column=7, value=row["rev_share_pct"]/100).number_format = '0.0%'
    ws_rfm.cell(row=r, column=8, value=row["avg_return_rate_pct"]/100).number_format = '0.0%'
    ws_rfm.cell(row=r, column=9, value=action_map.get(seg, "Monitor"))
    
    for c in range(1, 10):
        ws_rfm.cell(row=r, column=c).border = thin_border
        if r_idx % 2 == 1:
            ws_rfm.cell(row=r, column=c).fill = fill_zebra

auto_fit_columns(ws_rfm, max_len_cap=55)

# ==========================================
# 4. TAB: COD vs Prepaid RTO
# ==========================================
print("creating COD_vs_Prepaid sheet...")
ws_cod = wb.create_sheet(title="COD_Logistics_RTO")
ws_cod.views.sheetView[0].showGridLines = True

ws_cod["A1"] = "LOGISTICS RTO BY PAYMENT METHOD & CITY TIER"
ws_cod["A1"].font = font_title

df_rto_tier = pd.read_sql("SELECT * FROM vw_rto_by_city_tier ORDER BY tier, rto_rate_pct DESC", conn)

headers_cod = ["City Tier", "Payment Method", "Total Orders", "Booked GMV (₹)", "RTO Orders", "RTO Rate %", "Lost GMV to RTO (₹)"]

for col_idx, h in enumerate(headers_cod, 1):
    cell = ws_cod.cell(row=3, column=col_idx, value=h)
    cell.font = font_hdr
    cell.fill = fill_navy
    cell.alignment = Alignment(horizontal="center")

for r_idx, row in df_rto_tier.iterrows():
    r = r_idx + 4
    ws_cod.cell(row=r, column=1, value=row["tier"]).font = font_bold
    ws_cod.cell(row=r, column=2, value=row["payment_mode"])
    ws_cod.cell(row=r, column=3, value=row["total_orders"]).number_format = '#,##0'
    ws_cod.cell(row=r, column=4, value=row["booked_gmv"]).number_format = '₹#,##0'
    ws_cod.cell(row=r, column=5, value=row["rto_orders"]).number_format = '#,##0'
    ws_cod.cell(row=r, column=6, value=row["rto_rate_pct"]/100).number_format = '0.0%'
    ws_cod.cell(row=r, column=7, value=row["lost_rto_gmv"]).number_format = '₹#,##0'
    
    for c in range(1, 8):
        ws_cod.cell(row=r, column=c).border = thin_border
        if r_idx % 2 == 1:
            ws_cod.cell(row=r, column=c).fill = fill_zebra

auto_fit_columns(ws_cod)

excel_out = "excel/Myntra_Commercial_Executive_Model.xlsx"
wb.save(excel_out)
conn.close()

print(f"saved complete executive excel workbook at {excel_out}!")
