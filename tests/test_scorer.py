"""Tests for the scoring core.

The scanner's value is not the scraping, it is the ranking: two listings at the
same price are not the same investment. Everything below is pure logic, so it
runs without a network, a browser, or a single third-party package.
"""

from datetime import datetime, timedelta, timezone

import pytest

from immo_scanner.models import Property
from immo_scanner.scorer import (
    _is_suspicious,
    estimate_rent,
    score_properties,
    score_property,
)


def listing(**overrides) -> Property:
    """A plausible listing, so each test only states what it is about."""
    base = dict(
        title="Two-room flat, city centre",
        price=120_000,
        city="Lyon",
        surface=45.0,
        rooms=2,
        url="https://example.test/1",
    )
    base.update(overrides)
    return Property(**base)


class TestEstimateRent:
    def test_no_surface_means_no_estimate(self):
        """Without a surface there is nothing to multiply: better no answer
        than a number made up out of thin air."""
        assert estimate_rent(listing(surface=0)) is None

    def test_rent_is_proportional_to_surface(self):
        small = estimate_rent(listing(surface=30.0))
        large = estimate_rent(listing(surface=60.0))
        assert small is not None and large is not None
        assert large.monthly_rent == pytest.approx(small.monthly_rent * 2, rel=1e-6)

    def test_confidence_says_whether_the_city_is_referenced(self):
        """A city we have no reference for still gets an estimate, but it is
        labelled for what it is."""
        assert estimate_rent(listing(city="Lyon")).confidence == "medium"
        assert estimate_rent(listing(city="Trifouillis-les-Oies")).confidence == "low"


class TestScoreProperty:
    def test_gross_yield_is_annual_rent_over_price(self):
        prop = listing(price=100_000)
        rental = estimate_rent(prop)
        scored = score_property(prop, rental)
        expected = (rental.monthly_rent * 12) / 100_000 * 100
        assert scored.gross_yield == pytest.approx(expected, abs=0.01)

    def test_net_yield_stays_below_gross_yield(self):
        """Charges are subtracted, so the net can never be the higher of the
        two. This has to hold whatever the weights become."""
        prop = listing()
        scored = score_property(prop, estimate_rent(prop))
        assert scored.net_yield < scored.gross_yield

    @pytest.mark.parametrize("price", [15_000, 120_000, 3_000_000])
    def test_score_stays_within_bounds(self, price):
        """A score is comparable only if it is bounded. Extreme prices used to
        be the way to push a weighted sum outside its own scale."""
        prop = listing(price=price)
        scored = score_property(prop, estimate_rent(prop))
        assert 0 <= scored.score <= 100

    def test_a_listing_without_an_estimate_is_not_scored(self):
        """No rent, no yield: we return the listing unscored rather than
        ranking it on a guess."""
        scored = score_property(listing(), None)
        assert scored.score == 0
        assert scored.gross_yield is None or scored.gross_yield == 0

    def test_a_fresh_listing_scores_above_an_old_one(self):
        """Freshness is one of the weights, and it is the one that decides
        between two otherwise identical listings."""
        now = datetime.now(timezone.utc)
        fresh = listing(date_posted=now - timedelta(days=1))
        old = listing(date_posted=now - timedelta(days=90))
        assert (
            score_property(fresh, estimate_rent(fresh)).score
            > score_property(old, estimate_rent(old)).score
        )


class TestSuspiciousListings:
    def test_a_price_far_below_the_local_average_is_rejected(self):
        """A flat at a fifth of the going rate is a data error or a scam, and
        it would otherwise top the ranking: the yield looks spectacular."""
        assert _is_suspicious(listing(city="Colmar", surface=40.0, price=20_000))

    def test_a_merely_cheap_listing_is_kept(self):
        """The filter must not eat the good deals it exists to find."""
        assert not _is_suspicious(listing(city="Colmar", surface=40.0, price=67_000))

    def test_suspicious_listings_never_reach_the_ranking(self):
        scam = listing(city="Colmar", surface=40.0, price=20_000, title="Too good")
        honest = listing(city="Colmar", surface=40.0, price=67_000)
        ranked = score_properties([scam, honest])
        assert [p.property.price for p in ranked] == [67_000]


class TestRanking:
    def test_listings_come_back_best_first(self):
        cheap = listing(price=80_000)
        dear = listing(price=400_000)
        ranked = score_properties([dear, cheap])
        assert ranked[0].score >= ranked[1].score
        assert ranked[0].property.price == 80_000
