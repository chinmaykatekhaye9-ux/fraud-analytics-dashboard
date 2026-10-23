-- Each query starts with a "-- name: <label>" line. 03_sql_analysis.py runs them all.
-- Table: transactions(txn_id, customer_id, timestamp, ts_epoch, amount,
--                     merchant_category, channel, city, device_id, is_fraud, fraud_type)

-- name: daily_volume
SELECT DATE(timestamp)              AS txn_date,
       COUNT(*)                     AS txn_count,
       ROUND(SUM(amount), 2)        AS total_amount,
       ROUND(AVG(amount), 2)        AS avg_amount
FROM transactions
GROUP BY DATE(timestamp)
ORDER BY txn_date;

-- name: category_summary
SELECT merchant_category,
       COUNT(*)                     AS txn_count,
       ROUND(SUM(amount), 2)        AS total_amount,
       ROUND(AVG(amount), 2)        AS avg_amount
FROM transactions
GROUP BY merchant_category
HAVING COUNT(*) > 100
ORDER BY total_amount DESC;

-- name: customer_spend_profile
-- Typical behaviour per customer (the baseline fraud rules compare against)
SELECT customer_id,
       COUNT(*)                     AS txn_count,
       ROUND(AVG(amount), 2)        AS avg_amount,
       ROUND(MAX(amount), 2)        AS max_amount,
       COUNT(DISTINCT city)         AS cities_used,
       COUNT(DISTINCT device_id)    AS devices_used
FROM transactions
GROUP BY customer_id
ORDER BY max_amount DESC
LIMIT 50;

-- name: velocity_10min
-- WINDOW FUNCTION: how many txns did this customer make in the 10 minutes up to this one?
WITH v AS (
    SELECT txn_id, customer_id, timestamp, amount, is_fraud,
           COUNT(*) OVER (
               PARTITION BY customer_id
               ORDER BY ts_epoch
               RANGE BETWEEN 600 PRECEDING AND CURRENT ROW
           ) AS txns_last_10min
    FROM transactions
)
SELECT * FROM v
WHERE txns_last_10min >= 4
ORDER BY txns_last_10min DESC, timestamp
LIMIT 200;

-- name: city_change_within_2h
-- WINDOW FUNCTION: LAG() looks at the previous txn of the same customer
WITH t AS (
    SELECT txn_id, customer_id, timestamp, ts_epoch, city, amount, is_fraud,
           LAG(city)     OVER (PARTITION BY customer_id ORDER BY ts_epoch) AS prev_city,
           LAG(ts_epoch) OVER (PARTITION BY customer_id ORDER BY ts_epoch) AS prev_epoch
    FROM transactions
)
SELECT txn_id, customer_id, timestamp, prev_city, city,
       ROUND((ts_epoch - prev_epoch) / 60.0, 1) AS minutes_since_prev,
       amount, is_fraud
FROM t
WHERE prev_city IS NOT NULL
  AND city <> prev_city
  AND city <> 'Unknown' AND prev_city <> 'Unknown'
  AND (ts_epoch - prev_epoch) <= 7200
ORDER BY minutes_since_prev
LIMIT 200;

-- name: running_total_per_customer
-- WINDOW FUNCTION: cumulative spend per customer
SELECT customer_id, timestamp, amount,
       ROUND(SUM(amount) OVER (PARTITION BY customer_id ORDER BY ts_epoch), 2) AS running_total,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ts_epoch)           AS txn_number
FROM transactions
ORDER BY customer_id, ts_epoch
LIMIT 100;
