"""Eliza.Signature — recursive 2-bin (conditional bit-prefix) histogram.

The signature of a window of bytes at depth d is a 2^d-bin histogram:
each bin counts how many bytes in the window share the same d-bit prefix
(top d bits). At depth 0: one bin (window length). At depth 8: the full
byte histogram.

This is the F₂-native shape of the byte-frequency distribution: each
level is a 2-bin split (per bit position), the depth IS the CD rung
the signature is resolved at (depth 1 = F, depth 2 = V₄, depth 4 = H,
depth 8 = O). Truncating depth gives natural lossy approximations.

Used as a hashable feature key for `Sequitur_rotations`: windows with
the same depth-d signature get the same rotation suggestion.
"""

from __future__ import annotations

from typing import Tuple


def signature(window: bytes, depth: int = 4) -> Tuple[int, ...]:
    """Return the depth-d byte-prefix histogram: a tuple of 2^d counts.

    depth=0  → (window_length,)                — F rung
    depth=2  → (count_per_top-crumb, ...)      — V₄ rung
    depth=4  → (count_per_top-nibble, ...)     — H rung
    depth=8  → full byte histogram             — O rung
    """
    if depth == 0:
        return (len(window),)
    counts = [0] * (1 << depth)
    shift = 8 - depth
    for b in window:
        counts[b >> shift] += 1
    return tuple(counts)


def signature_entropy(sig: Tuple[int, ...]) -> float:
    """Shannon entropy of a signature (in bits), treating it as a
    distribution. Useful as a quick rotation-quality score."""
    import math
    total = sum(sig)
    if total == 0:
        return 0.0
    h = 0.0
    for c in sig:
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def normalize(sig: Tuple[int, ...]) -> Tuple[float, ...]:
    """Convert raw counts to probabilities; useful for stable hashing
    across windows of different sizes."""
    total = sum(sig)
    if total == 0:
        return tuple(0.0 for _ in sig)
    return tuple(c / total for c in sig)


def quantize(sig: Tuple[int, ...], levels: int = 16) -> Tuple[int, ...]:
    """Quantize the signature's probabilities to `levels` discrete
    buckets. Makes signatures of different-sized windows comparable
    and limits the Sequitur_rotations key space."""
    total = sum(sig)
    if total == 0:
        return tuple(0 for _ in sig)
    return tuple(min(levels - 1, (c * levels) // total) for c in sig)
