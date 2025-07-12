import requests
from bs4 import BeautifulSoup
from src.config_loader.config_loader import WebScraperConfig

class WebScraper:
    """Extracts visible text content from a given URL."""

    def __init__(self, config: WebScraperConfig):
        self.timeout = config.timeout

    def fetch_text(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, "html.parser")

            for tag in soup(["script", "style", "img", "input"]):
                tag.decompose()

            return soup.get_text(separator="\n", strip=True)

        except Exception as e:
            return f"[Error scraping page]: {e}"