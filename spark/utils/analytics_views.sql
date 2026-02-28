-- ============================================================
-- 1. KPI OVERVIEW: Revenue & Sales Metrics
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_kpi AS
SELECT
    d.year,
    d.month,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    COUNT(f.order_item_sk)              AS total_items_sold,
    SUM(f.price)                        AS total_revenue,
    SUM(f.freight_value)                AS total_freight,
    SUM(f.price + f.freight_value)      AS total_gmv,
    ROUND(AVG(f.price), 2)              AS avg_order_value,
    COUNT(DISTINCT f.customer_sk)       AS unique_customers
FROM dwh.fact_order_items f
JOIN dwh.dim_date d ON f.order_date_sk = d.date_sk
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


-- ============================================================
-- 2. CUSTOMER LIFETIME VALUE (CLV)
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_clv AS
SELECT
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.price)                        AS total_spent,
    ROUND(AVG(f.price), 2)              AS avg_order_value,
    MIN(d.date)                         AS first_order_date,
    MAX(d.date)                         AS last_order_date,
    MAX(d.date) - MIN(d.date)           AS customer_lifespan_days
FROM dwh.fact_order_items f
JOIN dwh.dim_customers c ON f.customer_sk = c.customer_sk
JOIN dwh.dim_date d ON f.order_date_sk = d.date_sk
GROUP BY c.customer_unique_id, c.customer_city, c.customer_state;


-- ============================================================
-- 3. RFM ANALYSIS (Recency, Frequency, Monetary)
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_rfm AS
WITH rfm_raw AS (
    SELECT
        c.customer_unique_id,
        MAX(d.date)                             AS last_order_date,
        COUNT(DISTINCT f.order_id)              AS frequency,
        SUM(f.price)                            AS monetary
    FROM dwh.fact_order_items f
    JOIN dwh.dim_customers c ON f.customer_sk = c.customer_sk
    JOIN dwh.dim_date d ON f.order_date_sk = d.date_sk
    GROUP BY c.customer_unique_id
),
rfm_scored AS (
    SELECT
        customer_unique_id,
        last_order_date,
        frequency,
        ROUND(monetary, 2) AS monetary,
        CURRENT_DATE - last_order_date AS recency_days,
        NTILE(5) OVER (ORDER BY CURRENT_DATE - last_order_date ASC)  AS r_score,
        NTILE(5) OVER (ORDER BY frequency DESC)                       AS f_score,
        NTILE(5) OVER (ORDER BY monetary DESC)                        AS m_score
    FROM rfm_raw
)
SELECT
    customer_unique_id,
    last_order_date,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    r_score + f_score + m_score AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers'
        ELSE 'Potential Loyalists'
    END AS customer_segment
FROM rfm_scored;


-- ============================================================
-- 4. SELLER PERFORMANCE
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_seller_performance AS
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    COUNT(f.order_item_sk)              AS total_items_sold,
    SUM(f.price)                        AS total_revenue,
    ROUND(AVG(f.price), 2)              AS avg_item_price,
    ROUND(AVG(r.review_score), 2)       AS avg_review_score,
    COUNT(r.review_id)                  AS total_reviews
FROM dwh.fact_order_items f
JOIN dwh.dim_sellers s ON f.seller_sk = s.seller_sk
LEFT JOIN dwh.fact_reviews r ON f.order_id = r.order_id
GROUP BY s.seller_id, s.seller_city, s.seller_state;


-- ============================================================
-- 5. PRODUCT INSIGHTS
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_product_insights AS
SELECT
    p.product_id,
    p.product_category_name,
    COUNT(f.order_item_sk)              AS total_sold,
    SUM(f.price)                        AS total_revenue,
    ROUND(AVG(f.price), 2)              AS avg_price,
    ROUND(AVG(r.review_score), 2)       AS avg_review_score,
    COUNT(r.review_id)                  AS total_reviews
FROM dwh.fact_order_items f
JOIN dwh.dim_products p ON f.product_sk = p.product_sk
LEFT JOIN dwh.fact_reviews r ON f.order_id = r.order_id
GROUP BY p.product_id, p.product_category_name;


-- ============================================================
-- 6. PAYMENT ANALYSIS
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_payment_analysis AS
SELECT
    payment_type,
    COUNT(*)                            AS total_transactions,
    SUM(payment_value)                  AS total_value,
    ROUND(AVG(payment_value), 2)        AS avg_value,
    ROUND(AVG(payment_installments), 2) AS avg_installments
FROM dwh.fact_payments
GROUP BY payment_type
ORDER BY total_transactions DESC;


-- ============================================================
-- 7. SALES BY REGION
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_sales_by_region AS
SELECT
    c.customer_state,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    COUNT(DISTINCT f.customer_sk)       AS unique_customers,
    SUM(f.price)                        AS total_revenue,
    ROUND(AVG(f.price), 2)              AS avg_order_value
FROM dwh.fact_order_items f
JOIN dwh.dim_customers c ON f.customer_sk = c.customer_sk
GROUP BY c.customer_state
ORDER BY total_revenue DESC;


-- ============================================================
-- 8. REVIEW ANALYSIS
-- ============================================================
CREATE OR REPLACE VIEW dwh.view_review_analysis AS
SELECT
    review_score,
    COUNT(*)                            AS total_reviews,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM dwh.fact_reviews
GROUP BY review_score
ORDER BY review_score DESC;