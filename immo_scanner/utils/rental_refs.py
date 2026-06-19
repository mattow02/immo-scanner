RENTAL_PRICE_PER_SQM: dict[str, dict] = {
    "paris":              {"avg": 30.0, "studio": 35.0, "t1": 32.0, "t2": 29.0, "t3": 27.0, "house": 25.0},
    "marseille":          {"avg": 14.0, "studio": 16.0, "t1": 15.0, "t2": 13.5, "t3": 12.5, "house": 12.0},
    "lyon":               {"avg": 16.5, "studio": 19.0, "t1": 17.0, "t2": 15.5, "t3": 14.5, "house": 14.0},
    "toulouse":           {"avg": 13.5, "studio": 16.0, "t1": 14.5, "t2": 13.0, "t3": 12.0, "house": 11.5},
    "nice":               {"avg": 17.0, "studio": 20.0, "t1": 18.0, "t2": 16.5, "t3": 15.0, "house": 14.0},
    "nantes":             {"avg": 13.5, "studio": 15.5, "t1": 14.0, "t2": 13.0, "t3": 12.0, "house": 11.5},
    "montpellier":        {"avg": 15.0, "studio": 17.5, "t1": 15.5, "t2": 14.0, "t3": 13.0, "house": 12.5},
    "strasbourg":         {"avg": 13.5, "studio": 15.5, "t1": 14.0, "t2": 13.0, "t3": 12.0, "house": 11.5},
    "bordeaux":           {"avg": 15.0, "studio": 17.5, "t1": 16.0, "t2": 14.5, "t3": 13.0, "house": 12.5},
    "lille":              {"avg": 14.0, "studio": 16.5, "t1": 15.0, "t2": 13.5, "t3": 12.5, "house": 12.0},
    "rennes":             {"avg": 13.5, "studio": 15.5, "t1": 14.0, "t2": 13.0, "t3": 12.0, "house": 11.0},
    "reims":              {"avg": 11.5, "studio": 13.5, "t1": 12.0, "t2": 11.0, "t3": 10.0, "house": 9.5},
    "saint-etienne":      {"avg": 8.5,  "studio": 10.0, "t1": 9.0,  "t2": 8.0,  "t3": 7.5,  "house": 7.0},
    "le havre":           {"avg": 10.5, "studio": 12.0, "t1": 11.0, "t2": 10.0, "t3": 9.5,  "house": 9.0},
    "toulon":             {"avg": 12.5, "studio": 14.5, "t1": 13.0, "t2": 12.0, "t3": 11.0, "house": 10.5},
    "grenoble":           {"avg": 12.5, "studio": 14.5, "t1": 13.0, "t2": 12.0, "t3": 11.0, "house": 10.5},
    "dijon":              {"avg": 11.5, "studio": 13.5, "t1": 12.0, "t2": 11.0, "t3": 10.0, "house": 9.5},
    "angers":             {"avg": 12.0, "studio": 14.0, "t1": 12.5, "t2": 11.5, "t3": 10.5, "house": 10.0},
    "nimes":              {"avg": 11.0, "studio": 13.0, "t1": 11.5, "t2": 10.5, "t3": 9.5,  "house": 9.0},
    "clermont-ferrand":   {"avg": 11.0, "studio": 13.0, "t1": 11.5, "t2": 10.5, "t3": 9.5,  "house": 9.0},
    "le mans":            {"avg": 10.0, "studio": 11.5, "t1": 10.5, "t2": 9.5,  "t3": 9.0,  "house": 8.5},
    "aix-en-provence":    {"avg": 16.0, "studio": 18.5, "t1": 16.5, "t2": 15.5, "t3": 14.5, "house": 14.0},
    "brest":              {"avg": 10.0, "studio": 11.5, "t1": 10.5, "t2": 9.5,  "t3": 9.0,  "house": 8.5},
    "tours":              {"avg": 12.0, "studio": 14.0, "t1": 12.5, "t2": 11.5, "t3": 10.5, "house": 10.0},
    "amiens":             {"avg": 11.0, "studio": 12.5, "t1": 11.5, "t2": 10.5, "t3": 9.5,  "house": 9.0},
    "limoges":            {"avg": 9.5,  "studio": 11.0, "t1": 10.0, "t2": 9.0,  "t3": 8.5,  "house": 8.0},
    "perpignan":          {"avg": 10.0, "studio": 11.5, "t1": 10.5, "t2": 9.5,  "t3": 9.0,  "house": 8.5},
    "metz":               {"avg": 11.0, "studio": 12.5, "t1": 11.5, "t2": 10.5, "t3": 9.5,  "house": 9.0},
    "besancon":           {"avg": 10.5, "studio": 12.0, "t1": 11.0, "t2": 10.0, "t3": 9.5,  "house": 9.0},
    "orleans":            {"avg": 12.0, "studio": 14.0, "t1": 12.5, "t2": 11.5, "t3": 10.5, "house": 10.0},
    "rouen":              {"avg": 12.5, "studio": 14.5, "t1": 13.0, "t2": 12.0, "t3": 11.0, "house": 10.5},
    "mulhouse":           {"avg": 9.0,  "studio": 10.5, "t1": 9.5,  "t2": 8.5,  "t3": 8.0,  "house": 7.5},
    "caen":               {"avg": 11.5, "studio": 13.5, "t1": 12.0, "t2": 11.0, "t3": 10.0, "house": 9.5},
    "nancy":              {"avg": 11.5, "studio": 13.0, "t1": 12.0, "t2": 11.0, "t3": 10.0, "house": 9.5},
    "avignon":            {"avg": 11.5, "studio": 13.0, "t1": 12.0, "t2": 11.0, "t3": 10.0, "house": 9.5},
    "poitiers":           {"avg": 10.5, "studio": 12.0, "t1": 11.0, "t2": 10.0, "t3": 9.5,  "house": 9.0},
    "pau":                {"avg": 10.0, "studio": 11.5, "t1": 10.5, "t2": 9.5,  "t3": 9.0,  "house": 8.5},
    "la rochelle":        {"avg": 13.0, "studio": 15.0, "t1": 13.5, "t2": 12.5, "t3": 11.5, "house": 11.0},
    "calais":             {"avg": 9.0,  "studio": 10.5, "t1": 9.5,  "t2": 8.5,  "t3": 8.0,  "house": 7.5},
    "colmar":             {"avg": 10.5, "studio": 12.0, "t1": 11.0, "t2": 10.0, "t3": 9.5,  "house": 9.0},
    "valence":            {"avg": 10.5, "studio": 12.0, "t1": 11.0, "t2": 10.0, "t3": 9.5,  "house": 9.0},
    "dunkerque":          {"avg": 9.5,  "studio": 11.0, "t1": 10.0, "t2": 9.0,  "t3": 8.5,  "house": 8.0},
    "ajaccio":            {"avg": 13.0, "studio": 15.0, "t1": 13.5, "t2": 12.5, "t3": 11.5, "house": 11.0},
    "bourges":            {"avg": 9.5,  "studio": 11.0, "t1": 10.0, "t2": 9.0,  "t3": 8.5,  "house": 8.0},
    "troyes":             {"avg": 10.0, "studio": 11.5, "t1": 10.5, "t2": 9.5,  "t3": 9.0,  "house": 8.5},
    "quimper":            {"avg": 9.5,  "studio": 11.0, "t1": 10.0, "t2": 9.0,  "t3": 8.5,  "house": 8.0},
}

TENSION_LOCATIVE: dict[str, float] = {
    "paris": 0.95, "lyon": 0.90, "bordeaux": 0.88, "montpellier": 0.87,
    "toulouse": 0.85, "nantes": 0.85, "rennes": 0.84, "lille": 0.83,
    "nice": 0.82, "strasbourg": 0.82, "marseille": 0.78, "grenoble": 0.80,
    "aix-en-provence": 0.85, "rouen": 0.78, "tours": 0.77, "dijon": 0.76,
    "angers": 0.77, "la rochelle": 0.80, "reims": 0.74, "caen": 0.75,
    "orleans": 0.76, "clermont-ferrand": 0.73, "nancy": 0.74,
    "toulon": 0.75, "avignon": 0.73, "metz": 0.72, "amiens": 0.71,
    "besancon": 0.72, "poitiers": 0.70, "le mans": 0.68, "limoges": 0.65,
    "nimes": 0.72, "perpignan": 0.70, "pau": 0.68, "brest": 0.72,
    "le havre": 0.70, "mulhouse": 0.65, "saint-etienne": 0.62,
    "valence": 0.71, "colmar": 0.72, "dunkerque": 0.64, "calais": 0.62,
    "ajaccio": 0.75, "bourges": 0.63, "troyes": 0.67, "quimper": 0.68,
}


def get_rental_price(city: str, rooms: int | None = None, surface: float = 0) -> float:
    from immo_scanner.utils.geo import normalize_city
    city_key = normalize_city(city)
    data = RENTAL_PRICE_PER_SQM.get(city_key)
    if not data:
        return 11.0

    if rooms:
        type_map = {0: "studio", 1: "studio", 2: "t1", 3: "t2", 4: "t3"}
        type_key = type_map.get(rooms, "t3")
        return data.get(type_key, data["avg"])

    if surface and surface > 0:
        if surface <= 20:
            return data.get("studio", data["avg"])
        elif surface <= 35:
            return data.get("t1", data["avg"])
        elif surface <= 55:
            return data.get("t2", data["avg"])
        else:
            return data.get("t3", data["avg"])

    return data["avg"]


def get_tension(city: str) -> float:
    from immo_scanner.utils.geo import normalize_city
    city_key = normalize_city(city)
    return TENSION_LOCATIVE.get(city_key, 0.65)
