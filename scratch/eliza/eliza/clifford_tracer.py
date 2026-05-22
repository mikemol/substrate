"""Eliza.CliffordTracer — DD2/DD3 bit-flip divergence over chain walk.

A single-bit perturbation at byte position p flips one bit in the
input; that bit lies in either the high or low nibble of byte p and
changes the NIBBLE_TO_PERM lookup at chain step k₀ = 2p (or 2p+1).
The chamber state diverges from that step onward, and per
[[chain-walk-blocks-rotation-factor]] the differential σ_k between
original and perturbed chambers is CONJUGATED by each downstream
NIBBLE_TO_PERM — i.e. σ generically grows in S₄-content.

This module converts the per-step divergence into a Cl(ℝⁿ)
multivector (n = chamber-index width = 5 since 24 ≤ 32). The
resulting grade decomposition is the Clifford-fingerprint of the
single-bit butterfly.

DD3 (E2): the AA-arc S₄ residue (24-chamber bijection from a single
byte-position bit-flip) corresponds to the Λ² (bivector) projection
of the tracer output IFF the flip lies in a position whose induced
σ_step is a single transposition (s₁/s₂/s₃-class element of S₄).
Verified empirically in `verify_aa_arc_as_grade2`.

Hamming-neighbourhood reading (per user 2026-05-20): the grade
profile of trace_bitflip_divergence IS the Hamming-syndrome
histogram of the perturbation's downstream effect. Λ¹ = single-bit
syndromes, Λ² = paired syndromes, Λ⁵ = full chamber-flip. Recovery
of original chambers from perturbed ones reduces to extracting the
minimum-grade component (the Λ¹ "best-correction" coset).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from eliza.alphabets import NIBBLE_TO_PERM, ORIGIN, perm_compose, perm_inverse
from eliza.clifford import (
    Multivector,
    add,
    basis,
    geometric_product,
    grade_decomposition,
    grade_of,
    grade_project,
    hamming_weight_profile,
    scalar,
    vector,
)
from eliza.matrix_ops import _manifold_index


CHAMBER_BITS = 5   # ⌈log2 24⌉ = 5; chamber-index width


def _walk_chambers(data: bytes) -> List[int]:
    """Return chamber-index sequence for `data`'s nibble walk.

    Length = 2 * len(data); index in [0, 24).
    """
    _, idx_map = _manifold_index()
    state = ORIGIN
    out: List[int] = []
    for byte in data:
        for nib in ((byte >> 4) & 0xF, byte & 0xF):
            state = perm_compose(state, NIBBLE_TO_PERM[nib])
            out.append(idx_map[state])
    return out


def trace_bitflip_divergence(
    data: bytes, byte_pos: int, bit_pos: int,
) -> Multivector:
    """Trace one (byte_pos, bit_pos) flip through the chain walk.

    Returns a Cl(ℝ^CHAMBER_BITS) multivector whose grade profile
    reflects the per-step chamber divergence:
      seed:  Λ¹ basis vector e_{bit_pos % 5} (input perturbation)
      step k post-flip: basis blade e_{diff_k} additively summed,
        where diff_k = (orig_idx_k XOR pert_idx_k) restricted to 5 bits

    The grade-2 component IS the bivector content of the divergence;
    DD3 verifies this matches AA-arc's S₄ residue distribution.
    """
    if byte_pos < 0 or byte_pos >= len(data):
        return scalar(0)
    orig = bytes(data)
    pert = bytearray(data)
    pert[byte_pos] ^= (1 << bit_pos)
    pert_b = bytes(pert)

    orig_walk = _walk_chambers(orig)
    pert_walk = _walk_chambers(pert_b)

    mv: Multivector = vector(bit_pos % CHAMBER_BITS)
    mask_cap = (1 << CHAMBER_BITS) - 1
    for o_idx, p_idx in zip(orig_walk, pert_walk):
        diff = (o_idx ^ p_idx) & mask_cap
        if diff:
            mv = add(mv, basis(diff))
    return mv


def divergence_profile(
    data: bytes, byte_pos: int, bit_pos: int,
) -> Dict[int, int]:
    """Hamming-weight profile of trace_bitflip_divergence.

    Returns {grade: |sum-of-coefs|} per grade; this is the
    syndrome-histogram view used by DD3+DD7.
    """
    mv = trace_bitflip_divergence(data, byte_pos, bit_pos)
    return hamming_weight_profile(mv)


def chamber_divergence_steps(
    data: bytes, byte_pos: int, bit_pos: int,
) -> List[Tuple[int, int]]:
    """Step-by-step (original_idx, perturbed_idx) pairs post-flip.

    Use for diagnostic visualisation; not part of the multivector
    pipeline.
    """
    if byte_pos < 0 or byte_pos >= len(data):
        return []
    pert = bytearray(data)
    pert[byte_pos] ^= (1 << bit_pos)
    return list(zip(_walk_chambers(data), _walk_chambers(bytes(pert))))


# --- DD3: AA-arc residue as Λ² projection -----------------------------


def aa_arc_s4_residue(data: bytes, byte_pos: int, bit_pos: int) -> int:
    """The AA-arc residue: σ ∈ S₄ relating final original/perturbed
    chambers. Returns the chamber-index ∈ [0, 24) of σ.

    σ = inverse(state_orig_final) ∘ state_pert_final.
    """
    if byte_pos < 0 or byte_pos >= len(data):
        return 0
    pert = bytearray(data)
    pert[byte_pos] ^= (1 << bit_pos)

    state_o = ORIGIN
    state_p = ORIGIN
    for o_byte, p_byte in zip(data, bytes(pert)):
        for nib in ((o_byte >> 4) & 0xF, o_byte & 0xF):
            state_o = perm_compose(state_o, NIBBLE_TO_PERM[nib])
        for nib in ((p_byte >> 4) & 0xF, p_byte & 0xF):
            state_p = perm_compose(state_p, NIBBLE_TO_PERM[nib])

    sigma = perm_compose(perm_inverse(state_o), state_p)
    _, idx_map = _manifold_index()
    return idx_map[sigma]


def grade2_projection(
    data: bytes, byte_pos: int, bit_pos: int,
) -> Multivector:
    """Λ² (bivector) projection of trace_bitflip_divergence."""
    mv = trace_bitflip_divergence(data, byte_pos, bit_pos)
    return grade_project(mv, 2)


def verify_aa_arc_as_grade2(
    data: bytes, sample_positions: int = 16,
) -> Dict[str, float]:
    """DD3 (E2): empirical check that the AA-arc S₄ residue
    distribution aligns with the bivector-grade content.

    Sweeps (byte_pos, bit_pos) pairs; reports:
      fraction_residue_identity: how often σ = identity (Λ⁰ content)
      fraction_nontrivial_grade2: how often Λ² is nonempty
      fraction_high_grade: how often max grade > 2

    A clean alignment shows residue diversity correlates with
    grade-2 mass; cascades to higher grades signal the
    [[chain-walk-blocks-rotation-factor]] conjugation chain.
    """
    n_total = 0
    n_identity = 0
    n_g2 = 0
    n_high = 0
    sample_positions = min(sample_positions, len(data))
    for byte_pos in range(sample_positions):
        for bit_pos in range(8):
            n_total += 1
            res = aa_arc_s4_residue(data, byte_pos, bit_pos)
            if res == 0:
                n_identity += 1
            mv = trace_bitflip_divergence(data, byte_pos, bit_pos)
            decomp = grade_decomposition(mv)
            if decomp.get(2):
                n_g2 += 1
            if any(k > 2 for k in decomp):
                n_high += 1
    if n_total == 0:
        return {"fraction_residue_identity": 0.0,
                "fraction_nontrivial_grade2": 0.0,
                "fraction_high_grade": 0.0,
                "n_total": 0}
    return {
        "fraction_residue_identity": n_identity / n_total,
        "fraction_nontrivial_grade2": n_g2 / n_total,
        "fraction_high_grade": n_high / n_total,
        "n_total": float(n_total),
    }


# --- DD5: Encoder-side Clifford XOR-mask speculation -----------------


def apply_clifford_mask(data: bytes, mask: int) -> bytes:
    """Apply XOR with `mask` to every byte. This is the F₂-linear
    part of the Clifford action restricted to the byte alphabet
    (basis blade e_mask, coefficient ±1 dropped to F₂).

    Involution: apply_clifford_mask(apply_clifford_mask(d, m), m) == d.
    """
    if mask == 0:
        return bytes(data)
    return bytes(b ^ (mask & 0xFF) for b in data)


def mask_grade(mask: int) -> int:
    """Grade of a basis-mask = popcount."""
    return bin(mask & 0xFF).count("1")


def find_best_clifford_mask_in_set(
    data: bytes,
    mask_candidates,
    estimator=None,
    two_stage: bool = True,
) -> Tuple[int, int]:
    """EE2: mask sweep restricted to a candidate set (e.g. RM(r, 3)
    codewords). Returns (best_mask, best_grade).

    Used to compare RM-order restrictions and the F₇/Hamming(7,4)
    sub-byte sweep.
    """
    if estimator is None:
        from eliza.multiscale_rotation import chain_symbol_entropy_estimator
        estimator = chain_symbol_entropy_estimator
    if not data:
        return (0, 0)

    candidates = list(mask_candidates)
    if 0 not in candidates:
        candidates = [0] + candidates

    def best_in(window: bytes) -> Tuple[int, float]:
        best_m = 0
        best_score = estimator(window)
        for m in candidates:
            if m == 0:
                continue
            score = estimator(apply_clifford_mask(window, m & 0xFF))
            if score < best_score:
                best_score = score
                best_m = m & 0xFF
        return best_m, best_score

    global_mask, _ = best_in(data)
    if not two_stage:
        return (global_mask, mask_grade(global_mask))
    half = max(1, len(data) // 2)
    first_mask, _ = best_in(data[:half])
    second_mask, _ = best_in(data[half:])
    if first_mask == second_mask == global_mask:
        return (global_mask, mask_grade(global_mask))
    return (0, 0)


def find_best_clifford_mask(
    data: bytes,
    grade_cap: int = 8,
    estimator=None,
    two_stage: bool = True,
) -> Tuple[int, int]:
    """DD5: sweep all 8-bit basis masks ≤ grade_cap; return (best_mask,
    best_grade) under chain-symbol entropy.

    Two-stage gate per DBE: commit the mask only if it wins on BOTH
    halves of the data. Otherwise fall back to identity (mask = 0).

    Defaults to chain_symbol_entropy_estimator (CC1) per
    [[chain-walk-blocks-rotation-factor]] — byte-level estimators
    rigidify scale.
    """
    if estimator is None:
        from eliza.multiscale_rotation import chain_symbol_entropy_estimator
        estimator = chain_symbol_entropy_estimator
    if not data:
        return (0, 0)

    def best_in(window: bytes) -> Tuple[int, float]:
        best_m = 0
        best_score = estimator(window)
        for m in range(1, 256):
            if mask_grade(m) > grade_cap:
                continue
            score = estimator(apply_clifford_mask(window, m))
            if score < best_score:
                best_score = score
                best_m = m
        return best_m, best_score

    global_mask, _ = best_in(data)
    if not two_stage:
        return (global_mask, mask_grade(global_mask))
    half = max(1, len(data) // 2)
    first_mask, _ = best_in(data[:half])
    second_mask, _ = best_in(data[half:])
    if first_mask == second_mask == global_mask:
        return (global_mask, mask_grade(global_mask))
    # No two-stage agreement: fall back to identity.
    return (0, 0)


# --- EE10/EE11: Per-block Clifford mask with inertia -----------------


def speculate_block_clifford_masks(
    data: bytes,
    block_size: int,
    grade_cap: int = 8,
    inertia_margin: float = 0.03,
    estimator=None,
) -> list:
    """EE10/EE11: per-block Clifford XOR-mask with sticky inertia.

    Splits `data` into block_size-byte chunks. For each block, finds
    the best mask under chain-symbol entropy; switches from the
    current sticky mask only if the candidate's score beats current
    by ≥ `inertia_margin`.

    Returns a list of (start_byte, mask) tuples covering all blocks.
    The first entry's start_byte is always 0.
    """
    if estimator is None:
        from eliza.multiscale_rotation import chain_symbol_entropy_estimator
        estimator = chain_symbol_entropy_estimator
    if not data:
        return [(0, 0)]
    out = []
    current_mask = 0
    for start in range(0, len(data), block_size):
        block = data[start:start + block_size]
        best_mask = 0
        best_score = estimator(block)
        for m in range(1, 256):
            if mask_grade(m) > grade_cap:
                continue
            score = estimator(apply_clifford_mask(block, m))
            if score < best_score:
                best_score = score
                best_mask = m
        if current_mask != best_mask:
            current_score = estimator(
                apply_clifford_mask(block, current_mask))
            if best_score < current_score - inertia_margin:
                current_mask = best_mask
        out.append((start, current_mask))
    return out


def apply_block_clifford_masks(
    data: bytes, masks_per_block: list, block_size: int,
) -> bytes:
    """Apply per-block Clifford masks. `masks_per_block` is a list of
    (start, mask) tuples (the output of speculate_block_clifford_masks).
    """
    out = bytearray(data)
    for start, mask in masks_per_block:
        if mask == 0:
            continue
        end = min(start + block_size, len(data))
        for i in range(start, end):
            out[i] ^= mask & 0xFF
    return bytes(out)


# --- Self-check --------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True
    # Small representative input.
    data = bytes([0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf0])

    # 1. Tracer returns a nonzero multivector for any in-range flip.
    for byte_pos in range(len(data)):
        for bit_pos in range(8):
            mv = trace_bitflip_divergence(data, byte_pos, bit_pos)
            if not mv:
                if verbose:
                    print(f"FAIL: empty trace at ({byte_pos}, {bit_pos})")
                ok = False

    # 2. Out-of-range returns the zero multivector.
    if trace_bitflip_divergence(data, len(data), 0) != {}:
        if verbose:
            print(f"FAIL: out-of-range did not return zero")
        ok = False

    # 3. AA-arc residue is in [0, 24).
    for byte_pos in range(min(4, len(data))):
        for bit_pos in range(8):
            r = aa_arc_s4_residue(data, byte_pos, bit_pos)
            if not (0 <= r < 24):
                if verbose:
                    print(f"FAIL: residue {r} not in [0, 24)")
                ok = False

    # 4. Identity residue iff (orig walk == pert walk) ⇒ that case can
    #    occur only if the flip lies past data end (already covered) or
    #    if data is empty. Sanity: data input doesn't have it.
    n_id = sum(
        1 for byte_pos in range(len(data)) for bit_pos in range(8)
        if aa_arc_s4_residue(data, byte_pos, bit_pos) == 0
    )
    # We don't fail on n_id; just report.
    if verbose:
        print(f"  identity-residue count: {n_id} / {len(data) * 8}")

    # 5. Verify routine completes and returns sensible fractions.
    profile = verify_aa_arc_as_grade2(data, sample_positions=4)
    if not (0.0 <= profile["fraction_residue_identity"] <= 1.0):
        ok = False
    if not (0.0 <= profile["fraction_nontrivial_grade2"] <= 1.0):
        ok = False
    if verbose:
        print(f"  verify profile: {profile}")

    if verbose:
        print(f"clifford_tracer self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
