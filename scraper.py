import requests
from bs4 import BeautifulSoup


def scrape_text_from_url(url: str, timeout: int = 5) -> str:
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unnecessary scripts, styles, etc.
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        clean_text = "\n".join([line for line in lines if line])
        return clean_text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""


def extract_title(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    title_tag = soup.find('title')
    return title_tag.get_text(strip=True) if title_tag else "No Title Found"
