"""HH4: Sweep (p, q) ∈ small primes² × axis assignments; measure
mutual information between the prime-sampled chain context and the
substrate's actual S₄ chain symbol at each step.

The TARGET is the chain symbol at byte position k. The CONTEXT is
the prime-sampled triple-crumb stream evaluated at the byte-aligned
bit position (16*k = 8 bits/byte × 2 nibbles, hmm; actually k_byte
=> bit k_byte*8). We measure I(chain_sym; context).

The empirical question: which (p, q, axis_assignment) tuples have
the highest mutual information per corpus? Higher MI = stronger
predictive capacity = a useful predictor context.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
from eliza.matrix_ops import _manifold_index
from eliza.prime_chain import combine_crumbs, mutual_information
from eliza.walsh_hadamard import bits_msb_first
from tests.test_substrate_atlas import CORPORA


def chain_symbols(data: bytes) -> np.ndarray:
    """Compute the substrate's actual chain-walk symbol stream:
    chamber index after each nibble (so length 2 * len(data)).
    """
    chambers, idx_map = _manifold_index()
    state = ORIGIN
    out: list = []
    for byte in data:
        for nib in ((byte >> 4) & 0xF, byte & 0xF):
            state = perm_compose(state, NIBBLE_TO_PERM[nib])
            out.append(idx_map[state])
    return np.array(out, dtype=np.int64)


def context_stream_for_chain(
    data: bytes, p: int, q: int, assignment: str,
) -> np.ndarray:
    """Compute context aligned with the chain symbol stream:
    one context value per nibble (= per 4 bits).

    For nibble at bit position 4*k (k = 0, 1, 2, ...), the context
    samples crumbs at bit positions (4*k, 4*k + p, 4*k + q).
    """
    bits = bits_msb_first(data)
    n = len(bits)
    n_nibbles = n // 4
    out = np.zeros(n_nibbles, dtype=np.int64)
    for k in range(n_nibbles):
        pos = 4 * k
        # Sample three crumbs at (pos, pos + p, pos + q).
        def crumb(start: int) -> int:
            if start < 0 or start + 1 >= n:
                return 0
            return (int(bits[start]) << 1) | int(bits[start + 1])
        c0 = crumb(pos)
        c1 = crumb(pos + p)
        c2 = crumb(pos + q)
        out[k] = combine_crumbs(c0, c1, c2, assignment)
    return out


def main() -> int:
    primes = [3, 5, 7, 11, 13]
    assignments = ["v4-abelian", "v4-s3-chirality",
                   "s4-quotient", "s3-abelian"]

    print("HH4: Mutual information sweep (chain symbol ← prime-sampled context)")
    print()
    sizes = (2048,)
    for size in sizes:
        for name, builder in CORPORA.items():
            data = builder(size)
            chain = chain_symbols(data)
            h_chain = mutual_information(chain, chain, 24)[0]
            print(f"--- {name} ({size}B) H(chain) = {h_chain:.3f} bits ---")
            # Compute MI for each (p, q, assignment) combo.
            best = {a: (None, None, 0.0) for a in assignments}
            for p in primes:
                for q in primes:
                    if p >= q:
                        continue
                    for a in assignments:
                        ctx = context_stream_for_chain(data, p, q, a)
                        # Trim to same length.
                        N = min(len(chain), len(ctx))
                        if N < 64:
                            continue
                        mi_h, mi_h_c, mi = mutual_information(
                            chain[:N], ctx[:N], 24)
                        if mi > best[a][2]:
                            best[a] = (p, q, mi)
            for a, (p_best, q_best, mi) in best.items():
                if p_best is not None:
                    print(f"  {a:<22} best (p={p_best},q={q_best}): "
                          f"MI = {mi:.3f} bits "
                          f"({mi/h_chain*100:.1f}% of H(chain))")
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
