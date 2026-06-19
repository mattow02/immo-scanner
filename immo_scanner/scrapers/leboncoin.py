import logging
from datetime import datetime
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import get_department

logger = logging.getLogger(__name__)

CATEGORY_VENTE = "9"
CATEGORY_LOCATION = "10"

TYPE_MAP = {
    "apartment": "1",
    "house": "2",
    "building": "6",
}


class LeBonCoinScraper(BaseScraper):
    name = "leboncoin"
    base_url = "https://api.leboncoin.fr/finder/search"

    def _needs_cloudscraper(self) -> bool:
        return True

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        category = CATEGORY_LOCATION if criteria.transaction_type == "rent" else CATEGORY_VENTE

        filters = {"category": {"id": category}}

        ranges = {}
        if criteria.budget_min or criteria.budget_max:
            price_range = {}
            if criteria.budget_min:
                price_range["min"] = criteria.budget_min
            if criteria.budget_max:
                price_range["max"] = criteria.budget_max
            ranges["price"] = price_range

        if criteria.surface_min or criteria.surface_max:
            square_range = {}
            if criteria.surface_min:
                square_range["min"] = criteria.surface_min
            if criteria.surface_max:
                square_range["max"] = criteria.surface_max
            ranges["square"] = square_range

        if ranges:
            filters["ranges"] = ranges

        real_estate_types = []
        for pt in criteria.property_types:
            if pt in TYPE_MAP:
                real_estate_types.append(TYPE_MAP[pt])
        if real_estate_types:
            filters["enums"] = {"real_estate_type": real_estate_types}

        location = {}
        if criteria.cities:
            locations = []
            for city in criteria.cities:
                dept = get_department(city)
                loc = {"city": city.capitalize(), "locationType": "city"}
                if dept:
                    loc["department_id"] = dept
                locations.append(loc)
            location["locations"] = locations
        elif criteria.departments:
            location["locations"] = [
                {"department_id": d, "locationType": "department"} for d in criteria.departments
            ]

        payload = {
            "limit": 35,
            "limit_alu": 0,
            "offset": (page - 1) * 35,
            "filters": filters,
        }
        if location:
            payload["filters"]["location"] = location

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api_key": "ba0c2dad52b3ec",
            "Origin": "https://www.leboncoin.fr",
            "Referer": "https://www.leboncoin.fr/",
        }

        resp = self.client.session.post(
            self.base_url,
            json=payload,
            headers={**headers, "User-Agent": self.client.session.headers.get("User-Agent", "")},
            timeout=self.client.timeout,
        )

        if not resp or resp.status_code != 200:
            logger.warning(f"[leboncoin] HTTP {resp.status_code if resp else 'None'}")
            return []

        data = resp.json()
        ads = data.get("ads", [])
        results = []
        for ad in ads:
            prop = self._parse_listing(ad)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_listing(self, raw: dict) -> Property | None:
        try:
            attrs = {}
            for attr in raw.get("attributes", []):
                attrs[attr.get("key", "")] = attr.get("value", "")

            price = 0
            price_list = raw.get("price", [])
            if price_list:
                price = int(price_list[0])

            location = raw.get("location", {})
            images = raw.get("images", {})
            image_url = ""
            if images and images.get("urls"):
                image_url = images["urls"][0]

            date_posted = None
            if raw.get("first_publication_date"):
                try:
                    date_posted = datetime.fromisoformat(raw["first_publication_date"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

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

            return Property(
                title=raw.get("subject", ""),
                price=price,
                city=location.get("city", ""),
                postal_code=location.get("zipcode", ""),
                address=location.get("address", ""),
                surface=surface,
                rooms=rooms,
                property_type=attrs.get("real_estate_type", ""),
                description=raw.get("body", ""),
                url=raw.get("url", f"https://www.leboncoin.fr/ad/ventes_immobilieres/{raw.get('list_id', '')}"),
                source="leboncoin",
                image_url=image_url,
                dpe=attrs.get("energy_rate", ""),
                latitude=location.get("lat"),
                longitude=location.get("lng"),
                date_posted=date_posted,
                raw_data=raw,
            )
        except Exception as e:
            logger.debug(f"[leboncoin] Parse error: {e}")
            return None
