-- ============================================================
-- 1. KPI OVERVIEW: Revenue & Sales Metrics
-- ============================================================
DROP VIEW IF EXISTS dwh.view_kpi CASCADE;
CREATE OR REPLACE VIEW dwh.view_kpi AS
WITH order_level AS (
    SELECT
        f.order_id,
        f.customer_sk,
        d.year,
        d.month,
        SUM(f.price) AS order_revenue,
        SUM(f.freight_value) AS order_freight
    FROM dwh.fact_order_items f
    JOIN dwh.dim_date d ON f.order_date_sk = d.date_sk
    GROUP BY f.order_id, f.customer_sk, d.year, d.month
)
SELECT
    year,
    month,
    COUNT(order_id)                          AS total_orders,
    SUM(order_revenue)                       AS total_revenue,
    SUM(order_freight)                       AS total_freight,
    SUM(order_revenue + order_freight)       AS total_gmv,
    ROUND(AVG(order_revenue), 4)             AS avg_order_value,
    COUNT(DISTINCT customer_sk)              AS unique_customers
FROM order_level
GROUP BY year, month
ORDER BY year, month;


-- ============================================================
-- 2. CUSTOMER LIFETIME VALUE (CLV)
-- ============================================================
DROP VIEW IF EXISTS dwh.view_clv CASCADE;
CREATE OR REPLACE VIEW dwh.view_clv AS
WITH order_level AS (
    SELECT
        f.order_id,
        f.customer_sk,
        SUM(f.price) AS order_revenue,
        MIN(d.date) AS order_date
    FROM dwh.fact_order_items f
    JOIN dwh.dim_date d ON f.order_date_sk = d.date_sk
    GROUP BY f.order_id, f.customer_sk
)
SELECT
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    COUNT(order_id)                          AS total_orders,
    SUM(order_revenue)                       AS total_spent,
    ROUND(AVG(order_revenue), 4)             AS avg_order_value,
    MIN(order_date)                          AS first_order_date,
    MAX(order_date)                          AS last_order_date,
    MAX(order_date) - MIN(order_date)        AS customer_lifespan_days
FROM order_level o
JOIN dwh.dim_customers c ON o.customer_sk = c.customer_sk
GROUP BY c.customer_unique_id, c.customer_city, c.customer_state;


-- ============================================================
-- 3. RFM ANALYSIS (Recency, Frequency, Monetary)
-- ============================================================
DROP VIEW IF EXISTS dwh.view_rfm CASCADE;
CREATE OR REPLACE VIEW dwh.view_rfm AS
WITH order_level AS (
    SELECT
        f.order_id,
        f.customer_sk,
        SUM(f.price) AS order_revenue,
        MAX(d.date) AS order_date
    FROM dwh.fact_order_items f
    JOIN dwh.dim_date d ON f.order_date_sk = d.date_sk
    GROUP BY f.order_id, f.customer_sk
),
rfm_raw AS (
    SELECT
        c.customer_unique_id,
        MAX(order_date) AS last_order_date,
        COUNT(order_id) AS frequency,
        SUM(order_revenue) AS monetary
    FROM order_level o
    JOIN dwh.dim_customers c ON o.customer_sk = c.customer_sk
    GROUP BY c.customer_unique_id
),
rel_current_date AS (
    SELECT MAX(last_order_date) AS relative_current_date
    FROM rfm_raw
),
rfm_scored AS (
    SELECT
        r.*,
        rel.relative_current_date - r.last_order_date AS recency_days,
        NTILE(5) OVER (ORDER BY rel.relative_current_date - r.last_order_date DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_raw r
    CROSS JOIN rel_current_date rel
)
SELECT
    *,
    r_score + f_score + m_score AS rfm_total,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost Customers'
        ELSE 'Potential Loyalists'
    END AS customer_segment
FROM rfm_scored;


-- ============================================================
-- 4. SELLER PERFORMANCE
-- ============================================================
DROP VIEW IF EXISTS dwh.view_seller_performance CASCADE;
CREATE OR REPLACE VIEW dwh.view_seller_performance AS
WITH seller_order AS (
    SELECT
        f.order_id,
        f.seller_sk,
        SUM(f.price) AS order_revenue,
        COUNT(f.order_item_sk) AS items_sold
    FROM dwh.fact_order_items f
    GROUP BY f.order_id, f.seller_sk
),
review_per_order AS (
    SELECT
        order_id,
        MAX(review_score) AS review_score
    FROM dwh.fact_reviews
    GROUP BY order_id
)
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT so.order_id) AS total_orders,
    SUM(so.items_sold) AS total_items_sold,
    SUM(so.order_revenue) AS total_revenue,
    ROUND(AVG(so.order_revenue), 2) AS avg_order_value,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    COUNT(r.order_id) AS total_reviews
FROM seller_order so
JOIN dwh.dim_sellers s ON so.seller_sk = s.seller_sk
LEFT JOIN review_per_order r ON so.order_id = r.order_id
GROUP BY s.seller_id, s.seller_city, s.seller_state;


-- ============================================================
-- 5. PRODUCT INSIGHTS
-- ============================================================
DROP VIEW IF EXISTS dwh.view_product_insights CASCADE;
CREATE OR REPLACE VIEW dwh.view_product_insights AS
WITH product_sales AS (
    SELECT
        f.order_id,
        f.product_sk,
        SUM(f.price) AS revenue,
        COUNT(f.order_item_sk) AS items_sold
    FROM dwh.fact_order_items f
    GROUP BY f.order_id, f.product_sk
),
review_per_order AS (
    SELECT
        order_id,
        MAX(review_score) AS review_score
    FROM dwh.fact_reviews
    GROUP BY order_id
)
SELECT
    p.product_id,
    p.product_category_name,
    SUM(ps.items_sold) AS total_sold,
    SUM(ps.revenue) AS total_revenue,
    ROUND(AVG(ps.revenue), 2) AS avg_revenue_per_order,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    COUNT(r.order_id) AS total_reviews
FROM product_sales ps
JOIN dwh.dim_products p ON ps.product_sk = p.product_sk
LEFT JOIN review_per_order r ON ps.order_id = r.order_id
GROUP BY p.product_id, p.product_category_name;

-- ============================================================
-- 6. PAYMENT ANALYSIS
-- ============================================================
DROP VIEW IF EXISTS dwh.view_payment_analysis CASCADE;
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
DROP VIEW IF EXISTS dwh.view_sales_by_region CASCADE;
CREATE OR REPLACE VIEW dwh.view_sales_by_region AS
WITH order_level AS (
    SELECT
        f.order_id,
        f.customer_sk,
        SUM(f.price) AS order_revenue
    FROM dwh.fact_order_items f
    GROUP BY f.order_id, f.customer_sk
)
SELECT
    c.customer_state,
    COUNT(o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_sk) AS unique_customers,
    SUM(o.order_revenue) AS total_revenue,
    ROUND(AVG(o.order_revenue), 2) AS avg_order_value
FROM order_level o
JOIN dwh.dim_customers c ON o.customer_sk = c.customer_sk
GROUP BY c.customer_state
ORDER BY total_revenue DESC;


-- ============================================================
-- 8. REVIEW ANALYSIS
-- ============================================================
DROP VIEW IF EXISTS dwh.view_review_analysis CASCADE;
CREATE OR REPLACE VIEW dwh.view_review_analysis AS
SELECT
    review_score,
    COUNT(*)                            AS total_reviews,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM dwh.fact_reviews
GROUP BY review_score
ORDER BY review_score DESC;