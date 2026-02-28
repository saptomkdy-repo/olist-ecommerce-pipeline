from pyspark.sql.types import *

orders_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("customer_id", StringType(), False),
    StructField("order_status", StringType(), False),
    StructField("order_purchase_timestamp", StringType(), False),
    StructField("order_approved_at", StringType(), True),
    StructField("order_delivered_carrier_date", StringType(), True),
    StructField("order_delivered_customer_date", StringType(), True),
    StructField("order_estimated_delivery_date", StringType(), False)
])

order_items_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("order_item_id", IntegerType(), False),
    StructField("product_id", StringType(), False),
    StructField("seller_id", StringType(), False),
    StructField("shipping_limit_date", StringType(), False),
    StructField("price", DecimalType(10, 2), False),
    StructField("freight_value", DecimalType(10, 2), False)
])

order_payments_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("payment_sequential", IntegerType(), False),
    StructField("payment_type", StringType(), False),
    StructField("payment_installments", IntegerType(), False),
    StructField("payment_value", DecimalType(10, 2), False)
])

order_reviews_schema = StructType([
    StructField("review_id", StringType(), False),
    StructField("order_id", StringType(), False),
    StructField("review_score", IntegerType(), False),
    StructField("review_comment_title", StringType(), True),
    StructField("review_comment_message", StringType(), True),
    StructField("review_creation_date", StringType(), False),
    StructField("review_answer_timestamp", StringType(), False)
])

customers_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("customer_unique_id", StringType(), False),
    StructField("customer_zip_code_prefix", IntegerType(), False),
    StructField("customer_city", StringType(), False),
    StructField("customer_state", StringType(), False)
])

products_schema = StructType([
    StructField("product_id", StringType(), False),
    StructField("product_category_name", StringType(), True),
    StructField("product_name_lenght", DecimalType(10, 2), True),
    StructField("product_description_lenght", DecimalType(10, 2), True),
    StructField("product_photos_qty", DecimalType(10, 2), True),
    StructField("product_weight_g", DecimalType(10, 2), True),
    StructField("product_length_cm", DecimalType(10, 2), True),
    StructField("product_height_cm", DecimalType(10, 2), True),
    StructField("product_width_cm", DecimalType(10, 2), True)
])

sellers_schema = StructType([
    StructField("seller_id", StringType(), False),
    StructField("seller_zip_code_prefix", IntegerType(), False),
    StructField("seller_city", StringType(), False),
    StructField("seller_state", StringType(), False)
])