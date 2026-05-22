"""Eliza.Golay — binary Golay code [23, 12, 7] for the EE-arc.

Sporadic perfect code at length 23. 4096 codewords; corrects up to 3
single-bit errors. Symmetry group M₂₃ ⊂ Mathieu (one of the
five sporadic simple groups in the smallest Mathieu family).

Per the user's RM(1,3) intuition: the substrate's F₇ structure
expects code-family alignment. Hamming(7,4) is the perfect single-
error code at length 7; Golay [23, 12, 7] is the perfect triple-
error code at length 23. The substrate's F₇ aligns naturally with
Hamming(7,4); does it align with Golay? Off-byte-alignment likely
makes it expensive.

Construction (standard): Golay [24, 12, 8] extended code is generated
by the matrix [I₁₂ | B] where B is the bordered 12 × 12 incidence
matrix of the icosahedron. Puncture one position to get [23, 12, 7].

For codec use: each Golay codeword is 23 bits; we'd need a 23-bit
framing layer (or pad to 24 = 3 bytes). Inefficient at byte
boundaries; expected to underperform RM(r, 3-5) due to alignment
overhead.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np


# Standard B matrix for the extended Golay code [24, 12, 8].
# 12 × 12 binary matrix; rows form the parity portion of the
# generator [I₁₂ | B].
# Reference: Conway & Sloane "Sphere Packings, Lattices and Groups"
# Ch. 11 — the "icosahedral" form.

_B_MATRIX: Tuple[Tuple[int, ...], ...] = (
    (1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1),
    (1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1),
    (0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1),
    (1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1),
    (1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1),
    (1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1),
    (0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1),
    (0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1),
    (0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1),
    (1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1),
    (0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0),
)


def extended_golay_generator() -> np.ndarray:
    """Return the (12, 24) generator matrix [I₁₂ | B] for the
    extended Golay code [24, 12, 8].
    """
    I = np.eye(12, dtype=np.int8)
    B = np.array(_B_MATRIX, dtype=np.int8)
    return np.hstack([I, B])


def all_extended_golay_codewords() -> List[int]:
    """All 2^12 = 4096 codewords of the extended Golay [24, 12, 8],
    each packed as a 24-bit integer (MSB-first).
    """
    G = extended_golay_generator()
    out: List[int] = []
    for msg in range(1 << 12):
        bits = np.array([(msg >> (11 - i)) & 1 for i in range(12)],
                          dtype=np.int8)
        cw = (bits @ G) & 1
        c = 0
        for j in range(24):
            c |= int(cw[j]) << (23 - j)
        out.append(c)
    return out


def all_golay_codewords_23() -> List[int]:
    """All 2^12 = 4096 codewords of the punctured Golay [23, 12, 7],
    obtained by dropping the last bit of each extended codeword.
    """
    return [c >> 1 for c in all_extended_golay_codewords()]


def codeword_weight_distribution(codewords: List[int]) -> dict:
    """Returns {weight: count}."""
    out: dict = {}
    for c in codewords:
        w = bin(c).count("1")
        out[w] = out.get(w, 0) + 1
    return out


# --- Sweep -------------------------------------------------------------


def apply_golay_mask_24(data: bytes, mask24: int) -> bytes:
    """XOR a 24-bit mask aligned on 3-byte boundaries. Tail bytes
    XOR with the prefix of the mask.
    """
    if mask24 == 0:
        return bytes(data)
    triple = [(mask24 >> 16) & 0xFF,
              (mask24 >> 8) & 0xFF,
              mask24 & 0xFF]
    return bytes(b ^ triple[i % 3] for i, b in enumerate(data))


def find_best_golay_mask(
    data: bytes, estimator=None, two_stage: bool = True,
) -> Tuple[int, int]:
    """EE13: 24-bit XOR-mask sweep over extended Golay codewords.

    Returns (best_mask_24bit, weight).
    """
    if estimator is None:
        from eliza.multiscale_rotation import chain_symbol_entropy_estimator
        estimator = chain_symbol_entropy_estimator
    if not data:
        return (0, 0)
    codewords = all_extended_golay_codewords()

    def best_in(window: bytes) -> int:
        best_m = 0
        best_score = estimator(window)
        for m in codewords:
            if m == 0:
                continue
            score = estimator(apply_golay_mask_24(window, m))
            if score < best_score:
                best_score = score
                best_m = m
        return best_m

    global_m = best_in(data)
    if not two_stage:
        return (global_m, bin(global_m).count("1"))
    half = max(1, len(data) // 2)
    first_m = best_in(data[:half])
    second_m = best_in(data[half:])
    if first_m == second_m == global_m:
        return (global_m, bin(global_m).count("1"))
    return (0, 0)


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Extended Golay has 4096 codewords.
    cws = all_extended_golay_codewords()
    if len(cws) != 4096:
        if verbose:
            print(f"FAIL: |extended Golay| = {len(cws)} ≠ 4096")
        ok = False

    # 2. Minimum distance of extended Golay is 8.
    nonzero_min = min(bin(c).count("1") for c in cws if c != 0)
    if nonzero_min != 8:
        if verbose:
            print(f"FAIL: min weight {nonzero_min} ≠ 8 "
                  f"(B matrix may be wrong)")
        ok = False

    # 3. Punctured Golay has 4096 codewords with min weight 7.
    cws_23 = all_golay_codewords_23()
    if len(cws_23) != 4096:
        if verbose:
            print(f"FAIL: |Golay 23| ≠ 4096")
        ok = False
    nonzero_min_23 = min(bin(c).count("1") for c in cws_23 if c != 0)
    if nonzero_min_23 != 7:
        if verbose:
            print(f"FAIL: min weight at length 23 {nonzero_min_23} ≠ 7")
        ok = False

    # 4. Mask application is involution.
    data = bytes(range(96))
    for m in (0x000000, 0x123456, 0xABCDEF, 0xFFFFFF):
        twice = apply_golay_mask_24(apply_golay_mask_24(data, m), m)
        if twice != data:
            if verbose:
                print(f"FAIL: Golay mask {m:06x} not involution")
            ok = False

    if verbose:
        wd = codeword_weight_distribution(cws)
        print(f"  Extended Golay weight distribution: {sorted(wd.items())}")
        print(f"hamming/golay self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
