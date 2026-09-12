# scripts/generate_data.py
# generates 50,000+ synthetic transactions for fashion ecommerce

import random
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

os.makedirs("data/raw", exist_ok=True)

print("generating customers...")
cities_tier1 = [("Bengaluru", "Karnataka"), ("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), 
                ("Hyderabad", "Telangana"), ("Pune", "Maharashtra"), ("Chennai", "Tamil Nadu")]
cities_tier2 = [("Jaipur", "Rajasthan"), ("Lucknow", "Uttar Pradesh"), ("Indore", "Madhya Pradesh"),
                ("Chandigarh", "Punjab"), ("Ahmedabad", "Gujarat"), ("Kochi", "Kerala")]
cities_tier3 = [("Varanasi", "Uttar Pradesh"), ("Bhopal", "Madhya Pradesh"), ("Patna", "Bihar"),
                ("Ranchi", "Jharkhand"), ("Guwahati", "Assam"), ("Dehradun", "Uttarakhand")]

first_names_m = ["Aarav", "Rohan", "Rahul", "Aditya", "Vikram", "Kabir", "Arjun", "Kunal", "Amit", "Varun"]
first_names_f = ["Ananya", "Priya", "Sneha", "Pooja", "Riya", "Kavya", "Tanvi", "Neha", "Ishita", "Divya"]
last_names = ["Sharma", "Verma", "Patel", "Mehta", "Singh", "Kumar", "Gupta", "Reddy", "Nair", "Iyer"]

n_cust = 12000
cust_list = []
start_signup = datetime(2023, 6, 1)

for i in range(1, n_cust + 1):
    cid = f"CUST_{i:05d}"
    g = random.choice(["Male", "Female"])
    fn = random.choice(first_names_m if g == "Male" else first_names_f)
    ln = random.choice(last_names)
    name = f"{fn} {ln}"
    
    r_tier = random.random()
    if r_tier < 0.45:
        tier = "Tier 1"
        city, state = random.choice(cities_tier1)
    elif r_tier < 0.80:
        tier = "Tier 2"
        city, state = random.choice(cities_tier2)
    else:
        tier = "Tier 3"
        city, state = random.choice(cities_tier3)
        
    signup = start_signup + timedelta(days=random.randint(0, 550))
    cust_list.append({
        "cust_id": cid,
        "name": name,
        "gender": g,
        "city": city,
        "state": state,
        "tier": tier,
        "signup_date": signup.strftime("%Y-%m-%d")
    })

df_cust = pd.DataFrame(cust_list)
df_cust.to_csv("data/raw/customers.csv", index=False)
print(f"saved {len(df_cust)} customers.")

# product catalog
print("generating catalog...")
brands_by_cat = {
    "Men Western": ["Roadster", "HRX", "Levi's", "Wrangler", "Tommy Hilfiger"],
    "Women Western": ["DressBerry", "Mast & Harbour", "Mango", "Zara", "ONLY"],
    "Women Ethnic": ["Anouk", "Biba", "W for Woman", "Libas", "FabIndia"],
    "Footwear": ["Puma", "Nike", "Red Tape", "HRX", "Bata"],
    "Beauty & Grooming": ["Maybelline", "Lakme", "Mamaearth", "Beardo", "Minimalist"],
    "Accessories": ["Fastrack", "Fossil", "Wildcraft", "Baggit", "Skybags"]
}

base_prices = {
    "Men Western": (899, 3299),
    "Women Western": (799, 2999),
    "Women Ethnic": (1199, 4499),
    "Footwear": (1499, 5999),
    "Beauty & Grooming": (299, 1299),
    "Accessories": (499, 2499)
}

prod_list = []
pid = 1
for cat, brands in brands_by_cat.items():
    p_min, p_max = base_prices[cat]
    for b in brands:
        for item_idx in range(1, 7):
            mrp = round(random.uniform(p_min, p_max), -1)
            cost = round(mrp * random.uniform(0.42, 0.55), 2)
            prod_list.append({
                "prod_id": f"PRD_{pid:04d}",
                "prod_name": f"{b} {cat} Series {item_idx}",
                "category": cat,
                "brand": b,
                "mrp": mrp,
                "cost_price": cost
            })
            pid += 1

df_prod = pd.DataFrame(prod_list)
df_prod.to_csv("data/raw/products.csv", index=False)
print(f"saved {len(df_prod)} products.")

# order generation (52,000 orders)
print("generating 52,000 orders spanning 2024 to 2025...")
n_orders = 52000
start_order_date = datetime(2024, 1, 1)
end_order_date = datetime(2025, 12, 31)
total_days = (end_order_date - start_order_date).days

# seasonal multipliers: June (EORS Summer), Oct (Diwali / BFF), Dec (EORS Winter)
def get_season_weight(dt):
    m = dt.month
    if m in [6, 12]:
        return 1.8  # EORS surge
    elif m == 10:
        return 1.9  # Festive Diwali surge
    elif m in [1, 7]:
        return 1.2
    return 1.0

# assign purchase propensities across customers (Pareto: top 20% buy 60% orders)
cust_ids = df_cust["cust_id"].values
cust_weights = np.random.pareto(a=1.5, size=len(cust_ids))
cust_weights /= cust_weights.sum()

orders_list = []
order_items_list = []
returns_list = []

payment_modes = ["UPI", "Credit Card", "Debit Card", "COD"]
pay_weights = [0.42, 0.20, 0.08, 0.30]

return_reasons_pool = [
    ("Size / Fit Issue", 0.42),
    ("Quality Not as Expected", 0.22),
    ("Defective / Damaged Item", 0.12),
    ("Late Delivery", 0.09),
    ("Found Better Price Elsewhere", 0.05),
    ("Customer Refused at Doorstep", 0.10)
]

item_id_counter = 1

# precalculate days weights
day_weights = []
for d in range(total_days + 1):
    curr_dt = start_order_date + timedelta(days=d)
    day_weights.append(get_season_weight(curr_dt))
day_weights = np.array(day_weights) / sum(day_weights)

chosen_days = np.random.choice(total_days + 1, size=n_orders, p=day_weights)
chosen_custs = np.random.choice(cust_ids, size=n_orders, p=cust_weights)

# dictionary to get cust tier quickly
cust_tier_map = dict(zip(df_cust["cust_id"], df_cust["tier"]))
prod_lookup = df_prod.set_index("prod_id").to_dict(orient="index")
prod_ids = list(prod_lookup.keys())

for idx in range(n_orders):
    oid = f"ORD_{idx+1:06d}"
    cid = chosen_custs[idx]
    c_tier = cust_tier_map[cid]
    
    odt = start_order_date + timedelta(days=int(chosen_days[idx]))
    
    # flag sale event
    is_eors = 1 if odt.month in [6, 10, 12] else 0
    sale_tag = "EORS / BFF Event" if is_eors else "BAU Regular"
    
    # COD is higher in Tier 2/3
    if c_tier == "Tier 3":
        pay_mode = np.random.choice(payment_modes, p=[0.25, 0.10, 0.05, 0.60])
    elif c_tier == "Tier 2":
        pay_mode = np.random.choice(payment_modes, p=[0.38, 0.15, 0.07, 0.40])
    else:
        pay_mode = np.random.choice(payment_modes, p=[0.50, 0.28, 0.07, 0.15])
        
    # number of items in order: 1 (65%), 2 (25%), 3 (10%)
    n_items = np.random.choice([1, 2, 3], p=[0.65, 0.25, 0.10])
    
    order_gross = 0.0
    order_discount = 0.0
    order_cogs = 0.0
    
    # track categories in this order to check footwear/ethnic sizing returns
    cats_in_order = []
    
    for _ in range(n_items):
        pr_id = random.choice(prod_ids)
        pr_info = prod_lookup[pr_id]
        cats_in_order.append(pr_info["category"])
        
        # discount: EORS has deeper discounts (35-65%), BAU (15-40%)
        if is_eors:
            disc_pct = round(random.uniform(0.35, 0.60), 2)
        else:
            disc_pct = round(random.uniform(0.12, 0.38), 2)
            
        qty = 1
        mrp = pr_info["mrp"]
        item_disc = round(mrp * disc_pct, 2)
        selling_price = round(mrp - item_disc, 2)
        cogs = pr_info["cost_price"]
        
        order_gross += mrp
        order_discount += item_disc
        order_cogs += cogs
        
        order_items_list.append({
            "item_id": f"ITEM_{item_id_counter:07d}",
            "order_id": oid,
            "prod_id": pr_id,
            "qty": qty,
            "mrp": mrp,
            "discount_amount": item_disc,
            "selling_price": selling_price,
            "cogs": cogs
        })
        item_id_counter += 1
        
    net_gmv = round(order_gross - order_discount, 2)
    
    # order fulfillment status:
    # Cancellation before dispatch: ~6%
    # COD has high RTO (~22%), Prepaid has low RTO (~4%)
    # Delivered has normal customer returns (~18% in apparel/footwear, ~8% in beauty/accessories)
    r_stat = random.random()
    if r_stat < 0.06:
        status = "Cancelled"
    else:
        # check RTO risk
        is_cod = (pay_mode == "COD")
        rto_prob = 0.22 if is_cod else 0.045
        if random.random() < rto_prob:
            status = "RTO"
        else:
            # check customer return risk after delivery
            has_fit_sensitive = any(c in ["Footwear", "Women Ethnic", "Women Western"] for c in cats_in_order)
            ret_prob = 0.22 if has_fit_sensitive else 0.09
            if random.random() < ret_prob:
                status = "Returned"
            else:
                status = "Delivered"
                
    # delivery date
    deliv_days = random.randint(2, 6)
    deliv_dt = (odt + timedelta(days=deliv_days)).strftime("%Y-%m-%d") if status in ["Delivered", "Returned"] else None
    
    orders_list.append({
        "order_id": oid,
        "cust_id": cid,
        "order_date": odt.strftime("%Y-%m-%d"),
        "delivery_date": deliv_dt,
        "order_status": status,
        "payment_mode": pay_mode,
        "sale_event": sale_tag,
        "gross_gmv": round(order_gross, 2),
        "discount_amount": round(order_discount, 2),
        "net_gmv": net_gmv,
        "order_cogs": round(order_cogs, 2)
    })
    
    # if returned or RTO, record in return reasons
    if status in ["Returned", "RTO"]:
        if status == "RTO":
            reason = "Customer Refused at Doorstep"
        else:
            reasons, r_probs = zip(*return_reasons_pool[:-1]) # exclude doorstep refusal
            norm_probs = np.array(r_probs) / sum(r_probs)
            reason = np.random.choice(reasons, p=norm_probs)
            
        returns_list.append({
            "order_id": oid,
            "return_type": "RTO (Undelivered)" if status == "RTO" else "Customer Return",
            "return_reason": reason,
            "refund_amount": net_gmv
        })

df_orders = pd.DataFrame(orders_list)
df_items = pd.DataFrame(order_items_list)
df_returns = pd.DataFrame(returns_list)

df_orders.to_csv("data/raw/orders.csv", index=False)
df_items.to_csv("data/raw/order_items.csv", index=False)
df_returns.to_csv("data/raw/return_cancellations.csv", index=False)

print(f"saved {len(df_orders)} orders.")
print(f"saved {len(df_items)} order items.")
print(f"saved {len(df_returns)} returns/cancellations.")
print(f"cod orders count: {len(df_orders[df_orders['payment_mode'] == 'COD'])}, rto count: {len(df_orders[df_orders['order_status'] == 'RTO'])}")
print("data generation finished successfully.")
