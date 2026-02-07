
WITH SaticiCiro AS (
    SELECT 
        s.seller_city AS Sehir,
        s.seller_id AS Satici_ID,
        SUM(oi.price) AS Ciro
    FROM 
        olist_order_items_dataset oi
    JOIN 
        olist_sellers_dataset s ON oi.seller_id = s.seller_id
    GROUP BY 
        s.seller_city, s.seller_id
),
SiraliSaticilar AS (
    SELECT 
        Sehir,
        Satici_ID,
        Ciro,
        ROW_NUMBER() OVER (PARTITION BY Sehir ORDER BY Ciro DESC) as Sira
    FROM 
        SaticiCiro
)
SELECT * FROM SiraliSaticilar 
WHERE Sira = 1
ORDER BY Ciro DESC;