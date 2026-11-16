# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""POLARIS + AURORA polar-frame reference (the (theta, r) node frame; how it works, decomposed).
The conformance checks f090_2_polar_* pin THIS. Built on AURORA's emd_circular (algorithms_ref) -- the
polar frame COMPOSES POLARIS (theta) + AURORA (r), it does not reinvent registration.

POLARIS supplies the ANGLE theta: each peer gets an angular coordinate from its CANONICAL structural rank,
  theta_p = 2*pi * rank(p) / |N|  (rank = position in the canonical, weight-sorted ordering of the peers).
AURORA supplies the RADIUS r: the virtual-rotation magnitude needed to register this node's angular
  peer-distribution against a reference orientation = the S^1 registration cost (AURORA's emd_circular shift).
Together (theta, r) is ONE polar frame -- the report's "underspecified radial coordinate" hole, closed
internally (both coords corpus-supplied, no external spectral embedding).

CANON+RESIDUE law (AI-CANON-RESIDUE): canonicalize(node) = (canonical_frame, residue) where canonical_frame
is the rotation-INVARIANT representation (registered against the reference, so orientation is quotiented out)
and the residue is EXACTLY what registration discarded -- the rotation that recovers the original orientation.
canonical_frame alone is lossy (all rotations of a node share it); canonical_frame + residue is LOSSLESS:
recover(canonical_frame, residue) reproduces the original angular distribution. This is the conservation
reading made operational: registration RELEASES the trivial 'orientation is fixed' and the residue (the
rotation) is the carried witness.
"""
import math
from importlib import util as _il
import os as _os

def _aurora():
    # reuse AURORA's emd_circular -- DO NOT reinvent registration
    spec = _il.spec_from_file_location("ar", _os.path.join(_os.path.dirname(__file__), "algorithms_ref.py"))
    m = _il.module_from_spec(spec); spec.loader.exec_module(m); return m

# ---- POLARIS: canonical rank -> angle ----
def polaris_angles(peers_with_weight):
    """peers_with_weight: list of (peer, weight). Returns {peer: theta} by canonical weight-sorted rank.
    theta_p = 2*pi * rank / n. Ties broken by peer identity (so the canonical order is total/deterministic)."""
    ordered = sorted(peers_with_weight, key=lambda pw: (-pw[1], pw[0]))  # weight desc, then identity
    n = len(ordered)
    return {p: 2*math.pi*rank/n for rank, (p, w) in enumerate(ordered)}, [p for p, w in ordered]

# ---- the angular peer-distribution histogram (what AURORA registers) ----
def angular_histogram(peers_with_weight, nbuckets):
    """Bin peers into nbuckets by their POLARIS angle, weighting by peer weight. This is the QUANTUM
    discretization of the theta axis; AURORA registers THIS histogram."""
    angles, _ = polaris_angles(peers_with_weight)
    hist = [0.0]*nbuckets
    wmap = dict(peers_with_weight)
    for p, th in angles.items():
        b = int(th / (2*math.pi) * nbuckets) % nbuckets
        hist[b] += wmap[p]
    return hist

# ---- AURORA: radius = registration cost against a reference ----
def aurora_radius(hist, reference):
    """r = the S^1 registration of hist against reference. Returns (r_distance, rotation_shift).
    rotation_shift is AURORA's rotation (the residue); r_distance is the radial magnitude."""
    a = _aurora()
    dist, shift = a.emd_circular(hist, reference)
    return dist, shift

# ---- the full polar frame ----
def polar_frame(peers_with_weight, reference, nbuckets):
    """Returns (theta_map, r) -- the (POLARIS angle per peer, AURORA radius). The node's polar coordinates."""
    theta_map, _ = polaris_angles(peers_with_weight)
    hist = angular_histogram(peers_with_weight, nbuckets)
    r, _shift = aurora_radius(hist, reference)
    return theta_map, r

# ---- CANON + RESIDUE (lossless) ----
def canonicalize(hist, reference):
    """canonical_frame = hist rotated INTO registration with reference (orientation quotiented out);
    residue = the rotation shift that undoes the registration (recovers the original orientation).
    canonical_frame alone is rotation-invariant (lossy); + residue is lossless."""
    _r, shift = aurora_radius(hist, reference)
    n = len(hist)
    canonical_frame = hist[shift:] + hist[:shift]   # rotate into the registered orientation
    residue = shift                                  # the witness: how far we rotated
    return canonical_frame, residue

def recover(canonical_frame, residue):
    """Invert canonicalize: rotate the canonical frame back by the residue -> the original histogram."""
    n = len(canonical_frame); shift = residue
    return canonical_frame[n-shift:] + canonical_frame[:n-shift] if shift else list(canonical_frame)
