import re
import logging
from abc import ABC, abstractmethod
from immo_scanner.models import Property, SearchCriteria

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    name: str = "base"
    base_url: str = ""
    needs_browser: bool = True
    supports_multi_city: bool = False

    def __init__(self, browser=None):
        self.browser = browser

    def search(self, criteria: SearchCriteria) -> list[Property]:
        if self.supports_multi_city or len(criteria.cities) <= 1:
            return self._search_criteria(criteria)

        all_properties = []
        for city in criteria.cities:
            city_criteria = SearchCriteria(
                cities=[city],
                departments=criteria.departments,
                radius_km=criteria.radius_km,
                budget_min=criteria.budget_min,
                budget_max=criteria.budget_max,
                surface_min=criteria.surface_min,
                surface_max=criteria.surface_max,
                property_types=criteria.property_types,
                rooms_min=criteria.rooms_min,
                rooms_max=criteria.rooms_max,
                max_pages=criteria.max_pages,
                transaction_type=criteria.transaction_type,
            )
            props = self._search_criteria(city_criteria)
            all_properties.extend(props)
            logger.info(f"[{self.name}] {city}: {len(props)} annonces")
        return all_properties

    def _search_criteria(self, criteria: SearchCriteria) -> list[Property]:
        all_properties = []
        for page_num in range(1, criteria.max_pages + 1):
            try:
                props = self._search_page(criteria, page_num)
                if not props:
                    break
                for prop in props:
                    if self._filter_result(prop, criteria):
                        all_properties.append(prop)
                logger.info(f"[{self.name}] Page {page_num}: {len(props)} annonces")
            except Exception as e:
                logger.error(f"[{self.name}] Erreur page {page_num}: {e}")
                break
        return all_properties

    @abstractmethod
    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        pass

    EXCLUDED_KEYWORDS = re.compile(
        r"viager|r[ée]sidence\s+senior|r[ée]sidence\s+g[ée]r[ée]e|ehpad|"
        r"lmnp\s+g[ée]r[ée]|r[ée]sidence\s+[ée]tudiante|r[ée]sidence\s+service|"
        r"bail\s+commercial|droit\s+au\s+bail|murs\s+commerc|"
        r"bouquet|rente\s+viag[èe]re|occup[ée]\s+[àa]\s+vie",
        re.IGNORECASE,
    )

    EXCLUDED_NOT_HOUSING = re.compile(
        r"caves?\s+[àa]\s+vendre|lot\s+de\s+caves?|ensemble\s+de\s+caves?|"
        r"parking\s+[àa]\s+vendre|place\s+de\s+parking|box\s+[àa]\s+vendre|"
        r"garage\s+[àa]\s+vendre|local\s+commercial|terrain\s+nu|"
        r"^parking\b|^garage\b|^cave\b|^box\b|^local\b",
        re.IGNORECASE,
    )

    def _filter_result(self, prop: Property, criteria: SearchCriteria) -> bool:
        if criteria.budget_min and prop.price < criteria.budget_min:
            return False
        if criteria.budget_max and prop.price > criteria.budget_max:
            return False
        if criteria.surface_min and prop.surface and prop.surface < criteria.surface_min:
            return False
        if criteria.surface_max and prop.surface and prop.surface > criteria.surface_max:
            return False
        searchable = f"{prop.title} {prop.description}"
        if self.EXCLUDED_KEYWORDS.search(searchable):
            logger.debug(f"[{self.name}] Excluded (viager/managed): {prop.title[:60]}")
            return False
        if self.EXCLUDED_NOT_HOUSING.search(searchable):
            logger.debug(f"[{self.name}] Excluded (not housing): {prop.title[:60]}")
            return False
        return True

    @staticmethod
    def _extract_price(text: str) -> int:
        text = text.replace("\xa0", " ").replace(" ", " ")
        m = re.search(r"([\d\s]+)\s*€", text)
        if m:
            return int(m.group(1).replace(" ", ""))
        return 0

    @staticmethod
    def _extract_surface(text: str) -> float:
        m = re.search(r"(\d+[.,]?\d*)\s*m[²2]", text)
        if m:
            return float(m.group(1).replace(",", "."))
        return 0.0

    @staticmethod
    def _extract_rooms(text: str) -> int | None:
        m = re.search(r"(\d+)\s*(?:pièce|pi[eè]ce|p\.)", text)
        if m:
            return int(m.group(1))
        return None
