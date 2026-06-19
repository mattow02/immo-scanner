import re
import json
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class LeBonCoinScraper(BaseScraper):
    name = "leboncoin"
    base_url = "https://www.leboncoin.fr"

    def _build_url(self, criteria: SearchCriteria, page: int) -> str:
        city = criteria.cities[0] if criteria.cities else ""
        from immo_scanner.utils.geo import get_postal_code
        postal = get_postal_code(city) or ""

        url = f"{self.base_url}/recherche?category=9"
        if city:
            url += f"&locations={city}__{postal}"
        if criteria.budget_min or criteria.budget_max:
            pmin = criteria.budget_min or 0
            pmax = criteria.budget_max or 999999999
            url += f"&price={pmin}-{pmax}"
        if criteria.surface_min:
            url += f"&square={criteria.surface_min}-max"
        if page > 1:
            url += f"&page={page}"
        return url

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        url = self._build_url(criteria, page)
        pw_page = self.browser.new_page(url)
        if not pw_page:
            return []

        try:
            import time
            time.sleep(5)

            captcha = pw_page.query_selector_all("iframe[src*='captcha'], [class*='captcha']")
            if captcha:
                logger.warning("[leboncoin] Captcha detected, skipping")
                return []

            script_data = pw_page.evaluate("""() => {
                const scripts = document.querySelectorAll('script[type="application/json"], script#__NEXT_DATA__');
                const results = [];
                scripts.forEach(s => { if (s.textContent.length > 500) results.push(s.textContent); });
                return results;
            }""")

            results = []
            for raw in script_data:
                try:
                    data = json.loads(raw)
                    ads = self._find_ads(data)
                    for ad in ads:
                        prop = self._parse_ad(ad)
                        if prop:
                            results.append(prop)
                except (json.JSONDecodeError, TypeError):
                    continue

            if not results:
                results = self._parse_html(pw_page)

            return results
        finally:
            pw_page.close()

    def _find_ads(self, data, depth=0) -> list[dict]:
        if depth > 6:
            return []
        results = []
        if isinstance(data, dict):
            if "list_id" in data and "subject" in data:
                results.append(data)
            if "ads" in data and isinstance(data["ads"], list):
                return data["ads"]
            for v in data.values():
                results.extend(self._find_ads(v, depth + 1))
        elif isinstance(data, list):
            for item in data:
                results.extend(self._find_ads(item, depth + 1))
        return results

    def _parse_ad(self, ad: dict) -> Property | None:
        try:
            price_list = ad.get("price", [])
            price = int(price_list[0]) if price_list else 0
            if not price:
                return None

            location = ad.get("location", {})
            attrs = {a.get("key", ""): a.get("value", "") for a in ad.get("attributes", [])}

            surface = float(attrs.get("square", 0) or 0)
            rooms = int(attrs.get("rooms", 0) or 0) or None

            return Property(
                title=ad.get("subject", ""),
                price=price,
                city=location.get("city", ""),
                postal_code=location.get("zipcode", ""),
                surface=surface,
                rooms=rooms,
                property_type=attrs.get("real_estate_type", ""),
                url=ad.get("url", f"{self.base_url}/ad/ventes_immobilieres/{ad.get('list_id', '')}"),
                source="leboncoin",
                dpe=attrs.get("energy_rate", ""),
                latitude=location.get("lat"),
                longitude=location.get("lng"),
            )
        except Exception as e:
            logger.debug(f"[leboncoin] Parse error: {e}")
            return None

    def _parse_html(self, pw_page) -> list[Property]:
        cards = pw_page.query_selector_all("a[href*='/ad/']")
        results = []
        seen = set()
        for card in cards:
            href = card.get_attribute("href") or ""
            if not href or href in seen or "/ad/" not in href:
                continue
            seen.add(href)
            text = card.inner_text()
            price = self._extract_price(text)
            surface = self._extract_surface(text)
            rooms = self._extract_rooms(text)
            if price:
                url = href if href.startswith("http") else f"{self.base_url}{href}"
                results.append(Property(
                    title=text.split("\n")[0][:80],
                    price=price, surface=surface, rooms=rooms,
                    city="", url=url, source="leboncoin",
                ))
        return results
