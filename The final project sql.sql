use sypply_chain;
#Q: Which suppliers are highly relied upon despite having lower reliability scores
SELECT
    s.supplier_id,
    s.supplier_name,
    s.reliability_score,
    COUNT(po.po_id) AS total_purchase_orders
FROM suppliers s
JOIN purchase_orders po
    ON s.supplier_id = po.supplier_id
GROUP BY
    s.supplier_id,
    s.supplier_name,
    s.reliability_score
ORDER BY
    total_purchase_orders DESC,
    reliability_score ASC;

##########################
#Q: Which warehouses generate the highest operational issues
SELECT
    warehouse_id,
    COUNT(*) AS total_orders,
    SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) AS delayed_orders,
    ROUND(
        SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END)*100.0/
        COUNT(*)
    ,2) AS delay_percentage
FROM sales_orders
GROUP BY warehouse_id
ORDER BY delay_percentage DESC;

###############################
#Q: Which products have the highest return frequency relative to sales
SELECT
    p.product_id,
    COUNT(DISTINCT r.return_id) AS total_returns,
    SUM(s.quantity) AS total_sold
FROM products p
LEFT JOIN sales_orders s
    ON p.product_id=s.product_id
LEFT JOIN returns r
    ON p.product_id=r.product_id
GROUP BY p.product_id
ORDER BY total_returns DESC;

###########################
#Q: Which categories contribute most to total revenue
SELECT
    p.category,
    SUM(s.`Revenue Amount`) AS total_revenue
FROM sales_orders s
JOIN products p
    ON p.product_id=s.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

#########################
#Q: Which customers generate the highest demand	
SELECT
    customer_id,
    SUM(quantity) AS total_quantity,
    SUM(`Revenue Amount`) AS total_revenue
FROM sales_orders
GROUP BY customer_id
ORDER BY total_revenue DESC;

##########################
#Which suppliers consistently under-deliver ordered quantities
SELECT
    s.supplier_name,
    COUNT(*) AS total_orders,
    SUM(
        CASE
           WHEN po.quantity_received < po.quantity_ordered
           THEN 1
           ELSE 0
        END
    ) AS under_delivered_orders
FROM suppliers s
JOIN purchase_orders po
    ON s.supplier_id=po.supplier_id
GROUP BY s.supplier_name
ORDER BY under_delivered_orders DESC;

#######################
#Which products sell faster than inventory availability
WITH inventory_summary AS
(
    SELECT
        product_id,
        AVG(stock_on_hand) AS avg_stock
    FROM inventory
    GROUP BY product_id
),

sales_summary AS
(
    SELECT
        product_id,
        SUM(quantity) AS total_sales
    FROM sales_orders
    GROUP BY product_id
)

SELECT
    p.product_id,
    p.category,
    ROUND(i.avg_stock,2) AS avg_stock,
    s.total_sales,
    ROUND(
        s.total_sales / NULLIF(i.avg_stock,0),
        2
    ) AS turnover_ratio
FROM products p
JOIN inventory_summary i
    ON p.product_id=i.product_id
JOIN sales_summary s
    ON p.product_id=s.product_id
ORDER BY turnover_ratio DESC;

############################
#What are the most common return causes
SELECT
    reason,
    COUNT(*) AS total_returns
FROM returns
GROUP BY reason
ORDER BY total_returns DESC;

########################
#Q: What percentage of total revenue is lost due to returns
SELECT
    SUM(r.`Return Amount`) AS return_value,
    (
      SELECT SUM(`Revenue Amount`)
      FROM sales_orders
    ) AS total_revenue,
    ROUND(
       SUM(r.`Return Amount`) * 100.0 /
       (
          SELECT SUM(`Revenue Amount`)
          FROM sales_orders
       )
    ,2) AS loss_percentage
FROM returns r;

###################
#Which products generate the highest revenue
SELECT
    so.product_id,
    p.sub_category, 
    SUM(so.`Revenue Amount`) AS total_revenue
FROM sales_orders so
JOIN products p
    ON so.product_id = p.product_id
GROUP BY
    so.product_id,
    p.sub_category
ORDER BY
    total_revenue DESC
LIMIT 10;
