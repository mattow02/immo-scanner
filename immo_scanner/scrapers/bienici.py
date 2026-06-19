import logging
from datetime import datetime
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import get_postal_code

logger = logging.getLogger(__name__)

TYPE_MAP = {"apartment": "flat", "house": "house", "building": "building"}


class BienIciScraper(BaseScraper):
    name = "bienici"
    base_url = "https://www.bienici.com/realEstateAds.json"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        property_types = [TYPE_MAP.get(t, "flat") for t in criteria.property_types]

        filters = {
            "size": 24,
            "from": (page - 1) * 24,
            "filterType": "rent" if criteria.transaction_type == "rent" else "buy",
            "propertyType": property_types,
            "sortBy": "relevance",
            "sortOrder": "desc",
        }

        if criteria.budget_min:
            filters["minPrice"] = criteria.budget_min
        if criteria.budget_max:
            filters["maxPrice"] = criteria.budget_max
        if criteria.surface_min:
            filters["minArea"] = criteria.surface_min
        if criteria.surface_max:
            filters["maxArea"] = criteria.surface_max
        if criteria.rooms_min:
            filters["minRooms"] = criteria.rooms_min
        if criteria.rooms_max:
            filters["maxRooms"] = criteria.rooms_max

        if criteria.cities:
            zone_ids = []
            for city in criteria.cities:
                pc = get_postal_code(city)
                if pc:
                    zone_ids.append(pc)
            if zone_ids:
                filters["zoneIdsByTypes"] = {"zoneIds": [{"id": z, "type": "postalCode"} for z in zone_ids]}

        headers = {
            "Accept": "application/json",
            "Referer": "https://www.bienici.com/",
            "Origin": "https://www.bienici.com",
        }

        data = self.client.get_json(self.base_url, headers=headers, params={"filters": str(filters)})
        if not data:
            resp = self.client.get(
                "https://www.bienici.com/recherche/achat/" + (criteria.cities[0] if criteria.cities else "france"),
                headers={"Accept": "text/html"},
            )
            if resp:
                return self._parse_html(resp.text, criteria)
            return []

        ads = data.get("realEstateAds", [])
        results = []
        for ad in ads:
            prop = self._parse_listing(ad)
            if prop and self._filter_result(prop, criteria):
                results.append(prop)
        return results

    def _parse_html(self, html: str, criteria: SearchCriteria) -> list[Property]:
        import re
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        cards = soup.select("[class*='RealEstateAd'], article, [class*='ad-overview']")

        results = []
        for card in cards:
            title_el = card.select_one("h2, [class*='Title'], a[title]")
            title = title_el.get_text(strip=True) if title_el else ""

            price_el = card.select_one("[class*='Price'], [class*='price']")
            price = 0
            if price_el:
                price_text = re.sub(r"[^\d]", "", price_el.get_text())
                if price_text:
                    price = int(price_text)

            link_el = card.select_one("a[href*='/annonce/']") or card.select_one("a[href]")
            url = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                url = href if href.startswith("http") else f"https://www.bienici.com{href}"

            if price:
                prop = Property(title=title, price=price, city="", url=url, source="bienici")
                if self._filter_result(prop, criteria):
                    results.append(prop)
        return results

    def _parse_listing(self, raw: dict) -> Property | None:
        try:
            city = raw.get("city", "")
            postal = raw.get("postalCode", "")
            price = int(raw.get("price", 0))

            date_posted = None
            if raw.get("publicationDate"):
                try:
                    date_posted = datetime.fromisoformat(raw["publicationDate"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            photos = raw.get("photos", [])
            image_url = photos[0].get("url", "") if photos else ""

            return Property(
                title=raw.get("title", f"{raw.get('propertyType', '')} {raw.get('roomsQuantity', '')} pièces"),
                price=price,
                city=city,
                postal_code=postal,
                address=raw.get("street", ""),
                surface=float(raw.get("surfaceArea", 0)),
                rooms=raw.get("roomsQuantity"),
                property_type=raw.get("propertyType", ""),
                description=raw.get("description", ""),
                url=f"https://www.bienici.com/annonce/{raw.get('id', '')}",
                source="bienici",
                image_url=image_url,
                floor=raw.get("floor"),
                year_built=raw.get("yearOfConstruction"),
                dpe=raw.get("energyClassification", ""),
                charges=raw.get("charges"),
                latitude=raw.get("blurredLatitude"),
                longitude=raw.get("blurredLongitude"),
                date_posted=date_posted,
                raw_data=raw,
            )
        except Exception as e:
            logger.debug(f"[bienici] Parse error: {e}")
            return None
