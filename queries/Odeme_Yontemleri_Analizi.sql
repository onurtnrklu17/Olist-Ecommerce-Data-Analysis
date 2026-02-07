
SELECT 
    payment_type AS Odeme_Yontemi,
    COUNT(order_id) AS Islem_Sayisi,
    AVG(payment_value) AS Ortalama_Sepet_Tutari,
    SUM(payment_value) AS Toplam_Hacim
FROM 
    olist_order_payments_dataset
GROUP BY 
    payment_type
ORDER BY 
    Islem_Sayisi DESC;