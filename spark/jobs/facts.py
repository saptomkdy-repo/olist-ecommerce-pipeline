from pyspark.sql.functions import *

from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import to_postgres

spark = create_spark_session("facts")

# =========================
# Load Dimensions (for Surrogate/Foreign Keys)
# =========================

dim_customers = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_customers", properties=POSTGRES_PROPERTIES
)

dim_products = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_products", properties=POSTGRES_PROPERTIES
)

dim_sellers = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_sellers", properties=POSTGRES_PROPERTIES
)

# =========================
# Fact Order Items
# =========================

items = spark.read.jdbc(
    POSTGRES_URL, "stg.order_items", properties=POSTGRES_PROPERTIES
)

df_orders = spark.read.jdbc(
    POSTGRES_URL, "stg.orders", properties=POSTGRES_PROPERTIES
)

fact_items = (
    items
    .join(dim_products, "product_id")
    .join(dim_sellers, "seller_id")
    .join(df_orders.select("order_id", "customer_id"), "order_id")
    .join(dim_customers, "customer_id")
    .select(
        "order_id",              # degenerate dimension
        "order_item_id",
        "customer_sk",
        "product_sk",
        "seller_sk",
        "price",
        "freight_value"
    )
)

to_postgres(fact_items, "dwh.fact_order_items")

# =========================
# Fact Payments
# =========================

payments = spark.read.jdbc(
    POSTGRES_URL, "stg.order_payments", properties=POSTGRES_PROPERTIES
)

fact_payments = (
    payments
    .join(orders.select("order_id","customer_id"), "order_id")
    .join(dim_customers, "customer_id")
    .select(
        "order_id",
        "customer_sk",
        "payment_type",
        "payment_installments",
        "payment_value"
    )
)

to_postgres(fact_payments, "dwh.fact_payments")

# =========================
# FACT REVIEWS
# =========================

reviews = spark.read.jdbc(
    POSTGRES_URL, "stg.order_reviews", properties=POSTGRES_PROPERTIES
)

fact_reviews = (
    reviews
    .join(orders.select("order_id","customer_id"), "order_id")
    .join(dim_customers, "customer_id")
    .select(
        "order_id",
        "customer_sk",
        "review_score"
    )
)

to_postgres(fact_reviews, "dwh.fact_reviews")
