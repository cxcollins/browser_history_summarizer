import os
import json
import pika
import time
from ingester import ingest_safari_history

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
DAYS_BACK = int(os.getenv("DAYS_BACK", "1"))


def connect_rabbitmq():
    """Connect to RabbitMQ with retry logic"""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            print(f"[publisher] connected to RabbitMQ at {RABBITMQ_HOST}")
            return connection
        except Exception as e:
            print(f"[publisher] failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    raise Exception("Failed to connect to RabbitMQ after all retries")


def main():
    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue="urls", durable=True)

    print(f"[publisher] ingesting Safari history for last {DAYS_BACK} days...")
    records = ingest_safari_history(days_back=DAYS_BACK)
    print(f"[publisher] found {len(records)} history records")

    published = 0
    for url, visit_time in records:
        if not url:
            continue
        message = json.dumps({"url": url, "visit_time": visit_time})
        channel.basic_publish(
            exchange="",
            routing_key="urls",
            body=message.encode("utf-8"),
            properties=pika.BasicProperties(delivery_mode=2)  # persistent
        )
        published += 1
        if published % 100 == 0:
            print(f"[publisher] queued {published} URLs...")

    print(f"[publisher] finished - queued {published} URLs total")
    connection.close()


if __name__ == "__main__":
    main()
