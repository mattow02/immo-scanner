import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import normalize_city

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "appartement", "house": "maison", "building": "immeuble"}
TRANSACTION_MAP = {"buy": "vente", "rent": "location"}


class PapScraper(BaseScraper):
    name = "pap"
    base_url = "https://www.pap.fr/annonce"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        transaction = TRANSACTION_MAP.get(criteria.transaction_type, "vente")
        types_path = "-".join(TYPE_MAP.get(t, "appartement") for t in criteria.property_types)

        city_part = ""
        if criteria.cities:
            city_part = "-".join(normalize_city(c) for c in criteria.cities)
        else:
            city_part = "france"

        url = f"{self.base_url}/{transaction}-{types_path}-{city_part}"

        params = {"page": str(page)}
        if criteria.budget_min:
            params["prix-min"] = str(criteria.budget_min)
        if criteria.budget_max:
            params["prix-max"] = str(criteria.budget_max)
        if criteria.surface_min:
            params["surface-min"] = str(criteria.surface_min)
        if criteria.surface_max:
            params["surface-max"] = str(criteria.surface_max)

        resp = self.client.get(url, params=params)
        if not resp:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select(".search-list-item, .search-results-item, [class*='adListItem']")

        results = []
        for card in cards:
            prop = self._parse_card(card)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_card(self, card) -> Property | None:
        try:
            title_el = card.select_one("h2, .item-title, [class*='title'] a")
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = card.select_one("a[href*='annonce']")
            url = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                url = href if href.startswith("http") else f"https://www.pap.fr{href}"

            price_el = card.select_one(".item-price, [class*='price']")
            price = 0
            if price_el:
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                if price_text:
                    price = int(price_text)

            city_el = card.select_one(".item-description em, .item-city, [class*='city']")
            city = ""
            if city_el:
                city_text = city_el.get_text(strip=True)
                city = re.sub(r"\(\d+\)", "", city_text).strip()

            surface = 0.0
            rooms = None
            tags_el = card.select(".item-tags li, .item-criteria span, [class*='Tag']")
            for tag in tags_el:
                text = tag.get_text(strip=True).lower()
                m = re.search(r"(\d+[.,]?\d*)\s*m", text)
                if m:
                    surface = float(m.group(1).replace(",", "."))
                m = re.search(r"(\d+)\s*p", text)
                if m:
                    rooms = int(m.group(1))

            if not price:
                return None

            return Property(
                title=title, price=price, city=city, surface=surface,
                rooms=rooms, url=url, source="pap",
            )
        except Exception as e:
            logger.debug(f"[pap] Parse error: {e}")
            return None

    def _parse_listing(self, raw: dict) -> Property | None:
        return None
