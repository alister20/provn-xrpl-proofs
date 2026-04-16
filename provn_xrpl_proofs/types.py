# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class XrplTx:
    tx_hash: str
    from_addr: str
    to_addr: str
    amount_drops: str
    amount_xrp: Decimal
    ledger_index: int
    timestamp: Optional[datetime]
    validated: bool
    tx_type: str = "Payment"
    currency: str = "XRP"


@dataclass(frozen=True)
class NormalizedXrplPayment:
    tx_hash: str
    from_addr: str
    to_addr: str
    amount_xrp: Decimal
    fee_xrp: Decimal
    ledger_index: int
    validated: bool
    tx_result: str
    destination_tag: Optional[int]
    reference: str
    raw: dict = field(repr=False)


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    reason: str
    detail: str
    tx_hash: str
    checks: list[Check] = field(default_factory=list)
