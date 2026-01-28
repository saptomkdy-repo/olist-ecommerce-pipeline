df_items = spark.read.jdbc(
    POSTGRES_URL, "stg_order_items", properties=POSTGRES_PROPERTIES
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

df_fact_items.write.jdbc(
    POSTGRES_URL,
    "fact_order_items",
    mode="overwrite",
    properties=POSTGRES_PROPERTIES
)
