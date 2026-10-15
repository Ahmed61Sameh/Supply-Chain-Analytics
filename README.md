# Supply Chain & Inventory Analytics

An end-to-end analytics project on synthetic supply chain data — raw data cleaned in Python, modeled and analyzed in SQL Server, with 50K+ transactional records across products, suppliers, warehouses, purchase orders, sales orders, and returns.

## Project Pipeline

**1. Raw Data → Python (pandas) Cleaning → SQL Server (SSMS)**

Data was intentionally generated with real-world messiness (mixed date formats, inconsistent casing, nulls, duplicates, negative/impossible values) to simulate a real cleaning workflow rather than analyzing pre-cleaned data.

## Dataset

| Table | Description |
|---|---|
| `products` | Product catalog — category, sub-category, unit cost/price, linked supplier |
| `suppliers` | Supplier master — country, lead time, reliability score |
| `warehouses` | Warehouse master — location, capacity |
| `inventory` | Weekly stock snapshots per product-warehouse — stock on hand, reorder point, safety stock |
| `purchase_orders` | Supplier orders — order/expected/actual delivery dates, quantity ordered vs. received, status |
| `sales_orders` | Customer orders/shipments — order/ship/delivery dates, quantity, status |
| `returns` | Product returns — reason, quantity, linked order |

**Scale:** 80 products, 12 suppliers, 5 warehouses, ~10.6K inventory snapshots, 1.8K purchase orders, ~5.7K sales orders (post-cleaning), 295 returns.

## 1. Data Cleaning (Python / pandas)

Performed table-by-table in Jupyter, with inspection (`.info()`, `.isnull().sum()`, `.duplicated().sum()`, unique-value checks) before every cleaning step.

Key fixes applied:
- **Mixed date formats** parsed and standardized (`pd.to_datetime(..., format="mixed")`) across `inventory`, `purchase_orders`, `sales_orders`, and `returns`
- **Inconsistent categorical casing/whitespace** standardized (e.g., product categories, warehouse names, order status)
- **Impossible values corrected** — negative stock/quantity clipped or corrected, negative supplier lead-time sentinel values treated as missing
- **Duplicate rows removed** across all tables
- **Missing values handled per-column context** — e.g., forward-fill for time-series inventory stock, median imputation for supplier metrics, and deliberate null retention for `actual_delivery_date` / `delivery_date` where the null itself is meaningful (order not yet delivered/cancelled)
- Exported clean CSVs and loaded into SQL Server via SQLAlchemy (`to_sql`)

## 2. SQL Analysis (SQL Server / SSMS)

13 queries answering distinct business questions, using CTEs, window functions (`RANK`, `LAG`, `NTILE`-style cumulative logic, rolling averages), and conditional aggregation:

| Area | Business Questions Answered |
|---|---|
| Inventory & Stock Health | Stockout frequency by product/warehouse, reorder-point breach rate, inventory turnover ratio, ABC product classification by revenue |
| Supplier Performance | Average/max delivery delay by supplier, combined delay + reliability risk scoring, partial-fulfillment rate |
| Warehouse & Fulfillment | On-time fulfillment rate by warehouse, stockout-to-sales risk ratio |
| Sales & Demand | Monthly demand trend (3-month rolling average), top products per category, month-over-month revenue growth |
| Returns & Quality | Return rate by category and reason |

## Key Insights

- **65.6% of purchase orders were only partially fulfilled** by suppliers, with the 3 worst-performing suppliers averaging 6–7 day delivery delays — pointing to supplier reliability, not inventory planning, as the primary stockout risk.
- **Inventory turnover varies 2.3x across categories** (Home & Kitchen highest, Electronics lowest), flagging over-stocked electronics inventory as a working-capital reduction opportunity.
- **ABC revenue classification shows 43.8% of products drive 70% of revenue** — a flatter distribution than typical Pareto patterns, arguing against limiting reorder/safety-stock policies to a narrow "top movers" list.

## Tech Stack

Python (pandas) · SQL Server (T-SQL, SSMS) · SQLAlchemy
