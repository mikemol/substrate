"""Eliza.Frames — variable-frame codec architecture.

Each input stream is partitioned into windows. Each window is encoded
as one of four frame types, indexed by Cayley-Dickson rung:

  I-frame  (F₂ rung)
    Independent. The window is encoded by the underlying gt+AC codec
    (eliza.codec.encode) with no reference. Largest per-frame cost,
    no algebraic constraint.

  P-frame  (V₄ rung; lose F-linearity)
    Predicted. The window is encoded as (ref_window_id, V₄_residue)
    meaning "the V₄-residue rotation of reference window ref_window_id."
    Cost: log₂(n_windows_so_far) + 2 (V₄ residue) bits.

  Patch    (V₄ + sparse-correction rung)
    Like P, but with a sparse bitmap of positions where the reference
    is wrong. The base is `apply(V₄_residue, reference)`; the patch
    XORs a Reed-Muller-style low-weight codeword. Cost:
    log₂(n_windows) + 2 + bitmap_bits.
    A P-frame is a Patch with empty bitmap.

  B-frame  (H rung; lose V₄-commutativity)
    Bidirectional. Encoded as a function of TWO reference windows
    (typically one back, one forward) plus a permutation living at
    the next CD rung. Sacrifices associativity: B-frames don't chain.
    Most expensive per frame, most flexible.

The chooser picks the cheapest frame type per window, with the constraint
that B-frames can only reference I/P frames (not other B-frames, since
they don't chain).

Composition / patches don't nest: applying patch A then patch B to a
reference equals applying A⊕B (XOR of bitmaps), so a patch-of-a-patch
collapses to one patch. Patches CHAIN with P-frames if the codec
commits to a canonical order — we encode `patch-after-rotation`, so the
bitmap lives in the rotated coordinate system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class FrameType(Enum):
    I = "I"
    P = "P"
    PATCH = "Patch"
    B = "B"


@dataclass
class IFrame:
    """Independent: window encoded by the underlying gt+AC codec."""
    payload: bytes  # AC output for the window's bytes
    n_bytes: int    # window size (needed for decode)


@dataclass
class PFrame:
    """V₄-rotation of a reference window."""
    ref_window_id: int
    v4_residue: str  # ∈ {e, α, β, γ}


@dataclass
class PatchFrame:
    """P-frame + sparse correction bitmap (Reed-Muller low-weight class).

    `bitmap_positions` is a list of byte-offsets within the window where
    the reference (after V₄ rotation) is wrong. `bitmap_xors` are the
    XOR-deltas to apply at those positions.

    A P-frame is `PatchFrame(.., bitmap_positions=[], bitmap_xors=[])`.
    """
    ref_window_id: int
    v4_residue: str
    bitmap_positions: List[int]
    bitmap_xors: List[int]  # same length as positions


@dataclass
class BFrame:
    """Bidirectional: function of two reference windows.

    The combining function is one rung up the Cayley-Dickson ladder
    from V₄. We encode it as (ref_back, ref_fwd, octonion_residue_idx)
    where octonion_residue_idx ∈ [0, 16) selects one of the 16
    octonion-based combinations.
    """
    ref_back_window_id: int
    ref_fwd_window_id: int
    octonion_residue: int  # ∈ [0, 16)


Frame = IFrame | PFrame | PatchFrame | BFrame


@dataclass
class EncodedStream:
    """The full stream of frame-tagged windows."""
    window_size: int   # all windows same size for first cut
    frames: List[Frame] = field(default_factory=list)

    def n_windows(self) -> int:
        return len(self.frames)


# --- Frame-tag bit costs --------------------------------------------------
# 2-bit tag per frame indicates its type (I=00, P=01, Patch=10, B=11).
# This is fixed-length to keep the parser simple. A variable-length
# Huffman over frame types could save 1-2 bits per frame on average if
# the type distribution is skewed; deferred.

FRAME_TAG_BITS = 2

V4_RESIDUE_BITS = 2  # ∈ {e, α, β, γ}, fixed 2 bits.
OCTONION_RESIDUE_BITS = 4  # 16 octonion-based combinations


def frame_cost_bits(
    frame: Frame, n_windows_so_far: int, window_size_bytes: int
) -> float:
    """Cost in bits to encode this frame given how many windows came before."""
    tag = FRAME_TAG_BITS
    if isinstance(frame, IFrame):
        return tag + len(frame.payload) * 8
    ref_bits = max(1.0, _log2(max(1, n_windows_so_far)))
    if isinstance(frame, PFrame):
        return tag + ref_bits + V4_RESIDUE_BITS
    if isinstance(frame, PatchFrame):
        # Bitmap encoding: log₂(C(W, k)) for k positions in window of W bytes.
        n_pos = len(frame.bitmap_positions)
        W = window_size_bytes
        bitmap_bits = _log2_binomial(W, n_pos) + n_pos * 8  # +8 per XOR byte
        return tag + ref_bits + V4_RESIDUE_BITS + bitmap_bits
    if isinstance(frame, BFrame):
        return tag + 2 * ref_bits + OCTONION_RESIDUE_BITS
    raise TypeError(f"unknown frame: {frame!r}")


def _log2(x: float) -> float:
    import math
    return math.log2(x)


def _log2_binomial(n: int, k: int) -> float:
    """log₂(C(n, k)) — bits to encode a k-element subset of an n-set."""
    import math
    if k == 0 or k == n:
        return 0.0
    if k < 0 or k > n:
        return float("inf")
    # log₂(n! / (k! (n-k)!)) via lgamma
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(2)
