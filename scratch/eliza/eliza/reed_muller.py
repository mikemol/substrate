"""Eliza.ReedMuller — RM(r, m) code runtime for the EE-arc.

Reed-Muller code RM(r, m) over F₂:
  length    n = 2^m
  dimension k = Σ_{i=0}^{r} C(m, i)
  minimum-distance d = 2^(m-r)

Generator matrix rows: monomials in {x_1, ..., x_m} of total degree ≤ r,
each evaluated at all 2^m points of F₂^m.

GL(m, F₂)-invariant code family. Per [[expose-generator-not-orbit]]:
GL(m, F₂) is the gauge generator; RM(r, m) is the r-th orbit in its
invariant filtration RM(0,m) ⊂ RM(1,m) ⊂ ... ⊂ RM(m,m) = F₂^(2^m).

Per [[168-tower-as-fanout]] at m = 3: GL(3, F₂) = PSL(2, 7),
|G| = 168 = 2³·3·7 — the substrate's three-Sylow target.
Higher m: |GL(4, F₂)| = 20160 = 2⁶·3²·5·7 — F₇ recurs, order-5 emerges.

Per [[3plus1-parity-universal]]: RM(1, m) at any m has the special
weight distribution {0, 2^(m-1), 2^m} with 14 (or 2^(m+1)−2)
non-trivial weight-2^(m-1) codewords — a generalised 3+1.
"""

from __future__ import annotations

from itertools import combinations
from typing import Iterator, List, Tuple

import numpy as np


def _ev_point(m: int, p: int) -> Tuple[int, ...]:
    """Decode point index p ∈ [0, 2^m) as (x_1, ..., x_m) ∈ F₂^m.

    Convention: x_1 is the high bit of p (i = 0 in the bitmask),
    x_m is the low bit.
    """
    return tuple((p >> (m - 1 - i)) & 1 for i in range(m))


def _monomial_value(point: Tuple[int, ...], variables: Tuple[int, ...]) -> int:
    """Value of monomial ∏_{i ∈ variables} x_i at the given point.

    Empty product (constant 1) returns 1. Variables are 0-indexed.
    """
    v = 1
    for i in variables:
        v &= point[i]
    return v


def _all_monomial_subsets(m: int, max_degree: int) -> Iterator[Tuple[int, ...]]:
    """Iterate variable-index subsets of size ≤ max_degree."""
    for deg in range(max_degree + 1):
        for combo in combinations(range(m), deg):
            yield combo


def generator_matrix(m: int, r: int) -> np.ndarray:
    """Return RM(r, m)'s generator matrix as a (k, n) int8 array.

    Rows: monomials of degree ≤ r (in lex order on variable subsets).
    Columns: evaluation points 0..2^m − 1.
    """
    n = 1 << m
    rows: List[List[int]] = []
    for variables in _all_monomial_subsets(m, r):
        row = [_monomial_value(_ev_point(m, p), variables) for p in range(n)]
        rows.append(row)
    return np.array(rows, dtype=np.int8)


def dimension(m: int, r: int) -> int:
    """k(r, m) = Σ_{i=0}^{r} C(m, i)."""
    if r < 0:
        return 0
    if r >= m:
        return 1 << m
    out = 0
    coef = 1
    for i in range(r + 1):
        out += coef
        coef = coef * (m - i) // (i + 1)
    return out


def min_distance(m: int, r: int) -> int:
    """d(r, m) = 2^(m − r) when 0 ≤ r ≤ m."""
    if r < 0:
        return 1 << m
    if r >= m:
        return 1
    return 1 << (m - r)


def all_codewords(m: int, r: int) -> List[int]:
    """All 2^k codewords of RM(r, m), each as an integer (bit i = bit at
    position i in big-endian convention).

    For m = 5, k can be up to 26 — 67M codewords; use with care.
    For m ≤ 4 this is always tractable.
    """
    G = generator_matrix(m, r)
    k = G.shape[0]
    n = 1 << m
    out: List[int] = []
    for msg in range(1 << k):
        # message bits as int8 row vector
        bits = np.array([(msg >> (k - 1 - i)) & 1 for i in range(k)],
                          dtype=np.int8)
        codeword_row = (bits @ G) & 1
        c = 0
        for j in range(n):
            c |= int(codeword_row[j]) << (n - 1 - j)
        out.append(c)
    return out


def is_codeword(c: int, m: int, r: int) -> bool:
    """Membership decider via syndrome check against the dual RM(m−r−1, m).

    A vector c ∈ F₂^(2^m) is in RM(r, m) iff it is orthogonal to every
    codeword of RM(m − r − 1, m) (Reed-Muller duality).

    For small (m, r) we can equivalently check c ∈ all_codewords(m, r).
    Implemented as the latter at m ≤ 4; syndrome view useful in proofs.
    """
    if r >= m:
        return True
    codewords = set(all_codewords(m, r))
    return c in codewords


# --- GL(m, F₂) action --------------------------------------------------


def apply_gl_action(c: int, m: int, perm: List[int]) -> int:
    """Permute bit positions of `c` by `perm`: new position perm[i] gets
    the bit at old position i. `perm` is a permutation of {0,...,2^m−1}.

    Useful for verifying GL(m, F₂)-invariance of RM(r, m): the image
    of a codeword under any permutation arising from a linear bijection
    of F₂^m remains a codeword.
    """
    n = 1 << m
    out = 0
    for i in range(n):
        bit = (c >> (n - 1 - i)) & 1
        if bit:
            out |= 1 << (n - 1 - perm[i])
    return out


def linear_permutation(m: int, A: np.ndarray) -> List[int]:
    """Build the bit-position permutation induced by a linear map A ∈
    GL(m, F₂). A is an (m, m) F₂ matrix; the induced permutation sends
    point p ∈ F₂^m to (A · p) mod 2.

    Returned as a length 2^m index list: perm[i] = (A · point(i)) as int.
    """
    n = 1 << m
    perm: List[int] = []
    for p in range(n):
        point = np.array(_ev_point(m, p), dtype=np.int8)
        ap = (A @ point) % 2
        new_p = 0
        for i in range(m):
            new_p |= int(ap[i]) << (m - 1 - i)
        perm.append(new_p)
    return perm


# --- Convenient codeword views ----------------------------------------


def codewords_by_weight(m: int, r: int) -> dict:
    """Return {weight: list of codewords with that Hamming weight}."""
    out: dict = {}
    for c in all_codewords(m, r):
        w = bin(c).count("1")
        out.setdefault(w, []).append(c)
    return out


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. RM(1, 3) = [8, 4, 4]: 16 codewords, weights {0, 4, 8}.
    cws = all_codewords(3, 1)
    if len(cws) != 16:
        if verbose:
            print(f"FAIL: RM(1,3) cardinality {len(cws)} ≠ 16")
        ok = False
    weights = sorted({bin(c).count("1") for c in cws})
    if weights != [0, 4, 8]:
        if verbose:
            print(f"FAIL: RM(1,3) weight set {weights} ≠ [0, 4, 8]")
        ok = False

    # 2. RM(2, 3) = [8, 7, 2]: 128 codewords = all even-weight bytes.
    cws = all_codewords(3, 2)
    if len(cws) != 128:
        if verbose:
            print(f"FAIL: RM(2,3) cardinality {len(cws)} ≠ 128")
        ok = False
    if not all(bin(c).count("1") % 2 == 0 for c in cws):
        if verbose:
            print(f"FAIL: RM(2,3) contains odd-weight codeword")
        ok = False

    # 3. RM(3, 3) = [8, 8, 1]: 256 codewords = full space.
    if len(all_codewords(3, 3)) != 256:
        if verbose:
            print(f"FAIL: RM(3,3) cardinality ≠ 256")
        ok = False

    # 4. Dimensions match formula.
    for m in range(2, 5):
        for r in range(m + 1):
            cws = all_codewords(m, r)
            if len(cws) != (1 << dimension(m, r)):
                if verbose:
                    print(f"FAIL: |RM({r},{m})| = {len(cws)} ≠ "
                          f"2^{dimension(m, r)}")
                ok = False

    # 5. RM(1, 4) = [16, 5, 8]: 32 codewords, nonzero weights {8, 16}.
    cws = all_codewords(4, 1)
    if len(cws) != 32:
        if verbose:
            print(f"FAIL: RM(1,4) cardinality {len(cws)} ≠ 32")
        ok = False
    nonzero_weights = sorted({bin(c).count("1") for c in cws if c != 0})
    if nonzero_weights != [8, 16]:
        if verbose:
            print(f"FAIL: RM(1,4) nonzero weights {nonzero_weights}")
        ok = False

    # 6. GL(m, F₂) invariance check: apply identity perm, codeword
    #    stays. Apply a swap of x_0 and x_1, all codewords remain in
    #    RM(r, m) (sanity).
    m, r = 3, 1
    cws_set = set(all_codewords(m, r))
    identity_perm = list(range(1 << m))
    for c in list(cws_set)[:4]:
        if apply_gl_action(c, m, identity_perm) != c:
            if verbose:
                print(f"FAIL: identity perm changed codeword")
            ok = False
    # Apply swap-x_0-x_1: matrix [[0,1,0],[1,0,0],[0,0,1]].
    A = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]], dtype=np.int8)
    swap_perm = linear_permutation(3, A)
    for c in list(cws_set)[:8]:
        if apply_gl_action(c, m, swap_perm) not in cws_set:
            if verbose:
                print(f"FAIL: GL swap moved codeword out of RM(1, 3)")
            ok = False

    # 7. is_codeword consistency.
    if not is_codeword(0xFF, 3, 1):   # all-ones IS RM(1, 3) codeword
        if verbose:
            print(f"FAIL: 0xFF not recognised as RM(1, 3) codeword")
        ok = False
    if is_codeword(0x2d, 3, 1):       # the substrate_agda pick is NOT RM(1, 3)
        if verbose:
            print(f"FAIL: 0x2d incorrectly recognised as RM(1, 3)")
        ok = False
    if not is_codeword(0x2d, 3, 2):   # but IS RM(2, 3)
        if verbose:
            print(f"FAIL: 0x2d not recognised as RM(2, 3) codeword")
        ok = False

    if verbose:
        print(f"reed_muller self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
