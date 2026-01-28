df_customers = spark.read.jdbc(
    POSTGRES_URL, "stg.customers", properties=POSTGRES_PROPERTIES
)

# Create dimension table for customers.
# Choose relevant columns and remove duplicates.
# Dimension = attribute data about entities (customers in this case).
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

df_dim_customers.write.jdbc(
    POSTGRES_URL,
    "dim.customers",
    mode="overwrite",
    properties=POSTGRES_PROPERTIES
)
