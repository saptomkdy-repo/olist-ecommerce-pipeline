# This code does not use hardcoded Spark & ​​Postgres
# configuration, but is separated into the utils folder.
from spark.utils.postgres import POSTGRES_PROPERTIES, POSTGRES_URL

# Spark reads raw orders data from PostgreSQL.
df_orders = spark.read.jdbc(
    POSTGRES_URL, "raw_orders", properties=POSTGRES_PROPERTIES
)

# Data cleaning and transformation
# .filter out records with null order_id
# .cast order_purchase_timestamp to timestamp type
# .withColumn overrides the existing column if the column name already exists
df_orders_clean = (
    df_orders
    .filter("order_id IS NOT NULL")
    .withColumn("order_purchase_timestamp",
                df_orders.order_purchase_timestamp.cast("timestamp"))
)

df_orders_clean.write \
    .mode("overwrite") \
    .jdbc(
        POSTGRES_URL,
        "stg.orders",
        properties=POSTGRES_PROPERTIES
    )
