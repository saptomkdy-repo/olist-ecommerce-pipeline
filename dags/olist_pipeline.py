from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from utils.data_quality import run_data_quality
from datetime import datetime
import importlib.util
import os

def run_spark_job(job_path):
    spec = importlib.util.spec_from_file_location("job", job_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

def create_schemas():
    pgconn = PostgresHook(postgres_conn_id="smh-postgres")
    pgconn.run("""
        CREATE SCHEMA IF NOT EXISTS raw;
        CREATE SCHEMA IF NOT EXISTS stg;
        CREATE SCHEMA IF NOT EXISTS dwh;
    """)

def create_views():
    pgconn = PostgresHook(postgres_conn_id="smh-postgres")
    sql_path = "/opt/airflow/spark/utils/analytics_views.sql"
    with open(sql_path, "r") as f:
        sql = f.read()
    pgconn.run(sql)

def add_constraints(**context):
    pgconn = PostgresHook(postgres_conn_id="smh-postgres")

    # Primary Keys
    pgconn.run("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_customers_pkey') THEN
                ALTER TABLE dwh.dim_customers    ADD PRIMARY KEY (customer_sk);    END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_products_pkey') THEN
                ALTER TABLE dwh.dim_products     ADD PRIMARY KEY (product_sk);     END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_sellers_pkey') THEN
                ALTER TABLE dwh.dim_sellers      ADD PRIMARY KEY (seller_sk);      END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_date_pkey') THEN
                ALTER TABLE dwh.dim_date         ADD PRIMARY KEY (date_sk);        END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fact_order_items_pkey') THEN
                ALTER TABLE dwh.fact_order_items ADD PRIMARY KEY (order_item_sk);  END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fact_payments_pkey') THEN
                ALTER TABLE dwh.fact_payments    ADD PRIMARY KEY (payment_sk);     END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fact_reviews_pkey') THEN
                ALTER TABLE dwh.fact_reviews     ADD PRIMARY KEY (review_sk);      END IF;
        END $$;
    """)

    # Indexes
    pgconn.run("""
        CREATE INDEX IF NOT EXISTS idx_fact_order_items_customer_sk ON dwh.fact_order_items (customer_sk);
        CREATE INDEX IF NOT EXISTS idx_fact_order_items_product_sk  ON dwh.fact_order_items (product_sk);
        CREATE INDEX IF NOT EXISTS idx_fact_order_items_seller_sk   ON dwh.fact_order_items (seller_sk);
        CREATE INDEX IF NOT EXISTS idx_fact_order_items_date_sk     ON dwh.fact_order_items (order_date_sk);
        CREATE INDEX IF NOT EXISTS idx_fact_payments_order_id       ON dwh.fact_payments (order_id);
        CREATE INDEX IF NOT EXISTS idx_fact_reviews_order_id        ON dwh.fact_reviews (order_id);
    """)

JOBS_PATH = "/opt/airflow/spark/jobs"

with DAG(
    dag_id="olist_pipeline",
    description="ETL Pipeline: build schema -> raw -> staging -> dimensions -> facts -> data quality check -> constraints -> analytics",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["olist", "etl", "batch"],
) as dag:

    build_schemas = PythonOperator(
        task_id="build_schemas",
        python_callable=create_schemas,
    )

    load_raw = PythonOperator(
        task_id="load_raw_data",
        python_callable=run_spark_job,
        op_kwargs={"job_path": f"{JOBS_PATH}/load_raw_data.py"},
    )

    staging = PythonOperator(
        task_id="staging",
        python_callable=run_spark_job,
        op_kwargs={"job_path": f"{JOBS_PATH}/staging.py"},
    )

    dimensions = PythonOperator(
        task_id="dimensions",
        python_callable=run_spark_job,
        op_kwargs={"job_path": f"{JOBS_PATH}/dimensions.py"},
    )

    facts = PythonOperator(
        task_id="facts",
        python_callable=run_spark_job,
        op_kwargs={"job_path": f"{JOBS_PATH}/facts.py"},
    )

    constraints = PythonOperator(
    task_id='add_constraints',
    python_callable=add_constraints,
)

    dq_check = PythonOperator(
        task_id="data_quality_check",
        python_callable=run_data_quality,
        provide_context=True,
    )

    analytics = PythonOperator(
        task_id="analytics_views",
        python_callable=create_views,
    )

    build_schemas >> load_raw >> staging >> dimensions >> facts >> dq_check >> constraints >> analytics