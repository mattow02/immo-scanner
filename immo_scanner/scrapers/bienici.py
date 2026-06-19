import re
import json
import logging
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.utils.geo import get_postal_code

logger = logging.getLogger(__name__)


class BienIciScraper(BaseScraper):
    needs_browser = False
    name = "bienici"
    base_url = "https://www.bienici.com"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        city = criteria.cities[0] if criteria.cities else "france"
        postal = get_postal_code(city)
        slug = f"{city.lower()}-{postal}" if postal else city.lower()

        transaction = "location" if criteria.transaction_type == "rent" else "achat"
        url = f"{self.base_url}/recherche/{transaction}/{slug}"

        params = {}
        if criteria.budget_max:
            params["prix-max"] = str(criteria.budget_max)
        if criteria.budget_min:
            params["prix-min"] = str(criteria.budget_min)
        if criteria.surface_min:
            params["surface-min"] = str(criteria.surface_min)
        if page > 1:
            params["page"] = str(page)

        import time, random
        time.sleep(random.uniform(1, 2.5))

        try:
            resp = cffi_requests.get(
                url, params=params,
                headers={
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "fr-FR,fr;q=0.9",
                    "Referer": "https://www.bienici.com/",
                },
                impersonate="chrome",
                timeout=20,
            )
        except Exception as e:
            logger.error(f"[bienici] Request failed: {e}")
            return []

        if resp.status_code != 200:
            logger.warning(f"[bienici] HTTP {resp.status_code}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.select("a[href*='/annonce/']")

        results = []
        seen = set()
        for link in links:
            href = link.get("href", "")
            if href in seen:
                continue
            seen.add(href)
            prop = self._parse_card(link, href)
            if prop:
                results.append(prop)
        return results

    def _parse_card(self, el, href: str) -> Property | None:
        try:
            text = el.get_text(" ", strip=True)
            if not text or len(text) < 10:
                return None

            price = self._extract_price(text)
            surface = self._extract_surface(text)
            rooms = self._extract_rooms(text)

            city = ""
            postal_code = ""
            m = re.search(r"(\d{5})\s+([A-ZÀ-Ÿ][a-zà-ÿ\s-]+)", text)
            if m:
                postal_code = m.group(1)
                city = m.group(2).strip()

            prop_type = ""
            text_lower = text.lower()
            if "appartement" in text_lower or "studio" in text_lower:
                prop_type = "apartment"
            elif "maison" in text_lower:
                prop_type = "house"

            if not price:
                return None

            full_url = href if href.startswith("http") else f"{self.base_url}{href}"
            full_url = re.sub(r"\?.*", "", full_url)

            title_parts = []
            if prop_type:
                title_parts.append("Appartement" if prop_type == "apartment" else "Maison")
            if rooms:
                title_parts.append(f"{rooms}p")
            if surface:
                title_parts.append(f"{surface:.0f}m²")

            return Property(
                title=" ".join(title_parts) or text[:60],
                price=price, city=city, postal_code=postal_code,
                surface=surface, rooms=rooms, property_type=prop_type,
                url=full_url, source="bienici",
            )
        except Exception as e:
            logger.debug(f"[bienici] Parse error: {e}")
            return None
