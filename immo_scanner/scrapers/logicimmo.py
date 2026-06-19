import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import normalize_city

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "1", "house": "2", "building": "4"}
TRANSACTION_MAP = {"buy": "vente", "rent": "location"}


class LogicImmoScraper(BaseScraper):
    name = "logicimmo"
    base_url = "https://www.logic-immo.com"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        transaction = TRANSACTION_MAP.get(criteria.transaction_type, "vente")

        city_slug = "france"
        if criteria.cities:
            city_slug = ",".join(normalize_city(c) for c in criteria.cities)

        url = f"{self.base_url}/{transaction}-immobilier-{city_slug}.html"
        params = {"page": str(page)}

        if criteria.budget_min:
            params["pricemin"] = str(criteria.budget_min)
        if criteria.budget_max:
            params["pricemax"] = str(criteria.budget_max)
        if criteria.surface_min:
            params["areamin"] = str(criteria.surface_min)
        if criteria.surface_max:
            params["areamax"] = str(criteria.surface_max)

        types = [TYPE_MAP.get(t) for t in criteria.property_types if t in TYPE_MAP]
        if types:
            params["type"] = ",".join(types)

        resp = self.client.get(url, params=params)
        if not resp:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select(".offer-list__item, [class*='announceCard'], article[class*='Announce']")

        results = []
        for card in cards:
            prop = self._parse_card(card)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_card(self, card) -> Property | None:
        try:
            title_el = card.select_one("h3, .offer-details__title, [class*='Title']")
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = card.select_one("a[href*='detail']") or card.select_one("a[href]")
            url = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                url = href if href.startswith("http") else f"{self.base_url}{href}"

            price_el = card.select_one("[class*='price'], .offer-price")
            price = 0
            if price_el:
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                if price_text:
                    price = int(price_text)

            city_el = card.select_one("[class*='city'], .offer-details__location")
            city = city_el.get_text(strip=True) if city_el else ""
            city = re.sub(r"\(\d+\)", "", city).strip()

            surface = 0.0
            rooms = None
            criteria_els = card.select("[class*='criteria'] li, .offer-details__criteria span, [class*='Tag']")
            for el in criteria_els:
                text = el.get_text(strip=True).lower()
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
                rooms=rooms, url=url, source="logicimmo",
            )
        except Exception as e:
            logger.debug(f"[logicimmo] Parse error: {e}")
            return None

    def _parse_listing(self, raw: dict) -> Property | None:
        return None
