from ingester import ingest_safari_history
from scraper import scrape_text_from_url
from scraper import extract_title
from summarizer import summarize_text
from setup_db import setup
import sqlite3


def main():
    setup()
    records = ingest_safari_history(days_back=1)

    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()

    existing_urls = get_existing_urls(cursor)

    for record in records:
        url = record[0]
        time_visited = record[1]
        print(f"\n URL: {url}")

        if url in existing_urls:
            print(f"Skipping {url} - already processed")
            continue

        content = scrape_text_from_url(url)
        title = extract_title(content)

        if not content:
            print("Scraping error")
            continue

        summary = summarize_text(content)
        save_summary(cursor, url, title, summary, time_visited)
        existing_urls.add(url)

        print(f"Summary: {summary}")

    conn.commit()
    conn.close()


def get_existing_urls(cursor) -> set:
    cursor.execute('SELECT url FROM summaries')
    return {row[0] for row in cursor.fetchall()}


def save_summary(cursor, url: str, title: str, summary: str, visit_time: int):

    cursor.execute('''
    INSERT INTO summaries (url, title, summary, visit_time)
    VALUES (?, ?, ?, ?)
    ''', (url, title, summary, visit_time))


if __name__ == '__main__':
    main()
