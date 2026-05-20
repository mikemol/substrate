"""Eliza.FrameCodecCrumb — variable-frame codec at CRUMB granularity.

V₄ rotation is the substrate-natural action at the 2-bit-crumb scale.
A crumb is a V₄ element; V₄ rotation is XOR with a V₄ index.

At crumb granularity, ASCII text has structure: the top crumb of every
byte (bits 6–7) is `01` for letters or `00` for control/punctuation —
i.e., it's a 1-of-2 V₄ pattern at a fixed sub-byte position. Byte-level
codecs can't see this. Crumb-level can.

Frame types parallel `eliza.frames`, but windows are in crumbs.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from eliza.arith import RangeEncoder
from eliza.codec import encode_crumbs


@dataclass
class CrumbIFrame:
    payload: bytes
    n_crumbs: int


@dataclass
class CrumbPFrame:
    ref_window_id: int
    v4_residue: int  # ∈ [0, 4)


@dataclass
class CrumbPatchFrame:
    ref_window_id: int
    v4_residue: int
    bitmap_positions: List[int]   # crumb indices within window
    bitmap_xors: List[int]        # XOR delta, ∈ [0, 4)


CrumbFrame = CrumbIFrame | CrumbPFrame | CrumbPatchFrame


def v4_rotate_crumbs(crumbs: List[int], residue: int) -> List[int]:
    """Apply V₄ XOR uniformly across all crumbs."""
    return [c ^ residue for c in crumbs]


def best_crumb_patch_frame(
    window: List[int],
    references: List[List[int]],
    max_patches: int,
) -> Optional[CrumbPatchFrame]:
    """Find the (reference, residue) with smallest crumb-mismatch count.
    Returns the best PatchFrame or None if no reference fits length-wise
    or all exceed max_patches."""
    best: Optional[Tuple[int, int, List[int], List[int]]] = None
    best_n = max_patches + 1
    W = len(window)
    for ref_id, ref in enumerate(references):
        if len(ref) != W:
            continue
        for residue in range(4):
            positions: List[int] = []
            xors: List[int] = []
            for i in range(W):
                d = window[i] ^ (ref[i] ^ residue)
                if d != 0:
                    positions.append(i)
                    xors.append(d)
                if len(positions) >= best_n:
                    break
            if len(positions) < best_n:
                best = (ref_id, residue, positions, xors)
                best_n = len(positions)
                if best_n == 0:
                    return CrumbPatchFrame(
                        ref_window_id=ref_id,
                        v4_residue=residue,
                        bitmap_positions=[],
                        bitmap_xors=[],
                    )
    if best is None or best_n > max_patches:
        return None
    ref_id, residue, positions, xors = best
    return CrumbPatchFrame(
        ref_window_id=ref_id,
        v4_residue=residue,
        bitmap_positions=positions,
        bitmap_xors=xors,
    )


def _log2(x: float) -> float:
    import math
    return math.log2(x)


def _log2_binomial(n: int, k: int) -> float:
    import math
    if k <= 0 or k >= n:
        return 0.0
    return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)) / math.log(2)


FRAME_TAG_BITS = 2     # I=00, P=01, Patch=10, (reserved=11)
V4_RESIDUE_BITS = 2


def crumb_frame_cost(
    frame: CrumbFrame, n_windows_so_far: int, window_size_crumbs: int
) -> float:
    tag = FRAME_TAG_BITS
    if isinstance(frame, CrumbIFrame):
        return tag + len(frame.payload) * 8
    ref_bits = max(1.0, _log2(max(1, n_windows_so_far)))
    if isinstance(frame, CrumbPFrame):
        return tag + ref_bits + V4_RESIDUE_BITS
    if isinstance(frame, CrumbPatchFrame):
        n_pos = len(frame.bitmap_positions)
        W = window_size_crumbs
        # Each XOR is a V₄ index (2 bits).
        bitmap_bits = _log2_binomial(W, n_pos) + n_pos * 2
        return tag + ref_bits + V4_RESIDUE_BITS + bitmap_bits
    raise TypeError(f"unknown crumb frame: {frame!r}")


def encode_crumb_i_frame(window: List[int]) -> CrumbIFrame:
    payload = encode_crumbs(window, vocab_size=4)
    return CrumbIFrame(payload=payload, n_crumbs=len(window))


def choose_crumb_frame(
    window: List[int],
    references: List[List[int]],
    window_size_crumbs: int,
    n_windows_so_far: int,
    max_patches: int,
) -> CrumbFrame:
    i_frame = encode_crumb_i_frame(window)
    best: CrumbFrame = i_frame
    best_cost = crumb_frame_cost(i_frame, n_windows_so_far, window_size_crumbs)
    patch = best_crumb_patch_frame(window, references, max_patches=max_patches)
    if patch is not None:
        if len(patch.bitmap_positions) == 0:
            p = CrumbPFrame(
                ref_window_id=patch.ref_window_id,
                v4_residue=patch.v4_residue,
            )
            c = crumb_frame_cost(p, n_windows_so_far, window_size_crumbs)
            if c < best_cost:
                best, best_cost = p, c
        else:
            c = crumb_frame_cost(patch, n_windows_so_far, window_size_crumbs)
            if c < best_cost:
                best, best_cost = patch, c
    return best


def encode_crumb_stream(
    crumbs: List[int],
    window_size: int = 1024,  # crumbs per window
    max_patches: int = 64,
) -> Tuple[List[CrumbFrame], float, Counter]:
    """Partition the crumb stream into fixed-size windows, encode each
    as the cheapest frame. Returns (frames, total_bits, type_counter)."""
    windows: List[List[int]] = []
    for start in range(0, len(crumbs), window_size):
        w = crumbs[start:start + window_size]
        if w:
            windows.append(w)
    frames: List[CrumbFrame] = []
    references: List[List[int]] = []
    total = 0.0
    for w in windows:
        f = choose_crumb_frame(
            w, references, window_size, len(frames), max_patches=max_patches
        )
        frames.append(f)
        total += crumb_frame_cost(f, len(frames) - 1, window_size)
        references.append(w)
    counts = Counter(type(f).__name__ for f in frames)
    return frames, total, counts
