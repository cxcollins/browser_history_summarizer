from ingester import ingest_safari_history
from scraper import scrape_text_from_url
from summarizer import summarize_text

def main():
    records = ingest_safari_history(days_back=1)

    for record in records[10:]:
        url = record[0]
        print(f"\n URL: {url}")
        content = scrape_text_from_url(url)

        if not content:
            print("Scraping error")
            continue

        summary = summarize_text(content)
        print(f"Summary: {summary}")


if __name__ == '__main__':
    main()
