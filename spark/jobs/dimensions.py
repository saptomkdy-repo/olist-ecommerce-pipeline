from pyspark.sql.functions import *
# from pyspark.sql.window import Window
from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import to_postgres

spark = create_spark_session("dimensions")

# =====================
# Dim Geolocation
# =====================
# df_geolocation = spark.read.jdbc(
#     POSTGRES_URL, "stg.geolocation", properties=POSTGRES_PROPERTIES
# )

# # window = Window.orderBy("geolocation_zip_code_prefix")

# dim_geolocation = (
#     df_geolocation
#     .dropDuplicates(["geolocation_zip_code_prefix"])
#     # .withColumn("geolocation_sk", row_number().over(window))
#     .withColumn("geolocation_sk",sha2(col("geolocation_zip_code_prefix"),256))
# )

# to_postgres(dim_geolocation, "dwh.dim_geolocation")

# =====================
# Dim Customers
# =====================
df_customers = spark.read.jdbc(
    POSTGRES_URL, "stg.customers", properties=POSTGRES_PROPERTIES
)

# window = Window.orderBy("customer_id")

dim_customers = (
    df_customers
    .dropDuplicates(["customer_id"])
    # .join(
    #         dim_geolocation,
    #         df_customers.customer_zip_code_prefix
    #         == dim_geolocation.geolocation_zip_code_prefix,
    #         "left"
    # )
    .select(
            "customer_id",
            "customer_unique_id",
            "customer_city",
            "customer_state",
            "customer_zip_code_prefix"
            # "geolocation_sk"
    )
    # .withColumn("customer_sk", row_number().over(window))
    .withColumn("customer_sk",sha2(col("customer_id"),256))
)

to_postgres(dim_customers, "dwh.dim_customers")

# =====================
# Dim Products
# =====================
df_products = spark.read.jdbc(
    POSTGRES_URL, "stg.products", properties=POSTGRES_PROPERTIES
)

# window = Window.orderBy("product_id")

dim_products = (
    df_products
    .dropDuplicates(["product_id"])
    # .withColumn("product_sk", row_number().over(window))
    .withColumn("product_sk",sha2(col("product_id"),256))
)

to_postgres(dim_products, "dwh.dim_products")

# =====================
# Dim Sellers
# =====================
df_sellers = spark.read.jdbc(
    POSTGRES_URL, "stg.sellers", properties=POSTGRES_PROPERTIES
)

# window = Window.orderBy("seller_id")

dim_sellers = (
    df_sellers
    .dropDuplicates(["seller_id"])
    # .join(
    #         dim_geolocation,
    #         df_sellers.seller_zip_code_prefix
    #         == dim_geolocation.geolocation_zip_code_prefix,
    #         "left"
    # )
    .select(
            "seller_id",
            "seller_city",
            "seller_state",
            "seller_zip_code_prefix"
            # "geolocation_sk"
    )
    # .withColumn("seller_sk", row_number().over(window))
    .withColumn("seller_sk",sha2(col("seller_id"),256))
)

to_postgres(dim_sellers, "dwh.dim_sellers")

# =====================
# Dim Date
# =====================
df_orders = spark.read.jdbc(
    POSTGRES_URL, "stg.orders", properties=POSTGRES_PROPERTIES
)

df_order_items = spark.read.jdbc(
    POSTGRES_URL, "stg.order_items", properties=POSTGRES_PROPERTIES
)

df_reviews = spark.read.jdbc(
    POSTGRES_URL, "stg.order_reviews", properties=POSTGRES_PROPERTIES
)

df_date = (
    df_orders.select(to_date("order_purchase_timestamp").alias("d"))
        .union(df_order_items.select(to_date("shipping_limit_date").alias("d")))
        .union(df_reviews.select(to_date("review_creation_date").alias("d")))
        .distinct()
)

dim_date = (
    df_date
        .withColumn("date_sk", date_format("d","yyyyMMdd").cast("int"))
        .withColumn("day",dayofmonth("d"))
        .withColumn("month",month("d"))
        .withColumn("year",year("d"))
        .withColumn("weekday",date_format("d","E"))
        .withColumn("weekend",
            when(dayofweek("d").isin([1,7]),1).otherwise(0)
        )
        .withColumnRenamed("d","date")
)

to_postgres(dim_date, "dwh.dim_date")
