import requests
import random
import time
import logging
from bs4 import BeautifulSoup
from typing import Optional
from src.config import USER_AGENTS, PROXY_LIST

logger = logging.getLogger(__name__)


class Scraper:
    """
    Resilient web scraper with:
    - Random User-Agent rotation
    - Proxy rotation
    - Rate limiting with jitter
    - Retry logic with exponential backoff
    - Error recovery
    """

    def __init__(self, delay_range: tuple = (1.5, 4.0), max_retries: int = 3):
        self.delay_range  = delay_range
        self.max_retries  = max_retries
        self.proxies_list = [p for p in PROXY_LIST if p.strip()]
        self.session      = requests.Session()

    def _get_headers(self) -> dict:
        return {
            "User-Agent":      random.choice(USER_AGENTS),
            "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT":             "1",
            "Connection":      "keep-alive",
        }

    def _get_proxy(self) -> Optional[dict]:
        if not self.proxies_list:
            return None
        proxy = random.choice(self.proxies_list)
        return {"http": proxy, "https": proxy}

    def _wait(self):
        """Wait with random jitter to avoid rate limiting."""
        time.sleep(random.uniform(*self.delay_range))

    def fetch(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a URL and return BeautifulSoup object."""
        for attempt in range(1, self.max_retries + 1):
            try:
                self._wait()
                response = self.session.get(
                    url,
                    headers=self._get_headers(),
                    proxies=self._get_proxy(),
                    timeout=15
                )
                response.raise_for_status()
                return BeautifulSoup(response.text, "html.parser")

            except requests.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limited — wait longer
                    wait = 30 * attempt
                    logger.warning(f"Rate limited. Waiting {wait}s before retry {attempt}...")
                    time.sleep(wait)
                elif e.response.status_code in (403, 404):
                    logger.error(f"Access denied or not found: {url}")
                    return None
                else:
                    logger.error(f"HTTP {e.response.status_code} for {url}")

            except requests.RequestException as e:
                backoff = 2 ** attempt
                logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {backoff}s...")
                time.sleep(backoff)

        logger.error(f"All {self.max_retries} attempts failed for {url}")
        return None

    def extract_price(self, soup: BeautifulSoup, selectors: list) -> Optional[float]:
        """
        Try multiple CSS selectors to extract a price.
        Returns cleaned float or None.
        """
        for selector in selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    raw = element.get_text(strip=True)
                    price = self._clean_price(raw)
                    if price:
                        return price
            except Exception:
                continue
        return None

    def _clean_price(self, raw: str) -> Optional[float]:
        """Clean price strings like '₹1,299.00' or 'Rs. 450' to float."""
        import re
        # Remove currency symbols and whitespace
        cleaned = re.sub(r"[₹$€£Rs.\s,]", "", raw)
        # Extract number
        match = re.search(r"(\d+\.?\d*)", cleaned)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
