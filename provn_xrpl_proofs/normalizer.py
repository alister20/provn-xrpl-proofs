# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from .encoding import drops_to_xrp
from .types import NormalizedXrplPayment


class UnsupportedPayment(ValueError):
    pass


def _extract_reference(tx: dict) -> str:
    memos = tx.get("Memos") or []
    for m in memos:
        memo = (m or {}).get("Memo") or {}
        if memo:
            return "xrpl:memo"

    dt = tx.get("DestinationTag")
    if isinstance(dt, int):
        return f"xrpl:dt:{dt}"

    return "xrpl:import"


def _get_delivered_drops(tx: dict) -> str:
    meta = tx.get("meta") or {}
    delivered = meta.get("delivered_amount")
    if delivered is None:
        delivered = meta.get("DeliveredAmount")

    if isinstance(delivered, str) and delivered.strip():
        return delivered.strip()

    if isinstance(delivered, dict):
        raise UnsupportedPayment(
            "DeliveredAmount is issued currency. Only XRP-denominated payments are supported."
        )

    amt = tx.get("Amount")
    if isinstance(amt, str) and amt.strip():
        return amt.strip()

    raise UnsupportedPayment(
        "No delivered XRP amount found (checked delivered_amount/DeliveredAmount/Amount)."
    )


def normalize_xrpl_payment(tx: dict) -> NormalizedXrplPayment:
    validated = bool(tx.get("validated", False))
    if not validated:
        raise UnsupportedPayment("TX is not validated yet (validated=false).")

    if tx.get("status") != "success":
        raise UnsupportedPayment(f"XRPL tx status not success: {tx.get('status')}")

    tx_type = tx.get("TransactionType")
    if tx_type != "Payment":
        raise UnsupportedPayment(f"Only Payment is supported. Got: {tx_type}")

    meta = tx.get("meta") or {}
    tx_result = meta.get("TransactionResult")
    if tx_result != "tesSUCCESS":
        raise UnsupportedPayment(f"XRPL tx not successful: {tx_result}")

    from_addr = tx.get("Account")
    to_addr = tx.get("Destination")
    if not from_addr or not to_addr:
        raise UnsupportedPayment("Missing Account or Destination in tx.")

    fee_drops = tx.get("Fee")
    if not isinstance(fee_drops, str) or not fee_drops.strip():
        raise UnsupportedPayment("Missing/invalid Fee in tx.")

    ledger_index = tx.get("ledger_index")
    if not isinstance(ledger_index, int):
        raise UnsupportedPayment("Missing/invalid ledger_index in tx.")

    delivered_drops = _get_delivered_drops(tx)

    destination_tag = tx.get("DestinationTag") if isinstance(tx.get("DestinationTag"), int) else None
    reference = _extract_reference(tx)

    tx_hash = tx.get("hash")
    if not tx_hash:
        raise UnsupportedPayment("Missing tx hash field.")

    return NormalizedXrplPayment(
        tx_hash=tx_hash.lower(),
        from_addr=from_addr,
        to_addr=to_addr,
        amount_xrp=drops_to_xrp(delivered_drops),
        fee_xrp=drops_to_xrp(fee_drops),
        ledger_index=ledger_index,
        validated=True,
        tx_result=tx_result,
        destination_tag=destination_tag,
        reference=reference,
        raw=tx,
    )
