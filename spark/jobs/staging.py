from pyspark.sql.functions import col
from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import to_postgres

spark = create_spark_session("staging")

# =========================
# Staging Orders
# =========================

df_orders = spark.read.jdbc(
    POSTGRES_URL, "raw.orders", properties=POSTGRES_PROPERTIES
)

df_stg_orders = (
    df_orders
    .filter("order_id IS NOT NULL")
    .withColumn("order_purchase_timestamp", col("order_purchase_timestamp").cast("timestamp"))
    .withColumn("order_approved_at", col("order_approved_at").cast("timestamp"))
    .dropDuplicates(["order_id"])
)

to_postgres(df_stg_orders, "stg.orders")

# =========================
# Staging Customers
# =========================

df_customers = spark.read.jdbc(
    POSTGRES_URL, "raw.customers", properties=POSTGRES_PROPERTIES
)

df_stg_customers = (
    df_customers
    .filter("customer_id IS NOT NULL")
    .dropDuplicates(["customer_id"])
)

to_postgres(df_stg_customers, "stg.customers")

# =========================
# Staging Order Items
# =========================

df_order_items = spark.read.jdbc(
    POSTGRES_URL, "raw.order_items", properties=POSTGRES_PROPERTIES
)

df_stg_order_items = (
    df_order_items
    .filter("order_id IS NOT NULL AND order_item_id IS NOT NULL")
    .withColumn("shipping_limit_date", col("shipping_limit_date").cast("timestamp"))
    .dropDuplicates(["order_id","order_item_id"])
)

to_postgres(df_stg_order_items, "stg.order_items")

# =========================
# Staging Reviews
# =========================

df_reviews = spark.read.jdbc(
    POSTGRES_URL, "raw.order_reviews", properties=POSTGRES_PROPERTIES
)

df_stg_reviews = (
    df_reviews
    .filter("order_id IS NOT NULL AND review_id IS NOT NULL")
    .withColumn("review_creation_date", col("review_creation_date").cast("timestamp"))
    .dropDuplicates(["order_id","review_id"])
)

to_postgres(df_stg_reviews, "stg.order_reviews")

# =========================
# Staging Payments
# =========================

df_payments = spark.read.jdbc(
    POSTGRES_URL, "raw.order_payments", properties=POSTGRES_PROPERTIES
)

df_stg_payments = (
    df_payments
    .filter("order_id IS NOT NULL and payment_sequential IS NOT NULL")
    .dropDuplicates(["order_id","payment_sequential"])
)

to_postgres(df_stg_payments, "stg.order_payments")

# =========================
# Staging Products
# =========================

df_products = spark.read.jdbc(
    POSTGRES_URL, "raw.products", properties=POSTGRES_PROPERTIES
)

df_stg_products = (
    df_products
    .filter("product_id IS NOT NULL")
    .dropDuplicates(["product_id"])
)

to_postgres(df_stg_products, "stg.products")

# =========================
# Staging Sellers
# =========================

df_sellers = spark.read.jdbc(
    POSTGRES_URL, "raw.sellers", properties=POSTGRES_PROPERTIES
)

df_stg_sellers = (
    df_sellers
    .filter("seller_id IS NOT NULL")
    .dropDuplicates(["seller_id"])
)

to_postgres(df_stg_sellers, "stg.sellers")

# =========================
# Staging Geolocation
# =========================

# df_stg_geo = (
#     df_geo
#     .filter("geolocation_zip_code_prefix IS NOT NULL")
#     .groupBy("geolocation_zip_code_prefix")
#     .agg(
#         first("geolocation_city").alias("geolocation_city"),
#         first("geolocation_state").alias("geolocation_state")
#     )
# )