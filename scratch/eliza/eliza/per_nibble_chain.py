"""Eliza.PerNibbleChain — chain stream at every nibble (lossless granularity).

Per the user's directive: "how can we achieve using the chain,
exclusively, as our output data, and then reconstruct the original
from it?"

At per-window granularity the chain is many-to-one (256 bytes fold to
one chain, so reconstruction is lossy). At per-nibble granularity the
chamber-walk transition is INVERTIBLE: knowing (chamber_before,
chamber_after) uniquely determines the nibble that produced it (when
such a nibble exists, which it always does on bytes that came from
real input — bijection over the 16 reachable transitions per chamber).

This module realises the per-nibble chain stream + the inverse lookup
that takes (chamber_before, chamber_after) → nibble. Together they
make the chain-only output LOSSLESS.

Trade-off vs per-window: 2 chain symbols per byte instead of 1 per 256
bytes. At log₂(24) ≈ 4.58 bits per chain, raw cost is 9.16 b/byte —
worse than raw bytes. The hope is that adaptive prediction over the
chain alphabet captures enough W-axis redundancy to beat byte trigram.
Empirical question; F5 measures.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterator, List, Optional, Tuple

from eliza.alphabets import (
    Chamber, NIBBLE_TO_PERM, ORIGIN, perm_compose,
)
from eliza.chain_symbol import ChainSymbol


# --- F2: chamber-pair → nibble inverse lookup ---------------------------


@lru_cache(maxsize=1)
def _build_inverse_table() -> Dict[Tuple[Chamber, Chamber], int]:
    """For every (before, after) chamber pair reachable by some nibble,
    return the nibble that produced the transition.

    Each chamber has exactly 16 outgoing nibble-transitions (one per
    nibble), so the table has 24 × 16 = 384 entries. The 16 outgoing
    transitions land on distinct chambers iff the 16 nibble perms are
    distinct (they are, since NIBBLE_TO_PERM enumerates V₄ × S₃-invol).
    Hence the inverse is unambiguous.
    """
    from eliza.manifold import Manifold
    m = Manifold()
    table: Dict[Tuple[Chamber, Chamber], int] = {}
    for before in m.nodes:
        for nib in range(16):
            after = perm_compose(before, NIBBLE_TO_PERM[nib])
            key = (before, after)
            if key in table:
                # Sanity: should not happen if the 16 perms are distinct.
                raise ValueError(
                    f"collision in inverse table: ({before}, {after}) "
                    f"reachable by both nibble {table[key]} and nibble {nib}"
                )
            table[key] = nib
    return table


def nibble_from_transition(before: Chamber, after: Chamber) -> Optional[int]:
    """Return the unique nibble n with perm_compose(before, n_perm) == after,
    or None if no such nibble exists (after is unreachable from before
    via a single nibble)."""
    return _build_inverse_table().get((before, after))


# --- F1: per-nibble chain emitter ---------------------------------------


def bytes_to_nibbles(window: bytes) -> List[int]:
    """Split each byte into (hi, lo) nibbles in order."""
    out: List[int] = []
    for b in window:
        out.append((b >> 4) & 0xF)
        out.append(b & 0xF)
    return out


def nibbles_to_bytes(nibbles: List[int]) -> bytes:
    """Pair nibbles into bytes (hi, lo). Odd-length nibble list raises."""
    if len(nibbles) % 2 != 0:
        raise ValueError("nibble list has odd length; cannot pair into bytes")
    out = bytearray()
    for i in range(0, len(nibbles), 2):
        out.append((nibbles[i] << 4) | nibbles[i + 1])
    return bytes(out)


def per_nibble_chain_stream(data: bytes) -> List[ChainSymbol]:
    """Emit one ChainSymbol per nibble of input, tracking the chamber
    walk from ORIGIN. The chain is the decomposition of the
    chamber-after-the-nibble.
    """
    state = ORIGIN
    out: List[ChainSymbol] = []
    for n in bytes_to_nibbles(data):
        state = perm_compose(state, NIBBLE_TO_PERM[n])
        out.append(ChainSymbol.from_s4(state))
    return out


def per_nibble_stream_to_bytes(chain_stream: List[ChainSymbol]) -> bytes:
    """Lossless reconstruction: walk chain_stream from ORIGIN, invert
    each (before, after) chamber pair to its producing nibble, pair
    nibbles into bytes."""
    state = ORIGIN
    nibbles: List[int] = []
    for ch in chain_stream:
        after = ch.to_s4()
        nib = nibble_from_transition(state, after)
        if nib is None:
            raise ValueError(
                f"chain stream invalid: transition ({state}, {after}) "
                f"has no producing nibble"
            )
        nibbles.append(nib)
        state = after
    return nibbles_to_bytes(nibbles)


# --- Self-check: round-trip ---------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path

    HERE = Path(__file__).resolve().parent

    # (1) Inverse table is well-formed (no collisions, full coverage).
    table = _build_inverse_table()
    expected_size = 24 * 16
    coverage_ok = len(table) == expected_size

    # (2) Round-trip on real text.
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:4096]
    chain_stream = per_nibble_chain_stream(data)
    reconstructed = per_nibble_stream_to_bytes(chain_stream)
    round_trip_ok = reconstructed == data

    # (3) Stream length: 2 chains per byte.
    expected_stream_len = 2 * len(data)
    length_ok = len(chain_stream) == expected_stream_len

    # (4) Distinct chain symbols in stream (≤ 24).
    distinct = len(set(chain_stream))

    if verbose:
        print("=== PerNibbleChain self-check ===")
        print(f"  inverse table size:   {len(table)} / {expected_size}  "
              f"{'OK' if coverage_ok else 'FAIL'}")
        print(f"  stream length:        {len(chain_stream)} / "
              f"{expected_stream_len}  {'OK' if length_ok else 'FAIL'}")
        print(f"  distinct symbols:     {distinct}")
        print(f"  round-trip on {len(data)}-byte text: "
              f"{'OK' if round_trip_ok else 'FAIL'}")
        ok = coverage_ok and round_trip_ok and length_ok
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
        return ok
    return coverage_ok and round_trip_ok and length_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
