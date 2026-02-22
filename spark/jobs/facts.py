from pyspark.sql.functions import *

from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import to_postgres

spark = create_spark_session("facts")

# =========================
# Load Dimensions (for Surrogate/Foreign Keys)
# =========================

# dim_geolocation = spark.read.jdbc(
#     POSTGRES_URL, "dwh.dim_geolocation", properties=POSTGRES_PROPERTIES
# )

dim_customers = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_customers", properties=POSTGRES_PROPERTIES
)

dim_products = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_products", properties=POSTGRES_PROPERTIES
)

dim_sellers = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_sellers", properties=POSTGRES_PROPERTIES
)

dim_date = spark.read.jdbc(
    POSTGRES_URL, "dwh.dim_date", properties=POSTGRES_PROPERTIES
)

# =========================
# Fact Order Items
# =========================

df_order_items = spark.read.jdbc(
    POSTGRES_URL, "stg.order_items", properties=POSTGRES_PROPERTIES
)

df_orders = spark.read.jdbc(
    POSTGRES_URL, "stg.orders", properties=POSTGRES_PROPERTIES
)

fact_items = (
    df_order_items
    .join(dim_products, "product_id", "left")
    .join(dim_sellers, "seller_id", "left")
    .join(df_orders.select("order_id", "customer_id", "order_purchase_timestamp"), "order_id")
    .join(dim_customers, "customer_id", "left")
    .select(
        "order_id",              # degenerate dimension
        "order_item_id",
        "customer_sk",
        "product_sk",
        "seller_sk",
        "price",
        "freight_value",
        "order_purchase_timestamp",
        "shipping_limit_date"
    )
    .withColumn("order_item_sk",
            sha2(concat_ws("||", "order_id", "order_item_id"), 256)
    )
    .withColumn("order_date_sk",
            date_format("order_purchase_timestamp","yyyyMMdd").cast("int")
    )
    .withColumn("shipping_limit_date_sk",
            date_format("shipping_limit_date","yyyyMMdd").cast("int")
    )
)

to_postgres(fact_items, "dwh.fact_order_items")

# =========================
# Fact Payments
# =========================

df_payments = spark.read.jdbc(
    POSTGRES_URL, "stg.order_payments", properties=POSTGRES_PROPERTIES
)

fact_payments = (
    df_payments
    .join(df_orders.select("order_id"), "order_id")
    .select(
        "order_id",
        "payment_type",
        "payment_installments",
        "payment_value",
        "payment_sequential"
    )
    .withColumn("payment_sk",
            sha2(concat_ws("||", "order_id", "payment_sequential"), 256)
    )
)

to_postgres(fact_payments, "dwh.fact_payments")

# =========================
# FACT REVIEWS
# =========================

df_reviews = spark.read.jdbc(
    POSTGRES_URL, "stg.order_reviews", properties=POSTGRES_PROPERTIES
)

fact_reviews = (
    df_reviews
    .join(df_orders.select("order_id"), "order_id")
    .select(
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message"
    ).withColumn("review_sk",
            sha2(concat_ws("||", "order_id", "review_id"), 256)
    )
    .withColumn("review_creation_date_sk",
            date_format("review_creation_date","yyyyMMdd").cast("int")
    )
)

to_postgres(fact_reviews, "dwh.fact_reviews")