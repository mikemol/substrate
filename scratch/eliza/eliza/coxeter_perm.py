"""Eliza.CoxeterPerm — adjacent-transposition Coxeter words for S_{2ⁿ}.

CC-arc runtime per [[octonion-loop-expressivity-limit]]: the F₂ⁿ × F₂
group from BB-arc covers only 2^(n+1) of (2ⁿ)! bit permutations.
S_{2ⁿ} via adjacent transpositions reaches ALL bit permutations.

Coxeter generators at scale n (bit-width 2ⁿ):
  s_i  = swap of bit positions (i, i+1) for i ∈ [0, 2ⁿ-1)

Relations:
  sᵢ² = 1                          [involution]
  sᵢsⱼ = sⱼsᵢ for |i - j| ≥ 2      [commutation]
  sᵢsᵢ₊₁sᵢ = sᵢ₊₁sᵢsᵢ₊₁              [braid]

A Coxeter word is a list of generator indices; word multiplication is
list concatenation (modulo relations for reduction, which we don't
enforce — encoder may emit non-reduced words; decoder still applies
them correctly).

The action on a bit_width-bit value applies each generator left to
right.
"""

from __future__ import annotations

from typing import List


def apply_adjacent_transposition(value: int, bit_width: int, i: int) -> int:
    """Swap bits at positions (i, i+1) in a bit_width-bit value.

    Position 0 = MSB; position bit_width-1 = LSB. `i` must be in
    [0, bit_width-1). Returns the bit-swapped value.
    """
    if i < 0 or i + 1 >= bit_width:
        return value
    msb_i = bit_width - 1 - i
    msb_j = bit_width - 1 - (i + 1)
    bit_i = (value >> msb_i) & 1
    bit_j = (value >> msb_j) & 1
    if bit_i != bit_j:
        mask = (1 << msb_i) | (1 << msb_j)
        return value ^ mask
    return value


def apply_coxeter_word(value: int, bit_width: int,
                          word: List[int]) -> int:
    """Apply a Coxeter word (sequence of generator indices) to a value."""
    for i in word:
        value = apply_adjacent_transposition(value, bit_width, i)
    return value


def invert_coxeter_word(word: List[int]) -> List[int]:
    """Inverse of a Coxeter word: reverse the generator sequence.

    Each generator is an involution, so inverse of (sᵢ₁ sᵢ₂ ... sᵢₖ)
    is (sᵢₖ ... sᵢ₂ sᵢ₁).
    """
    return list(reversed(word))


def apply_coxeter_word_to_bytes(data: bytes, scale: int,
                                  word: List[int]) -> bytes:
    """Apply a Coxeter word at the given scale to a byte stream.

    scale ∈ [0, 5]; bit_width = 1 << scale (1, 2, 4, 8, 16, 32).
    """
    if scale == 0:
        # 1-bit width: no swaps possible. Word is essentially ignored.
        return bytes(data)
    bit_width = 1 << scale
    if bit_width == 8:
        return bytes(apply_coxeter_word(b, 8, word) for b in data)
    if bit_width == 4:
        out = bytearray(len(data))
        for i, byte in enumerate(data):
            hi = apply_coxeter_word((byte >> 4) & 0xF, 4, word)
            lo = apply_coxeter_word(byte & 0xF, 4, word)
            out[i] = (hi << 4) | lo
        return bytes(out)
    if bit_width == 2:
        out = bytearray(len(data))
        for i, byte in enumerate(data):
            new_byte = 0
            for c in range(4):
                crumb = (byte >> (6 - 2 * c)) & 0b11
                new_byte |= apply_coxeter_word(crumb, 2, word) << (6 - 2 * c)
            out[i] = new_byte
        return bytes(out)
    if bit_width == 16:
        pad = len(data) % 2
        padded = data + b"\x00" * pad
        out = bytearray(len(padded))
        for i in range(0, len(padded), 2):
            word_val = (padded[i] << 8) | padded[i + 1]
            new_word = apply_coxeter_word(word_val, 16, word)
            out[i] = (new_word >> 8) & 0xFF
            out[i + 1] = new_word & 0xFF
        return bytes(out[:len(data)])
    if bit_width == 32:
        pad = (-len(data)) % 4
        padded = data + b"\x00" * pad
        out = bytearray(len(padded))
        for i in range(0, len(padded), 4):
            dword = ((padded[i] << 24) | (padded[i + 1] << 16)
                     | (padded[i + 2] << 8) | padded[i + 3])
            new_dword = apply_coxeter_word(dword, 32, word)
            out[i] = (new_dword >> 24) & 0xFF
            out[i + 1] = (new_dword >> 16) & 0xFF
            out[i + 2] = (new_dword >> 8) & 0xFF
            out[i + 3] = new_dword & 0xFF
        return bytes(out[:len(data)])
    raise NotImplementedError(f"scale {scale} not yet supported")


def involution_check(scale: int, word: List[int]) -> bool:
    """Verify (word ∘ word⁻¹) acts as identity on a sample.

    Word's inverse is the reverse-sequence application; composed, the
    pair should act as identity.
    """
    data = bytes(range(min(64, 1 << (1 << scale))))
    once = apply_coxeter_word_to_bytes(data, scale, word)
    inv = invert_coxeter_word(word)
    back = apply_coxeter_word_to_bytes(once, scale, inv)
    return data == back


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    """Verify Coxeter word + inverse round-trips at multiple scales."""
    ok = True
    test_words = [
        [],            # identity
        [0],           # single swap of positions 0,1
        [0, 2],        # commuting pair
        [0, 1, 0],     # braid: should equal [1, 0, 1]
        [1, 0, 2, 1],  # longer word
    ]
    for scale in (1, 2, 3, 4):
        bw = 1 << scale
        for word in test_words:
            # Skip generators out of range for small scales.
            if word and max(word) + 1 >= bw:
                continue
            if not involution_check(scale, word):
                if verbose:
                    print(f"FAIL: scale={scale}, word={word}")
                ok = False
        if verbose:
            print(f"scale={scale} bit_width={bw}  {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
