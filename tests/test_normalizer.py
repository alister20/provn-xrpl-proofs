from decimal import Decimal

import pytest

from provn_xrpl_proofs.normalizer import UnsupportedPayment, normalize_xrpl_payment


def test_valid_payment_normalizes(tx_payment_valid):
    n = normalize_xrpl_payment(tx_payment_valid)
    assert n.tx_hash == tx_payment_valid["hash"].lower()
    assert n.from_addr == "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"
    assert n.to_addr == "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1"
    assert n.amount_xrp == Decimal("12.345678")
    assert n.fee_xrp == Decimal("0.000012")
    assert n.validated is True
    assert n.tx_result == "tesSUCCESS"
    assert n.destination_tag == 20250415
    assert n.reference == "xrpl:dt:20250415"


def test_memo_reference(tx_payment_with_memo):
    n = normalize_xrpl_payment(tx_payment_with_memo)
    assert n.reference == "xrpl:memo"
    assert n.destination_tag is None


def test_unvalidated_rejected(tx_payment_unvalidated):
    with pytest.raises(UnsupportedPayment, match="validated=false"):
        normalize_xrpl_payment(tx_payment_unvalidated)


def test_failed_payment_rejected(tx_payment_failed):
    with pytest.raises(UnsupportedPayment, match="tecPATH_DRY"):
        normalize_xrpl_payment(tx_payment_failed)


def test_non_payment_rejected(tx_offer_create):
    with pytest.raises(UnsupportedPayment, match="OfferCreate"):
        normalize_xrpl_payment(tx_offer_create)


def test_issued_currency_rejected(tx_payment_valid):
    tx_payment_valid["meta"]["delivered_amount"] = {
        "currency": "USD",
        "issuer": "rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1",
        "value": "10",
    }
    with pytest.raises(UnsupportedPayment, match="issued currency"):
        normalize_xrpl_payment(tx_payment_valid)
