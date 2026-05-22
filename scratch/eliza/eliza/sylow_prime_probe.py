"""Eliza.SylowPrimeProbe — JJ-arc minimal-probe per-Sylow-prime atlas.

Per the user's original framing 2026-05-21 + JJ question 2026-05-21:
'sniffing at prime numbers of bits ... 2 bits (crumb), 3 bits, 5
bits, 7 bits ... how many different sylow primes can we compose?'

The minimal Sylow-class atlas: ONE probe per Sylow prime, sampling
the V₄-coset crumb of the chain symbol at offset = Sylow prime
nibbles back. Joint k-Sylow atlas = 4ᵏ context values, tractable
at all dataset sizes.

Sylow-class roster (substrate's full discrete-prime ladder):
  Sylow-2  → probe at offset  2 nibbles back
  Sylow-3  → probe at offset  3 nibbles back
  Sylow-5  → probe at offset  5 nibbles back (GL(4, F₂) introduces 5)
  Sylow-7  → probe at offset  7 nibbles back (GL(3, F₂) introduces 7)
  Sylow-11 → probe at offset 11 nibbles back (GL(10, F₂))
  Sylow-13 → probe at offset 13 nibbles back (GL(12, F₂))
  Sylow-17 → probe at offset 17 nibbles back (GL(8, F₂))
  Sylow-31 → probe at offset 31 nibbles back (Mersenne, GL(5, F₂))

Per [[168-tower-as-fanout]]: the substrate's primary group GL(3, F₂)
has Sylow primes {2, 3, 7}; adding Sylow-5 lifts to GL(4, F₂).
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np


def _v4_part_table():
    from eliza.coarse_residue import coset_members, n_cosets
    out = [0] * 24
    for ci in range(n_cosets()):
        members = sorted(coset_members(ci))
        for pos, m in enumerate(members):
            out[m] = pos
    return out


_V4_PART = _v4_part_table()


# Substrate-aligned Sylow primes per GL(n, F₂) nested tower.
SYLOW_PRIMES_GL3 = (2, 3, 7)          # 168 = 2³·3·7
SYLOW_PRIMES_GL4 = (2, 3, 5, 7)       # 20160 = 2⁶·3²·5·7
SYLOW_PRIMES_GL5 = (2, 3, 5, 7, 31)   # Mersenne
SYLOW_PRIMES_GL8 = (2, 3, 5, 7, 17, 31, 127)


def sylow_probe_value(chain: np.ndarray, k: int, prime: int) -> int:
    """V₄-part crumb of chain[k - prime]; 0 if out-of-range."""
    pos = k - prime
    if pos < 0 or pos >= len(chain):
        return 0
    c = int(chain[pos])
    return _V4_PART[c] if 0 <= c < 24 else 0


def joint_sylow_context(
    chain: np.ndarray, primes: Iterable[int],
) -> np.ndarray:
    """Joint context value at each chain position k.

    For each prime p in primes, sample crumb at k-p. Pack as 2-bit
    fields into a single int. Width = 2 * len(primes).
    """
    plist = list(primes)
    out = np.zeros(len(chain), dtype=np.int64)
    for k in range(len(chain)):
        ctx = 0
        for i, p in enumerate(plist):
            crumb = sylow_probe_value(chain, k, p)
            ctx |= (crumb & 3) << (2 * i)
        out[k] = ctx
    return out


def all_subsets(items: List) -> List[Tuple]:
    """All non-empty subsets ordered by size."""
    n = len(items)
    out = []
    for mask in range(1, 1 << n):
        subset = tuple(items[i] for i in range(n) if (mask >> i) & 1)
        out.append(subset)
    out.sort(key=lambda s: (len(s), s))
    return out


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Probe value in [0, 4).
    chain = np.arange(24, dtype=np.int64)
    v = sylow_probe_value(chain, 10, 3)
    if not (0 <= v < 4):
        if verbose:
            print(f"FAIL: probe value {v} out of range")
        ok = False

    # 2. Joint context: width matches primes count.
    chain = np.array([5, 12, 7, 19, 0, 14, 3, 22] * 8, dtype=np.int64)
    ctx = joint_sylow_context(chain, [2, 3, 5])
    max_ctx = (1 << 6) - 1   # 3 primes × 2 bits = 6 bits
    if not all(0 <= c <= max_ctx for c in ctx):
        if verbose:
            print(f"FAIL: joint ctx out of range")
        ok = False

    # 3. Subset enumeration.
    subs = all_subsets([2, 3, 5, 7])
    if len(subs) != 15:   # 2^4 - 1 non-empty subsets
        if verbose:
            print(f"FAIL: subsets {len(subs)} ≠ 15")
        ok = False

    if verbose:
        print(f"sylow_prime_probe self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
