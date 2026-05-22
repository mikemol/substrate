"""Eliza.PrimeContextPredictor — HH5 prime-sampled context predictor
using PAST chain-symbol V₄-coset positions (decoder-symmetric).

Maintains a separate count table per prime-sampled context value.
Given the empirical (p, q) pair chosen at encoder init, the
predictor's cumfreqs/update are routed by the current context value
computed from the chain_terminals history.

Per HH4 (revised) empirical with past-chain-symbol context:
  Best (p, q) = (2, 3) consistently across tested corpora.
  Predictive capacity (MI / H(chain)):
    substrate_agda:    13.6%
    substrate_memory:  13.5%
    substrate_opcodes: 70.5%
    t1t2_handcrafted:  82.2%

Per [[expose-generator-not-orbit]]: the (p, q) prime pair is the
gauge generator; chain-context predictor is one orbit of the family.
"""

from __future__ import annotations

from math import log2
from typing import Optional, Tuple

import numpy as np

from eliza.prime_chain import combine_crumbs
from eliza.v7_predictor import Predictor, _smoothed_cumfreqs


_PRIME_CTX_ALPHABET = {
    "v4-abelian":       64,
    "v4-s3-chirality":  64,
    "s4-quotient":      24,
    "s3-abelian":        6,
    "past-chain-v4":    64,   # 3 V₄-crumbs from past chain symbols
}


def _v4_part_table():
    from eliza.coarse_residue import coset_members, n_cosets
    out = [0] * 24
    for ci in range(n_cosets()):
        members = sorted(coset_members(ci))
        for pos, m in enumerate(members):
            out[m] = pos
    return out


_V4_PART_TABLE = _v4_part_table()


def past_chain_v4_context(
    chain_symbols: list, k: int, p: int, q: int,
) -> int:
    """Three-crumb context at chain position k using past V₄-parts
    of chain symbols at offsets (k-1, k-p, k-q). Both encoder and
    decoder can compute this since chain_symbols history is
    available at emission time.

    Out-of-range (k - offset < 0) returns 0 for that crumb.
    """

    def crumb(offset: int) -> int:
        pos = k - offset
        if pos < 0 or pos >= len(chain_symbols):
            return 0
        c = chain_symbols[pos]
        if c < 0 or c >= 24:
            return 0
        return _V4_PART_TABLE[c]

    c0 = crumb(1)
    c1 = crumb(p)
    c2 = crumb(q)
    return c0 | (c1 << 2) | (c2 << 4)


def prime_context_for_nibble(bits: np.ndarray, nibble_idx: int,
                                p: int, q: int, assignment: str) -> int:
    """Compute the prime-sampled context value for the nibble at index
    `nibble_idx` (= bit position 4 * nibble_idx).

    Context samples three crumbs at offsets (0, p, q) from the nibble's
    bit position, then combines via the assignment.
    """
    n = len(bits)
    base = 4 * nibble_idx

    def crumb(start: int) -> int:
        if start < 0 or start + 1 >= n:
            return 0
        return (int(bits[start]) << 1) | int(bits[start + 1])

    c0 = crumb(base)
    c1 = crumb(base + p)
    c2 = crumb(base + q)
    return combine_crumbs(c0, c1, c2, assignment)


class PrimeContextPredictor(Predictor):
    """Predictor whose count table is selected by the prime-sampled
    context computed externally each step.

    Use:
      pred = PrimeContextPredictor(max_alphabet, p, q, assignment)
      pred.set_context(ctx_value)
      pred.cumfreqs(a_size, None)
      pred.update(emit_idx, None)

    `set_context` is called per emission with the value of the
    prime-sampled context at that step.
    """

    name = "prime_context"

    def __init__(self, max_alphabet: int, p: int = 5, q: int = 7,
                   assignment: str = "v4-abelian"):
        self.p = p
        self.q = q
        self.assignment = assignment
        self.n_ctx = _PRIME_CTX_ALPHABET[assignment]
        self.counts = np.zeros((self.n_ctx, max_alphabet),
                                 dtype=np.int64)
        self.ctx = 0

    def set_context(self, ctx_value: int) -> None:
        self.ctx = ctx_value % self.n_ctx

    def cumfreqs(self, alphabet_size, context=None):
        return _smoothed_cumfreqs(self.counts[self.ctx], alphabet_size)

    def update(self, emit_idx, context=None):
        self.counts[self.ctx, emit_idx] += 1

    def grow_to(self, new_alphabet_size):
        if new_alphabet_size > self.counts.shape[1]:
            new_counts = np.zeros((self.n_ctx, new_alphabet_size),
                                    dtype=np.int64)
            new_counts[:, :self.counts.shape[1]] = self.counts
            self.counts = new_counts


def best_prime_context_for(data: bytes) -> Tuple[int, int, str]:
    """Sweep small primes and assignments; return the (p, q,
    assignment) giving highest MI on this data.

    Uses chain_symbols + context_stream from the test_hh_arc_prime_sweep
    machinery. Truncated to small primes [3, 5, 7, 11, 13] and the
    top-2 assignments ("v4-abelian", "s4-quotient") for speed.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from tests.test_hh_arc_prime_sweep import (
        chain_symbols, context_stream_for_chain,
    )
    from eliza.prime_chain import mutual_information

    chain = chain_symbols(data)
    primes = (3, 5, 7, 11, 13)
    assignments = ("v4-abelian", "s4-quotient")
    best_p = 5
    best_q = 7
    best_a = "v4-abelian"
    best_mi = -1.0
    for p in primes:
        for q in primes:
            if p >= q:
                continue
            for a in assignments:
                ctx = context_stream_for_chain(data, p, q, a)
                N = min(len(chain), len(ctx))
                if N < 64:
                    continue
                _, _, mi = mutual_information(chain[:N], ctx[:N], 24)
                if mi > best_mi:
                    best_mi = mi
                    best_p = p
                    best_q = q
                    best_a = a
    return (best_p, best_q, best_a)


# --- Self-check ------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True
    from eliza.walsh_hadamard import bits_msb_first

    bits = bits_msb_first(bytes(range(64)))
    ctx = prime_context_for_nibble(bits, nibble_idx=0, p=5, q=7,
                                       assignment="v4-abelian")
    if not (0 <= ctx < 64):
        if verbose:
            print(f"FAIL: ctx {ctx} out of range")
        ok = False

    p = PrimeContextPredictor(32, p=5, q=7, assignment="v4-abelian")
    p.set_context(7)
    p.update(3, None)
    if p.counts[7, 3] != 1:
        if verbose:
            print(f"FAIL: update didn't reach context 7")
        ok = False
    cf = p.cumfreqs(32, None)
    if cf.shape[0] != 33 or cf[-1] <= 0:
        if verbose:
            print(f"FAIL: cumfreqs malformed")
        ok = False
    p.grow_to(64)
    if p.counts.shape[1] != 64:
        if verbose:
            print(f"FAIL: grow_to didn't resize")
        ok = False

    if verbose:
        print(f"prime_context_predictor self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
