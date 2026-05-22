"""HH4 (revised): MI sweep using PAST chain-symbol context.

The encoder-decoder symmetric context: at chain position k, sample
three V₄-coset-position crumbs from past chain symbols at offsets
(k-1, k-p, k-q) for primes p, q ∈ small primes. This context is
available to both encoder and decoder via the chain_terminals list.

Each chain symbol c ∈ [0, 24) decomposes via V₄ left coset:
  v4_part(c) = within_coset_position(c) ∈ {0, 1, 2, 3}

Three such crumbs give 4³ = 64 context values.

Per the user 2026-05-21: 'connect the three axes to three crumb
samples spaced apart ... tested at different prime intervals'.
This is the SYMMETRIC realisation of that idea.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.alphabets import V4_PERMS, NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.matrix_ops import _manifold_index
from eliza.prime_chain import mutual_information
from tests.test_substrate_atlas import CORPORA


def chain_symbols(data: bytes) -> np.ndarray:
    chambers, idx_map = _manifold_index()
    state = ORIGIN
    out: list = []
    for byte in data:
        for nib in ((byte >> 4) & 0xF, byte & 0xF):
            state = perm_compose(state, NIBBLE_TO_PERM[nib])
            out.append(idx_map[state])
    return np.array(out, dtype=np.int64)


def v4_part_table() -> np.ndarray:
    """v4_part[chamber_idx] ∈ {0..3} — within-coset position."""
    from eliza.coarse_residue import coset_members, n_cosets
    out = np.zeros(24, dtype=np.int64)
    for ci in range(n_cosets()):
        members = sorted(coset_members(ci))
        for pos, m in enumerate(members):
            out[m] = pos
    return out


_V4_PART = v4_part_table()


def past_chain_context(
    chain: np.ndarray, k: int, p: int, q: int,
) -> int:
    """Three-crumb context at chain position k using past V₄-parts
    of chain symbols at offsets (k-1, k-p, k-q).

    Out-of-range (k - offset < 0) returns 0 for that crumb.
    """

    def crumb(offset: int) -> int:
        pos = k - offset
        if pos < 0 or pos >= len(chain):
            return 0
        return int(_V4_PART[chain[pos]])

    c0 = crumb(1)
    c1 = crumb(p)
    c2 = crumb(q)
    return c0 | (c1 << 2) | (c2 << 4)


def past_chain_context_stream(
    chain: np.ndarray, p: int, q: int,
) -> np.ndarray:
    return np.array([past_chain_context(chain, k, p, q)
                       for k in range(len(chain))], dtype=np.int64)


def main() -> int:
    primes = [2, 3, 5, 7, 11, 13]

    print("HH4 (revised): MI sweep with PAST chain-symbol context")
    print()
    for name, builder in CORPORA.items():
        data = builder(2048)
        chain = chain_symbols(data)
        h_chain = mutual_information(chain, chain, 24)[0]
        print(f"--- {name} (2048B)  H(chain) = {h_chain:.3f} bits ---")
        best_p, best_q, best_mi = 2, 3, 0.0
        for p in primes:
            for q in primes:
                if p >= q:
                    continue
                ctx = past_chain_context_stream(chain, p, q)
                _, _, mi = mutual_information(chain, ctx, 24)
                if mi > best_mi:
                    best_mi = mi
                    best_p = p
                    best_q = q
        print(f"  best (p={best_p}, q={best_q}): MI = {best_mi:.3f} bits "
              f"({best_mi/h_chain*100:.1f}% of H(chain))")
        # Show top 5.
        all_mis = []
        for p in primes:
            for q in primes:
                if p >= q:
                    continue
                ctx = past_chain_context_stream(chain, p, q)
                _, _, mi = mutual_information(chain, ctx, 24)
                all_mis.append((p, q, mi))
        all_mis.sort(key=lambda t: -t[2])
        for p, q, mi in all_mis[:5]:
            print(f"    p={p}, q={q}: MI = {mi:.3f} bits "
                  f"({mi/h_chain*100:.1f}%)")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
