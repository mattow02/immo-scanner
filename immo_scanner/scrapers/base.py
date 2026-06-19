import re
import logging
from abc import ABC, abstractmethod
from immo_scanner.models import Property, SearchCriteria

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    name: str = "base"
    base_url: str = ""
    needs_browser: bool = True

    def __init__(self, browser=None):
        self.browser = browser

    def search(self, criteria: SearchCriteria) -> list[Property]:
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

    def _filter_result(self, prop: Property, criteria: SearchCriteria) -> bool:
        if criteria.budget_min and prop.price < criteria.budget_min:
            return False
        if criteria.budget_max and prop.price > criteria.budget_max:
            return False
        if criteria.surface_min and prop.surface and prop.surface < criteria.surface_min:
            return False
        if criteria.surface_max and prop.surface and prop.surface > criteria.surface_max:
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
