"""Eliza.Recovery — Clifford / Hamming recovery operators for the EE-arc.

Runtime realisation of DD9's `CliffordRecovery n` record:
  recover : Word → Multivector → Word
  recovery-law : recover w' (perturbation w w') ≡ w

Two recovery operators:

  recover_via_hamming_7_4 :
    Given a perturbed 7-bit word that started as a Hamming(7, 4)
    codeword and was flipped in ≤ 1 position, returns the original.

  recover_via_clifford_reverse :
    Given a perturbation Multivector (DD2's trace_bitflip_divergence
    output) and a perturbed word, apply the reverse-anti-automorphism
    of the multivector as the unwinding operator. Restricted to
    grade-1 perturbations (single bit-flips) for which the wedge
    reading IS the bit-flip pattern.

Per the user's DD-arc trigger: "the wedge product can be used to
unwind a set of transformation-paths to a reference point."
"""

from __future__ import annotations

from typing import Tuple

from eliza.clifford import Multivector, grade_project, hamming_weight_profile
from eliza.hamming import all_codewords_7_4, correct_single_error, syndrome


def recover_via_hamming_7_4(perturbed_low7: int) -> int:
    """Single-error correction over Hamming(7, 4).

    `perturbed_low7` is a 7-bit value (LSB-aligned in an 8-bit byte;
    the high bit is preserved separately).

    Returns the nearest codeword in [0, 128); identical to
    `correct_single_error` for cleaner naming at the recovery layer.
    """
    return correct_single_error(perturbed_low7 & 0x7F)


def detect_error(perturbed_low7: int) -> Tuple[bool, int]:
    """Returns (is_codeword, error_position).

    error_position ∈ [0, 7]; 0 = no error.
    """
    s = syndrome(perturbed_low7 & 0x7F)
    return (s == 0, s)


# --- Clifford-multivector recovery -----------------------------------


def grade1_bit_position(mv: Multivector) -> int:
    """Extract the single bit position from a grade-1 multivector.

    Returns -1 if the multivector has no grade-1 content or has
    multiple grade-1 components.
    """
    g1 = grade_project(mv, 1)
    if not g1:
        return -1
    if len(g1) > 1:
        return -1
    only = next(iter(g1.keys()))
    # `only` is a power of 2; find which bit.
    for i in range(64):
        if only == (1 << i):
            return i
    return -1


def recover_via_clifford_reverse(
    perturbed_byte: int, perturbation_mv: Multivector,
) -> int:
    """EE7: apply the perturbation multivector's reverse-anti-
    automorphism to recover the original byte.

    For grade-1 perturbations (single bit-flips): the recovery is
    to XOR the byte with the bit-mask indicated by the grade-1
    component.

    For higher-grade perturbations: the cascade chain
    (per [[chain-walk-blocks-rotation-factor]]) means recovery
    requires the FULL trajectory, not just the final multivector;
    returns the byte unchanged with the limitation flagged.
    """
    profile = hamming_weight_profile(perturbation_mv)
    if profile.get(1, 0) == 1 and all(profile.get(k, 0) == 0
                                         for k in profile
                                         if k not in (0, 1)):
        pos = grade1_bit_position(perturbation_mv)
        if 0 <= pos < 8:
            return perturbed_byte ^ (1 << pos)
    return perturbed_byte


# --- Verification: recovery_law -----------------------------------


def verify_recovery_law(verbose: bool = True) -> bool:
    """Verify Hamming(7, 4) single-error recovery on all (codeword,
    flip position) pairs.

    For every codeword and every single-bit flip, recovery must
    return the original codeword.
    """
    ok = True
    cws = all_codewords_7_4()
    for c in cws:
        for pos in range(7):
            flipped = c ^ (1 << pos)
            recovered = recover_via_hamming_7_4(flipped)
            if recovered != c:
                if verbose:
                    print(f"FAIL: cw {c:07b} flip {pos} → "
                          f"got {recovered:07b}, expected {c:07b}")
                ok = False
    return ok


def verify_clifford_recovery(verbose: bool = True) -> bool:
    """Verify Clifford grade-1 recovery on byte single-bit flips."""
    from eliza.clifford import vector
    ok = True
    for byte in (0x00, 0x37, 0xAA, 0xFF):
        for pos in range(8):
            flipped = byte ^ (1 << pos)
            mv = vector(pos)
            recovered = recover_via_clifford_reverse(flipped, mv)
            if recovered != byte:
                if verbose:
                    print(f"FAIL: byte {byte:08b} flip {pos} → "
                          f"got {recovered:08b}, expected {byte:08b}")
                ok = False
    return ok


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    if not verify_recovery_law(verbose):
        ok = False
    if not verify_clifford_recovery(verbose):
        ok = False

    # detect_error: codewords pass through.
    for c in all_codewords_7_4():
        is_cw, err = detect_error(c)
        if not is_cw or err != 0:
            if verbose:
                print(f"FAIL: codeword {c:07b} mis-detected as error")
            ok = False

    # detect_error: single flip detected.
    base = 0b0110011
    flipped = base ^ (1 << 3)
    is_cw, err = detect_error(flipped)
    # 0b0110011 is a Hamming codeword? — let's not assume; verify only
    # that detect_error reports something nonzero on a known flip.
    if base in set(all_codewords_7_4()):
        if is_cw or err == 0:
            if verbose:
                print(f"FAIL: flipped codeword not detected")
            ok = False

    if verbose:
        print(f"recovery self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
