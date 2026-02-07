
SELECT TOP 10
    p.product_category_name AS Kategori,
    COUNT(oi.order_id) AS Toplam_Satis_Adedi,
    SUM(oi.price) AS Toplam_Ciro
FROM 
    olist_order_items_dataset oi
JOIN 
    olist_products_dataset p ON oi.product_id = p.product_id
GROUP BY 
    p.product_category_name
ORDER BY 
    Toplam_Ciro DESC;