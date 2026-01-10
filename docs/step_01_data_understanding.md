# 1\. Step 01 – Data Understanding

## Objective

**Purposes:** understanding the structure, relationships, and data quality characteristics of the Olist Brazilian
E-Commerce dataset before designing the data pipeline.

No transformation, cleaning, or other modifications is performed in this step, we are simply exploring the dataset.

## 2\. Dataset Overview

* Dataset: Olist Brazilian E-Commerce
* Source: [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
* License: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0)
* Data Format: CSV

### CSV Filenames (Tablenames)

* olist_orders_dataset (orders)
* olist_order_items_dataset (order_items)
* olist_order_payments_dataset (order_payments)
* olist_order_reviews_dataset (ordeR_reviews)
* olist_customers_dataset (customers)
* olist_products_dataset (products)
* olist_sellers_dataset (sellers)
* olist_geolocation_dataset (geolocation)
* product_category_name_translation (category_name)

### Table: orders

**Grain:** 1 row represents 1 order

**Primary Key:** `order_id`

**Foreign Keys:** `customer_id` → `customers` (`customer_id`)

**Key Observations:**

- One order belongs to exactly one customer
- One order (`order_id`) can have multiple order items (`order_items_id`), payments (`order_payments`), and reviews (`order_reviews`)

**Data Quality Notes:**

- No duplicate values found in `order_id`.
- Null values were only found in `order_approved_at`, `order_delivered_carrier_date`, and `order_delivered_customer_date`.

### Table: order_items

**Grain:** 1 row represents 1 `order_item_id` within an order.

**Primary Key:** Composite key `(order_id, order_item_id)`

**Foreign Keys:**  
- `order_id` → `orders` (`order_id`)
- `product_id` → `products`. (`product_id`)
- `seller_id` → `sellers` (`seller_id`)

**Key Observations:**
- `order_item_id` is only unique within one order, not globally unique in the table.
- `order_id` is not a unique column.
- One order (`order_id`) can contain multiple items (`order_item_id`).

**Data Quality Notes:**
- No null values found in all columns.
- No duplicate combinations of `(order_id, order_item_id)` observed.

### Table: order_payments

**Grain:** 1 row represents 1 payment (`payment_sequential`) within an order.

**Primary Key:** Composite key `(order_id, payment_sequential)`

**Foreign Keys:** `order_id` → `orders` (`order_id`)

**Key Observations:**
- `payment_sequential` is only unique within one order, not globally unique in the table.
- `order_id` is not a unique column.
- One order (`order_id`) can contain multiple payments (`payment_sequential`).

**Data Quality Notes:**
- No null values found in all columns.
- No duplicate combinations of `(order_id, payment_sequential)` observed.

### Table: order_reviews

**Grain:** 1 row represents 1 payment (`payment_sequential`) within an order.

**Primary Key:** Composite key `(order_id, payment_sequential)`

**Foreign Keys:**  
- `order_id` → `orders` (`order_id`)

**Key Observations:**
- `payment_sequential` is only unique within one order, not globally unique in the table.
- `order_id` is not a unique column.
- One order (`order_id`) can contain multiple payments (`payment_sequential`).

**Data Quality Notes:**
- No duplicate combinations of `(order_id, payment_sequential)` observed.
- Null values were only found in `review_comment_title` and `review_comment_message`.

### Table: customers

**Grain:** 1 row represents a customer snapshot (`customer_id`).

**Primary Key:** `customer_id`

**Foreign Keys (Logical):** `customer_zip_code_prefix` → geolocation (`geolocation_zip_code_prefix`)
- **Notes:** `customer_zip_code_prefix` is logically related to geolocation data based on zip code prefix, but referential integrity is not enforced due to non-unique keys (`geolocation_zip_code_prefix`) in the geolocation table.

**Key Observations:**
- `customer_unique_id` is not a unique column.
- Multiple `customer_id` values can map to the same `customer_unique_id`.
- `customer_unique_id may` represents the actual customer (real person identifier).
- `customer_unique_id` should not be used as a primary key.

**Data Quality Notes:**
- No null values found in all columns.
- No duplicate values found in `customer_id`.

### Table: products

**Grain:** 1 row represents 1 product (`product_id`).

**Primary Key:** `product_id`

**Foreign Keys:** `product_category_name` → category_name (`product_category_name`)

**Data Quality Notes:**
- Null values were only found in `product_category_name`, `product_name_lenght`, `product_description_lenght`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, and `product_width_cm`
- No duplicate values found in `product_id`.

### Table: sellers

**Grain:** 1 row represents 1 seller.

**Primary Key:** `seller_id`

**Foreign Keys (Logical):** `seller_zip_code_prefix` → geolocation (`geolocation_zip_code_prefix`)
- **Notes:** `seller_zip_code_prefix` is logically related to geolocation data based on zip code prefix, but referential integrity is not enforced due to non-unique keys (`geolocation_zip_code_prefix`) in the geolocation table.

**Data Quality Notes:**
- No null values found in all columns.
- No duplicate values found in `seller_id`.

### Table: geolocation

**Grain:** \-

**Primary Key:** \-

**Foreign Keys:** \-

**Key Observations:**
- No primary key can be created in this table.
- This table can be used as a reference or lookup table for location (`*_zip_code_prefix`) mapping.

**Data Quality Notes:**
- Duplicates occur in all columns in the corresponding rows for a total of 390005 rows.

### Table: category_name

**Grain:** 1 row represents 1 product name.

**Primary Key:** `product_category_name`

**Foreign Keys:** \-

**Data Quality Notes:**
- No null values found in all columns.
- No duplicate values found in `product_category_name`.

## Join Testing Summary

- orders &larr; customers
  - No orders without customers found.
  - 1 order only has 1 `customer_id`.

- orders &larr; order_items
  - One order can have multiple items.
  - There are orders without items (because `order_item_id` contains 775 null values).

- orders &larr; order_payments
  - Multiple payment attempts per order observed.
  - There is order without payment (because `payment_*` columns each contain one null value).

- orders &larr; order_reviews
  - Multiple review events per order observed.
  - There are orders without reviews (because `review_id` column contains 768 null values).

- order_items &larr; products
  - Different `order_item_id` can have same `product_id` in one `order_id`.
  - There are no items without `product_id`.

- order_items &larr; sellers
  - Different `order_item_id` can have same `seller_id` in one `order_id`.
  - There are no items without `seller_id`.

## Key Takeaways for Next Steps

- Natural and composite primary keys will be preserved from source data.
- Surrogate keys (SK) will be introduced in the data warehouse.
- Fact tables will be designed at item-level grain.
- Reviews and payments require aggregation before analytical use.