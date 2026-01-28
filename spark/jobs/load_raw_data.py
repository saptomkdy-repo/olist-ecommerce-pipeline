# NO TRANSFORMATIONS

# This code does not use hardcoded Spark & ​​Postgres
# configuration, but is separated into the utils folder.

# So, it's:
# Reusable: other scripts can use the same configuration.
# Clean code: ETL logic ≠ config.
# Safer: DB credentials don't mix logic.

from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES

# Create a Spark session named "load_raw_data".
spark = create_spark_session("load_raw_data")

# Spark reads the raw CSV file into a DataFrame.
# header=True: first row = column name.
# /app/data/...: path inside the Spark container.
# Without .schema(), Spark infers data types automatically.
df_orders = spark.read.option("header", True).csv(
    "/app/data/raw/olist_orders_dataset.csv"
)

# Spark writes to the raw.orders table in PostgreSQL.
# mode("overwrite"): if the table exists, replace it.
df_orders.write \
    .mode("overwrite") \
    .jdbc(
        url=POSTGRES_URL,
        table="raw.orders",
        properties=POSTGRES_PROPERTIES
    )