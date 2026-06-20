import logging
from immo_scanner.models import Property, RentalEstimate, ScoredProperty
from immo_scanner.utils.rental_refs import get_rental_price, get_tension, RENTAL_PRICE_PER_SQM
from immo_scanner.utils.geo import normalize_city
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

WEIGHTS = {
    "yield": 0.40,
    "price_sqm": 0.15,
    "tension": 0.15,
    "typology": 0.10,
    "surface_fit": 0.10,
    "freshness": 0.10,
}

AVG_PURCHASE_PRICE_SQM: dict[str, float] = {
    "paris": 10500, "lyon": 5200, "marseille": 3200, "toulouse": 3500,
    "nice": 5000, "nantes": 3800, "montpellier": 3600, "strasbourg": 3400,
    "bordeaux": 4500, "lille": 3300, "rennes": 3800, "reims": 2600,
    "saint-etienne": 1200, "le havre": 1800, "toulon": 3000, "grenoble": 2800,
    "dijon": 2400, "angers": 2800, "nimes": 2200, "clermont-ferrand": 2100,
    "le mans": 1700, "aix-en-provence": 4800, "brest": 1800, "tours": 2600,
    "amiens": 2100, "limoges": 1400, "perpignan": 1600, "metz": 2200,
    "besancon": 2100, "orleans": 2500, "rouen": 2600, "mulhouse": 1200,
    "caen": 2500, "nancy": 2400, "avignon": 2200, "poitiers": 1900,
    "pau": 1800, "la rochelle": 3800, "calais": 1400, "colmar": 2100,
    "valence": 1900, "dunkerque": 1500, "ajaccio": 3200, "bourges": 1300,
    "troyes": 1600, "quimper": 1700,
}


def estimate_rent(prop: Property, mode: str = "avg_price") -> RentalEstimate | None:
    if not prop.surface or prop.surface <= 0:
        return None

    rent_per_sqm = get_rental_price(prop.city, prop.rooms, prop.surface)
    monthly = rent_per_sqm * prop.surface

    return RentalEstimate(
        monthly_rent=round(monthly, 2),
        source=mode,
        confidence="medium" if normalize_city(prop.city) in RENTAL_PRICE_PER_SQM else "low",
        rent_per_sqm=rent_per_sqm,
    )


def score_property(prop: Property, rental: RentalEstimate | None) -> ScoredProperty:
    details = {}
    scored = ScoredProperty(property=prop, rental_estimate=rental)

    if not rental or not prop.price or prop.price <= 0:
        return scored

    annual_rent = rental.monthly_rent * 12
    scored.gross_yield = round((annual_rent / prop.price) * 100, 2)

    estimated_charges = rental.monthly_rent * 1.0 + prop.price * 0.008
    scored.net_yield = round(((annual_rent - estimated_charges) / prop.price) * 100, 2)

    yield_score = min(scored.gross_yield / 12.0, 1.0) * 100
    details["yield"] = round(yield_score, 1)

    city_key = normalize_city(prop.city)
    avg_sqm = AVG_PURCHASE_PRICE_SQM.get(city_key, 2500)
    if prop.surface and prop.surface > 0:
        actual_sqm = prop.price / prop.surface
        ratio = actual_sqm / avg_sqm
        if ratio <= 0.7:
            price_score = 100
        elif ratio <= 1.0:
            price_score = 100 - (ratio - 0.7) * (60 / 0.3)
        else:
            price_score = max(0, 40 - (ratio - 1.0) * 40)
        details["price_sqm"] = round(price_score, 1)
    else:
        details["price_sqm"] = 50.0

    tension = get_tension(prop.city)
    tension_score = tension * 100
    details["tension"] = round(tension_score, 1)

    if prop.rooms:
        typology_scores = {1: 90, 2: 100, 3: 75, 4: 55, 5: 40}
        details["typology"] = typology_scores.get(prop.rooms, 35 if prop.rooms > 5 else 85)
    elif prop.surface:
        if prop.surface <= 30:
            details["typology"] = 90
        elif prop.surface <= 50:
            details["typology"] = 100
        elif prop.surface <= 80:
            details["typology"] = 75
        else:
            details["typology"] = 50
    else:
        details["typology"] = 60

    if prop.rooms and prop.surface:
        ideal_ranges = {1: (15, 35), 2: (25, 55), 3: (45, 80), 4: (65, 110), 5: (80, 140)}
        r = ideal_ranges.get(prop.rooms, (80, 150))
        if r[0] <= prop.surface <= r[1]:
            details["surface_fit"] = 100
        else:
            off = min(abs(prop.surface - r[0]), abs(prop.surface - r[1]))
            details["surface_fit"] = max(0, 100 - off * 3)
    else:
        details["surface_fit"] = 60

    if prop.date_posted:
        now = datetime.now(timezone.utc)
        if prop.date_posted.tzinfo is None:
            from datetime import timezone as tz
            prop.date_posted = prop.date_posted.replace(tzinfo=tz.utc)
        days_old = (now - prop.date_posted).days
        if days_old <= 3:
            details["freshness"] = 100
        elif days_old <= 7:
            details["freshness"] = 85
        elif days_old <= 14:
            details["freshness"] = 65
        elif days_old <= 30:
            details["freshness"] = 40
        else:
            details["freshness"] = 20
    else:
        details["freshness"] = 50

    total = sum(details.get(k, 0) * w for k, w in WEIGHTS.items())
    scored.score = round(total, 1)
    scored.score_details = details

    return scored


def _is_suspicious(prop: Property) -> bool:
    if not prop.surface or prop.surface <= 0 or not prop.price:
        return False
    price_sqm = prop.price / prop.surface
    city_key = normalize_city(prop.city)
    avg = AVG_PURCHASE_PRICE_SQM.get(city_key, 2500)
    if price_sqm < avg * 0.30:
        return True
    return False


def score_properties(properties: list[Property], rental_mode: str = "avg_price") -> list[ScoredProperty]:
    scored = []
    for prop in properties:
        if _is_suspicious(prop):
            logger.debug(f"Suspicious listing filtered: {prop.title[:50]} ({prop.price}€ for {prop.surface}m² in {prop.city})")
            continue
        rental = estimate_rent(prop, rental_mode)
        sp = score_property(prop, rental)
        scored.append(sp)

    scored.sort(key=lambda s: s.score, reverse=True)
    return scored
