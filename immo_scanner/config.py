import os
from pathlib import Path
from immo_scanner.models import SearchCriteria

_ENV_LOADED = False


def _load_env():
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = value
    _ENV_LOADED = True


def _get(key: str, default: str = "") -> str:
    _load_env()
    return os.environ.get(key, default)


def _get_list(key: str, default: str = "") -> list[str]:
    val = _get(key, default)
    if not val:
        return []
    return [x.strip() for x in val.split(",") if x.strip()]


def _get_int(key: str, default: int = 0) -> int:
    val = _get(key, str(default))
    try:
        return int(val)
    except ValueError:
        return default


def _get_float(key: str, default: float = 0.0) -> float:
    val = _get(key, str(default))
    try:
        return float(val)
    except ValueError:
        return default


class Config:
    def __init__(self):
        self.cities = _get_list("IMMO_CITIES")
        self.departments = _get_list("IMMO_DEPARTMENTS")
        self.radius_km = _get_int("IMMO_RADIUS_KM", 20)
        self.budget_min = _get_int("IMMO_BUDGET_MIN", 30000)
        self.budget_max = _get_int("IMMO_BUDGET_MAX", 200000)
        self.surface_min = _get_int("IMMO_SURFACE_MIN", 15)
        self.surface_max = _get_int("IMMO_SURFACE_MAX", 0) or None
        self.property_types = _get_list("IMMO_TYPES", "apartment,house,building")
        self.rooms_min = _get_int("IMMO_ROOMS_MIN", 0) or None
        self.rooms_max = _get_int("IMMO_ROOMS_MAX", 0) or None
        self.rental_mode = _get("IMMO_RENTAL_MODE", "both")
        self.min_yield = _get_float("IMMO_MIN_YIELD", 5.0)
        self.sites = _get_list("IMMO_SITES", "leboncoin,seloger,bienici,laforet,orpi,figaro,pap")
        self.max_pages = _get_int("IMMO_MAX_PAGES", 5)
        self.delay_min = _get_int("IMMO_DELAY_MIN", 2)
        self.delay_max = _get_int("IMMO_DELAY_MAX", 5)
        self.proxy = _get("IMMO_PROXY") or None
        self.timeout = _get_int("IMMO_TIMEOUT", 15)
        self.output_dir = _get("IMMO_OUTPUT_DIR", "./output")
        self.excel_name = _get("IMMO_EXCEL_NAME", "resultats_immo")

    def to_criteria(self, **overrides) -> SearchCriteria:
        kwargs = {
            "cities": overrides.get("cities", self.cities),
            "departments": overrides.get("departments", self.departments),
            "radius_km": overrides.get("radius_km", self.radius_km),
            "budget_min": overrides.get("budget_min", self.budget_min),
            "budget_max": overrides.get("budget_max", self.budget_max),
            "surface_min": overrides.get("surface_min", self.surface_min),
            "surface_max": overrides.get("surface_max", self.surface_max),
            "property_types": overrides.get("property_types", self.property_types),
            "rooms_min": overrides.get("rooms_min", self.rooms_min),
            "rooms_max": overrides.get("rooms_max", self.rooms_max),
            "max_pages": overrides.get("max_pages", self.max_pages),
        }
        return SearchCriteria(**kwargs)

    def summary(self) -> dict:
        return {
            "Villes": ", ".join(self.cities) or "(toutes)",
            "Departements": ", ".join(self.departments) or "(non defini)",
            "Budget": f"{self.budget_min:,} - {self.budget_max:,} EUR",
            "Surface": f"{self.surface_min}+ m2" + (f" (max {self.surface_max} m2)" if self.surface_max else ""),
            "Types": ", ".join(self.property_types),
            "Rendement min": f"{self.min_yield}%",
            "Mode loyer": self.rental_mode,
            "Sites": ", ".join(self.sites),
            "Pages max/site": str(self.max_pages),
        }
