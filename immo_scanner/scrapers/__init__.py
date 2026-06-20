from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.scrapers.leboncoin import LeBonCoinScraper
from immo_scanner.scrapers.seloger import SeLogerScraper
from immo_scanner.scrapers.bienici import BienIciScraper
from immo_scanner.scrapers.pap import PapScraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "leboncoin": LeBonCoinScraper,
    "seloger": SeLogerScraper,
    "bienici": BienIciScraper,
    "pap": PapScraper,
}

try:
    from immo_scanner.scrapers.laforet import LaforetScraper
    from immo_scanner.scrapers.orpi import OrpiScraper
    from immo_scanner.scrapers.figaro import FigaroScraper
    SCRAPER_REGISTRY["laforet"] = LaforetScraper
    SCRAPER_REGISTRY["orpi"] = OrpiScraper
    SCRAPER_REGISTRY["figaro"] = FigaroScraper
except ImportError:
    pass


def get_scraper(name: str, browser=None) -> BaseScraper | None:
    cls = SCRAPER_REGISTRY.get(name.lower())
    if cls:
        return cls(browser=browser)
    return None


def available_scrapers() -> list[str]:
    return list(SCRAPER_REGISTRY.keys())
