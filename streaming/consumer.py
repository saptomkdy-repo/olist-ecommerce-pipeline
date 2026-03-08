import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType
)

# Environment variables and constants
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
POSTGRES_HOST   = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT   = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB     = os.getenv("POSTGRES_DB", "smh_db")
POSTGRES_USER   = os.getenv("POSTGRES_USER", "smh_user")
POSTGRES_PASS   = os.getenv("POSTGRES_PASSWORD", "smh_pass")
JAR_PATH        = os.getenv("POSTGRES_JAR_PATH", "/opt/spark/jars/postgresql-42.7.3.jar")

# PostgreSQL connection properties
POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
POSTGRES_PROPS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASS,
    "driver": "org.postgresql.Driver"
}

# Kafka JAR packages
KAFKA_PACKAGES = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"

# Schemas
order_schema = StructType([
    StructField("order_id",                  StringType()),
    StructField("customer_id",               StringType()),
    StructField("customer_unique_id",        StringType()),
    StructField("customer_city",             StringType()),
    StructField("customer_state",            StringType()),
    StructField("order_status",              StringType()),
    StructField("order_purchase_timestamp",  StringType()),
    StructField("order_approved_at",         StringType()),
    StructField("price",                     DoubleType()),
    StructField("freight_value",             DoubleType()),
    StructField("event_timestamp",           StringType()),
])

payment_schema = StructType([
    StructField("order_id",              StringType()),
    StructField("payment_sequential",    IntegerType()),
    StructField("payment_type",          StringType()),
    StructField("payment_installments",  IntegerType()),
    StructField("payment_value",         DoubleType()),
    StructField("event_timestamp",       StringType()),
])

# Create Spark session
def create_spark_session():
    return (
        SparkSession.builder
        .appName("OlistStreamingConsumer") # App name for Spark UI
        .config("spark.jars", JAR_PATH) # PostgreSQL JDBC driver
        .config("spark.jars.packages", KAFKA_PACKAGES) # Kafka connector
        .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoints") # Checkpoint for fault tolerance
        .getOrCreate()
    )

# Setup PostgreSQL schemas and tables
def setup_schemas():
    # Create tables if not exist using psycopg2 for better control over schema and data types
    import psycopg2
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASS
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS streaming;

        CREATE TABLE IF NOT EXISTS streaming.orders (
            order_id                  TEXT,
            customer_id               TEXT,
            customer_unique_id        TEXT,
            customer_city             TEXT,
            customer_state            TEXT,
            order_status              TEXT,
            order_purchase_timestamp  TIMESTAMP,
            order_approved_at         TIMESTAMP,
            price                     NUMERIC(10,2),
            freight_value             NUMERIC(10,2),
            event_timestamp           TIMESTAMP,
            ingested_at               TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS streaming.payments (
            order_id              TEXT,
            payment_sequential    INTEGER,
            payment_type          TEXT,
            payment_installments  INTEGER,
            payment_value         NUMERIC(10,2),
            event_timestamp       TIMESTAMP,
            ingested_at           TIMESTAMP DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_streaming_orders_order_id   ON streaming.orders (order_id);
        CREATE INDEX IF NOT EXISTS idx_streaming_payments_order_id ON streaming.payments (order_id);
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("[Consumer] Schema(s) and table(s) are ready.")

# Function to write streaming DataFrame to PostgreSQL
def write_to_postgres(df, epoch_id, table):
    if df.count() == 0:
        return
    df.write.jdbc(
        url=POSTGRES_URL,
        table=table,
        mode="append",
        properties=POSTGRES_PROPS
    )
    print(f"[Consumer] Wrote {df.count()} row(s) to {table} (epoch {epoch_id})")

# Function to read streaming data from Kafka topic and parse it using the provided schema
def read_stream(spark, topic, schema):
    return (
        spark.readStream
        .format("kafka") # Specify Kafka as the source for streaming data
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) # Kafka bootstrap servers
        .option("subscribe", topic) # Kafka topic to subscribe to
        .option("startingOffsets", "latest") # Start reading from the latest offset to avoid processing old data
        .option("failOnDataLoss", "false") # Don't fail if Kafka data is lost (e.g., due to retention policies)
        .load()
        .select(from_json(col("value").cast("string"), schema).alias("data")) # Parse the JSON string in the "value" column using the provided schema and alias it as "data"
        .select("data.*") # Select all fields from the parsed "data" struct to flatten the DataFrame for easier processing
    )

# Main function to run the consumer (Spark Structured Streaming application that reads from Kafka, transforms the data, and writes to PostgreSQL)
def main():
    spark = create_spark_session() # Create Spark session with necessary configurations for Kafka and PostgreSQL
    spark.sparkContext.setLogLevel("WARN") # Set log level to WARN to reduce verbosity in the console
    setup_schemas()

    # Orders Stream
    orders_df = read_stream(spark, "olist.orders", order_schema)
    orders_df = orders_df.withColumn(
        "order_purchase_timestamp", to_timestamp("order_purchase_timestamp")
    ).withColumn(
        "order_approved_at", to_timestamp("order_approved_at")
    ).withColumn(
        "event_timestamp", to_timestamp("event_timestamp")
    )

    # Write orders stream to PostgreSQL using foreachBatch
    orders_query = (
        orders_df.writeStream
        .foreachBatch(lambda df, epoch: write_to_postgres(df, epoch, "streaming.orders")) # Use foreachBatch to write each micro-batch to PostgreSQL with error handling
        .option("checkpointLocation", "/tmp/spark-checkpoints/orders") # Separate checkpoint location for orders stream to maintain state and ensure fault tolerance
        .trigger(processingTime="10 seconds") # Trigger the stream to process data every 10 seconds (micro-batch interval)
        .start()
    )

    # Payments Stream
    payments_df = read_stream(spark, "olist.payments", payment_schema)
    payments_df = payments_df.withColumn(
        "event_timestamp", to_timestamp("event_timestamp")
    )

    payments_query = (
        payments_df.writeStream
        .foreachBatch(lambda df, epoch: write_to_postgres(df, epoch, "streaming.payments")) # Use foreachBatch to write each micro-batch to PostgreSQL with error handling
        .option("checkpointLocation", "/tmp/spark-checkpoints/payments") # Separate checkpoint location for payments stream to maintain state and ensure fault tolerance
        .trigger(processingTime="10 seconds") # Trigger the stream to process data every 10 seconds (micro-batch interval)
        .start()
    )

    print("[Consumer] Streaming started. Waiting for data...")
    spark.streams.awaitAnyTermination() # Wait for any of the streaming queries to terminate (e.g., due to an error or manual stop)


if __name__ == "__main__":
    main()