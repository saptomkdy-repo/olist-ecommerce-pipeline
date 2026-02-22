from pyspark.sql.functions import col
from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import to_postgres

spark = create_spark_session("staging")

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
