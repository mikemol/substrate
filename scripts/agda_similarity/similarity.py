"""Cosine similarity per scale + geometric-mean composition.

The geometric mean is sharper than arithmetic: if any scale's
similarity is 0, the composite score is 0. Reading the per-scale
breakdown is more informative than the composite when files are
near-orbits whose block-level signature differs only by Zₙ digits.
"""

from __future__ import annotations

import math
from collections import Counter

from .tokenize import blocks, char_ngrams, lines, strip_comment_lines, tokens


SCALE_NAMES = ("char3", "token", "line", "block")


def cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in common)
    if dot == 0:
        return 0.0
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    return dot / (norm_a * norm_b)


def profile(text: str) -> tuple[Counter, Counter, Counter, Counter]:
    body = strip_comment_lines(text)
    return char_ngrams(body, 3), tokens(body), lines(body), blocks(body)


def pair_similarity(
    p1: tuple[Counter, Counter, Counter, Counter],
    p2: tuple[Counter, Counter, Counter, Counter],
) -> tuple[float, tuple[float, float, float, float]]:
    """Per-scale cosines + geometric-mean composite. A 0 in any scale
    zeros the composite — correct behavior since orbit detection
    relies on the breakdown, not the aggregate."""
    scores = tuple(cosine(a, b) for a, b in zip(p1, p2))
    if any(s == 0.0 for s in scores):
        return 0.0, scores
    geo = math.exp(sum(math.log(s) for s in scores) / len(scores))
    return geo, scores
