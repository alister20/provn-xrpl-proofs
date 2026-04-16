from datetime import datetime, timezone
from decimal import Decimal

from provn_xrpl_proofs.encoding import drops_to_xrp, ripple_date_to_utc


def test_drops_to_xrp_basic():
    assert drops_to_xrp("1000000") == Decimal("1.000000")


def test_drops_to_xrp_fractional():
    assert drops_to_xrp("12345678") == Decimal("12.345678")


def test_drops_to_xrp_accepts_int():
    assert drops_to_xrp(1) == Decimal("0.000001")


def test_ripple_date_to_utc():
    assert ripple_date_to_utc(0) == datetime(2000, 1, 1, tzinfo=timezone.utc)
    assert ripple_date_to_utc(828_000_000) == datetime(2026, 3, 28, 8, 0, 0, tzinfo=timezone.utc)
