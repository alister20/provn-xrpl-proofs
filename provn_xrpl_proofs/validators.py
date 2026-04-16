# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations


def is_valid_xrpl_address(address: str) -> bool:
    a = (address or "").strip()
    return 25 <= len(a) <= 40 and a.startswith("r")


def is_valid_xrpl_tx_hash(txh: str) -> bool:
    h = (txh or "").strip().lower()
    h = h.split(":", 1)[-1] if ":" in h else h
    if len(h) != 64:
        return False
    try:
        int(h, 16)
        return True
    except ValueError:
        return False


def normalize_xrpl_address(address: str) -> str:
    return (address or "").strip()


def normalize_xrpl_tx_hash(txh: str) -> str:
    h = (txh or "").strip().lower()
    return h.split(":", 1)[-1] if ":" in h else h
