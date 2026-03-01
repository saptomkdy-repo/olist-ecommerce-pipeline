import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from airflow.hooks.postgres_hook import PostgresHook

logger = logging.getLogger(__name__)

DQ_TABLE = "dwh.data_quality"

CHECKS = [
    ("raw.orders",           ["order_id", "customer_id", "order_status"]),
    ("raw.customers",        ["customer_id", "customer_state"]),
    ("raw.order_items",      ["order_id", "product_id", "seller_id", "price"]),
    ("raw.order_payments",   ["order_id", "payment_type", "payment_value"]),
    ("raw.order_reviews",    ["review_id", "order_id", "review_score"]),
    ("raw.products",         ["product_id"]),
    ("raw.sellers",          ["seller_id", "seller_state"]),
    ("stg.orders",           ["order_id", "customer_id"]),
    ("stg.order_items",      ["order_id", "product_id", "price"]),
    ("stg.order_payments",   ["order_id", "payment_value"]),
    ("dwh.dim_customers",    ["customer_sk", "customer_id", "customer_state"]),
    ("dwh.dim_products",     ["product_sk", "product_id"]),
    ("dwh.dim_sellers",      ["seller_sk", "seller_id"]),
    ("dwh.dim_date",         ["date_sk", "date"]),
    ("dwh.fact_order_items", ["order_item_sk", "order_id", "customer_sk", "price", "order_date_sk", "shipping_limit_date_sk"]),
    ("dwh.fact_payments",    ["payment_sk", "order_id", "payment_value"]),
    ("dwh.fact_reviews",     ["review_sk", "order_id", "review_score", "review_creation_date_sk"]),
]


def create_table(pgconn):
    pgconn.run(f"""
        CREATE TABLE IF NOT EXISTS {DQ_TABLE} (
            id                  SERIAL PRIMARY KEY,
            lastrun_timestamp   TIMESTAMP NOT NULL,
            table_name          TEXT NOT NULL,
            type                TEXT NOT NULL,
            column_name         TEXT,
            status              TEXT NOT NULL,
            detail              TEXT
        );
    """)


def save_result(pgconn, lastrun_ts, table, type, column, status, msg):
    pgconn.run(f"""
        INSERT INTO {DQ_TABLE}
            (lastrun_timestamp, table_name, type, column_name, status, detail)
        VALUES
            ('{lastrun_ts}', '{table}', '{type}', '{column}', '{status}', '{msg}');
    """)


def run_data_quality(**context):
    pgconn = PostgresHook(postgres_conn_id="smh_postgres")
    create_table(pgconn)

    lastrun_ts = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
    failures = []

    date_cols = ["date_sk", "order_date_sk", "shipping_limit_date_sk", "review_creation_date_sk"]

    for table, check_cols in CHECKS:

        # 1. Row Count Check
        row_count = pgconn.get_first(f"SELECT COUNT(*) FROM {table}")[0]
        if row_count == 0:
            msg = f"{row_count} row(s) found in {table}"
            save_result(pgconn, lastrun_ts, table, "row_count", "-", "FAILED", msg)
            failures.append(msg)
            logger.error(f"[DQ FAILED] {msg}")
        else:
            msg = f"{row_count} row(s) found in {table}"
            save_result(pgconn, lastrun_ts, table, "row_count", "-", "PASSED", msg)
            logger.info(f"[DQ PASSED] {msg}")

        # 2. Null & Freshness Check
        for col in check_cols:
            null_count = pgconn.get_first(
                f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL"
            )[0]
            if null_count > 0:
                msg = f"{null_count} null value(s) found in {table}.{col}"
                save_result(pgconn, lastrun_ts, table, "null_check", col, "FAILED", msg)
                failures.append(msg)
                logger.error(f"[DQ FAILED] {msg}")
                if col in date_cols: # Freshness check for date columns
                    msg = f"No date data found in {table}.{col}"
                    save_result(pgconn, lastrun_ts, table, "freshness", col, "FAILED", msg)
                    failures.append(msg)
                    logger.error(f"[DQ FAILED] {msg}")
            else:
                msg = f"{null_count} null value(s) found in {table}.{col}"
                save_result(pgconn, lastrun_ts, table, "null_check", col, "PASSED", msg)
                logger.info(f"[DQ PASSED] {msg}")
                if col in date_cols: # Freshness check for date columns
                    latest_sk = pgconn.get_first(
                    f"SELECT MAX({col}) FROM {table}")[0]
                    latest_date = datetime.strptime(str(latest_sk), "%Y%m%d").date()
                    msg = f"Latest date: {latest_date} found in {table}.{col}"
                    save_result(pgconn, lastrun_ts, table, "freshness", col, "PASSED", msg)
                    logger.info(f"[DQ PASSED] {msg}")

    # 3. Summary
    total_checks = len(CHECKS) + sum(len(cols) for _, cols in CHECKS)
    total_failures = len(failures)
    total_passed = total_checks - total_failures

    logger.info(f"\n{'='*50}")
    logger.info(f"DATA QUALITY SUMMARY")
    logger.info(f"Last run timestamp: {lastrun_ts}")
    logger.info(f"Total checks: {total_checks}")
    logger.info(f"Passed: {total_passed}")
    logger.info(f"Failed: {total_failures}")
    logger.info(f"{'='*50}")

    if failures:
        failure_msg = "\n".join(failures)
        raise ValueError(
            f"Data Quality check FAILED with {total_failures} issues:\n{failure_msg}"
        )

    logger.info("All data quality checks PASSED!")