# 3. Step 03 - Step Data Modeling

## Data Warehouse Schema

In our schema:
- **Fact** tables represent **events or transactions** (store quantitative, numerical measurements of business processes, e.g. quantity sold, price, etc.).
- **Dimension** tables represent the **context** or **descriptive attributes** (what, who, where, and when).
- Analytics (in data warehouse) requires OLAP (Online Analytical Processing) or denormalization schema and focuses on large-scale historical data analysis for decision making, using complex queries.

### Fact & Dimension Tables
a. Our **primary fact** is `olist_order_items_dataset` (`fact_order_items`) because:
- It represents actual sales/orders event.
- Most granular (or detailed): 1 row = 1 order item.

b. `olist_order_payments_dataset` (`fact_payments`) and `olist_order_reviews_dataset` (`fact_reviews`) are also selected as fact tables, but not primary facts because they contains amounts, measures, and can be summed.

c. `olist_order_customers_dataset` (`dim_customers`), `olist_products_dataset` (`dim_products`), `olist_sellers_dataset` (`dim_sellers`), and `olist_geolication_dataset` (`dim_geolocation`) are selected as dimension tables.

d. Date dimension (`dim_date`) need to be created to break down dates into attributes such as year, month, day, and so on to facilitate time analysis.

e. `olist_orders_dataset` is not selected as a fact table because it does not contain transactions but rather order headers.

### Notes for Primary Key & Foreign Key in Data Warehouse
We don't carry the primary key from the data source as is. We have to redesign it to suit our analytics needs. The warehouse isn't a mirror of the source. In this case, we need to design surrogate keys.
- Natural keys are unique, existing real-data attributes with business meaning.
- Surrogate keys are system-generated with no business meaning.
- Natural keys are used to identify records but risk needing updates if business rules change.
- Surrogate keys are superior in terms of stability, performance, and simplicity for join operations and data warehouse modeling.
- Natural keys are ideal for data validation.
- Surrogate keys are ideal for primary keys to ensure high performance and stability.

In this case, natural and composite keys are too long and have the potential to make joins slow and unstable, so we will use the surrogate key as the primary key, while the natural and composite keys remain stored in the table for traceability and debugging.

### Data Warehouse Schema Diagram
<img width="1085" height="513" alt="image" src="https://github.com/user-attachments/assets/19e32637-89e4-4f57-bcfa-7ec162728184" />
The diagram above is created using draw.io.

Our data warehouse schema follows a star schema design with a lightly snowflaked in geolocation dimension to avoid duplication and maintain consistent location attributes across customers and sellers.

Some columns need to be removed because they are not used for business analysis purposes, such as column `payment_sequential`, `product_description_length`, and etc.

In our schema, `order_id` is selected as a degenerate dimension since it is a business-critical identifier used across multiple fact tables without requiring additional descriptive attributes.

**Degenerate dimension** is a dimension key that is stored in the fact table, does not have its own dimension table, can be used for identification & join, and usually without descriptive attributes. So, it is a dimension conceptually (used for grouping or filtering), but it is "degenerate" because it has no description.

The `order_id` column is not made into a `dim_order` dimension since it does not have a stable attribute that needs to be "dimensioned".
