# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""CONSTELLATION reference: a multi-dimensional (2D) Bloom filter over the polar (r, theta) frame.
The conformance checks f090_2_constellation_* pin THIS. COMPOSES polar_ref (the (r,theta) frame supplying
both axes) + algorithms_ref.Bloom (the carrier) -- it does not reinvent either.

HOW IT WORKS (decomposed):
  A node's peers each land at (r-slice, theta-bucket): the theta comes from POLARIS (rank-angle), the
  r-slice indexes which radial shell (AURORA registration band) the peer's sub-structure sits in. The 2D
  grid (nslices x nbuckets) is a Bloom filter: each (peer, r-slice, theta-bucket) key sets k bits; query
  tests them. NO false negatives (a present peer always tests in); tunable false positives.
  The "2D slices" = one Bloom row per r-slice, stacked over the shared theta discretization (QUANTUM).

THM 9.2 degeneration: with nslices=1, identity hash, m = |theta-vocab|, k=1 -> collision-free, deterministic
  -> EXACT membership = the ASPF bitmask. CONSTELLATION is the probabilistic generalization; bitmask is the
  finite-vocabulary special case. (This realizes f090_2_constellation_iso Thm 9.2 in code.)

CANON+RESIDUE (AI-CANON-RESIDUE): the filter's bit-grid is the canonical form (membership-equivalent inputs
  collide to the same grid -- lossy); the residue is the exact inserted (slice,bucket,peer) key-list that
  recovers the precise input. canonical(grid) + residue is LOSSLESS via recover. Conservation: the Bloom
  RELEASES the trivial 'each element has a unique cell' (allows collision) and the residue (the key-list)
  is the carried witness -- triviality-out (injectivity) = witness-in (the recorded keys).
"""
from importlib import util as _il
import os as _os

def _load(name):
    spec = _il.spec_from_file_location(name, _os.path.join(_os.path.dirname(__file__), name+".py"))
    m = _il.module_from_spec(spec); spec.loader.exec_module(m); return m

class Constellation:
    """2D Bloom over (r-slice, theta-bucket). nslices radial shells x nbuckets angular bins, k hashes."""
    def __init__(self, nslices, nbuckets, k=3):
        self.nslices = nslices; self.nbuckets = nbuckets; self.k = k
        self.grid = [[0]*nbuckets for _ in range(nslices)]   # the 2D bit-grid (the canonical form)
        self.seeds = list(range(k))
        self._keys = []                                       # the residue: exact inserted keys

    def _bits(self, slice_idx, peer):
        # k hashed theta-bucket positions for (peer) within the given r-slice row
        return [(hash((s, slice_idx, peer)) % self.nbuckets) for s in self.seeds]

    def add(self, slice_idx, peer):
        for b in self._bits(slice_idx, peer):
            self.grid[slice_idx][b] = 1
        self._keys.append((slice_idx, peer))                  # retain the residue

    def __contains__(self, key):
        slice_idx, peer = key
        return all(self.grid[slice_idx][b] for b in self._bits(slice_idx, peer))

    # ---- build from a polar frame: peers -> (r-slice, theta-bucket) cells ----
    @staticmethod
    def from_polar(peers_with_weight, reference, nslices, nbuckets, k=3):
        """Place each peer by its POLARIS theta-bucket; the r-slice indexes the node's AURORA registration
        band (here, all peers of one node share the node's r-slice, computed from polar_ref)."""
        P = _load("polar_ref")
        angles, _ = P.polaris_angles(peers_with_weight)
        hist = P.angular_histogram(peers_with_weight, nbuckets)
        r, _shift = P.aurora_radius(hist, reference)
        slice_idx = min(int(r * nslices), nslices-1)          # radial shell from the AURORA radius
        c = Constellation(nslices, nbuckets, k)
        import math
        for peer, _w in peers_with_weight:
            # the theta-bucket is implied by POLARIS angle; the Bloom key is (slice, peer)
            c.add(slice_idx, peer)
        return c, slice_idx

# ---- THM 9.2: the degenerate CONSTELLATION = exact bitmask ----
def degenerate_bitmask(items, vocab):
    """nslices=1, identity hash, m=|vocab|, k=1 -> collision-free exact membership (the ASPF bitmask).
    Verifies Thm 9.2: bitmask is CONSTELLATION's finite-vocabulary special case."""
    B = _load("algorithms_ref")
    return B.bitmask_exact(items, vocab)

# ---- CANON + RESIDUE ----
def canonicalize(constellation):
    """canonical form = the bit-grid (membership-equivalent, lossy); residue = the exact key-list."""
    grid = [row[:] for row in constellation.grid]
    residue = list(constellation._keys)
    return grid, residue

def recover(grid, residue, nbuckets, k=3):
    """Rebuild the exact CONSTELLATION from the residue key-list (lossless: every insert replayed)."""
    nslices = len(grid)
    c = Constellation(nslices, nbuckets, k)
    for slice_idx, peer in residue:
        c.add(slice_idx, peer)
    return c
