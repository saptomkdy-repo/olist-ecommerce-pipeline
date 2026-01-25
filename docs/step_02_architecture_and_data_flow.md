# 2. Step 02 - Architecture and Data Flow

## Objective
**Purposes:** defines end-to-end data architecture and data flow
for the Olist Brazilian E-Commerce data pipeline, designs a scalable and reliable architecture
before implementing the real pipeline.

No transformation, cleaning, or other modifications are performed in this step.

---

## Pipeline

We design a hybrid data pipeline. It means our pipeline will consist of:
1. Batch pipeline.
2. Real-time streaming pipeline.

to reflect real-world e-commerce data workflows.

We will used:
1. Batch pipeline for historical and scheduled data ingestion.
2. Real-time streaming pipeline for simulating real-time order and payment events.

---

## Data Sources

### Batch Pipeline Data Sources
1. Olist CSV datasets:
   - Orders
   - Order Items
   - Customers
   - Products
   - Sellers
   - Payments
   - Reviews
   - Geolocation
   - Category Name
2. Data will be treated as historical and incremental batch data.

### Real-time Streaming Pipeline Data Sources
1. Simulated real-time order events.
2. Simulated real-time payment events.
3. Events will be published to Kafka topics.

---

## Ingestion Layer

### Batch Ingestion
Batch ingestion will be handled using Python scripts and orchestrated by Apache Airflow.

**Flow:**
1. CSV files will be extracted using Python.
2. Data will be loaded into raw tables in PostgreSQL Database.
3. Airflow will schedule and monitor batch ingestion jobs.

### Streaming Ingestion
Streaming ingestion will be handled using Apache Kafka (producers and consumers).

**Flow:**
1. Producers will publish events to Kafka topics.
2. Consumers will read events and write them to staging tables.

---

## Storage Architecture

The storage layer will be divided into three logical schemas:

### Raw Layer
1. Stores data in its original structure.
2. No transformations will be applied in this layer.
3. Used for audit and reprocessing.

**Why?**
1. If there's a bug downstream, it can be reprocessed.
2. Separates data ingestion from business logic.

### Staging Layer
1. Stores cleaned and standardized data.
2. Applies basic schema alignment and type casting.
3. Acts as an intermediate transformation layer.

**Why?**
1. To ensure a clean and stable warehouse.
2. The warehouse will be free from technical logic.

### Data Warehouse Layer
1. Stores analytical-ready data.
2. Uses optimized star schema design (fact and dimension tables).

**Why?**
1. Business Intelligence (BI) requires a stable schema.
2. Queries will be faster.
3. Business logic will be consolidated.

---

## Processing Layer

### Batch Processing
Batch transformations will be handled using PySpark.

**Tasks:**
1. Join transactional data.
2. Aggregate payments and reviews.
3. Build fact and dimension tables.

**Why?**

Spark excels when:
1. Joining multiple tables.
2. Large aggregations.
3. Layered transformations.
4. Scalability (if data grows).

### Streaming Processing
Streaming data will be handled using Kafka consumers and optionally Spark Structured Streaming.

**Tasks:**
1. Consume real-time events.
2. Append data to staging tables.

---

## Orchestration

Apache Airflow will be used to orchestrate batch workflows.

**Tasks:**
1. Schedule batch ingestion jobs.
2. Define task dependencies.
3. Handle retries and monitoring.

**Why?**

Airflow is:
1. Scheduler.
2. Orchestrator.
3. Dependency manager

Airflow is NOT:
1. Real-time engine.
2. Streaming processor.

---

## Presentation Layer

The data warehouse will be served as the source for analytics and reporting.

**Our use cases:**
1. Sales dashboards.
2. Customer segmentation (RFM analysis).
3. Seller performance.
4. Product recommendation.

---

## Error Handling and Data Quality

The pipeline will be designed with data quality and reliability in mind, include:
1. Row count validation.
2. Schema validation.
3. Duplicate detection.
4. Logging and alerting.

---

## Architecture Diagram

A high-level architecture diagram illustrates end-to-end data flow from data sources to analytics consumption.
<img width="1920" height="1080" alt="Step 2 - Architecture and Data Flow" src="https://github.com/user-attachments/assets/40f6407c-5e73-4932-b532-fcabefb6a327" />

---

## Key Takeaways

1. The architecture will separate ingestion, processing, and storage.
2. Batch and streaming pipelines will run side by side in a hybrid design.
3. The design will support scalability, maintainability, and future extension.
