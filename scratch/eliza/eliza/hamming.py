"""Eliza.Hamming — F₇ / Hamming(7, 4) sub-byte layer for the EE-arc.

Hamming(7, 4) = [7, 4, 3]: 16 codewords over 7 bits. Perfect
single-error-correcting code. Equivalent (under extension) to RM(1, 3)
which is the byte-level [8, 4, 4]. Per the substrate's F₇ / S₃ / F₂³
Sylow decomposition (per [[168-tower-as-fanout]]): Hamming(7, 4) is
the GL(3, F₂)-invariant code at length 7.

The sub-byte layer: each byte's LOW 7 BITS are read as a 7-bit
codeword; the high bit is left untouched. The mask sweep ranges
over the 16 Hamming(7, 4) codewords (or its complement set, the
weight-3 syndromes).

Per the user 2026-05-20: "hamming codes for recovery; we're living
right in their neighborhood" — F₇ at length 7 is the explicit
substrate-aligned member of the RM family.
"""

from __future__ import annotations

from typing import List, Tuple


# Canonical Hamming(7, 4) with parity-check columns equal to binary
# representations of positions 1..7:
#   H = [[0, 0, 0, 1, 1, 1, 1],     -- s_1
#        [0, 1, 1, 0, 0, 1, 1],     -- s_2
#        [1, 0, 1, 0, 1, 0, 1]]     -- s_3
# Codeword position j (1..7) is parity iff j is a power of 2: {1, 2, 4}.
# Message positions: {3, 5, 6, 7}. Syndrome ∈ [0, 8) = error position
# (1-indexed) or 0 = no error.


def encode_hamming(message: int) -> int:
    """Encode a 4-bit message into a 7-bit Hamming(7, 4) codeword.

    Message bits m₃, m₅, m₆, m₇ ∈ F₂ at codeword positions 3, 5, 6, 7.
    Parity at positions 1, 2, 4 chosen so syndromes vanish.

    `message` ∈ [0, 16) is encoded as (m₃ m₅ m₆ m₇) high-to-low.
    Returns codeword ∈ [0, 128) as 7-bit MSB-first value (position 1 = MSB).
    """
    m3 = (message >> 3) & 1
    m5 = (message >> 2) & 1
    m6 = (message >> 1) & 1
    m7 = message & 1
    c1 = m3 ^ m5 ^ m7
    c2 = m3 ^ m6 ^ m7
    c4 = m5 ^ m6 ^ m7
    return ((c1 << 6) | (c2 << 5) | (m3 << 4) |
            (c4 << 3) | (m5 << 2) | (m6 << 1) | m7)


def all_codewords_7_4() -> List[int]:
    """The 16 Hamming(7, 4) codewords as 7-bit integers."""
    return [encode_hamming(m) for m in range(16)]


def syndrome(received: int) -> int:
    """Compute the 3-bit syndrome of a 7-bit MSB-first received word.

    Codeword position j ∈ [1, 7] maps to bit (7 − j) of `received`.
    Syndrome value s ∈ [0, 8) is the 1-indexed error position
    (0 = no error), thanks to the column-equals-position layout of H.
    """
    # Bit at position j (1-indexed) = (received >> (7 - j)) & 1.
    def b(j: int) -> int:
        return (received >> (7 - j)) & 1
    s1 = b(4) ^ b(5) ^ b(6) ^ b(7)
    s2 = b(2) ^ b(3) ^ b(6) ^ b(7)
    s3 = b(1) ^ b(3) ^ b(5) ^ b(7)
    return (s1 << 2) | (s2 << 1) | s3


def correct_single_error(received: int) -> int:
    """Apply single-bit correction. The syndrome is the 1-indexed
    position of the flipped bit (or 0 if none); flip it to recover.
    """
    s = syndrome(received)
    if s == 0:
        return received
    return received ^ (1 << (7 - s))


# --- Sub-byte sweep ----------------------------------------------------


def apply_hamming_mask_low7(data: bytes, mask7: int) -> bytes:
    """XOR a 7-bit mask into the low 7 bits of every byte.

    The high bit (bit 7) is preserved. Involution.
    """
    if mask7 == 0:
        return bytes(data)
    m = mask7 & 0x7F
    return bytes(b ^ m for b in data)


def find_best_hamming_mask(
    data: bytes,
    use_complement: bool = False,
    estimator=None,
    two_stage: bool = True,
) -> Tuple[int, int]:
    """EE6: 7-bit XOR-mask sweep restricted to Hamming(7, 4) codewords.

    With `use_complement=False`: 16 codewords.
    With `use_complement=True`: 112 (= 128 - 16) non-codewords.

    Returns (best_mask_low7, weight). The mask is applied to the
    LOW 7 bits of every byte; the high bit is untouched.
    """
    if estimator is None:
        from eliza.multiscale_rotation import chain_symbol_entropy_estimator
        estimator = chain_symbol_entropy_estimator
    if not data:
        return (0, 0)
    codewords = all_codewords_7_4()
    if use_complement:
        candidates = [c for c in range(128) if c not in set(codewords)]
    else:
        candidates = codewords

    def best_in(window: bytes) -> int:
        best_m = 0
        best_score = estimator(window)
        for m in candidates:
            if m == 0:
                continue
            score = estimator(apply_hamming_mask_low7(window, m))
            if score < best_score:
                best_score = score
                best_m = m & 0x7F
        return best_m

    global_m = best_in(data)
    if not two_stage:
        return (global_m, bin(global_m).count("1"))
    half = max(1, len(data) // 2)
    first_m = best_in(data[:half])
    second_m = best_in(data[half:])
    if first_m == second_m == global_m:
        return (global_m, bin(global_m).count("1"))
    return (0, 0)


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. All-zero message encodes to all-zero codeword.
    if encode_hamming(0) != 0:
        if verbose:
            print(f"FAIL: encode(0) ≠ 0")
        ok = False

    # 2. All 16 codewords have syndrome 0.
    for c in all_codewords_7_4():
        if syndrome(c) != 0:
            if verbose:
                print(f"FAIL: codeword {c:07b} has nonzero syndrome")
            ok = False

    # 3. Single-bit flips produce nonzero syndromes that correct.
    base = encode_hamming(0b1011)
    for pos in range(7):
        flipped = base ^ (1 << pos)
        corrected = correct_single_error(flipped)
        if corrected != base:
            if verbose:
                print(f"FAIL: correction at pos {pos} produced {corrected:07b}")
            ok = False

    # 4. Hamming mask application is involution.
    data = bytes(range(64))
    for m in (0x00, 0x12, 0x55, 0x7F):
        twice = apply_hamming_mask_low7(apply_hamming_mask_low7(data, m), m)
        if twice != data:
            if verbose:
                print(f"FAIL: Hamming mask {m:07b} not involution")
            ok = False

    # 5. find_best_hamming_mask returns a codeword (or 0).
    data = bytes((i * 7) & 0xFF for i in range(256))
    m, w = find_best_hamming_mask(data)
    cws = set(all_codewords_7_4())
    if m != 0 and m not in cws:
        if verbose:
            print(f"FAIL: best mask {m:07b} not a Hamming codeword")
        ok = False

    # 6. Codewords have minimum distance 3.
    cws = all_codewords_7_4()
    min_d = 7
    for i in range(len(cws)):
        for j in range(i + 1, len(cws)):
            d = bin(cws[i] ^ cws[j]).count("1")
            if d < min_d:
                min_d = d
    if min_d != 3:
        if verbose:
            print(f"FAIL: min distance {min_d} ≠ 3")
        ok = False

    if verbose:
        print(f"hamming self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
