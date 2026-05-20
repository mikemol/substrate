"""Eliza.BitPack — GF(2)/numpy-packed representations of the substrate.

Slices 6-8 of the 20-slice plan, condensed: each of (alphabets+manifold,
octonion, signature) gets a numpy-packed equivalent. The original
Python-dict structures stay as the canonical reference; this module
provides drop-in vectorised replacements for hot loops.

The bit-packed forms are cupy-compatible by construction: every
operation is `array[index]` or `np.bincount` / `np.cumsum`. Replacing
`np` with `cp` ports to GPU.

Per GPU_ACCELERATION.md: chamber as uint8 (24 < 256), Gen as uint8
{0,1,2}, V₄ as uint8 {0,1,2,3}, all lookups via numpy arrays.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from eliza.alphabets import (
    Chamber, Gen, ORIGIN, V4_LABELS, V4_PERMS,
    NIBBLE_TO_PERM, perm_compose,
)
from eliza.manifold import Manifold, apply as _apply
from eliza.orbit import Cocycle


# --- Slice 6: alphabets + manifold ----------------------------------------


class ManifoldPacked:
    """Bit-packed Cayley graph of S₄.

    Stores:
      * `chambers : uint8[24][4]` — the 24 chambers as 4-element perms.
      * `chamber_idx : Dict[Chamber, int]` — reverse lookup.
      * `apply_table : uint8[24][3]` — `apply(chamber_idx, gen) → next_chamber_idx`.
      * `cocycle_table : uint8[24][2]` — `chamber_idx → (orbit_idx, fiber_idx)`.
      * `bruhat_table : uint8[24]` — `chamber_idx → bruhat distance`.

    Total memory: ~250 bytes. All cupy-compatible.
    """

    def __init__(self, manifold: Manifold):
        self.manifold = manifold
        self.chambers: np.ndarray = np.array(
            [list(c) for c in manifold.nodes], dtype=np.uint8
        )
        self.chamber_idx: Dict[Chamber, int] = {
            c: i for i, c in enumerate(manifold.nodes)
        }
        # apply_table[i, g] = node_index of apply(g, chambers[i]).
        gens = (Gen.s1, Gen.s2, Gen.s3)
        self.apply_table: np.ndarray = np.array([
            [self.chamber_idx[_apply(g, c)] for g in gens]
            for c in manifold.nodes
        ], dtype=np.uint8)
        # bruhat_table[i] = bruhat distance.
        self.bruhat_table: np.ndarray = np.array([
            manifold.bruhat_distance(c) for c in manifold.nodes
        ], dtype=np.uint8)

    def step(self, chamber_idx: int, gen_idx: int) -> int:
        """Vectorised chamber walk: O(1) array lookup."""
        return int(self.apply_table[chamber_idx, gen_idx])

    def step_batch(self, chamber_indices: np.ndarray,
                   gen_indices: np.ndarray) -> np.ndarray:
        """Batched chamber walk: `apply_table[chambers, gens]`."""
        return self.apply_table[chamber_indices, gen_indices]


class CocyclePacked:
    """Bit-packed V₄-cocycle decomposition.

    `cocycle_table[chamber_idx]` = `(orbit_idx, fiber_idx)`.
    `orbits` and `fibers` are the canonical label lookup tables.

    Encoded as:
      * `cocycle_table : uint8[24, 2]` — orbit and fiber indices.
      * `orbit_labels : List[str]` — canonical word for each orbit.
      * `fiber_labels : List[str]` — {e, α, β, γ}.
    """

    def __init__(self, cocycle: Cocycle, manifold_packed: ManifoldPacked):
        manifold = manifold_packed.manifold
        # Collect orbit canonical words in order of first occurrence.
        orbit_to_idx: Dict[str, int] = {}
        cocycle_rows: List[Tuple[int, int]] = []
        for chamber in manifold.nodes:
            info = cocycle.info(chamber)
            ow = info.canonical_word
            if ow not in orbit_to_idx:
                orbit_to_idx[ow] = len(orbit_to_idx)
            fiber_idx = V4_LABELS.index(info.fiber_label)
            cocycle_rows.append((orbit_to_idx[ow], fiber_idx))
        self.cocycle_table: np.ndarray = np.array(cocycle_rows, dtype=np.uint8)
        self.orbit_labels: List[str] = sorted(
            orbit_to_idx.keys(), key=lambda k: orbit_to_idx[k]
        )
        self.fiber_labels: Tuple[str, ...] = V4_LABELS

    def decompose(self, chamber_idx: int) -> Tuple[int, int]:
        """Return (orbit_idx, fiber_idx) for a chamber-index."""
        row = self.cocycle_table[chamber_idx]
        return int(row[0]), int(row[1])


# --- Slice 7: octonion (16 byte-rotations as numpy LUT) ------------------


def build_rotation_lut() -> np.ndarray:
    """16-rotation × 256-byte LUT as uint8 array.

    Mirrors `eliza.octonion.ROTATION_LUT` but as a single contiguous
    `np.ndarray(shape=(16, 256), dtype=uint8)` for vectorised access.
    """
    from eliza.octonion import ROTATION_LUT
    return np.array(ROTATION_LUT, dtype=np.uint8)


def rotate_bytes_packed(data: bytes, rotation_idx: int, lut: np.ndarray) -> np.ndarray:
    """Vectorised byte rotation: one lookup per byte."""
    arr = np.frombuffer(data, dtype=np.uint8)
    return lut[rotation_idx][arr]


def rotate_bytes_all_packed(data: bytes, lut: np.ndarray) -> np.ndarray:
    """All 16 rotations of the same byte stream in one shot.

    Returns shape (16, len(data)) — the 16 rotated versions stacked.
    Cupy-equivalent: identical with `cp.frombuffer` and `cp.ndarray`.
    """
    arr = np.frombuffer(data, dtype=np.uint8)
    # lut is (16, 256); arr is (N,); broadcast to get (16, N).
    return lut[:, arr]


# --- Slice 8: signature via np.bincount -----------------------------------


def signature_packed(window: bytes, depth: int = 4) -> np.ndarray:
    """Recursive 2-bin histogram via vectorised np.bincount.

    For a window of N bytes at depth d, returns 2^d bins counting how
    many bytes share the top-d-bit prefix.

    Equivalent to `eliza.signature.signature` but no Python loop.
    Cupy-equivalent: `cp.bincount(byte_array >> shift, minlength=...)`.
    """
    if depth == 0:
        return np.array([len(window)], dtype=np.int32)
    arr = np.frombuffer(window, dtype=np.uint8)
    shift = 8 - depth
    return np.bincount(arr >> shift, minlength=(1 << depth)).astype(np.int32)


def signature_batch_packed(rotated_windows: np.ndarray, depth: int = 4) -> np.ndarray:
    """Batched signature over all 16 rotations of a window.

    `rotated_windows` has shape (16, N) from `rotate_bytes_all_packed`.
    Returns shape (16, 2^d): one signature per rotation.

    Each rotation's signature is independently computable; we use a
    Python loop here because `bincount` doesn't broadcast along axes,
    but the 16 calls are still O(N) each and trivial on GPU via
    explicit cupy.bincount calls per rotation.
    """
    n_rot = rotated_windows.shape[0]
    n_bins = 1 << depth
    out = np.zeros((n_rot, n_bins), dtype=np.int32)
    shift = 8 - depth
    for r in range(n_rot):
        out[r] = np.bincount(rotated_windows[r] >> shift, minlength=n_bins)
    return out
