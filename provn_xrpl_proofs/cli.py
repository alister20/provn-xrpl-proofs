# Copyright 2026 Provn
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .verifier import verify_xrpl_payment

DEFAULT_RPC = "https://xrplcluster.com/"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="provn-xrpl-verify",
        description="Verify an XRPL transaction against expected values.",
    )
    parser.add_argument("tx_hash", help="XRPL transaction hash (64 hex chars)")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help=f"XRPL JSON-RPC endpoint (default: {DEFAULT_RPC})")
    parser.add_argument("--from-addr", dest="from_addr", default=None)
    parser.add_argument("--to-addr", dest="to_addr", default=None)
    parser.add_argument("--amount", dest="amount", default=None)
    parser.add_argument("--destination-tag", dest="dt", type=int, default=None)
    args = parser.parse_args(argv)

    result = verify_xrpl_payment(
        tx_hash=args.tx_hash,
        rpc_url=args.rpc,
        expected_from=args.from_addr,
        expected_to=args.to_addr,
        expected_amount_xrp=args.amount,
        expected_destination_tag=args.dt,
    )

    payload = {
        "ok": result.ok,
        "reason": result.reason,
        "detail": result.detail,
        "tx_hash": result.tx_hash,
        "checks": [asdict(c) for c in result.checks],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
