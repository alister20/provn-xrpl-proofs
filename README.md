# provn-xrpl-proofs

An independent, read-only verifier for XRPL payments referenced by Provn.

This library lets any third party, including regulators and banking partners, confirm that an XRPL transaction referenced by Provn actually exists on the ledger and matches the claimed values, using only a public XRPL RPC endpoint. It depends on nothing from Provn's infrastructure.

## What this library does

Given an XRPL transaction hash and a set of expectations (sender, recipient, amount, destination tag), the library will:

1. Fetch the transaction from an XRPL JSON-RPC node.
2. Check that it is **validated** by the network (not just submitted).
3. Check that it is a successful `Payment` that delivered XRP.
4. Compare each expectation you provide against the on-chain values.
5. Return a structured `VerificationResult` with a pass/fail reason and a per-check breakdown.

If every check passes, the transaction is exactly what Provn claims it to be.

## What this library does not do

This is a **verifier**, not a producer. It does not sign, anchor, submit, or otherwise produce proofs. It has no keys, no API credentials, and no state.

## Where this fits in the Provn pipeline

Provn observes payments across multiple chains, validates them, and produces tamper-evident receipts that are cryptographically anchored on-chain by Provn's commercial service. This open-source library covers the **observation and verification** step for XRPL only.

```
[XRPL ledger]  ──►  observe + validate  ──►  receipt produced  ──►  anchored on-chain
                            ▲
                            │
                  this library covers the
                  observe + validate step
                  for XRPL. Anyone can
                  re-run it against any tx
                  referenced in a receipt
```

The receipt-production and on-chain-anchoring layers are Provn's commercial product and are not included in this repository. The verification layer is open-source so that any third party (auditor, regulator, or counterparty) can independently confirm that an XRPL transaction referenced in a Provn receipt matches the ledger.

## Install

```bash
pip install provn-xrpl-proofs
```

Requires Python 3.10+.

## Verify an XRPL payment from the command line

General form:

```bash
provn-xrpl-verify <tx_hash> \
  --from-addr <rSENDER...> \
  --to-addr <rRECIPIENT...> \
  --amount <xrp-decimal> \
  --destination-tag <integer> \
  --rpc https://xrplcluster.com/
```

Any expectation flag you omit is simply not checked. Running with no expectation flags verifies only that the transaction is a validated successful XRP payment on the ledger.

Exit code is `0` on a full match, `1` on any mismatch, `2` on a malformed hash.

### Example 1: a real mainnet payment (no destination tag)

Copy and paste exactly as shown:

```bash
provn-xrpl-verify 0585A1DD9183905D32D61430F920633B75D3230288D9E72E56C3F6636C4582CD \
  --from-addr rBhUd4UefA5SRhRKRQNuRNZixKMpFNKXn7 \
  --to-addr rNY4JmizzS93qcjzj1bwY9GhxiyaTaWkdz \
  --amount 727
```

Expected output (abridged):

```json
{
  "ok": true,
  "reason": "ok",
  "detail": "All checks passed. Transaction is a validated successful XRP payment matching the expected values.",
  "tx_hash": "0585a1dd9183905d32d61430f920633b75d3230288d9e72e56c3f6636c4582cd",
  "checks": [
    {"name": "eligible_payment", "ok": true},
    {"name": "from_addr", "ok": true, "expected": "rBhUd4UefA5SRhRKRQNuRNZixKMpFNKXn7", "actual": "rBhUd4UefA5SRhRKRQNuRNZixKMpFNKXn7"},
    {"name": "to_addr", "ok": true, "expected": "rNY4JmizzS93qcjzj1bwY9GhxiyaTaWkdz", "actual": "rNY4JmizzS93qcjzj1bwY9GhxiyaTaWkdz"},
    {"name": "amount_xrp", "ok": true, "expected": "727", "actual": "727.000000"}
  ]
}
```

### Example 2: a real mainnet payment with a destination tag

```bash
provn-xrpl-verify 865B774AF4648AD87A06A98338F6399DBC3FA6B6D03474362B4ACC20CC9E2AE7 \
  --from-addr rhVJtSLJ7yRWd4GSzShJUs53kJ6nyEdCUZ \
  --to-addr rLHzPsX6oXkzU2qL12kHCH8G8cnZv1rBJh \
  --amount 180.173178 \
  --destination-tag 394099408
```

### Example 3: minimal check, no expectations

Just confirms the transaction is a validated successful XRP payment on the ledger:

```bash
provn-xrpl-verify 0585A1DD9183905D32D61430F920633B75D3230288D9E72E56C3F6636C4582CD
```

### Example 4: demonstrate a mismatch (should fail)

Deliberately wrong amount to show how a failure looks:

```bash
provn-xrpl-verify 0585A1DD9183905D32D61430F920633B75D3230288D9E72E56C3F6636C4582CD \
  --amount 1
```

Output:

```json
{
  "ok": false,
  "reason": "amount_mismatch",
  "detail": "amount_xrp mismatch: expected 1, got 727.000000",
  "tx_hash": "0585a1dd9183905d32d61430f920633b75d3230288d9e72e56c3f6636c4582cd",
  "checks": [
    {"name": "eligible_payment", "ok": true},
    {"name": "amount_xrp", "ok": false, "expected": "1", "actual": "727.000000"}
  ]
}
```

Exit code `1`.

### Example 5: use a different XRPL node

Any public XRPL JSON-RPC endpoint works. The library has no opinion about which node you trust:

```bash
provn-xrpl-verify 0585A1DD9183905D32D61430F920633B75D3230288D9E72E56C3F6636C4582CD \
  --rpc https://s1.ripple.com:51234/
```

## Use as a library

```python
from provn_xrpl_proofs import verify_xrpl_payment

result = verify_xrpl_payment(
    tx_hash="A1B2C3...",
    rpc_url="https://xrplcluster.com/",
    expected_from="rSENDER...",
    expected_to="rRECIPIENT...",
    expected_amount_xrp="12.345678",
    expected_destination_tag=20250415,
)

if result.ok:
    print("match")
else:
    print(f"mismatch: {result.reason} - {result.detail}")
```

## Failure reasons

| `reason` | Meaning |
|----------|---------|
| `ok` | All checks passed |
| `invalid_tx_hash` | The hash is not 64 hex characters |
| `fetch_failed` | RPC call failed or the transaction was not found |
| `not_eligible` | Transaction is not a validated successful XRP payment |
| `from_mismatch` | `Account` did not match `expected_from` |
| `to_mismatch` | `Destination` did not match `expected_to` |
| `amount_mismatch` | Delivered XRP did not match `expected_amount_xrp` |
| `dt_mismatch` | `DestinationTag` did not match `expected_destination_tag` |

## Payment eligibility rules

The library will reject any transaction that does not satisfy all of:

- `validated` is `true` (the network has finalized the transaction)
- RPC `status` is `"success"`
- `TransactionType` is `"Payment"`
- `meta.TransactionResult` is `"tesSUCCESS"` (the payment actually delivered)
- Delivered amount is XRP (issued-currency payments are out of scope)

These rules are intentionally strict: a verification only succeeds for transactions that have unambiguously delivered XRP on the ledger.

## Testing

```bash
pip install -e ".[dev]"
pytest
```

The test suite uses recorded XRPL transaction fixtures and runs entirely offline.

## License

Apache License 2.0. See [LICENSE](LICENSE).

## About Provn

Provn generates compliant payment receipts and anchors cryptographic evidence on-chain. This repository is the open, auditable **verification** side of Provn's XRPL pipeline. Partner and regulator questions welcome.
