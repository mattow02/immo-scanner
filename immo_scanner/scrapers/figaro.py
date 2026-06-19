import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import normalize_city

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "appartement", "house": "maison", "building": "immeuble"}
TRANSACTION_MAP = {"buy": "vente", "rent": "location"}


class FigaroScraper(BaseScraper):
    name = "figaro"
    base_url = "https://immobilier.lefigaro.fr"

    def _needs_cloudscraper(self) -> bool:
        return True

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        transaction = TRANSACTION_MAP.get(criteria.transaction_type, "vente")

        city_slug = "france"
        if criteria.cities:
            city_slug = normalize_city(criteria.cities[0])

        url = f"{self.base_url}/annonces/immobilier-{transaction}-{city_slug}.html"
        params = {"page": str(page)}

        if criteria.budget_min:
            params["prix-min"] = str(criteria.budget_min)
        if criteria.budget_max:
            params["prix-max"] = str(criteria.budget_max)
        if criteria.surface_min:
            params["surface-min"] = str(criteria.surface_min)

        resp = self.client.get(url, params=params)
        if not resp:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("[class*='classified-card'], article, [class*='AdCard']")

        results = []
        for card in cards:
            prop = self._parse_card(card)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_card(self, card) -> Property | None:
        try:
            title_el = card.select_one("h2, h3, [class*='title'], a[title]")
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = card.select_one("a[href*='annonce']") or card.select_one("a[href]")
            url = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                url = href if href.startswith("http") else f"{self.base_url}{href}"

            price_el = card.select_one("[class*='price'], [class*='Price']")
            price = 0
            if price_el:
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                if price_text:
                    price = int(price_text)

            city_el = card.select_one("[class*='city'], [class*='location'], [class*='City']")
            city = city_el.get_text(strip=True) if city_el else ""

            surface = 0.0
            rooms = None
            text = card.get_text(" ", strip=True).lower()
            m = re.search(r"(\d+[.,]?\d*)\s*m[²2]", text)
            if m:
                surface = float(m.group(1).replace(",", "."))
            m = re.search(r"(\d+)\s*(?:pièce|piece|p\.)", text)
            if m:
                rooms = int(m.group(1))

            if not price:
                return None

            return Property(
                title=title, price=price, city=city, surface=surface,
                rooms=rooms, url=url, source="figaro",
            )
        except Exception as e:
            logger.debug(f"[figaro] Parse error: {e}")
            return None

    def _parse_listing(self, raw: dict) -> Property | None:
        return None
