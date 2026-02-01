from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import write_to_postgres

spark = create_spark_session("facts")

df_items = spark.read.jdbc(
    POSTGRES_URL, "raw.order_items", properties=POSTGRES_PROPERTIES
)

df_fact_items = (
    df_items
    .select(
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "price",
        "freight_value"
    )
)

write_to_postgres(df_fact_items, "dwh.fact_order_items")
