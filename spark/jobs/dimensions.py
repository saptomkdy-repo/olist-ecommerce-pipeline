from utils.spark_session import create_spark_session
from utils.postgres import POSTGRES_URL, POSTGRES_PROPERTIES
from utils.write_db import write_to_postgres

spark = create_spark_session("dimensions")

df_customers = spark.read.jdbc(
    POSTGRES_URL, "raw.customers", properties=POSTGRES_PROPERTIES
)

df_dim_customers = (
    df_customers
    .select(
        "customer_id",
        "customer_unique_id",
        "customer_city",
        "customer_state"
    )
    .dropDuplicates(["customer_id"])
)

write_to_postgres(df_dim_customers, "dwh.dim_customers")
