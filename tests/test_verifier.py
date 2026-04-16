from decimal import Decimal

import pytest

from provn_xrpl_proofs import verifier as verifier_mod
from provn_xrpl_proofs.verifier import verify_xrpl_payment


@pytest.fixture
def mock_rpc(monkeypatch, tx_payment_valid):
    def _install(tx: dict):
        def fake_fetch(self, tx_hash: str) -> dict:
            return tx
        monkeypatch.setattr(verifier_mod.XrplClient, "fetch_tx_raw", fake_fetch)

    return _install


HASH = "A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890A1B2C3D4E5F67890"


def test_invalid_hash_returns_fast():
    r = verify_xrpl_payment("nothex", rpc_url="http://unused")
    assert not r.ok
    assert r.reason == "invalid_tx_hash"


def test_ok_no_expectations(mock_rpc, tx_payment_valid):
    mock_rpc(tx_payment_valid)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused")
    assert r.ok
    assert r.reason == "ok"
    assert any(c.name == "eligible_payment" and c.ok for c in r.checks)


def test_ok_all_expectations_match(mock_rpc, tx_payment_valid):
    mock_rpc(tx_payment_valid)
    r = verify_xrpl_payment(
        HASH,
        rpc_url="http://unused",
        expected_from="rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf",
        expected_to="rU6K7V3Po4snVhBBaU29sesqs2qTQJWDw1",
        expected_amount_xrp="12.345678",
        expected_destination_tag=20250415,
    )
    assert r.ok
    assert r.reason == "ok"
    names = [c.name for c in r.checks]
    assert names == ["eligible_payment", "from_addr", "to_addr", "amount_xrp", "destination_tag"]
    assert all(c.ok for c in r.checks)



def test_to_mismatch(mock_rpc, tx_payment_valid):
    mock_rpc(tx_payment_valid)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused", expected_to="rWRONG")
    assert not r.ok
    assert r.reason == "to_mismatch"
    assert "rWRONG" in r.detail


def test_amount_mismatch(mock_rpc, tx_payment_valid):
    mock_rpc(tx_payment_valid)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused", expected_amount_xrp=Decimal("99"))
    assert not r.ok
    assert r.reason == "amount_mismatch"


def test_dt_mismatch(mock_rpc, tx_payment_valid):
    mock_rpc(tx_payment_valid)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused", expected_destination_tag=1)
    assert not r.ok
    assert r.reason == "dt_mismatch"


def test_not_eligible_unvalidated(mock_rpc, tx_payment_unvalidated):
    mock_rpc(tx_payment_unvalidated)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused")
    assert not r.ok
    assert r.reason == "not_eligible"
    assert "validated=false" in r.detail


def test_not_eligible_non_payment(mock_rpc, tx_offer_create):
    mock_rpc(tx_offer_create)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused")
    assert not r.ok
    assert r.reason == "not_eligible"


def test_fetch_failed(monkeypatch):
    def raising_fetch(self, tx_hash: str) -> dict:
        raise RuntimeError("boom")
    monkeypatch.setattr(verifier_mod.XrplClient, "fetch_tx_raw", raising_fetch)
    r = verify_xrpl_payment(HASH, rpc_url="http://unused")
    assert not r.ok
    assert r.reason == "fetch_failed"
    assert "boom" in r.detail


def test_short_circuits_on_first_failure(mock_rpc, tx_payment_valid):
    mock_rpc(tx_payment_valid)
    r = verify_xrpl_payment(
        HASH,
        rpc_url="http://unused",
        expected_from="rWRONG",
        expected_to="rALSO_WRONG",
    )
    assert not r.ok
    assert r.reason == "from_mismatch"
    names = [c.name for c in r.checks]
    assert names == ["eligible_payment", "from_addr"]
