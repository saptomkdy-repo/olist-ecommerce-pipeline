from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES

spark = create_spark_session("load_raw_data")

df_orders = spark.read.option("header", True).csv(
    "/app/data/raw/olist_orders_dataset.csv"
)

df_orders.write \
    .mode("overwrite") \
    .jdbc(
        url=POSTGRES_URL,
        table="raw.orders",
        properties=POSTGRES_PROPERTIES
    )