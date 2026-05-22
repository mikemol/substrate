"""Eliza.PrimeChain — HH-arc three-crumb prime-sampled chain primitive.

For a bit stream, at each step position k, sample THREE 2-bit crumbs
at offsets (0, p_bits, q_bits) where p, q are primes (in bits).
The three crumbs jointly index a chain-walk element via an axis
assignment.

Per the user 2026-05-21: 'connect the three axes to three crumb
samples spaced apart ... those crumb samples' period tested at
different prime intervals'. The intent is RICHER CHAIN PHYSICS,
not spectral analysis of the input.

Per [[3plus1-parity-universal]]: three axes + one chirality is the
substrate's universal pattern. The three crumbs provide three
independent samples; how they combine into a chain element depends
on the axis assignment surveyed in HH2.

Per [[chain-walk-blocks-rotation-factor]]: the current S₄ chain
walk consumes consecutive nibbles. Sampling at PRIME offsets is
structurally different — it probes long-range correlations the
nibble walk cannot factor.

Per [[expose-generator-not-orbit]]: the (p, q) prime pair is the
gauge generator; the resulting chain stream is one orbit point.
"""

from __future__ import annotations

from typing import Callable, Tuple

import numpy as np


def sample_three_crumbs(bits: np.ndarray, k: int, p: int, q: int
                          ) -> Tuple[int, int, int]:
    """Sample three 2-bit crumbs at bit positions (k, k+p, k+q).

    Returns (c0, c1, c2) ∈ {0, 1, 2, 3}³.

    Out-of-range crumbs return 0 (zero-pad).
    """
    n = len(bits)

    def crumb(start: int) -> int:
        if start < 0 or start + 1 >= n:
            return 0
        return (int(bits[start]) << 1) | int(bits[start + 1])

    return crumb(k), crumb(k + p), crumb(k + q)


def prime_chain_stream(bits: np.ndarray, p: int, q: int,
                          stride: int = 2,
                          assignment: str = "v4-abelian",
                          ) -> np.ndarray:
    """Compute the prime-sampled chain stream over `bits`.

    For each step k ∈ {0, stride, 2*stride, ...}, sample three
    crumbs at (k, k+p, k+q) and combine via the named axis
    assignment.

    Returns int64 array of chain-element indices.
    """
    if len(bits) < max(p, q) + 2:
        return np.zeros(0, dtype=np.int64)

    n_steps = (len(bits) - max(p, q) - 1) // stride + 1
    if n_steps <= 0:
        return np.zeros(0, dtype=np.int64)
    out = np.zeros(n_steps, dtype=np.int64)
    for i in range(n_steps):
        k = i * stride
        c0, c1, c2 = sample_three_crumbs(bits, k, p, q)
        out[i] = combine_crumbs(c0, c1, c2, assignment)
    return out


# --- HH2: Axis assignment survey -------------------------------------


def combine_crumbs(c0: int, c1: int, c2: int, assignment: str) -> int:
    """Map (c0, c1, c2) ∈ {0..3}³ to a chain-element index.

    Assignments:
      "v4-abelian":      V₄³ = (Z/2)⁶, 64 elements (c0 | c1<<2 | c2<<4)
      "v4-s3-chirality": V₄ × S₃-invol × F₂² = 64 elements (with
                         structure-aware composition)
      "s4-quotient":     project 64 down to S₄ = 24 via composition
                         in S₄ = V₄ ⋊ S₃
      "s3-abelian":      project to S₃-invol × S₃-invol × S₃-invol;
                         only 4³ = 64 raw, but image lives in S₃
                         after composition (≤ 6 distinct values)
    """
    if assignment == "v4-abelian":
        return c0 | (c1 << 2) | (c2 << 4)
    if assignment == "v4-s3-chirality":
        # c0 = V₄ index, c1 = S₃-invol index, c2 = chirality (4 modes)
        return (c0 & 3) | ((c1 & 3) << 2) | ((c2 & 3) << 4)
    if assignment == "s4-quotient":
        # Compose in S₄ via the substrate's natural V₄ ⋊ S₃ structure.
        # c0 V₄ part * c1 S₃-invol part = an S₄ element;
        # c2 chirality is added modulo S₄'s outer (sign) automorphism.
        from eliza.alphabets import (NIBBLE_TO_PERM, S3_INVOLUTIONS,
                                       V4_PERMS, perm_compose)
        from eliza.matrix_ops import _manifold_index
        _, idx_map = _manifold_index()
        elt = perm_compose(V4_PERMS[c0 & 3], S3_INVOLUTIONS[c1 & 3])
        # c2 chirality: act by NIBBLE_TO_PERM[c2*4] modulo S₄ structure
        # to provide a 4-way "rotation" of the result.
        if c2:
            elt = perm_compose(elt, NIBBLE_TO_PERM[(c2 & 3) * 4])
        return int(idx_map[elt])
    if assignment == "s3-abelian":
        # Three S₃-involution slots; composition projects to S₃.
        from eliza.alphabets import S3_INVOLUTIONS, perm_compose
        x = perm_compose(S3_INVOLUTIONS[c0 & 3], S3_INVOLUTIONS[c1 & 3])
        x = perm_compose(x, S3_INVOLUTIONS[c2 & 3])
        # x is in S₃ (acts on {1,2,3,4} but fixes 4 always); read as
        # a 0..5 index by permuting {1,2,3} only.
        sig = (x[0], x[1], x[2])
        s3_table = [(1, 2, 3), (2, 1, 3), (1, 3, 2),
                    (3, 1, 2), (2, 3, 1), (3, 2, 1)]
        return s3_table.index(sig) if sig in s3_table else 0
    raise ValueError(f"unknown assignment {assignment!r}")


# --- HH3: Predictive capacity (mutual information) ------------------


def conditional_entropy(
    target: np.ndarray, context: np.ndarray, n_target_vals: int,
) -> float:
    """H(target | context) in bits, computed empirically from the
    joint distribution.

    Both `target` and `context` are int arrays of the same length.
    `n_target_vals` bounds the target alphabet size; context can be
    arbitrary nonneg int.
    """
    if len(target) == 0 or len(context) == 0:
        return 0.0
    n = min(len(target), len(context))
    target = target[:n]
    context = context[:n]
    # Joint distribution: dict {(ctx, tgt): count}.
    joint: dict = {}
    ctx_total: dict = {}
    for c, t in zip(context, target):
        ctx_total[c] = ctx_total.get(c, 0) + 1
        joint[(c, t)] = joint.get((c, t), 0) + 1
    h_cond = 0.0
    for c, tot_c in ctx_total.items():
        p_c = tot_c / n
        h_c = 0.0
        for (cc, t), j in joint.items():
            if cc != c:
                continue
            p_tc = j / tot_c
            if p_tc > 0:
                h_c -= p_tc * np.log2(p_tc)
        h_cond += p_c * h_c
    return float(h_cond)


def mutual_information(
    target: np.ndarray, context: np.ndarray, n_target_vals: int,
) -> Tuple[float, float, float]:
    """Returns (H(target), H(target | context), MI(context; target))
    in bits.

    MI = H(target) - H(target | context). Higher MI = better
    predictive capacity.
    """
    if len(target) == 0:
        return (0.0, 0.0, 0.0)
    # H(target).
    counts = np.bincount(target, minlength=n_target_vals).astype(np.float64)
    total = counts.sum()
    p = counts / total
    p = p[p > 0]
    h_t = float(-np.sum(p * np.log2(p)))
    # H(target | context).
    h_t_given_c = conditional_entropy(target, context, n_target_vals)
    return (h_t, h_t_given_c, h_t - h_t_given_c)


# --- Self-check ------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. sample_three_crumbs.
    bits = np.array([1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0],
                      dtype=np.int8)
    c0, c1, c2 = sample_three_crumbs(bits, 0, 3, 5)
    # c0 = bits[0:2] = (1, 0) → 0b10 = 2.
    # c1 = bits[3:5] = (1, 0) → 0b10 = 2.
    # c2 = bits[5:7] = (0, 1) → 0b01 = 1.
    if (c0, c1, c2) != (2, 2, 1):
        if verbose:
            print(f"FAIL: sample three crumbs ({c0}, {c1}, {c2}) "
                  f"≠ (2, 2, 1)")
        ok = False

    # 2. Out-of-range returns 0.
    c0, c1, c2 = sample_three_crumbs(bits, 0, 100, 200)
    if (c1, c2) != (0, 0):
        if verbose:
            print(f"FAIL: out-of-range non-zero")
        ok = False

    # 3. combine_crumbs assignments produce valid ranges.
    for a in ("v4-abelian", "v4-s3-chirality", "s4-quotient", "s3-abelian"):
        for c0 in range(4):
            for c1 in range(4):
                for c2 in range(4):
                    v = combine_crumbs(c0, c1, c2, a)
                    if a == "v4-abelian" and not (0 <= v < 64):
                        if verbose:
                            print(f"FAIL: v4-abelian out of range")
                        ok = False
                    if a == "v4-s3-chirality" and not (0 <= v < 64):
                        if verbose:
                            print(f"FAIL: v4-s3-chirality out of range")
                        ok = False
                    if a == "s4-quotient" and not (0 <= v < 24):
                        if verbose:
                            print(f"FAIL: s4-quotient out of range "
                                  f"({c0},{c1},{c2}) → {v}")
                        ok = False
                    if a == "s3-abelian" and not (0 <= v < 6):
                        if verbose:
                            print(f"FAIL: s3-abelian out of range")
                        ok = False

    # 4. Stream computation works.
    stream = prime_chain_stream(bits, p=3, q=5, stride=2,
                                  assignment="v4-abelian")
    if len(stream) == 0:
        if verbose:
            print(f"FAIL: empty stream on non-empty input")
        ok = False

    # 5. Mutual information sanity: identical streams → MI = H.
    a = np.array([0, 1, 2, 3, 0, 1, 2, 3] * 10, dtype=np.int64)
    h_t, h_tc, mi = mutual_information(a, a, n_target_vals=4)
    if not (abs(h_tc) < 1e-6 and abs(mi - h_t) < 1e-6):
        if verbose:
            print(f"FAIL: identity MI: h={h_t}, h|c={h_tc}, mi={mi}")
        ok = False

    # 6. MI sanity: independent streams → MI ≈ 0.
    rng = np.random.default_rng(7)
    a = rng.integers(0, 4, size=4096, dtype=np.int64)
    b = rng.integers(0, 64, size=4096, dtype=np.int64)
    h_t, h_tc, mi = mutual_information(a, b, n_target_vals=4)
    # MI from finite sample should be small; allow up to 0.15 bits.
    if abs(mi) > 0.15:
        if verbose:
            print(f"FAIL: independent MI {mi} not near 0")
        ok = False

    if verbose:
        print(f"prime_chain self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
