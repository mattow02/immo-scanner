import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import get_department

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "appartement", "house": "maison", "building": "immeuble"}


class ParuVenduScraper(BaseScraper):
    name = "paruvendu"
    base_url = "https://www.paruvendu.fr/immobilier/annonceimmo"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        transaction = "V" if criteria.transaction_type == "buy" else "L"

        params = {
            "tt": transaction,
            "p": str(page),
        }

        types = []
        for t in criteria.property_types:
            if t in TYPE_MAP:
                types.append(TYPE_MAP[t])
        if types:
            params["tbApp"] = "1" if "appartement" in types else "0"
            params["tbMai"] = "1" if "maison" in types else "0"

        if criteria.budget_min:
            params["px0"] = str(criteria.budget_min)
        if criteria.budget_max:
            params["px1"] = str(criteria.budget_max)
        if criteria.surface_min:
            params["sur0"] = str(criteria.surface_min)
        if criteria.surface_max:
            params["sur1"] = str(criteria.surface_max)

        if criteria.cities:
            dept = get_department(criteria.cities[0])
            if dept:
                params["lo"] = dept

        resp = self.client.get(f"{self.base_url}/", params=params)
        if not resp:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select(".ergov3-annonce, .annonce, [class*='annonce-list'] li")

        results = []
        for card in cards:
            prop = self._parse_card(card)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_card(self, card) -> Property | None:
        try:
            title_el = card.select_one("h3, .ergov3-annonce__title, [class*='title']")
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = card.select_one("a[href*='annonce']")
            url = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                url = href if href.startswith("http") else f"https://www.paruvendu.fr{href}"

            price_el = card.select_one("[class*='price'], .ergov3-annonce__price")
            price = 0
            if price_el:
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                if price_text:
                    price = int(price_text)

            city_el = card.select_one("[class*='city'], .ergov3-annonce__location, [class*='localisation']")
            city = ""
            if city_el:
                city = re.sub(r"\(\d+\)", "", city_el.get_text(strip=True)).strip()

            surface = 0.0
            rooms = None
            desc = card.get_text(" ", strip=True).lower()
            m = re.search(r"(\d+[.,]?\d*)\s*m[²2]", desc)
            if m:
                surface = float(m.group(1).replace(",", "."))
            m = re.search(r"(\d+)\s*(?:pièce|piece|p\.)", desc)
            if m:
                rooms = int(m.group(1))

            if not price:
                return None

            return Property(
                title=title, price=price, city=city, surface=surface,
                rooms=rooms, url=url, source="paruvendu",
            )
        except Exception as e:
            logger.debug(f"[paruvendu] Parse error: {e}")
            return None

    def _parse_listing(self, raw: dict) -> Property | None:
        return None
