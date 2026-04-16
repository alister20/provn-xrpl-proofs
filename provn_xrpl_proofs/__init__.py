# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from .client import XrplClient
from .encoding import drops_to_xrp, ripple_date_to_utc
from .normalizer import UnsupportedPayment, normalize_xrpl_payment
from .types import Check, NormalizedXrplPayment, VerificationResult, XrplTx
from .validators import (
    is_valid_xrpl_address,
    is_valid_xrpl_tx_hash,
    normalize_xrpl_address,
    normalize_xrpl_tx_hash,
)
from .verifier import verify_xrpl_payment

__all__ = [
    "Check",
    "NormalizedXrplPayment",
    "UnsupportedPayment",
    "VerificationResult",
    "XrplClient",
    "XrplTx",
    "drops_to_xrp",
    "is_valid_xrpl_address",
    "is_valid_xrpl_tx_hash",
    "normalize_xrpl_address",
    "normalize_xrpl_payment",
    "normalize_xrpl_tx_hash",
    "ripple_date_to_utc",
    "verify_xrpl_payment",
]

__version__ = "0.1.0"
