# Production DAX Measures Library (25+ Measures)

This library contains 25+ enterprise DAX formulas ready to paste into Power BI Desktop for the Myntra Commercial Analytics dashboard.

---

### Group 1: Base Commercial Volume & Revenue Measures

#### 1. Total Orders Placed
```dax
[Total Orders] = 
COUNTROWS(fact_orders)
```

#### 2. Gross Catalogue GMV (MRP)
```dax
[Gross Catalog GMV] = 
SUM(fact_orders[gross_gmv])
```

#### 3. Total Promotional Discounts
```dax
[Total Discounts] = 
SUM(fact_orders[discount_amount])
```

#### 4. Discount Depth %
```dax
[Discount Depth %] = 
DIVIDE([Total Discounts], [Gross Catalog GMV], 0)
```

#### 5. Net Booked GMV
```dax
[Net Booked GMV] = 
SUM(fact_orders[net_gmv])
```

#### 6. Delivered Orders Count
```dax
[Delivered Orders] = 
CALCULATE(
    COUNTROWS(fact_orders),
    fact_orders[order_status] = "Delivered"
)
```

#### 7. Net Realized GMV (NMV - Delivered Revenue)
```dax
[Net Realized GMV] = 
CALCULATE(
    SUM(fact_orders[net_gmv]),
    fact_orders[order_status] = "Delivered"
)
```

#### 8. Realized Cost of Goods Sold (COGS)
```dax
[Realized COGS] = 
CALCULATE(
    SUM(fact_orders[order_cogs]),
    fact_orders[order_status] = "Delivered"
)
```

#### 9. Gross Profit
```dax
[Gross Profit] = 
[Net Realized GMV] - [Realized COGS]
```

#### 10. Realized Gross Margin %
```dax
[Gross Margin %] = 
DIVIDE([Gross Profit], [Net Realized GMV], 0)
```

---

### Group 2: Operational Leakage & Return Measures

#### 11. Return-to-Origin (RTO) Orders
```dax
[RTO Orders] = 
CALCULATE(
    COUNTROWS(fact_orders),
    fact_orders[order_status] = "RTO"
)
```

#### 12. RTO Rate %
```dax
[RTO Rate %] = 
DIVIDE([RTO Orders], [Total Orders], 0)
```

#### 13. Lost GMV to RTO
```dax
[Lost RTO GMV] = 
CALCULATE(
    SUM(fact_orders[net_gmv]),
    fact_orders[order_status] = "RTO"
)
```

#### 14. Customer Returns Count
```dax
[Customer Returns] = 
CALCULATE(
    COUNTROWS(fact_orders),
    fact_orders[order_status] = "Returned"
)
```

#### 15. Customer Return Rate %
```dax
[Customer Return Rate %] = 
DIVIDE([Customer Returns], [Total Orders], 0)
```

#### 16. Net Realization Rate %
```dax
[Net Realization Rate %] = 
DIVIDE([Net Realized GMV], [Net Booked GMV], 0)
```

#### 17. COD RTO Rate %
```dax
[COD RTO Rate %] = 
DIVIDE(
    CALCULATE([RTO Orders], fact_orders[payment_mode] = "COD"),
    CALCULATE([Total Orders], fact_orders[payment_mode] = "COD"),
    0
)
```

---

### Group 3: Commercial Unit Economics & AOV

#### 18. Booked AOV (Average Order Value)
```dax
[Booked AOV] = 
DIVIDE([Net Booked GMV], [Total Orders], 0)
```

#### 19. Realized AOV
```dax
[Realized AOV] = 
DIVIDE([Net Realized GMV], [Delivered Orders], 0)
```

#### 20. Items Per Order (Basket Depth)
```dax
[Items Per Order] = 
DIVIDE(COUNTROWS(fact_order_items), [Total Orders], 0)
```

---

### Group 4: Time Intelligence (YoY & MoM)

#### 21. Realized GMV Previous Month (MoM)
```dax
[Realized GMV Prior Month] = 
CALCULATE(
    [Net Realized GMV],
    DATEADD(dim_date[date_key], -1, MONTH)
)
```

#### 22. MoM GMV Growth %
```dax
[Realized GMV MoM Growth %] = 
DIVIDE(
    [Net Realized GMV] - [Realized GMV Prior Month],
    [Realized GMV Prior Month],
    0
)
```

#### 23. Realized GMV Same Period Last Year (YoY)
```dax
[Realized GMV YoY] = 
CALCULATE(
    [Net Realized GMV],
    SAMEPERIODLASTYEAR(dim_date[date_key])
)
```

#### 24. YoY GMV Growth %
```dax
[Realized GMV YoY Growth %] = 
DIVIDE(
    [Net Realized GMV] - [Realized GMV YoY],
    [Realized GMV YoY],
    0
)
```

#### 25. Rolling 90-Day Realized Revenue
```dax
[Rolling 90D Realized GMV] = 
CALCULATE(
    [Net Realized GMV],
    DATESINPERIOD(dim_date[date_key], MAX(dim_date[date_key]), -90, DAY)
)
```

---

### Group 5: Customer Retention & Repeat Behavior

#### 26. Repeat Customer Orders
```dax
[Repeat Customer Orders] = 
CALCULATE(
    [Total Orders],
    FILTER(
        VALUES(fact_orders[cust_id]),
        CALCULATE(COUNTROWS(fact_orders)) > 1
    )
)
```

#### 27. Repeat Purchase Rate %
```dax
[Repeat Purchase Rate %] = 
DIVIDE([Repeat Customer Orders], [Total Orders], 0)
```
