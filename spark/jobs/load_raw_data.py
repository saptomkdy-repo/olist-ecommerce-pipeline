import sys
sys.path.append("/app/spark")

from utils.spark_session import create_spark_session
from utils.schemas import orders_schema, order_items_schema, customers_schema, order_payments_schema, order_reviews_schema, products_schema, sellers_schema #, geolocation_schema
from utils.write_db import to_postgres

import os
base_path = os.getenv("DATA_PATH", "/app/data/raw")

spark = create_spark_session("load_raw_data")

df_orders = spark.read.schema(orders_schema).option("header", True)\
    .csv(f"{base_path}/olist_orders_dataset.csv")

df_order_items = spark.read.schema(order_items_schema).option("header", True)\
    .csv(f"{base_path}/olist_order_items_dataset.csv")

df_customers = spark.read.schema(customers_schema).option("header", True)\
    .csv(f"{base_path}/olist_customers_dataset.csv")

df_order_payments = spark.read.schema(order_payments_schema).option("header", True)\
    .csv(f"{base_path}/olist_order_payments_dataset.csv")

df_order_reviews = spark.read.schema(order_reviews_schema).option("header", True)\
    .csv(f"{base_path}/olist_order_reviews_dataset.csv")

df_products = spark.read.schema(products_schema).option("header", True)\
    .csv(f"{base_path}/olist_products_dataset.csv")

df_sellers = spark.read.schema(sellers_schema).option("header", True)\
    .csv(f"{base_path}/olist_sellers_dataset.csv")

# df_geolocation = spark.read.schema(geolocation_schema).option("header", True)\
#     .csv(f"{base_path}/olist_geolocation_dataset.csv")

to_postgres(df_orders, "raw.orders")
to_postgres(df_order_items, "raw.order_items")
to_postgres(df_customers, "raw.customers")
to_postgres(df_order_payments, "raw.order_payments")
to_postgres(df_order_reviews, "raw.order_reviews")
to_postgres(df_products, "raw.products")
to_postgres(df_sellers, "raw.sellers")
# to_postgres(df_geolocation, "raw.geolocation")