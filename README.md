# Olist E-Commerce Data Engineering Pipeline

An end-to-end data engineering project built on the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). The pipeline covers batch ingestion, transformation, data warehousing, analytics views, data quality checks, and real-time streaming. All containerized with Docker.

---

## Architecture
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0c63d652-06a6-4492-b4f0-47ee9e104739" />

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Processing | Apache Spark 3.5.0 (PySpark) |
| Orchestration | Apache Airflow 2.8.0 (LocalExecutor) |
| Storage | PostgreSQL 14 |
| Streaming | Apache Kafka (Confluent 7.5.0) |
| Containerization | Docker |
| Language | Python 3.10 |

---

## Project Directory Tree

```
┗━━ olist-ecommerce-pipeline/
    ┣━━ .dockerignore
    ┣━━ .env
    ┣━━ .env.example               # Environment variable template
    ┣━━ .gitignore
    ┣━━ LICENSE
    ┣━━ README.md
    ┣━━ show_tree.py
    ┣━━ dags/
    ┃   ┗━━ olist_pipeline.py      # Airflow DAG definition
    ┣━━ data/
    ┃   ┗━━ raw/                   # Olist CSV files (not committed, access via Kaggle)
    ┣━━ docker/
    ┃   ┣━━ .env
    ┃   ┣━━ docker-compose.yaml
    ┃   ┣━━ Dockerfile.airflow
    ┃   ┣━━ Dockerfile.consumer
    ┃   ┣━━ Dockerfile.producer
    ┃   ┗━━ Dockerfile.spark
    ┣━━ docs/
    ┃   ┣━━ step_01_data_understanding.md
    ┃   ┣━━ step_02_architecture_and_data_flow.md
    ┃   ┣━━ step_03_data_modeling.md
    ┃   ┗━━ diagrams/
    ┃       ┣━━ Star_Schema_Olist_Pipeline_Data_Warehouse_dbdiagram.png
    ┃       ┗━━ Architecture_and_Data_Flow.png
    ┃       ┗━━ full_db_diagram.dbml
    ┣━━ logs/
    ┣━━ notebooks/
    ┃   ┗━━ step_01_data_understanding.ipynb
    ┣━━ plugins/
    ┣━━ spark/
    ┃   ┣━━ .gitkeep
    ┃   ┣━━ requirements.txt
    ┃   ┣━━ jobs/
    ┃   ┃   ┣━━ dimensions.py
    ┃   ┃   ┣━━ facts.py
    ┃   ┃   ┣━━ load_raw_data.py
    ┃   ┃   ┗━━ staging.py
    ┃   ┗━━ utils/
    ┃       ┣━━ analytics_views.sql
    ┃       ┣━━ data_quality.py
    ┃       ┣━━ postgres.py
    ┃       ┣━━ schemas.py
    ┃       ┣━━ spark_session.py
    ┃       ┣━━ write_db.py
    ┃       ┗━━ __init__.py
    ┗━━ streaming/
        ┣━━ consumer.py              # # Spark Structured Streaming
        ┗━━ producer.py              # Kafka producer (generate fake orders & payments)
```

---

## Prerequisites

- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) (with Docker Compose)
- [Git](https://git-scm.com/)
- [Python](https://www.python.org/downloads/)
- [VS Code](https://code.visualstudio.com/download)
- Olist dataset CSV files from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/saptomkdy-repo/olist-ecommerce-pipeline.git
cd olist-ecommerce-pipeline
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your preferred credentials:

```env
# Pipeline Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=smh_db
POSTGRES_USER=smh_user
POSTGRES_PASSWORD=smh_pass

# Airflow Metadata Database
AIRFLOW_POSTGRES_USER=airflow
AIRFLOW_POSTGRES_PASSWORD=airflow
AIRFLOW_POSTGRES_DB=airflow

# Airflow Admin User
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin123!
AIRFLOW_ADMIN_FIRSTNAME=Admin
AIRFLOW_ADMIN_LASTNAME=User
AIRFLOW_ADMIN_EMAIL=admin@email.com
```

### 3. Add Olist dataset

Download the dataset from Kaggle and place the CSV files in `data/raw/`:

```
data/raw/
├── olist_orders_dataset.csv
├── olist_customers_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_payments_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_products_dataset.csv
└── olist_sellers_dataset.csv
```

---

## How to Run

### 1. Start all services

```bash
cd docker
docker-compose up -d --build
```

This will start:
- `smh-postgres` for pipeline database (port **5434**)
- `airflow-postgres` for Airflow's metadata database (port **5433**)
- `airflow-webserver` for Airflow UI (port **8080**)
- `airflow-scheduler` for Airflow scheduler
- `smh-spark` for Spark master
- `zookeeper` & `kafka` for Kafka broker
- `kafka-producer` for fake data producer (auto-start)
- `kafka-consumer` for Spark Structured Streaming consumer (auto-start)

Verify all containers are running:

```bash
docker ps
```

### 2. Run the batch pipeline

Open Airflow UI at [http://localhost:8080](http://localhost:8080) and log in with your configured admin credentials.

Find the `olist_pipeline` DAG and click **Trigger DAG** (play button).

The pipeline runs 8 tasks in sequence:

```
build_schemas → load_raw → staging → dimensions → facts → dq_check → constraints → analytics
```

### 3. Verify data

**Batch pipeline:**
```bash
# You can connect via DBeaver or psql:
# Host: localhost | Port: 5434 | DB: smh_db | User: smh_user

# via psql:
docker exec smh-postgres psql -U smh_user -d smh_db -c "\dv dwh.*"
```

**Streaming pipeline:**
```bash
# Check producer is sending messages:
docker logs kafka-producer --tail 20

# Check data in PostgreSQL via DBeaver or psql.
# via psql:
docker exec smh-postgres psql -U smh_user -d smh_db \
  -c "SELECT COUNT(*) FROM streaming.orders;"
docker exec smh-postgres psql -U smh_user -d smh_db \
  -c "SELECT COUNT(*) FROM streaming.payments;"
```

---

## Database Schema

The data warehouse follows a **star schema** design:
<img width="1093" height="1108" alt="image" src="https://github.com/user-attachments/assets/bf67b4da-1b6f-46cf-b466-b28a20e112c7" />

## Full DB Diagram
See `docs/full_db_diagram.dbml` for the full schema (tables & views), then paste it at [dbdiagram.io](https://dbdiagram.io) to visualize.

## Schema Description

| Layer | Schema | Description |
|---|---|---|
| Raw | `raw` | Direct ingestion from CSV files |
| Staging | `stg` | Cleaned and type-cast data |
| Warehouse | `dwh` | Star schema (4 dimensions & 3 facts) |
| Analytics | `dwh` (views) | 8 pre-built KPI views |
| Streaming | `streaming` | Fake real-time orders & payments |

### Analytics Views

| View | Description |
|---|---|
| `view_kpi` | Monthly revenue, orders, GMV, AOV |
| `view_clv` | Customer lifetime value |
| `view_rfm` | RFM segmentation |
| `view_seller_performance` | Seller revenue and review scores |
| `view_product_insights` | Product analysis |
| `view_payment_analysis` | Payment method analysis |
| `view_sales_by_region` | Revenue by Brazilian state |
| `view_review_analysis` | Review score analysis |

---

## DBeaver Connection

| Database | Host | Port | DB Name | Username |
|---|---|---|---|---|
| Pipeline DB | localhost | 5434 | smh_db | smh_user |
| Airflow DB | localhost | 5433 | airflow | airflow |

> **Note:** Port 5434 is used for the pipeline database to avoid conflicts with any locally installed PostgreSQL instance (5432).

---

## Stopping the Pipeline

```bash
cd docker
docker-compose down        # stop containers, keep volumes
docker-compose down -v     # stop containers and delete all data if you want
```
