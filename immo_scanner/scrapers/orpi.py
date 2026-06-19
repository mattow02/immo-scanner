import re
import json
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class OrpiScraper(BaseScraper):
    name = "orpi"
    base_url = "https://www.orpi.com"

    def _build_url(self, criteria: SearchCriteria, page: int) -> str:
        city = criteria.cities[0].lower() if criteria.cities else ""
        types = []
        for t in criteria.property_types:
            if t == "apartment":
                types.append("appartement")
            elif t == "house":
                types.append("maison")
            elif t == "building":
                types.append("immeuble")

        parts = [f"{self.base_url}/recherche/buy?"]
        for i, t in enumerate(types):
            parts.append(f"types%5B{i}%5D={t}&")
        if city:
            parts.append(f"locations%5B0%5D%5Bvalue%5D={city}&locations%5B0%5D%5Blabel%5D={city.capitalize()}&")
        if criteria.budget_max:
            parts.append(f"maxPrice={criteria.budget_max}&")
        if criteria.budget_min:
            parts.append(f"minPrice={criteria.budget_min}&")
        if criteria.surface_min:
            parts.append(f"minSurface={criteria.surface_min}&")
        if page > 1:
            parts.append(f"page={page}&")

        return "".join(parts).rstrip("&")

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        url = self._build_url(criteria, page)
        pw_page = self.browser.new_page(url)
        if not pw_page:
            return []

        try:
            import time
            time.sleep(3)
            pw_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            script_data = pw_page.evaluate("""() => {
                const scripts = document.querySelectorAll('script[type="application/json"]');
                const results = [];
                scripts.forEach(s => {
                    if (s.textContent.length > 500) results.push(s.textContent);
                });
                return results;
            }""")

            results = []
            for raw in script_data:
                try:
                    data = json.loads(raw)
                    items = self._find_properties_in_json(data)
                    for item in items:
                        prop = self._parse_json_item(item)
                        if prop:
                            results.append(prop)
                except (json.JSONDecodeError, TypeError):
                    continue

            if not results:
                results = self._parse_html(pw_page)

            return results
        finally:
            pw_page.close()

    def _find_properties_in_json(self, data, depth=0) -> list[dict]:
        if depth > 5:
            return []
        results = []
        if isinstance(data, dict):
            if "price" in data and ("slug" in data or "address" in data):
                results.append(data)
            for v in data.values():
                results.extend(self._find_properties_in_json(v, depth + 1))
        elif isinstance(data, list):
            for item in data:
                results.extend(self._find_properties_in_json(item, depth + 1))
        return results

    def _parse_json_item(self, item: dict) -> Property | None:
        try:
            price = int(item.get("price", 0))
            if not price:
                return None

            slug = item.get("slug", "")
            url = f"{self.base_url}/acheter/{slug}" if slug else ""

            return Property(
                title=item.get("title", ""),
                price=price,
                city=item.get("city", ""),
                postal_code=str(item.get("zipcode", "")),
                surface=float(item.get("surface", 0)),
                rooms=item.get("nbRooms"),
                property_type=item.get("category", ""),
                url=url,
                source="orpi",
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
            )
        except Exception:
            return None

    def _parse_html(self, pw_page) -> list[Property]:
        cards = pw_page.query_selector_all("[class*='estate-overview'], [class*='annonce']")
        results = []
        for card in cards:
            text = card.inner_text()
            price = self._extract_price(text)
            surface = self._extract_surface(text)
            rooms = self._extract_rooms(text)

            link = card.query_selector("a[href*='/acheter/']")
            href = link.get_attribute("href") if link else ""
            full_url = href if href and href.startswith("http") else f"{self.base_url}{href}" if href else ""

            if price:
                results.append(Property(
                    title=text.split("\n")[0][:80],
                    price=price, surface=surface, rooms=rooms,
                    city="", url=full_url, source="orpi",
                ))
        return results
