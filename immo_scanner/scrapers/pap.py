import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class PapScraper(BaseScraper):
    name = "pap"
    base_url = "https://www.pap.fr"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        city = criteria.cities[0].lower() if criteria.cities else ""
        from immo_scanner.utils.geo import get_department
        dept = get_department(city) if city else ""

        url = f"{self.base_url}/annonce/vente-appartement-maison-{city}-{dept}"
        params = {"page": str(page)}
        if criteria.budget_max:
            params["prix-max"] = str(criteria.budget_max)
        if criteria.budget_min:
            params["prix-min"] = str(criteria.budget_min)

        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{param_str}"

        pw_page = self.browser.new_page(full_url)
        if not pw_page:
            return []

        try:
            import time
            time.sleep(3)

            captcha = pw_page.query_selector_all("iframe[src*='captcha'], [class*='captcha']")
            if captcha:
                logger.warning("[pap] Captcha detected, skipping")
                return []

            cards = pw_page.query_selector_all("[class*='search-list-item'], [class*='item-listing'], a[href*='annonces']")
            results = []
            for card in cards:
                text = card.inner_text()
                price = self._extract_price(text)
                surface = self._extract_surface(text)
                rooms = self._extract_rooms(text)

                link = card if card.evaluate("el => el.tagName") == "A" else card.query_selector("a[href]")
                href = link.get_attribute("href") if link else ""
                full_url = href if href and href.startswith("http") else f"{self.base_url}{href}" if href else ""

                if price:
                    results.append(Property(
                        title=text.split("\n")[0][:80],
                        price=price, surface=surface, rooms=rooms,
                        city="", url=full_url, source="pap",
                    ))
            return results
        finally:
            pw_page.close()
