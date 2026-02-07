
SELECT TOP 20
    c.customer_state AS Eyalet,
    AVG(DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date)) AS Ortalama_Teslimat_Gunu
FROM 
    olist_orders_dataset o
JOIN 
    olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE 
    o.order_status = 'delivered'
GROUP BY 
    c.customer_state
ORDER BY 
    Ortalama_Teslimat_Gunu ASC;