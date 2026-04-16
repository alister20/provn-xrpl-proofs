# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

import httpx

from .encoding import drops_to_xrp, ripple_date_to_utc
from .types import XrplTx


def _extract_amount(amount_field) -> tuple[str, Decimal, str]:
    if isinstance(amount_field, str):
        drops = amount_field.strip()
        return drops, drops_to_xrp(drops), "XRP"
    if isinstance(amount_field, dict):
        value = str(amount_field.get("value") or "0")
        currency = amount_field.get("currency") or "???"
        try:
            dec = Decimal(value)
        except Exception:
            dec = Decimal(0)
        return value, dec, currency
    return "0", Decimal(0), "XRP"


def _parse_tx(item: dict) -> Optional[XrplTx]:
    tx = item.get("tx") or {}
    meta = item.get("meta") or {}

    tx_hash = (tx.get("hash") or "").strip().lower()
    if not tx_hash or len(tx_hash) != 64:
        return None

    tx_type = tx.get("TransactionType") or "Unknown"
    account = tx.get("Account") or ""

    ripple_date = tx.get("date")
    ts: Optional[datetime] = ripple_date_to_utc(ripple_date) if isinstance(ripple_date, int) else None

    if tx_type == "Payment":
        destination = tx.get("Destination") or ""
        delivered = meta.get("delivered_amount")
        amount_field = delivered if delivered else tx.get("Amount")
        try:
            raw, dec, currency = _extract_amount(amount_field)
        except Exception:
            raw, dec, currency = "0", Decimal(0), "XRP"
        return XrplTx(
            tx_hash=tx_hash,
            from_addr=account,
            to_addr=destination,
            amount_drops=raw,
            amount_xrp=dec,
            ledger_index=int(tx.get("ledger_index") or 0),
            timestamp=ts,
            validated=bool(item.get("validated", False)),
            tx_type=tx_type,
            currency=currency,
        )

    destination = tx.get("Destination") or account
    fee = tx.get("Fee") or "0"
    try:
        fee_xrp = drops_to_xrp(fee)
    except Exception:
        fee_xrp = Decimal(0)

    return XrplTx(
        tx_hash=tx_hash,
        from_addr=account,
        to_addr=destination,
        amount_drops=fee,
        amount_xrp=fee_xrp,
        ledger_index=int(tx.get("ledger_index") or 0),
        timestamp=ts,
        validated=bool(item.get("validated", False)),
        tx_type=tx_type,
        currency="XRP",
    )


class XrplClient:
    def __init__(self, rpc_url: str, timeout: float = 30.0):
        self.rpc_url = rpc_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self) -> "XrplClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def rpc(self, method: str, params: list[dict]) -> dict:
        r = self._client.post(
            self.rpc_url,
            json={"method": method, "params": params},
            headers={"content-type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
        if "result" not in data:
            raise RuntimeError(f"Unexpected XRPL RPC response: {data}")
        return data["result"]

    def fetch_tx_raw(self, tx_hash: str) -> dict:
        res = self.rpc("tx", [{"transaction": tx_hash.upper(), "binary": False}])
        if res.get("error"):
            raise RuntimeError(
                f"XRPL tx error: {res.get('error')} {res.get('error_message') or ''}".strip()
            )
        return res

    def fetch_tx(self, tx_hash: str) -> Optional[XrplTx]:
        tx_hash_lower = (tx_hash or "").strip().lower()
        if not tx_hash_lower or len(tx_hash_lower) != 64:
            return None

        try:
            res = self.fetch_tx_raw(tx_hash_lower)
        except RuntimeError:
            return None

        item = {
            "tx": res,
            "meta": res.get("meta") or {},
            "validated": res.get("validated", False),
        }
        return _parse_tx(item)

    def fetch_txs(
        self,
        address: str,
        from_dt: datetime,
        to_dt: datetime,
        max_pages: int = 400,
    ) -> List[XrplTx]:
        address = (address or "").strip()
        from_dt = from_dt.astimezone(timezone.utc)
        to_dt = to_dt.astimezone(timezone.utc)

        out: List[XrplTx] = []
        marker = None
        pages = 0

        while True:
            pages += 1
            if pages > max_pages:
                raise RuntimeError("xrpl_account_tx_max_pages_reached")

            params: dict = {
                "account": address,
                "ledger_index_min": -1,
                "ledger_index_max": -1,
                "limit": 200,
                "forward": False,
            }
            if marker:
                params["marker"] = marker

            result = self.rpc("account_tx", [params])
            if result.get("error"):
                raise RuntimeError(
                    f"XRPL account_tx error: {result.get('error')} {result.get('error_message') or ''}".strip()
                )

            items = result.get("transactions") or []
            if not items:
                break

            stop = False
            for item in items:
                xtx = _parse_tx(item)
                if xtx is None:
                    continue

                if xtx.timestamp is not None:
                    if xtx.timestamp > to_dt:
                        continue
                    if xtx.timestamp < from_dt:
                        stop = True
                        break

                out.append(xtx)

            if stop:
                break

            marker = result.get("marker")
            if not marker:
                break

        return out
