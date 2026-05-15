"""verify_s4_structure.py — tests for the S_4 / V_4 ⋊ S_3 formalization."""

import sys
from itertools import permutations

from s4_structure import (
    AXES, Permutation, IDENTITY, S4_ELEMENTS,
    V4_AS_PERMUTATIONS, V4_ELEMENT_TO_NAME, V4_ELEMENTS,
    ANCHOR_AXIS, STAB_D,
    factor_s4, unfactor_s4,
    signature_to_permutation, permutation_to_signature,
    stab_d_to_orbit_key, orbit_key_to_stab_d,
    selection_sort_descent, descent_to_permutation,
    hodge_star_signature,
    signed_singleton_to_forbidden_codeword,
    forbidden_codeword_to_signed_singleton,
    sn_cayley_dickson_table,
    v4_swap_consistency,
    q5_vertices, p4_vertices, hodge_complement_vertices,
    k3_proper_face_count, k4_proper_face_count, k3_k4_proper_face_count,
    codeword_pairing_v4_fibers,
    triadic_signatures_count, hodge_dual_completion_count,
    constructed_codeword_count,
    verify_s4_cardinality, verify_v4_is_subgroup, verify_v4_is_klein_four,
    verify_v4_is_normal, verify_stab_d_size, verify_stab_d_is_subgroup,
    verify_stab_d_complements_v4, verify_unique_factorization,
    verify_signature_permutation_bijection, verify_s4_order_distribution,
    verify_hodge_dual_preimage_count,
    verify_forbidden_codeword_singleton_bijection,
    verify_orbit_key_coverage,
    verify_selection_sort_descent_bijection,
    verify_q5_p4_hodge_partition,
    verify_p4_vertices_correspond_to_s4,
    verify_hodge_complement_corresponds_to_signed_singletons,
    verify_codeword_v4_fiber_structure,
    verify_k3_k4_codeword_cardinality_match,
    verify_hodge_fiber_is_forbidden_codewords,
    verify_valid_fibers_are_24_p4_vertices,
    verify_24_is_s3_times_v4,
    verify_8_is_axes_times_chirality,
    verify_32_constructed_from_triadic_plus_hodge,
    verify_triadic_24_equals_p4_vertices,
    verify_hodge_completion_equals_forbidden_codewords,
    verify_s4_formalization,
)


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def run(self, name, test_fn):
        try:
            result = test_fn()
        except Exception as e:
            print(f"  ✗ {name}: {type(e).__name__}: {e}")
            self.failed += 1
            return
        if result is True:
            print(f"  ✓ {name}")
            self.passed += 1
        else:
            print(f"  ✗ {name}: {result}")
            self.failed += 1


# ============================================================
# Permutation class
# ============================================================

def test_identity_is_identity():
    if not IDENTITY.is_identity():
        return "IDENTITY.is_identity() returned False"
    return True


def test_compose_with_identity():
    σ = Permutation(('C', 'D', 'W', 'S'))
    if σ.compose(IDENTITY) != σ:
        return "σ ∘ e ≠ σ"
    if IDENTITY.compose(σ) != σ:
        return "e ∘ σ ≠ σ"
    return True


def test_inverse_undoes_permutation():
    for σ in S4_ELEMENTS:
        if σ.compose(σ.inverse()) != IDENTITY:
            return f"{σ} ∘ {σ.inverse()} != identity"
        if σ.inverse().compose(σ) != IDENTITY:
            return f"{σ.inverse()} ∘ {σ} != identity"
    return True


def test_sign_homomorphism():
    """sign(σ ∘ τ) = sign(σ) · sign(τ)."""
    for σ in S4_ELEMENTS[:10]:
        for τ in S4_ELEMENTS[:10]:
            if (σ.compose(τ)).sign() != σ.sign() * τ.sign():
                return f"sign homomorphism failed for {σ}, {τ}"
    return True


def test_order_divides_24():
    for σ in S4_ELEMENTS:
        if 24 % σ.order() != 0:
            return f"σ.order() = {σ.order()} does not divide 24"
    return True


# ============================================================
# S_4 enumeration
# ============================================================

def test_s4_has_24_elements():
    return verify_s4_cardinality() or "S_4 cardinality wrong"


def test_s4_elements_distinct():
    if len(set(S4_ELEMENTS)) != 24:
        return f"duplicates in S4_ELEMENTS: {len(set(S4_ELEMENTS))} unique"
    return True


def test_s4_order_distribution():
    return verify_s4_order_distribution() or "S_4 order distribution wrong"


# ============================================================
# V_4 subgroup
# ============================================================

def test_v4_is_subgroup():
    return verify_v4_is_subgroup() or "V_4 not closed"


def test_v4_is_klein_four():
    return verify_v4_is_klein_four() or "non-identity V_4 elements not order 2"


def test_v4_is_normal():
    return verify_v4_is_normal() or "V_4 not normal"


def test_v4_swap_consistency():
    return v4_swap_consistency() or "V4_AS_PERMUTATIONS disagrees with meta_protocol.V4_SWAPS"


def test_v4_elements_are_4():
    if len(V4_ELEMENTS) != 4:
        return f"|V_4| = {len(V4_ELEMENTS)}"
    return True


# ============================================================
# Stab(D) = S_3 complement
# ============================================================

def test_stab_d_size():
    return verify_stab_d_size() or f"|Stab(D)| = {len(STAB_D)}"


def test_stab_d_is_subgroup():
    return verify_stab_d_is_subgroup() or "Stab(D) not closed"


def test_stab_d_complements_v4():
    return verify_stab_d_complements_v4() or "Stab(D) not a complement to V_4"


def test_orbit_key_coverage():
    return verify_orbit_key_coverage() or "Stab(D) does not cover all 6 orbit keys"


def test_orbit_key_to_stab_d_inverse():
    for s in STAB_D:
        k = stab_d_to_orbit_key(s)
        if orbit_key_to_stab_d(k) != s:
            return f"orbit_key_to_stab_d({k}) != {s}"
    return True


# ============================================================
# V_4 ⋊ S_3 factorization
# ============================================================

def test_unique_factorization():
    return verify_unique_factorization() or "factorization not unique"


def test_factor_then_unfactor_identity():
    for σ in S4_ELEMENTS:
        v, s = factor_s4(σ)
        if unfactor_s4(v, s) != σ:
            return f"unfactor(factor({σ})) != {σ}"
    return True


def test_factor_v_in_v4():
    for σ in S4_ELEMENTS:
        v, s = factor_s4(σ)
        if v not in set(V4_ELEMENTS):
            return f"v = {v} not in V_4"
    return True


def test_factor_s_in_stab_d():
    for σ in S4_ELEMENTS:
        v, s = factor_s4(σ)
        if s.apply(ANCHOR_AXIS) != ANCHOR_AXIS:
            return f"s = {s} does not fix D"
    return True


# ============================================================
# Signature ↔ permutation bijection
# ============================================================

def test_signature_permutation_bijection():
    return verify_signature_permutation_bijection() or "bijection failed"


def test_signature_roundtrip():
    for sig in permutations(AXES, 3):
        σ = signature_to_permutation(sig)
        if permutation_to_signature(σ) != sig:
            return f"roundtrip failed for {sig}"
    return True


def test_24_signatures_correspond_to_s4():
    sigs = list(permutations(AXES, 3))
    perms = [signature_to_permutation(s) for s in sigs]
    if set(perms) != set(S4_ELEMENTS):
        return "signature images don't cover S_4"
    return True


# ============================================================
# Selection-sort descent (derived)
# ============================================================

def test_descent_bijection():
    return verify_selection_sort_descent_bijection() or "descent not a bijection"


def test_descent_roundtrip():
    for σ in S4_ELEMENTS:
        d = selection_sort_descent(σ)
        if descent_to_permutation(d) != σ:
            return f"roundtrip failed for {σ}"
    return True


def test_descent_fourth_axis_not_in_sig():
    for σ in S4_ELEMENTS:
        fourth, witness, source, sink = selection_sort_descent(σ)
        sig = (source, sink, witness)
        if fourth in sig:
            return f"fourth {fourth} should not be in sig {sig}"
    return True


# ============================================================
# Hodge dual / forbidden codewords
# ============================================================

def test_hodge_dual_preimage_count():
    return verify_hodge_dual_preimage_count() or "Hodge dual preimage count wrong"


def test_forbidden_codeword_singleton_bijection():
    return verify_forbidden_codeword_singleton_bijection() or "forbidden ↔ singleton bijection failed"


def test_hodge_star_outputs_8_distinct_singletons():
    seen = set()
    for σ in S4_ELEMENTS:
        seen.add(hodge_star_signature(permutation_to_signature(σ)))
    if len(seen) != 8:
        return f"expected 8 distinct singletons, got {len(seen)}"
    return True


def test_hodge_star_sign_correctness():
    """For sig with permutation σ, hodge_star returns (fourth, sign(σ))."""
    for σ in S4_ELEMENTS:
        sig = permutation_to_signature(σ)
        axis, sign = hodge_star_signature(sig)
        if axis != σ.image[3]:
            return f"hodge_star {sig}: axis {axis} != image[3] {σ.image[3]}"
        if sign != σ.sign():
            return f"hodge_star {sig}: sign {sign} != σ.sign() {σ.sign()}"
    return True


# ============================================================
# Q_5 = P_4 ⊔ Hodge_complement partition (v19.1)
# ============================================================

def test_q5_has_32_vertices():
    if len(q5_vertices()) != 32:
        return f"|V(Q_5)| = {len(q5_vertices())}"
    return True


def test_p4_has_24_vertices():
    if len(p4_vertices()) != 24:
        return f"|V(P_4)| = {len(p4_vertices())}"
    return True


def test_hodge_complement_has_8_vertices():
    if len(hodge_complement_vertices()) != 8:
        return f"|Hodge_complement| = {len(hodge_complement_vertices())}"
    return True


def test_q5_p4_hodge_partition():
    return verify_q5_p4_hodge_partition() or "Q_5 partition failed"


def test_p4_vertices_correspond_to_s4():
    return verify_p4_vertices_correspond_to_s4() or "P_4 ↔ S_4 cardinality mismatch"


def test_hodge_complement_corresponds_to_signed_singletons():
    return verify_hodge_complement_corresponds_to_signed_singletons() \
        or "Hodge complement ↔ signed singleton bijection failed"


def test_p4_and_hodge_are_disjoint():
    p4 = set(p4_vertices())
    hc = set(hodge_complement_vertices())
    if p4 & hc:
        return f"overlap: {p4 & hc}"
    return True


def test_p4_union_hodge_covers_q5():
    p4 = set(p4_vertices())
    hc = set(hodge_complement_vertices())
    q5 = set(q5_vertices())
    if p4 | hc != q5:
        return f"missing: {q5 - (p4 | hc)}"
    return True


# ============================================================
# K_3 × K_4 cardinality + V_4 fiber structure (v19.2)
# ============================================================

def test_k3_proper_face_count():
    if k3_proper_face_count() != 2:
        return f"K_3 has {k3_proper_face_count()} proper faces, expected 2"
    return True


def test_k4_proper_face_count():
    if k4_proper_face_count() != 10:
        return f"K_4 has {k4_proper_face_count()} proper faces, expected 10"
    return True


def test_k3_k4_proper_face_count():
    if k3_k4_proper_face_count() != 32:
        return f"K_3 × K_4 has {k3_k4_proper_face_count()} proper faces, expected 32"
    return True


def test_codeword_v4_fiber_structure():
    return verify_codeword_v4_fiber_structure() or "V_4 fiber structure failed"


def test_v4_fibers_have_8_each():
    fibers = codeword_pairing_v4_fibers()
    sizes = {len(f) for f in fibers.values()}
    if sizes != {8}:
        return f"V_4 fiber sizes: {sizes}, expected {{8}}"
    return True


def test_three_valid_fibers_sum_to_24():
    fibers = codeword_pairing_v4_fibers()
    valid = len(fibers[0b00]) + len(fibers[0b01]) + len(fibers[0b10])
    if valid != 24:
        return f"valid fibers sum to {valid}, expected 24"
    return True


def test_forbidden_fiber_is_8():
    fibers = codeword_pairing_v4_fibers()
    if len(fibers[0b11]) != 8:
        return f"forbidden fiber size {len(fibers[0b11])}, expected 8"
    return True


def test_k3_k4_codeword_cardinality_match():
    return verify_k3_k4_codeword_cardinality_match() \
        or "K_3 × K_4 proper face count ≠ codeword count"


def test_hodge_fiber_is_forbidden_codewords():
    return verify_hodge_fiber_is_forbidden_codewords() \
        or "Hodge fiber (pairing=11) ≠ forbidden codewords"


def test_valid_fibers_are_p4_vertices():
    return verify_valid_fibers_are_24_p4_vertices() \
        or "valid fibers ∪ ≠ P_4 vertices"


# ============================================================
# Triadic construction: 24 → +Hodge → 32 (v19.3)
# ============================================================
#
# Tests that the 32-element space is CONSTRUCTED from the operational
# 24 (S_3 × V_4) by adding the 8 Hodge dual completion, NOT a primary
# 32-element ambient with 8 forbidden.

def test_triadic_count_is_24():
    if triadic_signatures_count() != 24:
        return f"triadic count {triadic_signatures_count()}, expected 24"
    return True


def test_triadic_factors_as_s3_v4():
    return verify_24_is_s3_times_v4() or "24 ≠ |S_3| × |V_4|"


def test_hodge_completion_count_is_8():
    if hodge_dual_completion_count() != 8:
        return f"Hodge completion {hodge_dual_completion_count()}, expected 8"
    return True


def test_hodge_completion_factors_as_axes_chirality():
    return verify_8_is_axes_times_chirality() or "8 ≠ |axes| × |chirality|"


def test_constructed_count_is_32():
    if constructed_codeword_count() != 32:
        return f"constructed count {constructed_codeword_count()}, expected 32"
    return True


def test_32_constructed_from_24_plus_8():
    return verify_32_constructed_from_triadic_plus_hodge() \
        or "32 ≠ 24 (triadic) + 8 (Hodge)"


def test_triadic_24_equals_p4():
    return verify_triadic_24_equals_p4_vertices() \
        or "triadic 24 ≠ |V(P_4)|"


def test_hodge_completion_equals_forbidden():
    return verify_hodge_completion_equals_forbidden_codewords() \
        or "Hodge completion 8 ≠ |forbidden|"


def test_construction_matches_applied_grammar_operational_count():
    """The 24 triadic count matches applied_grammar's WitnessedOp count."""
    from applied_grammar import all_valid_signatures
    if triadic_signatures_count() != len(all_valid_signatures()):
        return f"mismatch: s4 triadic {triadic_signatures_count()} vs applied {len(all_valid_signatures())}"
    return True


# ============================================================
# Cayley-Dickson correspondence table
# ============================================================

def test_sn_cayley_dickson_at_known_levels():
    table = sn_cayley_dickson_table()
    expected = {0: (1, 1), 1: (1, 2), 2: (2, 4), 3: (6, 8),
                4: (24, 16), 5: (120, 32)}
    if table != expected:
        return f"table mismatch: {table}"
    return True


def test_thickness_ratio_at_level_4():
    """At level 4, |S_4|/2^n is 24/16, but the user said compare 24 to 32
    (with chirality), giving 24/32 = 3/4 (the parity sieve ratio)."""
    table = sn_cayley_dickson_table()
    sn4, cd4 = table[4]
    if sn4 != 24 or cd4 != 16:
        return f"level 4 mismatch: {sn4}, {cd4}"
    # Cayley-Dickson level 5 (adding chirality bit at top) gives 32.
    ambient_at_top = 2 ** 5
    if 4 * sn4 != 3 * ambient_at_top:
        return f"parity sieve 24/32 != 3/4: {sn4} vs {ambient_at_top}"
    return True


# ============================================================
# Aggregator
# ============================================================

def test_s4_formalization_aggregator():
    return verify_s4_formalization() or "aggregator failed"


def main():
    r = TestRunner()
    print("=" * 78)
    print("  verify_s4_structure — formal V_4 ⋊ S_3 group structure tests")
    print("=" * 78)

    print("\n[Permutation class]")
    r.run('identity_is_identity', test_identity_is_identity)
    r.run('compose_with_identity', test_compose_with_identity)
    r.run('inverse_undoes_permutation', test_inverse_undoes_permutation)
    r.run('sign_is_homomorphism', test_sign_homomorphism)
    r.run('order_divides_24', test_order_divides_24)

    print("\n[S_4 enumeration]")
    r.run('s4_has_24_elements', test_s4_has_24_elements)
    r.run('s4_elements_distinct', test_s4_elements_distinct)
    r.run('s4_order_distribution_{1:1, 2:9, 3:8, 4:6}', test_s4_order_distribution)

    print("\n[V_4 normal subgroup]")
    r.run('v4_is_subgroup', test_v4_is_subgroup)
    r.run('v4_is_klein_four', test_v4_is_klein_four)
    r.run('v4_is_normal', test_v4_is_normal)
    r.run('v4_matches_meta_protocol_swaps', test_v4_swap_consistency)
    r.run('v4_has_4_elements', test_v4_elements_are_4)

    print("\n[Stab(D) realizing S_3]")
    r.run('stab_d_size_6', test_stab_d_size)
    r.run('stab_d_is_subgroup', test_stab_d_is_subgroup)
    r.run('stab_d_complements_v4', test_stab_d_complements_v4)
    r.run('orbit_key_coverage_6', test_orbit_key_coverage)
    r.run('orbit_key_to_stab_d_inverse', test_orbit_key_to_stab_d_inverse)

    print("\n[V_4 ⋊ S_3 factorization (PRIMARY structure)]")
    r.run('unique_factorization', test_unique_factorization)
    r.run('factor_unfactor_identity', test_factor_then_unfactor_identity)
    r.run('factor_v_in_v4', test_factor_v_in_v4)
    r.run('factor_s_in_stab_d', test_factor_s_in_stab_d)

    print("\n[Signature ↔ Permutation bijection]")
    r.run('signature_permutation_bijection', test_signature_permutation_bijection)
    r.run('signature_roundtrip', test_signature_roundtrip)
    r.run('24_signatures_cover_s4', test_24_signatures_correspond_to_s4)

    print("\n[Selection-sort descent (derived)]")
    r.run('descent_bijection', test_descent_bijection)
    r.run('descent_roundtrip', test_descent_roundtrip)
    r.run('descent_fourth_axis_not_in_sig', test_descent_fourth_axis_not_in_sig)

    print("\n[Hodge dual / forbidden codewords]")
    r.run('hodge_dual_preimage_count_3', test_hodge_dual_preimage_count)
    r.run('forbidden_codeword_singleton_bijection', test_forbidden_codeword_singleton_bijection)
    r.run('hodge_star_outputs_8_distinct', test_hodge_star_outputs_8_distinct_singletons)
    r.run('hodge_star_sign_correctness', test_hodge_star_sign_correctness)

    print("\n[Q_5 = P_4 ⊔ Hodge_complement partition (v19.1)]")
    r.run('q5_has_32_vertices', test_q5_has_32_vertices)
    r.run('p4_has_24_vertices', test_p4_has_24_vertices)
    r.run('hodge_complement_has_8_vertices', test_hodge_complement_has_8_vertices)
    r.run('q5_p4_hodge_partition', test_q5_p4_hodge_partition)
    r.run('p4_vertices_correspond_to_s4', test_p4_vertices_correspond_to_s4)
    r.run('hodge_complement_corresponds_to_singletons', test_hodge_complement_corresponds_to_signed_singletons)
    r.run('p4_and_hodge_disjoint', test_p4_and_hodge_are_disjoint)
    r.run('p4_union_hodge_covers_q5', test_p4_union_hodge_covers_q5)

    print("\n[K_3 × K_4 cardinality + V_4 fiber structure (v19.2)]")
    r.run('k3_proper_face_count_is_2', test_k3_proper_face_count)
    r.run('k4_proper_face_count_is_10', test_k4_proper_face_count)
    r.run('k3_k4_proper_face_count_is_32', test_k3_k4_proper_face_count)
    r.run('codeword_v4_fiber_structure', test_codeword_v4_fiber_structure)
    r.run('v4_fibers_have_8_each', test_v4_fibers_have_8_each)
    r.run('three_valid_fibers_sum_to_24', test_three_valid_fibers_sum_to_24)
    r.run('forbidden_fiber_is_8', test_forbidden_fiber_is_8)
    r.run('k3_k4_codeword_cardinality_match', test_k3_k4_codeword_cardinality_match)
    r.run('hodge_fiber_is_forbidden_codewords', test_hodge_fiber_is_forbidden_codewords)
    r.run('valid_fibers_are_p4_vertices', test_valid_fibers_are_p4_vertices)

    print("\n[Triadic construction: 24 → +Hodge → 32 (v19.3)]")
    r.run('triadic_count_is_24', test_triadic_count_is_24)
    r.run('triadic_factors_as_s3_v4', test_triadic_factors_as_s3_v4)
    r.run('hodge_completion_count_is_8', test_hodge_completion_count_is_8)
    r.run('hodge_completion_factors_as_axes_chirality', test_hodge_completion_factors_as_axes_chirality)
    r.run('constructed_count_is_32', test_constructed_count_is_32)
    r.run('32_constructed_from_24_plus_8', test_32_constructed_from_24_plus_8)
    r.run('triadic_24_equals_p4_vertices', test_triadic_24_equals_p4)
    r.run('hodge_completion_equals_forbidden', test_hodge_completion_equals_forbidden)
    r.run('construction_matches_applied_grammar', test_construction_matches_applied_grammar_operational_count)

    print("\n[Cayley-Dickson correspondence]")
    r.run('sn_cd_table_correct', test_sn_cayley_dickson_at_known_levels)
    r.run('thickness_ratio_at_level_4', test_thickness_ratio_at_level_4)

    print("\n[Aggregator]")
    r.run('s4_formalization_aggregator', test_s4_formalization_aggregator)

    total = r.passed + r.failed
    print(f"\n  {r.passed}/{total} pass " + ("✓✓✓" if r.failed == 0 else f"  ({r.failed} failures)"))
    print()
    return 0 if r.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
