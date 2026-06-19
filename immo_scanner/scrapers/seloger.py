import logging
from datetime import datetime
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import get_postal_code

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "1", "house": "2", "building": "12"}
TRANSACTION_MAP = {"buy": "2", "rent": "1"}


class SeLogerScraper(BaseScraper):
    name = "seloger"
    base_url = "https://www.seloger.com/list.htm"

    def _needs_cloudscraper(self) -> bool:
        return True

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        transaction = TRANSACTION_MAP.get(criteria.transaction_type, "2")

        params = {
            "projects": transaction,
            "types": ",".join(TYPE_MAP.get(t, "1") for t in criteria.property_types),
            "natures": "1,2,4",
            "sort": "d_dt_crea",
            "LISTING-LISTpg": str(page),
        }

        if criteria.budget_min:
            params["pxmin"] = str(criteria.budget_min)
        if criteria.budget_max:
            params["pxmax"] = str(criteria.budget_max)
        if criteria.surface_min:
            params["surfacemin"] = str(criteria.surface_min)
        if criteria.surface_max:
            params["surfacemax"] = str(criteria.surface_max)

        if criteria.cities:
            codes = []
            for city in criteria.cities:
                pc = get_postal_code(city)
                if pc:
                    codes.append(pc)
            if codes:
                params["cp"] = ",".join(codes)
        elif criteria.departments:
            params["departments"] = ",".join(criteria.departments)

        headers = {
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://www.seloger.com/",
        }

        resp = self.client.get(self.base_url, headers=headers, params=params)
        if not resp:
            return []

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("[data-testid='sl.explore.card-container'], .c-pa-list .c-pa-city")

        if not cards:
            cards = soup.select("article, .Card__CardContainer, [class*='ListContent'] > div")

        results = []
        for card in cards:
            prop = self._parse_card(card)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_card(self, card) -> Property | None:
        try:
            title_el = card.select_one("a[title], h2, .card-title, [class*='Title']")
            title = title_el.get_text(strip=True) if title_el else ""

            link_el = card.select_one("a[href*='annonces']") or card.select_one("a[href]")
            url = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                url = href if href.startswith("http") else f"https://www.seloger.com{href}"

            price_el = card.select_one("[data-testid*='price'], .c-pa-cprice, [class*='Price']")
            price = 0
            if price_el:
                import re
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                if price_text:
                    price = int(price_text)

            city_el = card.select_one("[class*='City'], .c-pa-city, [class*='Location']")
            city = city_el.get_text(strip=True) if city_el else ""

            surface = 0.0
            rooms = None
            tags = card.select("[class*='Tag'], .c-pa-criterion, [class*='Criteria'] span")
            import re
            for tag in tags:
                text = tag.get_text(strip=True).lower()
                m = re.search(r"(\d+[.,]?\d*)\s*m", text)
                if m:
                    surface = float(m.group(1).replace(",", "."))
                m = re.search(r"(\d+)\s*p", text)
                if m:
                    rooms = int(m.group(1))

            if not title and not price:
                return None

            return Property(
                title=title,
                price=price,
                city=city,
                surface=surface,
                rooms=rooms,
                url=url,
                source="seloger",
            )
        except Exception as e:
            logger.debug(f"[seloger] Parse error: {e}")
            return None

    def _parse_listing(self, raw: dict) -> Property | None:
        return None
