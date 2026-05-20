"""Eliza.Octonion — 16 byte-rotations at the F₂-octonion-loop quotient.

True octonions over R/Q are non-associative (associator nonzero). Over F₂
the sign collapses (since -1 = 1), so direct CD doubling F→C→H→O over
F₂ degenerates by one F₂-axis at each step. To recover the "16 rotations"
the user's framing requires, we lift the bit-action by one F₂ explicitly:
each rotation is `(k ∈ F₂³, f ∈ F₂)` — the bit-position permutation
indexed by k, optionally followed by a bit-complement.

Group structure: (F₂³ × F₂, ⊕). 16 elements, all involutions, abelian.
This is the substrate-equivalent of the octonion-loop's `Q₁₆` at the
F₂-quotient — the structural shape the codec needs (16 distinct rotations,
group action on bytes), with the associativity that F₂ recovers for free.

Each rotation `(k, f)` acts on a byte b by:
  1. Permuting bit positions: position p → position p ⊕ k.
  2. If f = 1, XOR the result with 0xFF (bit-complement).

The 8 permutations are the F₂³ regular representation; the f bit lifts
to 16, matching the user's "cell per bit + sign flip" intuition.
"""

from __future__ import annotations

from typing import List, Tuple


def _bit_permute(byte: int, k: int) -> int:
    """Permute bit positions of a byte by XOR-k. Bit at position p moves
    to position (p ⊕ k). Bit position 0 = MSB (bit 7 of the byte value)."""
    result = 0
    for p in range(8):
        bit = (byte >> (7 - p)) & 1
        new_p = p ^ k
        result |= bit << (7 - new_p)
    return result


def _build_rotation_table() -> List[Tuple[int, int]]:
    """Materialize all 16 (k, f) rotations into a flat list of (k, f).
    Index i = (k, f) packs as i = 2*k + f, so f ∈ {0,1} is the low bit."""
    table = []
    for k in range(8):
        for f in range(2):
            table.append((k, f))
    return table


ROTATIONS: List[Tuple[int, int]] = _build_rotation_table()


def _build_rotation_lut() -> List[List[int]]:
    """For each rotation index r ∈ [0,16), a 256-entry lookup table
    mapping byte → rotated byte. Precomputed once at import."""
    lut = []
    for r in range(16):
        k, f = ROTATIONS[r]
        row = []
        for b in range(256):
            v = _bit_permute(b, k)
            if f:
                v ^= 0xFF
            row.append(v)
        lut.append(row)
    return lut


ROTATION_LUT: List[List[int]] = _build_rotation_lut()


def rotate_byte(byte: int, rotation_idx: int) -> int:
    """Apply rotation `rotation_idx ∈ [0,16)` to a single byte."""
    return ROTATION_LUT[rotation_idx][byte]


def rotate_bytes(data: bytes, rotation_idx: int) -> bytes:
    """Apply rotation to every byte of `data`."""
    lut = ROTATION_LUT[rotation_idx]
    return bytes(lut[b] for b in data)


def compose_rotations(r1: int, r2: int) -> int:
    """Compose: apply r1 then r2. Returns the rotation idx that does
    both in one step. Verifies the group law: (k1, f1) ∘ (k2, f2) =
    (k1 ⊕ k2, f1 ⊕ f2)."""
    k1, f1 = ROTATIONS[r1]
    k2, f2 = ROTATIONS[r2]
    k = k1 ^ k2
    f = f1 ^ f2
    return 2 * k + f
