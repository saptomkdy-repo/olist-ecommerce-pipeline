import json
import time
import os
import uuid
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from kafka import KafkaProducer
from faker import Faker

fake = Faker('pt_BR')  # Brazilian Portuguese locale sesuai dataset Olist

# Environment variables with defaults
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092") # Kafka bootstrap servers (default to 'kafka:29092' for Docker setup)
INTERVAL = float(os.getenv("PRODUCER_INTERVAL_SECONDS", "2")) # Default 2 seconds between messages

# Kafka topics
ORDERS_TOPIC = "olist.orders"
PAYMENTS_TOPIC = "olist.payments"

# Constants for generating realistic data
ORDER_STATUS_LIST = ["created", "approved", "processing", "shipped", "delivered", "canceled"]
PAYMENT_TYPE_LIST = ["credit_card", "boleto", "voucher", "debit_card"]
STATE_LIST = [
    "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "ES", "PE",
    "CE", "PA", "MT", "MS", "RN", "PB", "AL", "PI", "MA", "SE"
]

# Create Kafka producer with retry logic
def create_producer():
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVERS, # Kafka bootstrap servers
                value_serializer=lambda v: json.dumps(v).encode("utf-8"), # Serialize value as JSON
                key_serializer=lambda k: k.encode("utf-8") if k else None, # Serialize key as UTF-8 string
            )
            print(f"[Producer] Connected to Kafka at {BOOTSTRAP_SERVERS}.")
            return producer
        except Exception as e:
            print(f"[Producer] Kafka not ready yet: {e}. Retrying in 5s...")
            time.sleep(5)

# Generate realistic order data
def generate_order():
    order_id = str(uuid.uuid4()) # uuid4 for unique order IDs
    customer_id = str(uuid.uuid4()) # uuid4 for unique customer IDs
    status = random.choice(ORDER_STATUS_LIST)
    purchase_ts = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat() # Timestamp in Jakarta timezone
    event_ts = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat() # Timestamp in Jakarta timezone

    return {
        "order_id": order_id,
        "customer_id": customer_id,
        "customer_unique_id": str(uuid.uuid4()),
        "customer_city": fake.city(),
        "customer_state": random.choice(STATE_LIST),
        "order_status": status,
        "order_purchase_timestamp": purchase_ts,
        "order_approved_at": purchase_ts if status != "created" else None,
        "price": round(random.uniform(10.0, 1000.0), 2), # Random uniform price between 10 and 1000
        "freight_value": round(random.uniform(5.0, 80.0), 2), # Random uniform freight value between 5 and 80
        "event_timestamp": event_ts
    }

# Generate realistic payment data linked to an order
def generate_payment(order_id):
    payment_type = random.choice(PAYMENT_TYPE_LIST)
    installments = random.randint(1, 12) if payment_type == "credit_card" else 1
    value = round(random.uniform(10.0, 1000.0), 2)
    event_ts = datetime.now(ZoneInfo("Asia/Jakarta")).isoformat()

    return {
        "order_id": order_id,
        "payment_sequential": 1,
        "payment_type": payment_type,
        "payment_installments": installments,
        "payment_value": value,
        "event_timestamp": event_ts
    }

# Main function to run the producer
def main():
    producer = create_producer()
    print(f"[Producer] Starting - interval: {INTERVAL}s.")
    print(f"[Producer] Topics: {ORDERS_TOPIC}, {PAYMENTS_TOPIC}.")

    msg_count = 0
    while True:
        try:
            # Generate and send order
            order = generate_order()
            producer.send(
                ORDERS_TOPIC,
                key=order["order_id"],
                value=order
            )

            # Generate and send payment for the same order
            payment = generate_payment(order["order_id"])
            producer.send(
                PAYMENTS_TOPIC,
                key=payment["order_id"],
                value=payment
            )

            # Flush to ensure messages are sent
            producer.flush()
            msg_count += 1
            print(f"[Producer] Sent message #{msg_count}, order_id: {order['order_id'][:8]}..., status: {order['order_status']}, payment: {payment['payment_type']}, value: {payment['payment_value']}.")

            time.sleep(INTERVAL)

        # Graceful shutdown on Ctrl+C
        except KeyboardInterrupt:
            print("[Producer] Stopped.")
            break
        # Handle other exceptions (e.g., Kafka connection issues) and retry
        except Exception as e:
            print(f"[Producer] Error: {e}.")
            time.sleep(5)


if __name__ == "__main__":
    main()