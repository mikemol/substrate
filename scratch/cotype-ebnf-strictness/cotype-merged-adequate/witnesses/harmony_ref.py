# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""HARMONY reference: the similarity-measure family over peer distributions.
The conformance checks f090_2_harmony_* pin THIS. SOURCE-VERIFIED against echo/harmony
(1yMNz3C6AykbrfSEsXmd0od_6dGHBmh7FiOyjiHVQ-o8) -- HARMONY is a PLUGGABLE FAMILY of measures over the
different carriers, NOT a single formula. Similarity is computed AFTER AURORA alignment (the source's
interplay note). COMPOSES the existing refs: QUANTUM/polar angular vectors, CONSTELLATION Bloom,
algorithms_ref EMD (AURORA's S^1 machine), GALAXY signatures. It does not reinvent any carrier.

HOW IT WORKS (decomposed, per source -- four measure classes):
  1. Angular density vectors (from QUANTUM): Euclidean / Manhattan / cosine.
  2. Bloom filters (CONSTELLATION): Jaccard / Hamming on the bits.
  3. Density-function correlation.
  4. Earth Mover's Distance (the principled cross-bin measure; = AURORA's emd_circular).
The defining structural property: HARMONY is the COMPARATOR -- it consumes the carriers other subsystems
produce and returns a scalar similarity/distance. The choice of metric is a knob (source: 'Choice of Metric').

ALIGNMENT-FIRST (source interplay): for rotation-tolerant comparison, align with AURORA first, then measure.
This is why EMD-on-S^1 (which minimizes over rotations) is the principled member: it folds alignment INTO
the measure. The other measures compare at a fixed orientation and need explicit AURORA pre-alignment.

CANON+RESIDUE note (AI-CANON-RESIDUE): HARMONY does NOT canonicalize a node -- it COMPARES two already-
canonical frames and returns a scalar. The canonicalization (and thus the residue) lives in the carriers it
consumes (polar/CONSTELLATION/GALAXY), not in HARMONY. So HARMONY is EXEMPT from the per-ref canon+residue
obligation BY CONSTRUCTION: a comparator releases no triviality and carries no residue; it reads canonical
forms and emits a number. (This is itself a conservation reading: a pure comparator is the one operation
that adds no dimension -- it consumes the witnesses already carried, rather than releasing a new law.)
"""
import math
from importlib import util as _il
import os as _os

def _load(name):
    spec = _il.spec_from_file_location(name, _os.path.join(_os.path.dirname(__file__), name+".py"))
    m = _il.module_from_spec(spec); spec.loader.exec_module(m); return m

# ---- 1. angular density vectors ----
def euclidean(u, v):
    return math.sqrt(sum((a-b)**2 for a, b in zip(u, v)))
def manhattan(u, v):
    return sum(abs(a-b) for a, b in zip(u, v))
def cosine(u, v):
    dot = sum(a*b for a, b in zip(u, v))
    nu = math.sqrt(sum(a*a for a in u)); nv = math.sqrt(sum(b*b for b in v))
    return dot/(nu*nv) if nu and nv else 0.0

# ---- 2. Bloom-filter similarity (over CONSTELLATION grids / bit rows) ----
def jaccard(bits_a, bits_b):
    inter = sum(1 for a, b in zip(bits_a, bits_b) if a and b)
    union = sum(1 for a, b in zip(bits_a, bits_b) if a or b)
    return inter/union if union else 1.0
def hamming(bits_a, bits_b):
    return sum(1 for a, b in zip(bits_a, bits_b) if a != b)

# ---- 3. density-function correlation ----
def correlation(u, v):
    n = len(u); mu = sum(u)/n; mv = sum(v)/n
    cov = sum((a-mu)*(b-mv) for a, b in zip(u, v))
    du = math.sqrt(sum((a-mu)**2 for a in u)); dv = math.sqrt(sum((b-mv)**2 for b in v))
    return cov/(du*dv) if du and dv else 0.0

# ---- 4. EMD (the principled, rotation-folding measure; = AURORA's emd_circular) ----
def emd(u, v):
    A = _load("algorithms_ref")
    dist, _shift = A.emd_circular(u, v)
    return dist

# ---- the family dispatcher: HARMONY(metric) ----
_METRICS = {
    "euclidean": euclidean, "manhattan": manhattan, "cosine": cosine,
    "jaccard": jaccard, "hamming": hamming, "correlation": correlation, "emd": emd,
}
def harmony(u, v, metric="emd"):
    """The pluggable comparator: pick a metric from the family, return the scalar similarity/distance."""
    if metric not in _METRICS:
        raise ValueError(f"unknown HARMONY metric {metric!r}; choices: {sorted(_METRICS)}")
    return _METRICS[metric](u, v)

def harmony_aligned(u, v, metric="cosine"):
    """ALIGNMENT-FIRST: register v onto u with AURORA, THEN measure (rotation-tolerant comparison).
    For fixed-orientation metrics (cosine/euclidean/...), this is how the source says to use them."""
    A = _load("algorithms_ref")
    _dist, shift = A.emd_circular(u, v)         # AURORA finds the aligning rotation
    v_aligned = v[shift:] + v[:shift]
    return harmony(u, v_aligned, metric)

def metrics():
    return sorted(_METRICS)
