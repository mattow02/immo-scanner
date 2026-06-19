import re
import logging
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

CITY_PLACE_IDS = {
    "paris": "750056",
    "marseille": "130055",
    "lyon": "690123",
    "toulouse": "310555",
    "nice": "060088",
    "nantes": "440109",
    "montpellier": "340172",
    "strasbourg": "670482",
    "bordeaux": "330063",
    "lille": "590350",
    "rennes": "350238",
    "reims": "510454",
    "saint-etienne": "420218",
    "grenoble": "380185",
    "dijon": "210231",
    "angers": "490007",
    "nimes": "300189",
    "clermont-ferrand": "630113",
    "tours": "370261",
    "rouen": "760540",
    "caen": "140118",
    "orleans": "450234",
    "nancy": "540395",
    "metz": "570463",
}

TYPE_MAP = {"apartment": "1", "house": "2", "building": "12"}


class SeLogerScraper(BaseScraper):
    needs_browser = False
    supports_multi_city = True
    name = "seloger"
    base_url = "https://www.seloger.com/list.htm"

    def _get_place_id(self, city: str) -> str:
        from immo_scanner.utils.geo import normalize_city
        return CITY_PLACE_IDS.get(normalize_city(city), "")

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        places = []
        for city in criteria.cities:
            pid = self._get_place_id(city)
            if pid:
                places.append(f"{{ci:{pid}}}")
        if not places and criteria.departments:
            for dept in criteria.departments:
                places.append(f"{{cp:{dept}}}")

        if not places:
            logger.warning("[seloger] No valid city/department for search")
            return []

        types = ",".join(TYPE_MAP.get(t, "1") for t in criteria.property_types if t in TYPE_MAP)

        price_str = f"{criteria.budget_min or 'NaN'}/{criteria.budget_max or 'NaN'}"

        params = {
            "projects": "2",
            "types": types or "1,2",
            "natures": "1,2,4",
            "places": "[" + ",".join(places) + "]",
            "price": price_str,
            "enterprise": "0",
            "qsVersion": "1.0",
            "LISTING-LISTpg": str(page),
        }
        if criteria.surface_min:
            params["surface"] = f"{criteria.surface_min}/NaN"

        import time, random
        time.sleep(random.uniform(1.5, 3.5))

        try:
            resp = cffi_requests.get(
                self.base_url,
                params=params,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                    "Referer": "https://www.seloger.com/",
                },
                impersonate="chrome",
                timeout=20,
            )
        except Exception as e:
            logger.error(f"[seloger] Request failed: {e}")
            return []

        if resp.status_code != 200:
            logger.warning(f"[seloger] HTTP {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        cards = soup.select("[data-testid='sl.explore.card-container']")
        if not cards:
            cards = soup.select("article")

        results = []
        for card in cards:
            prop = self._parse_card(card)
            if prop:
                results.append(prop)
        return results

    def _parse_card(self, card) -> Property | None:
        try:
            text = card.get_text(" ", strip=True)

            link = card.select_one("a[href*='annonces']")
            href = link.get("href", "") if link else ""
            full_url = href if href.startswith("http") else f"https://www.seloger.com{href}" if href else ""

            prices = re.findall(r"([\d\s]+)\s*€", text.replace("\xa0", " "))
            price = 0
            if prices:
                price = int(prices[0].replace(" ", ""))

            surface_m = re.search(r"(\d+[.,]?\d*)\s*m[²2]", text)
            surface = float(surface_m.group(1).replace(",", ".")) if surface_m else 0.0

            rooms_m = re.search(r"(\d+)\s*pièce", text)
            rooms = int(rooms_m.group(1)) if rooms_m else None

            city = ""
            postal_code = ""
            city_m = re.search(r"à\s+([A-ZÀ-Ÿ][a-zà-ÿ\s-]+)\s*\((\d{5})\)", text)
            if city_m:
                city = city_m.group(1).strip()
                postal_code = city_m.group(2)
            else:
                city_m2 = re.search(r"(\d{5})", text)
                if city_m2:
                    postal_code = city_m2.group(1)

            prop_type = ""
            text_lower = text.lower()
            if "appartement" in text_lower or "studio" in text_lower:
                prop_type = "apartment"
            elif "maison" in text_lower:
                prop_type = "house"

            if not price:
                return None

            title_parts = []
            if prop_type == "apartment":
                if rooms and rooms == 1:
                    title_parts.append("Studio")
                else:
                    title_parts.append("Appartement")
            elif prop_type == "house":
                title_parts.append("Maison")
            if rooms and rooms > 1:
                title_parts.append(f"{rooms}p")
            if surface:
                title_parts.append(f"{surface:.0f}m²")

            return Property(
                title=" ".join(title_parts) or text[:60],
                price=price,
                city=city,
                postal_code=postal_code,
                surface=surface,
                rooms=rooms,
                property_type=prop_type,
                url=full_url,
                source="seloger",
            )
        except Exception as e:
            logger.debug(f"[seloger] Parse error: {e}")
            return None
