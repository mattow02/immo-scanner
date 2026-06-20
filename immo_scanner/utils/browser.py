import logging
import time
import random

logger = logging.getLogger(__name__)

PLAYWRIGHT_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright, Page
    from playwright_stealth import Stealth
    _stealth = Stealth()
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    sync_playwright = None
    Page = None
    _stealth = None


class BrowserClient:
    def __init__(self, headless=True, delay_min=2, delay_max=4):
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Install it with: pip install playwright playwright-stealth && playwright install chromium")
        self.headless = headless
        self.delay_min = delay_min
        self.delay_max = delay_max
        self._pw = None
        self._browser = None
        self._ctx = None

    def start(self):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        self._ctx = self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="fr-FR",
            timezone_id="Europe/Paris",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        )
        return self

    def stop(self):
        if self._ctx:
            self._ctx.close()
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.stop()

    def _wait(self):
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def new_page(self, url, wait_for=None, timeout=30000):
        self._wait()
        page = self._ctx.new_page()
        _stealth.apply_stealth_sync(page)
        try:
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            self._dismiss_cookies(page)
            if wait_for:
                try:
                    page.wait_for_selector(wait_for, timeout=8000)
                except Exception:
                    pass
            time.sleep(2)
            return page
        except Exception as e:
            logger.warning(f"Browser error on {url}: {e}")
            page.close()
            return None

    def _dismiss_cookies(self, page):
        for selector in [
            "button:has-text('Continuer sans accepter')",
            "button:has-text('Tout refuser')",
            "button:has-text('Refuser')",
            "button:has-text('Tout accepter')",
            "button[id*='accept']",
            "[class*='cookie'] button",
        ]:
            try:
                btn = page.query_selector(selector)
                if btn and btn.is_visible():
                    btn.click()
                    time.sleep(0.5)
                    return
            except Exception:
                continue
