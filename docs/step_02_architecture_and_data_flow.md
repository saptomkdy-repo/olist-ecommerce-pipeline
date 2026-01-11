# Step 02 - Architecture and Data Flow

## Objective
**Purposes:** defines end-to-end data architecture and data flow
for the Olist Brazilian E-Commerce data pipeline. The goal is to
design a scalable, reliable, and industry-aligned architecture
before implementing the pipeline.

No transformation, cleaning, or other modifications is performed in this step.

---

## Pipeline

We design a hybrid data pipeline. It means our pipeline will consist of:
1. batch pipeline; and
2. real-time streaming pipeline
to reflect real-world e-commerce data workflows.

We know that:
- Batch pipeline is used for historical and scheduled data ingestion.
- Real-time streaming pipeline is used to simulate real-time order and payment events.

---

## Data Sources

### Batch Data Sources
- Olist CSV datasets (Orders, Order Items, Customers, Products, Sellers, Payments, Reviews, Geolocation)
- Data is treated as historical and incremental batch data.

### Streaming Data Sources
- Simulated order events
- Simulated payment events
- Events are published to Kafka topics.

---

## Ingestion Layer

### Batch Ingestion
Batch ingestion is handled using Python scripts orchestrated by Apache Airflow.

Flow:
- CSV files are extracted using Python
- Data is loaded into raw tables in PostgreSQL
- Airflow schedules and monitors batch ingestion jobs

### Streaming Ingestion
Streaming ingestion is handled using Kafka producers and consumers.

Flow:
- Producers publish events to Kafka topics
- Consumers read events and write them to staging tables

---

## Storage Architecture

The storage layer is divided into three logical schemas:

### Raw Layer
- Stores data in its original structure
- No transformations are applied
- Used for audit and reprocessing

### Staging Layer
- Stores cleaned and standardized data
- Applies basic schema alignment and type casting
- Acts as an intermediate transformation layer

### Data Warehouse Layer
- Stores analytical-ready data
- Uses star schema design
- Contains fact and dimension tables

---

## Processing Layer

### Batch Processing
Batch transformations are handled using PySpark.

Responsibilities:
- Join transactional data
- Aggregate payments and reviews
- Build fact and dimension tables

### Streaming Processing
Streaming data is processed using Kafka consumers and optionally Spark Structured Streaming.

Responsibilities:
- Consume real-time events
- Append data to staging tables

---

## Orchestration

Apache Airflow is used to orchestrate batch workflows.

Responsibilities:
- Schedule batch ingestion jobs
- Define task dependencies
- Handle retries and monitoring

---

## Analytics and Consumption Layer

The data warehouse serves as the source for analytics and reporting.

Use cases include:
- Sales performance dashboards
- Customer segmentation (RFM analysis)
- Seller performance analysis
- Product recommendation inputs

---

## Error Handling and Data Quality (Design Consideration)

The pipeline is designed with data quality and reliability in mind.

Planned checks include:
- Row count validation
- Schema validation
- Duplicate detection
- Logging and alerting

---

## Architecture Diagram

A high-level architecture diagram illustrates the end-to-end data flow
from data sources to analytics consumption.

(The diagram is provided separately.)

---

## Key Takeaways

- The architecture separates ingestion, processing, and storage concerns
- Batch and streaming pipelines coexist in a hybrid design
- The design supports scalability, maintainability, and future extension
