-- SQLite. Executado por: python -m scripts.sql_report
-- A tabela orders tem UMA linha por pedido; não multiplicar preço por joins de itens.
SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
       COUNT(*) AS orders, ROUND(AVG(late), 4) AS late_rate,
       ROUND(SUM(price), 2) AS product_value
FROM orders GROUP BY month ORDER BY month;

SELECT customer_state, COUNT(*) AS orders, SUM(late) AS late_orders,
       ROUND(AVG(late), 4) AS late_rate,
       ROUND(AVG(delivery_days), 2) AS mean_delivery_days
FROM orders GROUP BY customer_state HAVING COUNT(*) >= 100
ORDER BY late_rate DESC;

SELECT category, COUNT(*) AS orders, ROUND(AVG(late), 4) AS late_rate
FROM orders GROUP BY category HAVING COUNT(*) >= 100
ORDER BY late_rate DESC LIMIT 15;
