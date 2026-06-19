import re
import unicodedata

CITY_POSTAL_CODES: dict[str, str] = {
    "paris": "75000", "marseille": "13000", "lyon": "69000",
    "toulouse": "31000", "nice": "06000", "nantes": "44000",
    "montpellier": "34000", "strasbourg": "67000", "bordeaux": "33000",
    "lille": "59000", "rennes": "35000", "reims": "51100",
    "saint-etienne": "42000", "le havre": "76600", "toulon": "83000",
    "grenoble": "38000", "dijon": "21000", "angers": "49000",
    "nimes": "30000", "clermont-ferrand": "63000", "le mans": "72000",
    "aix-en-provence": "13100", "brest": "29200", "tours": "37000",
    "amiens": "80000", "limoges": "87000", "perpignan": "66000",
    "metz": "57000", "besancon": "25000", "orleans": "45000",
    "rouen": "76000", "mulhouse": "68100", "caen": "14000",
    "nancy": "54000", "argenteuil": "95100", "saint-denis": "93200",
    "montreuil": "93100", "roubaix": "59100", "tourcoing": "59200",
    "avignon": "84000", "poitiers": "86000", "pau": "64000",
    "calais": "62100", "la rochelle": "17000", "colmar": "68000",
    "valence": "26000", "dunkerque": "59140", "ajaccio": "20000",
    "bourges": "18000", "troyes": "10000", "quimper": "29000",
}

CITY_DEPARTMENT: dict[str, str] = {
    code[:2]: city for city, code in CITY_POSTAL_CODES.items()
}


def normalize_city(name: str) -> str:
    name = name.strip().lower()
    name = unicodedata.normalize("NFD", name)
    name = re.sub(r"[̀-ͯ]", "", name)
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"\s+", "-", name)
    return name


def get_postal_code(city: str) -> str:
    normalized = normalize_city(city)
    return CITY_POSTAL_CODES.get(normalized, "")


def get_department(city: str) -> str:
    code = get_postal_code(city)
    if code:
        return code[:2]
    return ""


def postal_to_city(postal_code: str) -> str:
    prefix = postal_code[:2] if len(postal_code) >= 2 else postal_code
    for city, code in CITY_POSTAL_CODES.items():
        if code.startswith(prefix):
            return city
    return ""
