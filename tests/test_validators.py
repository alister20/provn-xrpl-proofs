from provn_xrpl_proofs.validators import (
    is_valid_xrpl_address,
    is_valid_xrpl_tx_hash,
    normalize_xrpl_address,
    normalize_xrpl_tx_hash,
)


class TestAddress:
    def test_valid(self):
        assert is_valid_xrpl_address("rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf")

    def test_missing_r_prefix(self):
        assert not is_valid_xrpl_address("GWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf")

    def test_too_short(self):
        assert not is_valid_xrpl_address("rShort")

    def test_empty(self):
        assert not is_valid_xrpl_address("")

    def test_whitespace_stripped(self):
        assert is_valid_xrpl_address("  rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf  ")


class TestTxHash:
    HASH = "a" * 64

    def test_valid_lower(self):
        assert is_valid_xrpl_tx_hash(self.HASH)

    def test_valid_upper_normalizes(self):
        assert is_valid_xrpl_tx_hash(self.HASH.upper())

    def test_chain_prefix_ok(self):
        assert is_valid_xrpl_tx_hash(f"xrpl:{self.HASH}")

    def test_too_short(self):
        assert not is_valid_xrpl_tx_hash("a" * 63)

    def test_non_hex(self):
        assert not is_valid_xrpl_tx_hash("z" * 64)

    def test_normalize_strips_prefix(self):
        assert normalize_xrpl_tx_hash(f"xrpl:{self.HASH.upper()}") == self.HASH


def test_normalize_address_preserves_case():
    addr = "rGWrZyQqhTp9Xu7G5Pkayo7bXjH4k4QYpf"
    assert normalize_xrpl_address(f"  {addr}  ") == addr
