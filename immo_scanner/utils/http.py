import random
import time
import logging
import cloudscraper
import requests
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

_ua = None


def _get_ua() -> UserAgent:
    global _ua
    if _ua is None:
        try:
            _ua = UserAgent()
        except Exception:
            _ua = None
    return _ua


def random_ua() -> str:
    ua = _get_ua()
    if ua:
        try:
            return ua.random
        except Exception:
            pass
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


class HttpClient:
    def __init__(self, delay_min=2, delay_max=5, timeout=15, proxy=None, use_cloudscraper=False):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout
        self.proxy = proxy
        self._last_request = 0.0

        if use_cloudscraper:
            self.session = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False}
            )
        else:
            self.session = requests.Session()

        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

    def _wait(self):
        elapsed = time.time() - self._last_request
        delay = random.uniform(self.delay_min, self.delay_max)
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def get(self, url, headers=None, params=None, max_retries=3) -> requests.Response | None:
        merged_headers = {"User-Agent": random_ua(), "Accept-Language": "fr-FR,fr;q=0.9"}
        if headers:
            merged_headers.update(headers)

        for attempt in range(max_retries):
            self._wait()
            try:
                resp = self.session.get(
                    url, headers=merged_headers, params=params, timeout=self.timeout
                )
                self._last_request = time.time()

                if resp.status_code == 200:
                    return resp
                if resp.status_code == 429:
                    wait = (2 ** attempt) * 5 + random.uniform(1, 3)
                    logger.warning(f"Rate limited on {url}, waiting {wait:.0f}s")
                    time.sleep(wait)
                    continue
                if resp.status_code >= 500:
                    wait = (2 ** attempt) * 2
                    logger.warning(f"Server error {resp.status_code} on {url}, retry in {wait}s")
                    time.sleep(wait)
                    continue
                logger.warning(f"HTTP {resp.status_code} on {url}")
                return None
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on {url} (attempt {attempt + 1})")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error on {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        logger.error(f"All retries failed for {url}")
        return None

    def get_json(self, url, headers=None, params=None) -> dict | list | None:
        resp = self.get(url, headers=headers, params=params)
        if resp:
            try:
                return resp.json()
            except ValueError:
                logger.warning(f"Invalid JSON from {url}")
        return None
