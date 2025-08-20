import os, json, sqlite3, pika, signal, sys, time
from scraper import scrape_text_from_url, extract_title
from summarizer import summarize_text
from setup_db import setup_database

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
BATCH_SIZE = 10
buffer = []

DB_PATH = "/app/data/summaries.db"


def save_buffer():
    global buffer
    if not buffer:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executemany("""
        INSERT OR IGNORE INTO summaries (url, title, summary, visit_time)
        VALUES (?, ?, ?, ?)
    """, buffer)
    conn.commit()
    conn.close()
    print(f"[worker] flushed {len(buffer)} records to DB")
    buffer = []


def callback(ch, method, properties, body):
    global buffer
    msg = json.loads(body.decode("utf-8"))
    url = msg["url"]
    visit_time = msg["visit_time"]

    print(f"[worker] processing {url}")
    content = scrape_text_from_url(url)
    if not content:
        print(f"[worker] scrape failed {url}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    title = extract_title(content)
    summary = summarize_text(content)
    if not summary:
        print(f"[worker] summarization failed {url}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    buffer.append((url, title, summary, visit_time))

    if len(buffer) >= BATCH_SIZE:
        save_buffer()

    ch.basic_ack(delivery_tag=method.delivery_tag)


def shutdown(sig, frame):
    print("[worker] shutting down, flushing buffer…")
    save_buffer()
    sys.exit(0)


def connect_rabbitmq():
    """Connect to RabbitMQ with retry logic"""
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            print(f"[worker] connected to RabbitMQ at {RABBITMQ_HOST}")
            return connection
        except Exception as e:
            print(f"[worker] failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    raise Exception("Failed to connect to RabbitMQ after all retries")


def main():
    setup_database()
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue="urls", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="urls", on_message_callback=callback)

    print("[worker] waiting for messages…")
    channel.start_consuming()


if __name__ == "__main__":
    main()
