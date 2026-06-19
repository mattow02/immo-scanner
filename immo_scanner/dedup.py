import logging
from immo_scanner.models import Property

logger = logging.getLogger(__name__)


def deduplicate(properties: list[Property]) -> list[Property]:
    seen: dict[str, Property] = {}
    dupes = 0

    for prop in properties:
        key = prop.dedup_key()
        if not key or key == "||":
            seen[id(prop)] = prop
            continue

        if key in seen:
            existing = seen[key]
            if _completeness(prop) > _completeness(existing):
                seen[key] = prop
            dupes += 1
        else:
            seen[key] = prop

    if dupes:
        logger.info(f"Deduplicated: {dupes} doublons supprimés, {len(seen)} biens uniques")

    return list(seen.values())


def _completeness(prop: Property) -> int:
    score = 0
    if prop.title:
        score += 1
    if prop.surface and prop.surface > 0:
        score += 2
    if prop.rooms:
        score += 1
    if prop.description:
        score += 1
    if prop.url:
        score += 1
    if prop.image_url:
        score += 1
    if prop.dpe:
        score += 1
    if prop.date_posted:
        score += 1
    if prop.latitude and prop.longitude:
        score += 2
    return score
