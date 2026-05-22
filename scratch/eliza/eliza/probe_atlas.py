"""Eliza.ProbeAtlas — II-arc kinematic-gauge-class probe atlases.

Per the user 2026-05-21 + [[multi-route-equivariance-recovery]] +
[[kinematic-gauge-sacrifice-catalog]]: each CV-joint family member
is a mechanism for transmitting rotational flexibility through
multiple bisecting elements jointly enforcing homokineticity.
Mapped to the codec: each kinematic gauge-class is a probe ATLAS
(set of past-chain-symbol offsets) reading the chain walk's state
at multiple distances simultaneously.

The full catalog (16 discrete-Sylow members from
[[kinematic-gauge-sacrifice-catalog]]) is encoded here as
parameterised offset patterns. Each atlas takes a base prime p
(and sometimes a second prime q) and produces a list of nibble-
offsets back from the current chain position.

Per the user: 'we won't know if it's worth it until we look to see
if it makes a difference' + 'combinatorial dot product, so we can
find which permutations work best with each other'.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple

import numpy as np


@dataclass(frozen=True)
class AtlasSpec:
    """A probe atlas specification.

    Each atlas is identified by:
      name: Thompson / Cardan / Rzeppa / Weiss / ...
      sylow: which Sylow class it inhabits (2, 3, or 7)
      offsets_fn: a function p, q -> list of nibble offsets
      max_probes: cap to keep joint context tractable (≤ 6 for MI)
    """
    name: str
    sylow: int
    offsets_fn: Callable[[int, int], List[int]]
    max_probes: int = 6


# --- Sylow-2 (F₂³) — axial / linkages ---------------------------------

def _thompson_offsets(p: int, q: int) -> List[int]:
    """Three nested binary probes — F₂³ flag filtration (Thompson)."""
    return [p, 2 * p, 4 * p]


def _cardan_offsets(p: int, q: int) -> List[int]:
    """Antiphase pair (Double Cardan)."""
    return [p, 2 * p]


def _cornay_offsets(p: int, q: int) -> List[int]:
    """External nested frame, 4 probes (Cornay max F₂³ saturation)."""
    return [p, 2 * p, 3 * p, 5 * p]


def _rag_offsets(p: int, q: int) -> List[int]:
    """Compliant soft cluster (Rag Joint) — overlapping nearby probes."""
    return [p, p + 1, p + 2]


def _clemens_offsets(p: int, q: int) -> List[int]:
    """4-layer F₂⁴ flat scaffold (Clemens)."""
    return [p, 2 * p, 4 * p, 8 * p]


# --- Sylow-3 (F₃ → S¹) — cyclic / phasing ------------------------------

def _rzeppa_offsets(p: int, q: int) -> List[int]:
    """6-ball cyclic cage (Rzeppa) — S₃ orbit."""
    return [p, 2 * p, 3 * p, 4 * p, 5 * p, 6 * p]


def _tripod_offsets(p: int, q: int) -> List[int]:
    """3-spider Z₃ (Tripod)."""
    return [p, 2 * p, 3 * p]


def _doj_offsets(p: int, q: int) -> List[int]:
    """Sylow-2 ↔ Sylow-3 crossover (Double Offset Joint).
    6-ball cyclic + axial sign-bit translation.
    """
    return [p, 2 * p, 3 * p, 4 * p, 5 * p, q]   # 5 cyclic + 1 axial


def _gear_offsets(p: int, q: int) -> List[int]:
    """Continuous-limit dense sampling (Gear Coupling)."""
    return [p, 2 * p, 3 * p, 4 * p, 5 * p, 6 * p]


def _swash_offsets(p: int, q: int) -> List[int]:
    """F₃ ⋊ Z₂ over continuous S¹ — two cyclic phased (Swashplate)."""
    return [p, 2 * p, 3 * p, q, 2 * q, 3 * q]


# --- Sylow-7 (F₇) — projective -----------------------------------------

def _weiss_offsets(p: int, q: int) -> List[int]:
    """Fano-plane 4 intersections (Weiss) — 4 probes at Fano points
    {1, 2, 4} (the 7-cycle generators) plus 3 (=1+2).
    """
    return [p, 2 * p, 3 * p, 4 * p]


def _birfield_offsets(p: int, q: int) -> List[int]:
    """Sylow-7 border variant (Birfield)."""
    return [p, 2 * p, 3 * p, 5 * p, 7 * p]


def _bendix_weiss_offsets(p: int, q: int) -> List[int]:
    """Self-dual interleaved (Bendix-Weiss) — pairs at Fano + duals."""
    return [p, 2 * p, 4 * p, 3 * p, 5 * p, 6 * p]


def _cross_groove_offsets(p: int, q: int) -> List[int]:
    """X-intersection track pattern (Cross-Groove)."""
    return [p, q, p + q, 2 * p + q]


def _countertrack_offsets(p: int, q: int) -> List[int]:
    """Internal antiphase alternation (Countertrack SX)."""
    return [p, 2 * p, 3 * p, 4 * p, 5 * p, 6 * p]


def _spherical_gear_offsets(p: int, q: int) -> List[int]:
    """F₇ → S² lift (Spherical Gear) — 2D projective; sample 6 of
    7×7 grid at (i*p + j*q) representative points.
    """
    return [p, q, p + q, 2 * p, 2 * q, p + 2 * q]


# --- Atlas registry ----------------------------------------------------


ATLAS_REGISTRY: List[AtlasSpec] = [
    # Sylow-2
    AtlasSpec("Thompson",    2, _thompson_offsets),
    AtlasSpec("Cardan",      2, _cardan_offsets),
    AtlasSpec("Cornay",      2, _cornay_offsets),
    AtlasSpec("Rag",         2, _rag_offsets),
    AtlasSpec("Clemens",     2, _clemens_offsets),
    # Sylow-3
    AtlasSpec("Rzeppa",      3, _rzeppa_offsets),
    AtlasSpec("Tripod",      3, _tripod_offsets),
    AtlasSpec("DOJ",         3, _doj_offsets),
    AtlasSpec("Gear",        3, _gear_offsets),
    AtlasSpec("Swash",       3, _swash_offsets),
    # Sylow-7
    AtlasSpec("Weiss",       7, _weiss_offsets),
    AtlasSpec("Birfield",    7, _birfield_offsets),
    AtlasSpec("BendixWeiss", 7, _bendix_weiss_offsets),
    AtlasSpec("CrossGroove", 7, _cross_groove_offsets),
    AtlasSpec("Countertrack",7, _countertrack_offsets),
    AtlasSpec("SphericalGear",7,_spherical_gear_offsets),
]


# --- Context evaluation ------------------------------------------------


def _v4_part_table():
    from eliza.coarse_residue import coset_members, n_cosets
    out = [0] * 24
    for ci in range(n_cosets()):
        members = sorted(coset_members(ci))
        for pos, m in enumerate(members):
            out[m] = pos
    return out


_V4_PART = _v4_part_table()


def atlas_context(
    chain: np.ndarray, k: int, atlas: AtlasSpec,
    p: int = 2, q: int = 3,
) -> int:
    """Compute the joint context value for `atlas` at chain position k.

    Each probe reads the V₄-part (0..3) of the chain symbol at offset
    `offset` back from k. Joint context = concatenation of probe
    crumbs (max 6 probes = 12 bits = 4096 values).
    """
    offsets = atlas.offsets_fn(p, q)[:atlas.max_probes]
    ctx = 0
    for i, offset in enumerate(offsets):
        pos = k - offset
        if pos < 0 or pos >= len(chain):
            crumb = 0
        else:
            c = int(chain[pos])
            crumb = _V4_PART[c] if 0 <= c < 24 else 0
        ctx |= (crumb & 3) << (2 * i)
    return ctx


def atlas_context_stream(
    chain: np.ndarray, atlas: AtlasSpec, p: int = 2, q: int = 3,
) -> np.ndarray:
    """Context value for each chain position."""
    out = np.zeros(len(chain), dtype=np.int64)
    for k in range(len(chain)):
        out[k] = atlas_context(chain, k, atlas, p, q)
    return out


def joint_atlas_context_stream(
    chain: np.ndarray, atlases: List[AtlasSpec],
    p: int = 2, q: int = 3, probe_cap: int = None,
) -> np.ndarray:
    """Combinatorial joint context: concatenation of each atlas's
    context value as a single int.

    `probe_cap` overrides each atlas's max_probes — useful for
    triple/quad-Sylow joints where global probe budget matters more
    than per-atlas budget.

    Caller must ensure the joint context size stays tractable (≤ ~10
    bits per atlas; ≤ 24 bits total).
    """
    streams = []
    widths = []
    for a in atlases:
        cap = probe_cap if probe_cap is not None else a.max_probes
        # Use truncated atlas: compute context with offsets[:cap].
        offsets = a.offsets_fn(p, q)[:cap]
        single_stream = np.zeros(len(chain), dtype=np.int64)
        for k in range(len(chain)):
            ctx = 0
            for i, offset in enumerate(offsets):
                pos = k - offset
                if pos < 0 or pos >= len(chain):
                    crumb = 0
                else:
                    c = int(chain[pos])
                    crumb = _V4_PART[c] if 0 <= c < 24 else 0
                ctx |= (crumb & 3) << (2 * i)
            single_stream[k] = ctx
        streams.append(single_stream)
        widths.append(2 * len(offsets))
    out = np.zeros(len(chain), dtype=np.int64)
    shift = 0
    for s, w in zip(streams, widths):
        out |= (s & ((1 << w) - 1)) << shift
        shift += w
    return out


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Catalog completeness: 16 atlases, 5 + 5 + 6 by Sylow class.
    if len(ATLAS_REGISTRY) != 16:
        if verbose:
            print(f"FAIL: catalog size {len(ATLAS_REGISTRY)} ≠ 16")
        ok = False
    sylow_counts = {}
    for a in ATLAS_REGISTRY:
        sylow_counts[a.sylow] = sylow_counts.get(a.sylow, 0) + 1
    if sylow_counts != {2: 5, 3: 5, 7: 6}:
        if verbose:
            print(f"FAIL: Sylow counts {sylow_counts}")
        ok = False

    # 2. Each atlas's offsets are positive and finite.
    for a in ATLAS_REGISTRY:
        offs = a.offsets_fn(2, 3)
        if not all(0 < o < 10000 for o in offs):
            if verbose:
                print(f"FAIL: {a.name} offsets out of range: {offs}")
            ok = False
        if len(offs) > 7:
            if verbose:
                print(f"FAIL: {a.name} has {len(offs)} probes (>7)")
            ok = False

    # 3. Context evaluation produces values in valid range.
    chain = np.arange(100) % 24
    for a in ATLAS_REGISTRY:
        ctx = atlas_context(chain, 50, a, p=2, q=3)
        max_ctx = (1 << (2 * a.max_probes)) - 1
        if not (0 <= ctx <= max_ctx):
            if verbose:
                print(f"FAIL: {a.name} ctx {ctx} > max {max_ctx}")
            ok = False

    # 4. Joint context for pair stays tractable.
    pair = [ATLAS_REGISTRY[0], ATLAS_REGISTRY[5]]   # Thompson + Rzeppa
    stream = joint_atlas_context_stream(chain, pair, p=2, q=3)
    if len(stream) != 100:
        if verbose:
            print(f"FAIL: joint stream length {len(stream)}")
        ok = False

    if verbose:
        print(f"  catalog: {[a.name for a in ATLAS_REGISTRY]}")
        print(f"probe_atlas self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
