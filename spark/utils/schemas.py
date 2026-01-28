from pyspark.sql.types import *

orders_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("order_status", StringType(), False),
    StructField("order_purchase_timestamp", StringType(), False),
    StructField("order_approved_at", StringType(), True),
    StructField("order_delivered_carrier_date", StringType(), True),
    StructField("order_delivered_customer_date", StringType(), True),
    StructField("order_estimated_delivery_date", StringType(), False),
])

order_items_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("order_item_id", IntegerType(), False),
    StructField("product_id", StringType(), False),
    StructField("seller_id", StringType(), False),
    StructField("shipping_limit_date", StringType(), False),
    StructField("price", DecimalType(10, 2), False),
    StructField("freight_value", DecimalType(10, 2), False),
])

customers_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("customer_unique_id", StringType(), False),
    StructField("customer_zip_code_prefix", IntegerType(), False),
    StructField("customer_city", StringType(), False),
    StructField("customer_state", StringType(), False),
])
