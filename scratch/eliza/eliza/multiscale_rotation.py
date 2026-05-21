"""Eliza.MultiscaleRotation — Cayley-Dickson rotation family.

Generalises eliza/octonion.py from byte-only to all scales n ∈ ℕ.
Per [[choice-rigidification-in-substrate]]: hardcoding "byte" was a
rigidification of the scale gauge; this module exposes the scale.

  scale n: bit-width 2^n, group F₂^n × F₂ (size 2^(n+1))

    n = 0:   1-bit  units, group  F₂ × F₂ = 2 elements
    n = 1:   2-bit  crumbs, group F₂² × F₂ = 4 elements
    n = 2:   4-bit  nibbles, group F₂³ × F₂ = 8 elements
    n = 3:   8-bit  bytes, group F₂⁴ × F₂ = 16 elements (= octonion.py)
    n = 4:  16-bit  words, group F₂⁵ × F₂ = 32 elements
    n = 5:  32-bit  dwords, group F₂⁶ × F₂ = 64 elements

Each rotation `(k ∈ F₂ⁿ, f ∈ F₂)` acts on a 2ⁿ-bit value:
  1. Permute bit positions: position p → position p ⊕ k.
  2. If f = 1, XOR with all-ones mask (bit-complement).

All rotations are involutions (self-inverse).

Per [[3plus1-parity-universal]]: at every scale n, the (n-axis ×
1-binding) structure realises the substrate's universal pattern —
n bit-permutation axes plus one chirality F₂.

Per [[expose-generator-not-orbit]]: scale IS the previously-hidden
generator; (k, f) at fixed scale was the orbit point. The
generator is now first-class.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def _bit_permute_single(value: int, bit_width: int, k: int) -> int:
    """Permute bit positions of a `bit_width`-bit value by XOR-k.

    Bit at position p (where position 0 is MSB) moves to position p ⊕ k.
    """
    if bit_width <= 0:
        return value
    result = 0
    for p in range(bit_width):
        bit = (value >> (bit_width - 1 - p)) & 1
        new_p = p ^ k
        result |= bit << (bit_width - 1 - new_p)
    return result


def apply_rotation(value: int, scale: int, k: int, f: int) -> int:
    """Apply (k ∈ F₂^scale, f ∈ F₂) at scale n.

    bit_width = 1 << scale. k must be < bit_width. f ∈ {0, 1}.
    All rotations are involutions: apply_rotation(apply_rotation(v) ) = v.
    """
    if scale == 0:
        # 1-bit width: k must be 0 (F₂⁰ is trivial). Just chirality.
        return (value & 1) ^ (f & 1)
    bit_width = 1 << scale
    permuted = _bit_permute_single(value, bit_width, k % bit_width)
    if f:
        permuted ^= (1 << bit_width) - 1
    return permuted


# --- Precomputed lookup tables for the most common scales -------------

_TABLE_CACHE: dict = {}


def _get_table(scale: int) -> np.ndarray:
    """Cached lookup table TBL[k, f, value] = rotated value at scale.

    Shape: (1 << scale, 2, 1 << (1 << scale)) for scale <= 3 (fits in
    memory). For higher scales we compute on demand.
    """
    if scale in _TABLE_CACHE:
        return _TABLE_CACHE[scale]
    bit_width = 1 << scale
    n_values = 1 << bit_width
    table = np.zeros((bit_width if bit_width > 0 else 1, 2, n_values),
                       dtype=np.int64)
    for k in range(bit_width if bit_width > 0 else 1):
        for f in range(2):
            for v in range(n_values):
                table[k, f, v] = apply_rotation(v, scale, k, f)
    _TABLE_CACHE[scale] = table
    return table


# --- Stream-level application -----------------------------------------


def apply_rotation_to_bytes(data: bytes, scale: int, k: int, f: int) -> bytes:
    """Apply rotation at the given scale to a byte stream.

    For scale ∈ [0, 3]: operates on bit/crumb/nibble/byte units within
    each byte. For scale=4: operates on 16-bit words (pads to even
    length if needed). Higher scales follow the same pattern but use
    larger units.

    Involution: apply_rotation_to_bytes(apply_rotation_to_bytes(data)) = data.
    """
    if scale == 0:
        # 1-bit units. k=0 only; f flips every bit.
        if not f:
            return bytes(data)
        return bytes(b ^ 0xFF for b in data)
    if scale == 1:
        # 2-bit crumbs (4 per byte).
        out = bytearray(len(data))
        table = _get_table(1)   # (2, 2, 4)
        for i, byte in enumerate(data):
            new_byte = 0
            for c in range(4):
                crumb = (byte >> (6 - 2 * c)) & 0b11
                rotated = int(table[k % 2, f & 1, crumb])
                new_byte |= rotated << (6 - 2 * c)
            out[i] = new_byte
        return bytes(out)
    if scale == 2:
        # 4-bit nibbles (2 per byte).
        out = bytearray(len(data))
        table = _get_table(2)   # (4, 2, 16)
        for i, byte in enumerate(data):
            hi = (byte >> 4) & 0xF
            lo = byte & 0xF
            new_hi = int(table[k % 4, f & 1, hi])
            new_lo = int(table[k % 4, f & 1, lo])
            out[i] = (new_hi << 4) | new_lo
        return bytes(out)
    if scale == 3:
        # 8-bit bytes (1 per byte).
        table = _get_table(3)   # (8, 2, 256)
        return bytes(int(table[k % 8, f & 1, b]) for b in data)
    if scale == 4:
        # 16-bit words. Pad to even.
        padded = data + (b"\x00" if len(data) % 2 else b"")
        out = bytearray(len(padded))
        for i in range(0, len(padded), 2):
            word = (padded[i] << 8) | padded[i + 1]
            rotated = apply_rotation(word, 4, k, f)
            out[i] = (rotated >> 8) & 0xFF
            out[i + 1] = rotated & 0xFF
        # Trim back to original length.
        return bytes(out[:len(data)])
    if scale == 5:
        # 32-bit dwords. Pad to mod 4.
        pad = (-len(data)) % 4
        padded = data + b"\x00" * pad
        out = bytearray(len(padded))
        for i in range(0, len(padded), 4):
            dword = ((padded[i] << 24) | (padded[i + 1] << 16)
                     | (padded[i + 2] << 8) | padded[i + 3])
            rotated = apply_rotation(dword, 5, k, f)
            out[i] = (rotated >> 24) & 0xFF
            out[i + 1] = (rotated >> 16) & 0xFF
            out[i + 2] = (rotated >> 8) & 0xFF
            out[i + 3] = rotated & 0xFF
        return bytes(out[:len(data)])
    raise NotImplementedError(f"scale {scale} not yet implemented")


# --- Validation helpers ------------------------------------------------


def is_involution(scale: int, k: int, f: int) -> bool:
    """Verify that double-application of a rotation returns the identity."""
    data = bytes(range(256))
    once = apply_rotation_to_bytes(data, scale, k, f)
    twice = apply_rotation_to_bytes(once, scale, k, f)
    return data == twice


# --- Group-element enumeration -----------------------------------------


def n_rotations(scale: int) -> int:
    """|F₂ⁿ × F₂| at scale n = 2^(n+1)."""
    if scale == 0:
        return 2
    return (1 << scale) * 2


def all_rotations(scale: int):
    """Iterator over all (k, f) at the given scale."""
    bit_width = 1 << scale if scale > 0 else 1
    for k in range(bit_width):
        for f in range(2):
            yield (k, f)


# --- BB5+BB6: per-block rotation with auto-speculation ----------------


def find_best_rotation_for_block(block: bytes, scale: int,
                                    bpb_estimator) -> tuple:
    """BB6: search (k, f) at the given scale; return (k, f, score)
    where lowest score wins.

    `bpb_estimator(rotated_bytes) → float` is the cost estimator
    (cheaper estimator → faster search; only needs to be ordinally
    comparable, not absolute).
    """
    bit_width = 1 << scale if scale > 0 else 1
    best_k = 0
    best_f = 0
    best_score = bpb_estimator(block)
    for k in range(bit_width):
        for f in range(2):
            if k == 0 and f == 0:
                continue   # already measured
            rotated = apply_rotation_to_bytes(block, scale, k, f)
            score = bpb_estimator(rotated)
            if score < best_score:
                best_score = score
                best_k = k
                best_f = f
    return (best_k, best_f, best_score)


def byte_entropy_estimator(data: bytes) -> float:
    """LEGACY (BB-arc): byte-frequency entropy. RIGIDIFIES scale to
    bytes per [[octonion-loop-expressivity-limit]] — use
    `chain_symbol_entropy_estimator` for substrate-aligned estimation.
    """
    if not data:
        return 0.0
    import math
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / n
            h -= p * math.log2(p)
    return h


def chain_symbol_entropy_estimator(data: bytes) -> float:
    """CC1: scale-agnostic entropy estimator using the codec's
    chain-symbol distribution.

    Performs the chamber walk on `data` and histograms the 24
    chain-symbol (S₄ chamber) outputs. Lower entropy → more
    compressible under the codec's actual cost function (which
    operates on chain symbols, not bytes).

    Per the user's audit: replaces byte_entropy_estimator's
    scale=3 rigidification with the codec's natural granularity.
    """
    if not data:
        return 0.0
    import math
    from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose
    from eliza.matrix_ops import _manifold_index
    chambers, idx_map = _manifold_index()
    counts = [0] * len(chambers)
    state = ORIGIN
    for byte in data:
        for nibble in ((byte >> 4) & 0xF, byte & 0xF):
            state = perm_compose(state, NIBBLE_TO_PERM[nibble])
            counts[idx_map[state]] += 1
    n = sum(counts)
    if n == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / n
            h -= p * math.log2(p)
    return h


def apply_block_rotations(data: bytes, block_size: int,
                           rotations: list) -> bytes:
    """Apply per-block rotations to a byte stream.

    `rotations` is a list of (scale, k, f) tuples, one per block.
    If shorter than the number of blocks, the LAST entry is reused.
    """
    out = bytearray()
    for i, block_start in enumerate(range(0, len(data), block_size)):
        block = data[block_start:block_start + block_size]
        rot = rotations[min(i, len(rotations) - 1)]
        rotated = apply_rotation_to_bytes(block, rot[0], rot[1], rot[2])
        out.extend(rotated)
    return bytes(out)


def speculate_block_rotations(data: bytes, block_size: int,
                                scale: int,
                                estimator=None) -> list:
    """BB6 auto-speculation: per block, find the best rotation at the
    given scale; return list of (scale, k, f).

    The estimator defaults to `chain_symbol_entropy_estimator` (CC1)
    which uses the codec's natural granularity. The legacy
    `byte_entropy_estimator` can be passed explicitly for the BB-arc
    behaviour but is structurally rigidified to scale=3.
    """
    if estimator is None:
        estimator = chain_symbol_entropy_estimator
    rotations = []
    for block_start in range(0, len(data), block_size):
        block = data[block_start:block_start + block_size]
        k, f, _ = find_best_rotation_for_block(block, scale, estimator)
        rotations.append((scale, k, f))
    return rotations


# --- CC6: Stream-level bit shift (Z/8 group) --------------------------


def bitshift_stream_left(data: bytes, shift: int) -> bytes:
    """CYCLIC left-shift of the whole byte stream by `shift` bits.

    Treats `data` as a single big-endian bit sequence of length 8n;
    rotates by `shift` positions, with the top bits wrapping to the
    end of the stream. Lossless under matched right-shift inverse.

    A non-cyclic left-shift would drop the top `shift` bits of
    `data[0]` — fix per CC7 sweep round-trip failures on text corpora.
    """
    shift = shift % 8
    if shift == 0:
        return bytes(data)
    n = len(data)
    if n == 0:
        return data
    out = bytearray(n)
    for i in range(n):
        hi = (data[i] << shift) & 0xFF
        lo = data[(i + 1) % n] >> (8 - shift)
        out[i] = hi | lo
    return bytes(out)


def bitshift_stream_right(data: bytes, shift: int) -> bytes:
    """CYCLIC right-shift; inverse of `bitshift_stream_left`.

    The Z/8 group action is cyclic; left and right are paired
    inverses.
    """
    shift = shift % 8
    if shift == 0:
        return bytes(data)
    n = len(data)
    if n == 0:
        return data
    out = bytearray(n)
    for i in range(n):
        lo = data[i] >> shift
        hi = (data[(i - 1) % n] << (8 - shift)) & 0xFF
        out[i] = lo | hi
    return bytes(out)


def bitshift_stream(data: bytes, shift: int) -> bytes:
    """Convenience: encoder-side left shift. Use bitshift_stream_right
    for the matching decoder-side inverse.
    """
    return bitshift_stream_left(data, shift)


def find_best_bit_shift(data: bytes, estimator=None) -> int:
    """CC8: find the bit shift ∈ [0, 8) that minimises the estimator.

    Defaults to `chain_symbol_entropy_estimator` (substrate-aligned)
    per CC1. Returns the best shift index.
    """
    if estimator is None:
        estimator = chain_symbol_entropy_estimator
    best_shift = 0
    best_score = estimator(data)
    for s in range(1, 8):
        shifted = bitshift_stream_left(data, s)
        score = estimator(shifted)
        if score < best_score:
            best_score = score
            best_shift = s
    return best_shift


def speculate_block_rotations_with_inertia(data: bytes, block_size: int,
                                              scale: int,
                                              inertia_margin: float = 0.05,
                                              estimator=None) -> list:
    """CC5: per-block rotation auto-speculation with inertia.

    Same as `speculate_block_rotations` but the encoder REFUSES to
    switch rotation unless the new rotation's score is BETTER than
    the current rotation's score by ≥ `inertia_margin`. Reduces
    rotation-table overhead by amortising across runs.
    """
    if estimator is None:
        estimator = chain_symbol_entropy_estimator
    rotations = []
    current_rot = None
    for block_start in range(0, len(data), block_size):
        block = data[block_start:block_start + block_size]
        candidate_k, candidate_f, candidate_score = find_best_rotation_for_block(
            block, scale, estimator)
        if current_rot is None:
            current_rot = (scale, candidate_k, candidate_f)
            rotations.append(current_rot)
            continue
        # Compare candidate to current.
        current_score = estimator(
            apply_rotation_to_bytes(
                block, current_rot[0], current_rot[1], current_rot[2]))
        if candidate_score < current_score - inertia_margin:
            current_rot = (scale, candidate_k, candidate_f)
        rotations.append(current_rot)
    return rotations


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    """Verify involution property + round-trip across all scales 0-5."""
    ok = True
    for scale in range(6):
        for k, f in all_rotations(scale):
            if not is_involution(scale, k, f):
                if verbose:
                    print(f"FAIL: scale={scale}, k={k}, f={f} not involution")
                ok = False
                break
        if verbose:
            print(f"scale={scale} bit_width={1<<scale if scale>0 else 1} "
                  f"n_rotations={n_rotations(scale)}  "
                  f"{'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
