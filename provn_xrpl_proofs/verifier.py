# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .client import XrplClient
from .normalizer import UnsupportedPayment, normalize_xrpl_payment
from .types import Check, VerificationResult
from .validators import is_valid_xrpl_tx_hash, normalize_xrpl_tx_hash


def _fail(tx_hash: str, reason: str, detail: str, checks: list[Check]) -> VerificationResult:
    return VerificationResult(ok=False, reason=reason, detail=detail, tx_hash=tx_hash, checks=checks)


def verify_xrpl_payment(
    tx_hash: str,
    rpc_url: str,
    expected_from: Optional[str] = None,
    expected_to: Optional[str] = None,
    expected_amount_xrp: Optional[str | Decimal] = None,
    expected_destination_tag: Optional[int] = None,
    timeout: float = 30.0,
) -> VerificationResult:
    canonical = normalize_xrpl_tx_hash(tx_hash)
    if not is_valid_xrpl_tx_hash(canonical):
        return _fail(canonical, "invalid_tx_hash", f"Not a 64-hex tx hash: {tx_hash!r}", [])

    checks: list[Check] = []

    with XrplClient(rpc_url, timeout=timeout) as client:
        try:
            raw = client.fetch_tx_raw(canonical)
        except Exception as e:
            return _fail(canonical, "fetch_failed", f"RPC fetch failed: {e}", checks)

    try:
        norm = normalize_xrpl_payment(raw)
    except UnsupportedPayment as e:
        checks.append(Check(name="eligible_payment", ok=False, actual=str(e)))
        return _fail(canonical, "not_eligible", str(e), checks)

    checks.append(Check(name="eligible_payment", ok=True))

    if expected_from is not None:
        ok = norm.from_addr == expected_from
        checks.append(Check(name="from_addr", ok=ok, expected=expected_from, actual=norm.from_addr))
        if not ok:
            return _fail(
                canonical,
                "from_mismatch",
                f"from_addr mismatch: expected {expected_from!r}, got {norm.from_addr!r}",
                checks,
            )

    if expected_to is not None:
        ok = norm.to_addr == expected_to
        checks.append(Check(name="to_addr", ok=ok, expected=expected_to, actual=norm.to_addr))
        if not ok:
            return _fail(
                canonical,
                "to_mismatch",
                f"to_addr mismatch: expected {expected_to!r}, got {norm.to_addr!r}",
                checks,
            )

    if expected_amount_xrp is not None:
        expected_dec = Decimal(str(expected_amount_xrp))
        ok = norm.amount_xrp == expected_dec
        checks.append(Check(
            name="amount_xrp", ok=ok, expected=str(expected_dec), actual=str(norm.amount_xrp),
        ))
        if not ok:
            return _fail(
                canonical,
                "amount_mismatch",
                f"amount_xrp mismatch: expected {expected_dec}, got {norm.amount_xrp}",
                checks,
            )

    if expected_destination_tag is not None:
        ok = norm.destination_tag == expected_destination_tag
        checks.append(Check(
            name="destination_tag", ok=ok,
            expected=str(expected_destination_tag), actual=str(norm.destination_tag),
        ))
        if not ok:
            return _fail(
                canonical,
                "dt_mismatch",
                f"destination_tag mismatch: expected {expected_destination_tag}, got {norm.destination_tag}",
                checks,
            )

    return VerificationResult(
        ok=True,
        reason="ok",
        detail="All checks passed. Transaction is a validated successful XRP payment matching the expected values.",
        tx_hash=canonical,
        checks=checks,
    )
