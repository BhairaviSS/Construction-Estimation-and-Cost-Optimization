"""
M.Tech Construction Cost Estimation – reproducible baseline model
Case: G+5 academic/institutional building, Kanpur
IMPORTANT: rates and several quantities are study assumptions; replace with
approved drawings, BBS, current quotations/UP SOR and detailed MEP schedules.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------- Inputs --------------------
AREA = 3600.0
RCC_QTY = 977.825
STEEL_QTY = RCC_QTY * 0.110

items = [
("Earthwork","Excavation",319.2,254.15),
("Foundation","PCC M10",12.0,6705.30),
("RCC","RCC M25",RCC_QTY,8522.22),
("RCC","Formwork",15000.0,900.00),
("Reinforcement","Fe500D steel",STEEL_QTY,81891.18),
("Masonry","Clay brick/equivalent masonry",891.6,8814.23),
("Plastering","Internal plaster",13440.0,286.60),
("Plastering","External plaster",1920.0,365.00),
("Flooring","Vitrified flooring",3600.0,1211.28),
("Flooring","Skirting",1200.0,140.00),
("Doors/windows","Doors",189.0,12000.00),
("Doors/windows","Windows",225.0,9000.00),
("Waterproofing","Waterproofing",1200.0,735.42),
("Painting","Internal painting",13440.0,221.71),
("Painting","External painting",1920.0,250.00),
("External works","Paving",1000.0,900.00),
("External works","Storm-water drain",250.0,1800.00),
("Services","Plumbing/sanitary",1.0,3200000.00),
("Services","Electrical",1.0,4800000.00),
("External works","Site development",1.0,1500000.00),
]
boq = pd.DataFrame(items, columns=["Group","Item","Quantity","Rate"])
boq["Amount"] = boq["Quantity"] * boq["Rate"]

# -------------------- Cost model --------------------
direct = boq["Amount"].sum()
overhead = 0.08 * direct
contingency = 0.03 * direct
profit = 0.10 * (direct + overhead + contingency)
pre_gst = direct + overhead + contingency + profit
gst = 0.18 * pre_gst
total = pre_gst + gst

print(f"Direct cost        : ₹{direct:,.0f}")
print(f"Overhead           : ₹{overhead:,.0f}")
print(f"Contingency        : ₹{contingency:,.0f}")
print(f"Profit             : ₹{profit:,.0f}")
print(f"Pre-GST cost       : ₹{pre_gst:,.0f}")
print(f"GST (illustrative) : ₹{gst:,.0f}")
print(f"Total incl. GST    : ₹{total:,.0f}")
print(f"Cost per m²        : ₹{total/AREA:,.0f}/m²")

# -------------------- Cost drivers --------------------
group = boq.groupby("Group")["Amount"].sum().sort_values(ascending=False)
print("\nTop cost components:")
print(group.head(5))

plt.figure(figsize=(9,5))
group.plot(kind="bar")
plt.ylabel("Direct cost (₹)")
plt.title("Direct Cost by Construction Component")
plt.tight_layout()
plt.show()

# -------------------- Sensitivity --------------------
components = {
    "Steel price": 0.13 * direct,
    "Labour cost": 0.25 * direct,
    "Cement/concrete input": 0.12 * direct,
    "Project duration / preliminaries": overhead,
}

rows=[]
for name, base in components.items():
    for change in [-15,-10,-5,0,5,10,15]:
        delta = base * change/100
        if name == "Project duration / preliminaries":
            new_direct = direct
            new_oh = overhead + delta
        else:
            new_direct = direct + delta
            new_oh = overhead
        new_pre = new_direct + new_oh + contingency + profit
        new_total = new_pre * 1.18
        rows.append([name, change, new_total, (new_total-total)/total*100])

sens = pd.DataFrame(rows, columns=["Variable","Change_%","Total_cost","Total_change_%"])
print("\nSensitivity table:")
print(sens.to_string(index=False))

# -------------------- 18-month cash flow --------------------
weights = np.array([0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.10,
                    0.10,0.10,0.09,0.08,0.06,0.05,0.04,0.02,0.02])
weights = weights / weights.sum()
cash = pd.DataFrame({
    "Month": np.arange(1,19),
    "Monthly_cost": pre_gst*weights
})
cash["Cumulative_cost"] = cash["Monthly_cost"].cumsum()
cash["Cumulative_%"] = 100*cash["Cumulative_cost"]/pre_gst

plt.figure(figsize=(9,5))
plt.plot(cash["Month"], cash["Cumulative_%"], marker="o")
plt.xlabel("Month")
plt.ylabel("Cumulative expenditure (%)")
plt.title("18-Month S-Curve")
plt.grid(True, alpha=0.25)
plt.tight_layout()
plt.show()

# Export reproducible tables
boq.to_csv("BOQ_reproducible.csv", index=False)
sens.to_csv("Sensitivity_reproducible.csv", index=False)
cash.to_csv("Cashflow_reproducible.csv", index=False)
