import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
folder = r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main" + "\\"

products  = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\products--.csv")
suppliers = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\suppliers-.csv")
sales     = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\sales_orders-.csv")
inventory = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\Clean inventory.csv")
orders    = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\purchase_orders--.csv")
returns   = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\returns--.csv")
warehouses = pd.read_csv(r"C:\Users\LOQ\OneDrive\Desktop\Supply-Chain-Inventory-Analytics-main\warehouses.csv")

sales["Revenue Amount"]  = sales["Revenue Amount"].str.replace(",", "").astype(float)
returns["Return Amount"] = returns["Return Amount"].str.replace(",", "").astype(float)

# Q1أعلى تصنيف في الإيراد
sales = sales.merge(products[["product_id", "category"]], on="product_id")
q1 = sales[sales.status != "Cancelled"].groupby("category")["Revenue Amount"].sum().sort_values(ascending=False) / 1e6

# Q2حالة الأوردرات في كل مخزن
sales = sales.merge(warehouses[["warehouse_id", "city"]], on="warehouse_id")
q2 = pd.crosstab(sales["city"], sales["status"], normalize="index") * 100

# Q3نسبة المخزون تحت الـ reorder point
inventory = inventory.merge(warehouses[["warehouse_id", "city"]], on="warehouse_id")
inventory["below"] = inventory["Reorder Status"] == "Below Reorder Point"
q3 = inventory.groupby("city")["below"].mean().mul(100).sort_values()

# Q4 reliability المورد vs التاخير في الميعاد
orders["expected"] = pd.to_datetime(orders["new expected_delivery_date"], dayfirst=True)
orders["actual"]   = pd.to_datetime(orders["new actual_delivery_date"], dayfirst=True)
orders = orders.dropna(subset=["actual"])
orders["on_time"] = orders["actual"] <= orders["expected"]
q4 = orders.groupby("supplier_id")["on_time"].mean().mul(100).reset_index(name="on_time_pct")
q4 = q4.merge(suppliers[["supplier_id", "reliability_score"]], on="supplier_id")

# سبب المرتجعات
q5 = returns.groupby("reason")["Return Amount"].sum().sort_values() / 1e3

def chart1(ax):
    q1.plot(kind="bar", ax=ax, color="#2563EB")
    ax.set_title("Q1: Revenue by category (M)")
    ax.tick_params(axis="x", rotation=20)
    ax.set_xlabel("")

def chart2(ax):
    q2[["Delivered", "Delayed", "Cancelled"]].plot(kind="bar", stacked=True, ax=ax,
                                                   color=["#16A34A", "#F59E0B", "#DC2626"])
    ax.set_title("Q2: Order status by warehouse (%)")
    ax.tick_params(axis="x", rotation=20)
    ax.set_xlabel("")

def chart3(ax):
    q3.plot(kind="bar", ax=ax, color="#7C3AED")
    ax.set_title("Q3: % stock below reorder point")
    ax.tick_params(axis="x", rotation=20)
    ax.set_xlabel("")

def chart4(ax):
    sns.regplot(data=q4, x="reliability_score", y="on_time_pct", ax=ax, color="#0F172A")
    ax.set_title("Q4: Supplier reliability vs on-time POs (%)")

def chart5(ax):
    q5.plot(kind="barh", ax=ax, color="#DC2626")
    ax.set_title("Q5: Returned value by reason (K)")
    ax.set_ylabel("")

charts = {"Q1_revenue": chart1, "Q2_warehouses": chart2, "Q3_stock": chart3,
          "Q4_suppliers": chart4, "Q5_returns": chart5}

for name, chart in charts.items():
    fig, ax = plt.subplots(figsize=(8, 5))
    chart(ax)
    plt.tight_layout()
    plt.savefig(folder + name + ".png", dpi=120)
    plt.close()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Supply Chain Dashboard", fontsize=20, fontweight="bold")

chart1(axes[0, 0])
chart2(axes[0, 1])
chart3(axes[0, 2])
chart4(axes[1, 0])
chart5(axes[1, 1])
axes[1, 2].axis("off")    

plt.tight_layout()
plt.savefig(folder + "dashboard.png", dpi=120)
plt.show()