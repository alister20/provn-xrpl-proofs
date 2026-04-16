from decimal import Decimal

from provn_xrpl_proofs.client import _parse_tx


def test_parse_payment(tx_payment_valid):
    item = {
        "tx": tx_payment_valid,
        "meta": tx_payment_valid["meta"],
        "validated": tx_payment_valid["validated"],
    }
    parsed = _parse_tx(item)
    assert parsed is not None
    assert parsed.tx_type == "Payment"
    assert parsed.currency == "XRP"
    assert parsed.amount_xrp == Decimal("12.345678")
    assert parsed.validated is True


def test_parse_offer_create(tx_offer_create):
    item = {
        "tx": tx_offer_create,
        "meta": tx_offer_create["meta"],
        "validated": tx_offer_create["validated"],
    }
    parsed = _parse_tx(item)
    assert parsed is not None
    assert parsed.tx_type == "OfferCreate"
    assert parsed.amount_drops == "10"
    assert parsed.amount_xrp == Decimal("0.000010")


def test_parse_missing_hash_returns_none():
    assert _parse_tx({"tx": {}, "meta": {}, "validated": True}) is None
