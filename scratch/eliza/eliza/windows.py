"""Eliza.Windows — natural window boundaries via V₄ chamber closure.

A V₄-closure point is a position where the cumulative XOR of all crumbs
seen so far equals identity (e = 0). At such a point the chamber-walk
state returns to origin, marking a structural seam in the input.

For a bit stream interpreted as sliding-stride-1 crumbs (each crumb =
(prev_bit, new_bit) ∈ V₄), closure points occur whenever the running
XOR of crumb-as-integer is 0.

Windows are the runs between consecutive closure points. The first
window starts at the stream's beginning; the last ends at the stream's
end (possibly without a final closure).
"""

from __future__ import annotations

from typing import Iterable, List, Tuple


def crumb_stream(data: bytes) -> Iterable[int]:
    """Yield 2-bit sliding-window crumbs over the input bits. N input
    bits yield N-1 crumbs."""
    prev: int | None = None
    for byte in data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            if prev is not None:
                yield (prev << 1) | bit
            prev = bit


def closure_positions(data: bytes) -> List[int]:
    """Positions (1-indexed; counts from start) where the cumulative
    XOR of crumb values is 0. Each position is the crumb-index AFTER
    the XOR returns to 0 — i.e., the start of the NEXT window."""
    positions: List[int] = []
    cum = 0
    for i, crumb in enumerate(crumb_stream(data)):
        cum ^= crumb
        if cum == 0:
            # Position i+1 = number of crumbs consumed when XOR returns to 0.
            positions.append(i + 1)
    return positions


def windows_from_closures(
    data: bytes,
    min_size_bytes: int = 16,
    max_size_bytes: int = 4096,
) -> List[Tuple[int, int]]:
    """Partition `data` into windows on byte boundaries closest to V₄-
    closure points. Returns list of (start_byte, end_byte) tuples.

    Honors min/max window sizes: closures producing too-small windows
    are merged into the next; runs without closure for max_size_bytes
    are force-split.
    """
    n_bytes = len(data)
    closures_crumbs = closure_positions(data)
    # Convert crumb-positions to byte-positions: crumb i covers bits
    # (i, i+1), so crumb-position k corresponds to bit-position k+1,
    # i.e., byte-position (k+1) / 8.
    closure_bytes = sorted(set(
        (k + 1) // 8 for k in closures_crumbs if (k + 1) % 8 == 0
    ))

    windows: List[Tuple[int, int]] = []
    start = 0
    while start < n_bytes:
        # Pick the next boundary: closest closure ≥ start + min_size, but
        # capped at start + max_size.
        candidates = [b for b in closure_bytes if start + min_size_bytes <= b <= start + max_size_bytes]
        if candidates:
            end = candidates[0]
        else:
            end = min(start + max_size_bytes, n_bytes)
        if end <= start:
            end = min(start + min_size_bytes, n_bytes)
        if end > n_bytes:
            end = n_bytes
        if end <= start:
            break
        windows.append((start, end))
        start = end
    return windows
