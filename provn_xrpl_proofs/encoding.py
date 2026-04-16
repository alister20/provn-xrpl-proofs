# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

RIPPLE_EPOCH_OFFSET = 946684800
DROPS_PER_XRP = Decimal("1000000")


def drops_to_xrp(drops: str | int) -> Decimal:
    return (Decimal(drops) / DROPS_PER_XRP).quantize(Decimal("0.000001"))


def ripple_date_to_utc(ripple_seconds: int) -> datetime:
    return datetime.fromtimestamp(ripple_seconds + RIPPLE_EPOCH_OFFSET, tz=timezone.utc)
