import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class LaforetScraper(BaseScraper):
    name = "laforet"
    base_url = "https://www.laforet.com"

    def _build_url(self, criteria: SearchCriteria, page: int) -> str:
        city = criteria.cities[0].lower() if criteria.cities else ""
        url = f"{self.base_url}/acheter/rechercher?lieu={city}"
        if criteria.budget_max:
            url += f"&budget_max={criteria.budget_max}"
        if criteria.budget_min:
            url += f"&budget_min={criteria.budget_min}"
        if criteria.surface_min:
            url += f"&surface_min={criteria.surface_min}"
        types = []
        for t in criteria.property_types:
            if t == "apartment":
                types.append("appartement")
            elif t == "house":
                types.append("maison")
        if types:
            url += f"&type_bien={','.join(types)}"
        if page > 1:
            url += f"&page={page}"
        return url

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        url = self._build_url(criteria, page)
        pw_page = self.browser.new_page(url, wait_for="[class*='property'], article, [class*='card']")
        if not pw_page:
            return []

        try:
            pw_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            import time
            time.sleep(2)

            cards = pw_page.query_selector_all("[class*='card-property'], [class*='CardProperty']")
            if not cards:
                cards = pw_page.query_selector_all("a[href*='/acheter/'][href*='pieces']")

            results = []
            seen_urls = set()
            for card in cards:
                prop = self._parse_card(card)
                if prop and prop.url not in seen_urls:
                    seen_urls.add(prop.url)
                    results.append(prop)
            return results
        finally:
            pw_page.close()

    def _parse_card(self, el) -> Property | None:
        try:
            link = el if el.evaluate("el => el.tagName") == "A" else el.query_selector("a[href*='/acheter/']")
            href = ""
            if link:
                href = link.get_attribute("href") or ""

            text = el.inner_text()
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            price = self._extract_price(text)
            surface = self._extract_surface(text)
            rooms = self._extract_rooms(text)

            city = ""
            property_type = ""
            for line in lines:
                low = line.lower()
                if "appartement" in low:
                    property_type = "apartment"
                elif "maison" in low:
                    property_type = "house"
                m = re.search(r"(?:à|a)\s+(.+?)(?:\s*\d{5})?$", line, re.I)
                if m and len(m.group(1)) > 2:
                    city = m.group(1).strip()

            if not city:
                for line in lines:
                    if re.match(r"^[A-ZÀ-Ÿ][a-zà-ÿ\s-]+$", line) and len(line) > 2:
                        city = line
                        break

            if not price:
                return None

            full_url = href if href.startswith("http") else f"{self.base_url}{href}"

            return Property(
                title=f"{property_type or 'Bien'} {rooms or ''}p {surface:.0f}m²" if surface else lines[0] if lines else "",
                price=price,
                city=city,
                surface=surface,
                rooms=rooms,
                property_type=property_type,
                url=full_url,
                source="laforet",
            )
        except Exception as e:
            logger.debug(f"[laforet] Parse error: {e}")
            return None
