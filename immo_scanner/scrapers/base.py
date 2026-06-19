import logging
from abc import ABC, abstractmethod
from immo_scanner.models import Property, SearchCriteria
from immo_scanner.utils.http import HttpClient

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    name: str = "base"
    base_url: str = ""

    def __init__(self, delay_min=2, delay_max=5, timeout=15, proxy=None):
        self.client = HttpClient(
            delay_min=delay_min,
            delay_max=delay_max,
            timeout=timeout,
            proxy=proxy,
            use_cloudscraper=self._needs_cloudscraper(),
        )

    def _needs_cloudscraper(self) -> bool:
        return False

    def search(self, criteria: SearchCriteria) -> list[Property]:
        all_properties = []
        for page in range(1, criteria.max_pages + 1):
            try:
                props = self._search_page(criteria, page)
                if not props:
                    break
                all_properties.extend(props)
                logger.info(f"[{self.name}] Page {page}: {len(props)} annonces")
            except Exception as e:
                logger.error(f"[{self.name}] Erreur page {page}: {e}")
                break
        return all_properties

    @abstractmethod
    def _search_page(self, criteria: SearchCriteria, page: int) -> list[Property]:
        pass

    @abstractmethod
    def _parse_listing(self, raw: dict) -> Property | None:
        pass

    def _filter_result(self, prop: Property, criteria: SearchCriteria) -> bool:
        if criteria.budget_min and prop.price < criteria.budget_min:
            return False
        if criteria.budget_max and prop.price > criteria.budget_max:
            return False
        if criteria.surface_min and prop.surface < criteria.surface_min:
            return False
        if criteria.surface_max and prop.surface > criteria.surface_max:
            return False
        return True

    def search_rentals(self, criteria: SearchCriteria) -> list[Property]:
        rental_criteria = SearchCriteria(
            cities=criteria.cities,
            departments=criteria.departments,
            radius_km=criteria.radius_km,
            surface_min=criteria.surface_min,
            surface_max=criteria.surface_max,
            property_types=criteria.property_types,
            rooms_min=criteria.rooms_min,
            rooms_max=criteria.rooms_max,
            max_pages=2,
            transaction_type="rent",
        )
        return self.search(rental_criteria)
