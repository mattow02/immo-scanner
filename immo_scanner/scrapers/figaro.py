import re
import logging
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class FigaroScraper(BaseScraper):
    name = "figaro"
    base_url = "https://immobilier.lefigaro.fr"

    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        city = criteria.cities[0].lower() if criteria.cities else "france"
        url = f"{self.base_url}/annonces/immobilier-vente-bien+appartement+maison-{city}.html"
        params = []
        if criteria.budget_max:
            params.append(f"prix-max={criteria.budget_max}")
        if criteria.budget_min:
            params.append(f"prix-min={criteria.budget_min}")
        if page > 1:
            params.append(f"page={page}")
        if params:
            url += "?" + "&".join(params)

        pw_page = self.browser.new_page(url)
        if not pw_page:
            return []

        try:
            import time
            time.sleep(4)

            articles = pw_page.query_selector_all("article")
            results = []
            for art in articles:
                text = art.inner_text()
                price = self._extract_price(text)
                surface = self._extract_surface(text)
                rooms = self._extract_rooms(text)

                link = art.query_selector("a[href]")
                href = link.get_attribute("href") if link else ""
                full_url = href if href and href.startswith("http") else f"{self.base_url}{href}" if href else ""

                city_found = ""
                for line in text.split("\n"):
                    m = re.search(r"(\d{5})\s+(.+)", line.strip())
                    if m:
                        city_found = m.group(2).strip()
                        break

                if price:
                    results.append(Property(
                        title=text.split("\n")[0][:80],
                        price=price, surface=surface, rooms=rooms,
                        city=city_found, url=full_url, source="figaro",
                    ))
            return results
        finally:
            pw_page.close()
