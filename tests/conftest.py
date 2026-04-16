import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def tx_payment_valid() -> dict:
    return _load("payment_valid.json")


@pytest.fixture
def tx_payment_with_memo() -> dict:
    return _load("payment_with_memo.json")


@pytest.fixture
def tx_payment_unvalidated() -> dict:
    return _load("payment_unvalidated.json")


@pytest.fixture
def tx_payment_failed() -> dict:
    return _load("payment_failed.json")


@pytest.fixture
def tx_offer_create() -> dict:
    return _load("offer_create.json")
