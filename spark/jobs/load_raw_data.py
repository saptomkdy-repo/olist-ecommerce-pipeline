from utils.spark_session import create_spark_session
from utils.schemas import orders_schema, order_items_schema, customers_schema
from utils.write_db import write_to_postgres

spark = create_spark_session("load_raw_data")

base_path = "/app/data/raw"

df_orders = spark.read.schema(orders_schema).option("header", True)\
    .csv(f"{base_path}/olist_orders_dataset.csv")

df_items = spark.read.schema(order_items_schema).option("header", True)\
    .csv(f"{base_path}/olist_order_items_dataset.csv")

df_customers = spark.read.schema(customers_schema).option("header", True)\
    .csv(f"{base_path}/olist_customers_dataset.csv")

write_to_postgres(df_orders, "raw.orders")
write_to_postgres(df_items, "raw.order_items")
write_to_postgres(df_customers, "raw.customers")