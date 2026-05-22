"""HH-arc extension: prime sweep up to 64-bit / 128-bit / 256-bit
look-back limits per user 2026-05-21.

Three sweeps:
  Past-chain-V₄ (streaming-decoder compatible):
    p, q are PRIME NIBBLE OFFSETS (each nibble = 4 bits).
    64-bit look-back → p, q ≤ 16 (nibbles)
  Bit-stream eager-decode (windowed-decoder compatible):
    p, q are PRIME BIT OFFSETS.
    64-bit look-ahead → p, q ≤ 64
    128-bit → ≤ 128
    256-bit → ≤ 256

Compute-alignment hint: primes near 64, 128, 256 are flagged.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.prime_chain import combine_crumbs, mutual_information
from eliza.walsh_hadamard import bits_msb_first
from tests.test_hh_arc_past_chain_mi import (
    chain_symbols, past_chain_context_stream,
)
from tests.test_substrate_atlas import CORPORA


def primes_below(n: int) -> list:
    """Sieve of Eratosthenes returning primes p with 2 ≤ p < n."""
    if n < 3:
        return []
    sieve = [True] * n
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n, i):
                sieve[j] = False
    return [i for i in range(2, n) if sieve[i]]


def bit_context_stream(bits: np.ndarray, p: int, q: int,
                          assignment: str = "v4-abelian",
                          stride_nibbles: int = 1) -> np.ndarray:
    """Bit-stream context aligned with chain symbols (eager decode).

    At chain symbol position k (= nibble position k), context samples
    three crumbs at bit positions (4k, 4k+p, 4k+q).
    """
    n = len(bits)
    n_nibbles = n // 4
    out = np.zeros(n_nibbles, dtype=np.int64)
    for k in range(n_nibbles):
        base = 4 * k

        def crumb(start):
            if start < 0 or start + 1 >= n:
                return 0
            return (int(bits[start]) << 1) | int(bits[start + 1])

        c0 = crumb(base)
        c1 = crumb(base + p)
        c2 = crumb(base + q)
        out[k] = combine_crumbs(c0, c1, c2, assignment)
    return out


def sweep_past_chain(chain: np.ndarray, primes: list) -> list:
    """Sweep (p, q) ∈ primes² for past-chain-v4 context."""
    h_chain = mutual_information(chain, chain, 24)[0]
    results = []
    for p in primes:
        for q in primes:
            if p >= q:
                continue
            ctx = past_chain_context_stream(chain, p, q)
            _, _, mi = mutual_information(chain, ctx, 24)
            results.append((p, q, mi, mi / h_chain if h_chain > 0 else 0.0))
    return sorted(results, key=lambda t: -t[2])


def sweep_bit_stream(data: bytes, primes: list,
                       max_pq_bits: int) -> list:
    """Sweep (p, q) ∈ primes² for bit-stream eager-decode context."""
    bits = bits_msb_first(data)
    chain = chain_symbols(data)
    h_chain = mutual_information(chain, chain, 24)[0]
    filtered = [p for p in primes if p <= max_pq_bits]
    results = []
    for p in filtered:
        for q in filtered:
            if p >= q:
                continue
            ctx = bit_context_stream(bits, p, q)
            N = min(len(chain), len(ctx))
            if N < 64:
                continue
            _, _, mi = mutual_information(chain[:N], ctx[:N], 24)
            results.append((p, q, mi, mi / h_chain if h_chain > 0 else 0.0))
    return sorted(results, key=lambda t: -t[2])


def compute_aligned(p: int, alignment: int) -> str:
    """Mark whether p falls just below a compute boundary."""
    if p > alignment * 0.85 and p < alignment:
        return "*"
    return " "


def main() -> int:
    primes_64 = [p for p in primes_below(64) if p <= 16]
    primes_64_bit = primes_below(64)
    primes_128_bit = primes_below(128)
    primes_256_bit = primes_below(256)

    print(f"Prime sets:")
    print(f"  past-chain (nibbles, ≤16): {primes_64}")
    print(f"  bit-stream ≤64:   {len(primes_64_bit)} primes")
    print(f"  bit-stream ≤128:  {len(primes_128_bit)} primes")
    print(f"  bit-stream ≤256:  {len(primes_256_bit)} primes")
    print()

    for name, builder in CORPORA.items():
        data = builder(2048)
        chain = chain_symbols(data)
        print(f"--- {name} (2048B)  H(chain) = "
              f"{mutual_information(chain, chain, 24)[0]:.3f} ---")

        # Past-chain at 64-bit look-back (16 nibbles).
        results_past = sweep_past_chain(chain, primes_64)
        print("  past-chain V₄ context (≤16 nibbles = 64 bits):")
        for p, q, mi, ratio in results_past[:3]:
            print(f"    (p={p:>3}, q={q:>3}): MI={mi:.3f}  "
                  f"({ratio*100:.1f}% of H(chain))")

        # Bit-stream at each compute-alignment tier.
        for tier_name, tier_primes, tier_max in [
            ("64-bit",  primes_64_bit,  64),
            ("128-bit", primes_128_bit, 128),
            ("256-bit", primes_256_bit, 256),
        ]:
            results_bit = sweep_bit_stream(data, tier_primes, tier_max)
            if not results_bit:
                continue
            print(f"  bit-stream eager ({tier_name}, "
                  f"|primes|={len(tier_primes)}):")
            for p, q, mi, ratio in results_bit[:3]:
                mark_p = compute_aligned(p, tier_max)
                mark_q = compute_aligned(q, tier_max)
                print(f"    (p={p:>3}{mark_p}, q={q:>3}{mark_q}): "
                      f"MI={mi:.3f}  ({ratio*100:.1f}%)")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
