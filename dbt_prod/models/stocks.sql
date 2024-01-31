WITH date_cte AS (
    SELECT
        FORMAT_TIMESTAMP('%Y%m%d', TIMESTAMP_SECONDS(timestamp)) AS formatted_date,
        FORMAT_TIMESTAMP('%H:%M:%S', TIMESTAMP_SECONDS(timestamp), 'America/New_York') AS formatted_time,
        DATETIME(TIMESTAMP_SECONDS(timestamp), 'America/New_York') AS new_york_time,
        ROUND(price, 2) AS price
    FROM 
        `premier_league_dataset.public_stocks`
    WHERE 
        DATE(TIMESTAMP_SECONDS(timestamp), 'America/New_York') IN (DATE_SUB(DATE(CURRENT_DATETIME('America/New_York')), INTERVAL 1 DAY))
)  

SELECT formatted_time, new_york_time, price
FROM date_cte
WHERE formatted_time < '16:00:00'
ORDER BY date_cte.new_york_time DESC