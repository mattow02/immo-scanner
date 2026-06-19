import re
import json
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class SeLogerScraper(BaseScraper):
    name = "seloger"
    base_url = "https://www.seloger.com"

    def _build_url(self, criteria: SearchCriteria, page: int) -> str:
        city = criteria.cities[0].lower() if criteria.cities else ""
        from immo_scanner.utils.geo import get_department
        dept = get_department(city) if city else ""
        slug = f"immo-{city}-{dept}" if dept else f"immo-{city}" if city else ""

        types = []
        for t in criteria.property_types:
            if t == "apartment":
                types.append("appartement")
            elif t == "house":
                types.append("maison")
        type_slug = "+".join(types) if types else "appartement"

        url = f"{self.base_url}/immobilier/achat/{slug}/bien-{type_slug}/"
        params = []
        if criteria.budget_max:
            params.append(f"prix-max={criteria.budget_max}")
        if criteria.budget_min:
            params.append(f"prix-min={criteria.budget_min}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            url += "?" + "&".join(params)
        return url

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        url = self._build_url(criteria, page)
        pw_page = self.browser.new_page(url)
        if not pw_page:
            return []

        try:
            import time
            time.sleep(4)

            captcha = pw_page.query_selector_all("iframe[src*='captcha'], [class*='captcha']")
            if captcha:
                logger.warning("[seloger] Captcha detected, skipping")
                return []

            cards = pw_page.query_selector_all("[data-testid*='card'], article, [class*='Card']")
            results = []
            for card in cards:
                prop = self._parse_card(card)
                if prop:
                    results.append(prop)
            return results
        finally:
            pw_page.close()

    def _parse_card(self, el) -> Property | None:
        try:
            text = el.inner_text()
            price = self._extract_price(text)
            surface = self._extract_surface(text)
            rooms = self._extract_rooms(text)

            link = el.query_selector("a[href]")
            href = link.get_attribute("href") if link else ""
            full_url = href if href and href.startswith("http") else f"{self.base_url}{href}" if href else ""

            if not price:
                return None

            lines = [l.strip() for l in text.split("\n") if l.strip()]
            city = ""
            for line in lines:
                m = re.match(r"(\d{5})\s+(.+)", line)
                if m:
                    city = m.group(2)
                    break

            return Property(
                title=lines[0][:80] if lines else "",
                price=price, surface=surface, rooms=rooms,
                city=city, url=full_url, source="seloger",
            )
        except Exception as e:
            logger.debug(f"[seloger] Parse error: {e}")
            return None
