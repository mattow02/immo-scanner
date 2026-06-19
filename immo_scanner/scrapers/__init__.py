from immo_scanner.scrapers.base import BaseScraper
from immo_scanner.scrapers.leboncoin import LeBonCoinScraper
from immo_scanner.scrapers.seloger import SeLogerScraper
from immo_scanner.scrapers.pap import PapScraper
from immo_scanner.scrapers.bienici import BienIciScraper
from immo_scanner.scrapers.logicimmo import LogicImmoScraper
from immo_scanner.scrapers.paruvendu import ParuVenduScraper
from immo_scanner.scrapers.figaro import FigaroScraper
from immo_scanner.scrapers.ouestfrance import OuestFranceScraper

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "leboncoin": LeBonCoinScraper,
    "seloger": SeLogerScraper,
    "pap": PapScraper,
    "bienici": BienIciScraper,
    "logicimmo": LogicImmoScraper,
    "paruvendu": ParuVenduScraper,
    "figaro": FigaroScraper,
    "ouestfrance": OuestFranceScraper,
}


def get_scraper(name: str, **kwargs) -> BaseScraper | None:
    cls = SCRAPER_REGISTRY.get(name.lower())
    if cls:
        return cls(**kwargs)
    return None


def available_scrapers() -> list[str]:
    return list(SCRAPER_REGISTRY.keys())
