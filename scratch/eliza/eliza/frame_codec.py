"""Eliza.FrameCodec — encode/decode windows as I/P/Patch/B frames.

Per-byte V₄ rotation is XOR with a mask derived from the residue:

  e (00) -> 0x00 (no change)
  α (01) -> 0x55 (every-other-bit, low bit of each crumb)
  β (10) -> 0xAA (every-other-bit, high bit of each crumb)
  γ (11) -> 0xFF (bit-complement)

This is the V₄ action on bytes-as-4-crumbs by left-translation in F₂²
applied to each crumb in parallel.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from eliza.codec import encode as binary_encode
from eliza.frames import (
    BFrame,
    EncodedStream,
    FRAME_TAG_BITS,
    Frame,
    IFrame,
    PFrame,
    PatchFrame,
    frame_cost_bits,
)


V4_BYTE_MASKS = {
    "e": 0x00,
    "α": 0x55,
    "β": 0xAA,
    "γ": 0xFF,
}


def v4_rotate_bytes(data: bytes, residue: str) -> bytes:
    """Apply the V₄ residue's byte mask: byte XOR mask, broadcast."""
    mask = V4_BYTE_MASKS[residue]
    return bytes(b ^ mask for b in data)


def try_p_frame(window: bytes, references: List[bytes]) -> Optional[PFrame]:
    """If `window` equals a V₄-rotation of any reference, return a P-frame.
    Otherwise None."""
    for ref_id, ref in enumerate(references):
        if len(ref) != len(window):
            continue
        for residue in ("e", "α", "β", "γ"):
            if v4_rotate_bytes(ref, residue) == window:
                return PFrame(ref_window_id=ref_id, v4_residue=residue)
    return None


def best_patch_frame(
    window: bytes, references: List[bytes], max_patches: int = 8
) -> Optional[PatchFrame]:
    """Find the (reference, residue) that minimizes patch positions.
    Returns a PatchFrame with the smallest bitmap. None if no reference
    matches the window's length."""
    best: Optional[Tuple[int, str, List[int], List[int]]] = None
    best_n = max_patches + 1
    for ref_id, ref in enumerate(references):
        if len(ref) != len(window):
            continue
        for residue in ("e", "α", "β", "γ"):
            rotated = v4_rotate_bytes(ref, residue)
            positions = []
            xors = []
            for i in range(len(window)):
                d = window[i] ^ rotated[i]
                if d != 0:
                    positions.append(i)
                    xors.append(d)
                if len(positions) >= best_n:
                    break
            if len(positions) < best_n:
                best = (ref_id, residue, positions, xors)
                best_n = len(positions)
                if best_n == 0:
                    return PatchFrame(
                        ref_window_id=ref_id,
                        v4_residue=residue,
                        bitmap_positions=[],
                        bitmap_xors=[],
                    )
    if best is None or best_n > max_patches:
        return None
    ref_id, residue, positions, xors = best
    return PatchFrame(
        ref_window_id=ref_id,
        v4_residue=residue,
        bitmap_positions=positions,
        bitmap_xors=xors,
    )


def encode_i_frame(window: bytes) -> IFrame:
    """Encode a window as an I-frame using the underlying binary codec."""
    payload = binary_encode(window, vocab_size=256)
    return IFrame(payload=payload, n_bytes=len(window))


def choose_frame(
    window: bytes,
    references: List[bytes],
    window_size_bytes: int,
    n_windows_so_far: int,
    max_patches: int = 16,
) -> Frame:
    """Pick the cheapest frame for this window. I-frame is always
    available; P/Patch require matching references."""
    # I-frame baseline.
    i_frame = encode_i_frame(window)
    best_frame: Frame = i_frame
    best_cost = frame_cost_bits(i_frame, n_windows_so_far, window_size_bytes)
    # Try P / Patch.
    patch = best_patch_frame(window, references, max_patches=max_patches)
    if patch is not None:
        if len(patch.bitmap_positions) == 0:
            p = PFrame(
                ref_window_id=patch.ref_window_id,
                v4_residue=patch.v4_residue,
            )
            p_cost = frame_cost_bits(p, n_windows_so_far, window_size_bytes)
            if p_cost < best_cost:
                best_frame, best_cost = p, p_cost
        else:
            patch_cost = frame_cost_bits(patch, n_windows_so_far, window_size_bytes)
            if patch_cost < best_cost:
                best_frame, best_cost = patch, patch_cost
    return best_frame


def try_b_frame(
    window: bytes, references: List[bytes]
) -> Optional[BFrame]:
    """B-frame stub: bidirectional reference. Find two past references
    whose pointwise XOR (after V₄-rotation pair) closest matches the
    window. The 'octonion residue' indexes the (residue_back, residue_fwd)
    pair × an extra bit for which way to combine.

    For the first cut we use only `ref_b XOR ref_f == window` as the
    combination — i.e., octonion_residue=0 (pure XOR). Higher rungs of
    the CD ladder would add associativity-sacrificing combinations.
    Returns the first ref pair found, or None.
    """
    n = len(references)
    if n < 2:
        return None
    for i in range(n - 1, -1, -1):
        for j in range(i):
            ri, rj = references[i], references[j]
            if len(ri) != len(window) or len(rj) != len(window):
                continue
            combined = bytes(a ^ b for a, b in zip(ri, rj))
            if combined == window:
                return BFrame(
                    ref_back_window_id=j,
                    ref_fwd_window_id=i,
                    octonion_residue=0,
                )
    return None


def encode_stream(
    data: bytes, window_size: int = 256, max_patches: int = 16,
    try_b: bool = True,
) -> Tuple[EncodedStream, float]:
    """Partition data into fixed-size windows, encode each as the best
    frame. Returns (EncodedStream, total_bits)."""
    n = len(data)
    windows_raw: List[bytes] = []
    for start in range(0, n, window_size):
        windows_raw.append(data[start:start + window_size])
    stream = EncodedStream(window_size=window_size, frames=[])
    references: List[bytes] = []
    total_bits = 0.0
    for w in windows_raw:
        frame = choose_frame(
            w, references, window_size, len(stream.frames), max_patches=max_patches
        )
        # B-frame: only consider if Patch was the best so far (since
        # B-frames are more expensive per tag).
        if try_b and not isinstance(frame, IFrame):
            b = try_b_frame(w, references)
            if b is not None:
                b_cost = frame_cost_bits(b, len(stream.frames), window_size)
                cur_cost = frame_cost_bits(frame, len(stream.frames), window_size)
                if b_cost < cur_cost:
                    frame = b
        stream.frames.append(frame)
        total_bits += frame_cost_bits(frame, len(stream.frames) - 1, window_size)
        references.append(w)
    return stream, total_bits
