import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class BienIciScraper(BaseScraper):
    name = "bienici"
    base_url = "https://www.bienici.com"

    def _build_url(self, criteria: SearchCriteria, page: int) -> str:
        city = criteria.cities[0] if criteria.cities else "france"
        from immo_scanner.utils.geo import get_postal_code
        postal = get_postal_code(city)
        slug = f"{city.lower()}-{postal}" if postal else city.lower()

        transaction = "location" if criteria.transaction_type == "rent" else "achat"
        url = f"{self.base_url}/recherche/{transaction}/{slug}"

        params = []
        if criteria.budget_max:
            params.append(f"prix-max={criteria.budget_max}")
        if criteria.budget_min:
            params.append(f"prix-min={criteria.budget_min}")
        if criteria.surface_min:
            params.append(f"surface-min={criteria.surface_min}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            url += "?" + "&".join(params)
        return url

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        url = self._build_url(criteria, page)
        pw_page = self.browser.new_page(url, wait_for="a[href*='/annonce/']")
        if not pw_page:
            return []

        try:
            links = pw_page.query_selector_all("a[href*='/annonce/']")
            results = []
            for link in links:
                prop = self._parse_card(link)
                if prop:
                    results.append(prop)
            return results
        finally:
            pw_page.close()

    def _parse_card(self, el) -> Property | None:
        try:
            href = el.get_attribute("href") or ""
            text = el.inner_text()
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            price = self._extract_price(text)
            surface = self._extract_surface(text)
            rooms = self._extract_rooms(text)

            city = ""
            postal_code = ""
            property_type = ""
            for line in lines:
                if re.match(r"\d{5}", line):
                    city, postal_code = self._extract_city_postal(line)
                elif "appartement" in line.lower():
                    property_type = "apartment"
                    city_m = re.search(r"\d{5}\s+(.+)", line)
                    if city_m:
                        city = city_m.group(1)
                elif "maison" in line.lower():
                    property_type = "house"

            for line in lines:
                m = re.match(r"(\d{5})\s+(.+?)(?:\s*\(|$)", line)
                if m:
                    postal_code = m.group(1)
                    city = m.group(2).strip()
                    break

            if not price:
                return None

            full_url = href if href.startswith("http") else f"{self.base_url}{href}"
            full_url = re.sub(r"\?.*", "", full_url)

            title_parts = []
            if property_type:
                title_parts.append(property_type.capitalize())
            if rooms:
                title_parts.append(f"{rooms}p")
            if surface:
                title_parts.append(f"{surface:.0f}m²")
            title = " ".join(title_parts) or lines[0] if lines else ""

            return Property(
                title=title,
                price=price,
                city=city,
                postal_code=postal_code,
                surface=surface,
                rooms=rooms,
                property_type=property_type,
                url=full_url,
                source="bienici",
            )
        except Exception as e:
            logger.debug(f"[bienici] Parse error: {e}")
            return None
