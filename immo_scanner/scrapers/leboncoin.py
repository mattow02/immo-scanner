import logging
from curl_cffi import requests as cffi_requests
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import get_department

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "1", "house": "2", "building": "6"}


class LeBonCoinScraper(BaseScraper):
    needs_browser = False
    name = "leboncoin"
    base_url = "https://api.leboncoin.fr/finder/search"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        filters = {"category": {"id": "9"}}

        ranges = {}
        if criteria.budget_min or criteria.budget_max:
            price_range = {}
            if criteria.budget_min:
                price_range["min"] = criteria.budget_min
            if criteria.budget_max:
                price_range["max"] = criteria.budget_max
            ranges["price"] = price_range
        if criteria.surface_min or criteria.surface_max:
            sq = {}
            if criteria.surface_min:
                sq["min"] = criteria.surface_min
            if criteria.surface_max:
                sq["max"] = criteria.surface_max
            ranges["square"] = sq
        if ranges:
            filters["ranges"] = ranges

        re_types = [TYPE_MAP[t] for t in criteria.property_types if t in TYPE_MAP]
        if re_types:
            filters["enums"] = {"real_estate_type": re_types}

        if criteria.cities:
            locations = []
            for city in criteria.cities:
                dept = get_department(city)
                loc = {"city": city.capitalize(), "locationType": "city"}
                if dept:
                    loc["department_id"] = dept
                locations.append(loc)
            filters["location"] = {"locations": locations}
        elif criteria.departments:
            filters["location"] = {
                "locations": [{"department_id": d, "locationType": "department"} for d in criteria.departments]
            }

        payload = {
            "limit": 35,
            "offset": (page - 1) * 35,
            "filters": filters,
        }

        import time, random
        time.sleep(random.uniform(1, 3))

        try:
            resp = cffi_requests.post(
                self.base_url,
                json=payload,
                headers={
                    "api_key": "ba0c2dad52b3ec",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Origin": "https://www.leboncoin.fr",
                    "Referer": "https://www.leboncoin.fr/",
                },
                impersonate="chrome",
                timeout=15,
            )
        except Exception as e:
            logger.error(f"[leboncoin] Request failed: {e}")
            return []

        if resp.status_code != 200:
            logger.warning(f"[leboncoin] HTTP {resp.status_code}")
            return []

        data = resp.json()
        ads = data.get("ads", [])
        results = []
        for ad in ads:
            prop = self._parse_ad(ad)
            if prop:
                results.append(prop)
        return results

    def _parse_ad(self, ad: dict) -> Property | None:
        try:
            price_list = ad.get("price", [])
            price = int(price_list[0]) if price_list else 0
            if not price:
                return None

            location = ad.get("location", {})
            attrs = {a.get("key", ""): a.get("value", "") for a in ad.get("attributes", [])}

            surface = 0.0
            if attrs.get("square"):
                try:
                    surface = float(attrs["square"])
                except (ValueError, TypeError):
                    pass

            rooms = None
            if attrs.get("rooms"):
                try:
                    rooms = int(attrs["rooms"])
                except (ValueError, TypeError):
                    pass

            from datetime import datetime
            date_posted = None
            if ad.get("first_publication_date"):
                try:
                    date_posted = datetime.fromisoformat(ad["first_publication_date"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            images = ad.get("images", {})
            image_url = images.get("urls", [""])[0] if images else ""

            return Property(
                title=ad.get("subject", ""),
                price=price,
                city=location.get("city", ""),
                postal_code=location.get("zipcode", ""),
                address=location.get("address", ""),
                surface=surface,
                rooms=rooms,
                property_type=attrs.get("real_estate_type", ""),
                description=ad.get("body", ""),
                url=ad.get("url", f"https://www.leboncoin.fr/ad/ventes_immobilieres/{ad.get('list_id', '')}"),
                source="leboncoin",
                image_url=image_url,
                dpe=attrs.get("energy_rate", ""),
                latitude=location.get("lat"),
                longitude=location.get("lng"),
                date_posted=date_posted,
            )
        except Exception as e:
            logger.debug(f"[leboncoin] Parse error: {e}")
            return None
