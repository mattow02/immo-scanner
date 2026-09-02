"""Tests for deduplication.

The same flat is listed on several portals at once. Showing it three times
would not just be untidy: it would push everything else down the ranking.
"""

from immo_scanner.dedup import deduplicate
from immo_scanner.models import Property


def listing(**overrides) -> Property:
    base = dict(title="Two-room flat", price=120_000, city="Lyon", surface=45.0)
    base.update(overrides)
    return Property(**base)


def test_the_same_flat_on_two_portals_is_kept_once():
    kept = deduplicate([listing(source="seloger"), listing(source="pap")])
    assert len(kept) == 1


def test_the_richer_of_two_duplicates_survives():
    """Portals do not describe a flat equally well. Keeping the fuller entry is
    what makes deduplication a gain rather than a loss of information."""
    bare = listing(source="a")
    detailed = listing(
        source="b",
        rooms=2,
        description="Third floor, lift, balcony.",
        url="https://example.test/2",
        image_url="https://example.test/2.jpg",
        dpe="C",
    )
    kept = deduplicate([bare, detailed])
    assert len(kept) == 1
    assert kept[0].source == "b"

    # And the order of arrival must not change the outcome.
    assert deduplicate([detailed, bare])[0].source == "b"


def test_a_different_price_is_a_different_listing():
    kept = deduplicate([listing(price=120_000), listing(price=125_000)])
    assert len(kept) == 2


def test_coordinates_separate_two_look_alikes():
    """Same city, same surface, same price, two different streets. Without the
    coordinates they would be merged, and one of the two would vanish."""
    here = listing(latitude=45.7640, longitude=4.8357)
    there = listing(latitude=45.7500, longitude=4.8500)
    assert len(deduplicate([here, there])) == 2


def test_an_empty_list_stays_empty():
    assert deduplicate([]) == []
