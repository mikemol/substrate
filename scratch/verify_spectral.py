"""
verify_spectral.py — tests for M40 spectral view.

Verifies:
  - Hadamard matrix property H · H^T = N · I (multiple levels)
  - WHT is involutory up to scale (multiple levels)
  - Fast WHT matches direct computation (multiple levels)
  - V_4 translations compose by XOR (form group isomorphic to F_2^n)
  - Chirality flip is involutive
  - V_4 commutes with chirality
  - Spectral matrix-product composition matches V_4 algebra
"""

from spectral_view import (
    hadamard_matrix, matvec, matmat, transpose, identity,
    fwht, v4_translation, chirality_flip,
    v4_translation_matrix, chirality_flip_matrix,
    verify_hadamard_property, verify_wht_is_involutory,
    verify_fwht_matches_direct, verify_v4_composition,
    verify_chirality_is_involutive, verify_v4_commutes_with_chirality,
    # v2 additions
    chi, inverse_wht,
    point_translation, point_modulation,
    spectral_translation, spectral_modulation,
    z3_cycle, z3_cycle_inverse, z3_cycle_matrix,
    spectral_modulation_matrix, point_modulation_matrix,
    spectral_of,
    verify_dc_is_sum_not_mean,
    verify_point_translation_to_spectral_modulation,
    verify_point_modulation_to_spectral_translation,
    verify_z3_cubed_is_identity, verify_z3_inverse_correct,
    verify_z3_inverse_equals_z_squared, verify_z3_fixes_dc,
    verify_z3_permutes_nonzero_masks, verify_z3_conjugates_v4_by_cycle,
    verify_z3_commutes_with_chirality,
    verify_a4_order_is_12, verify_a4_closure_under_composition,
    verify_a4_times_z2_order_is_24,
    verify_spectral_of_point_translation_is_spectral_modulation,
    _apply_a4_element,
    # v3 additions
    s3_swap_01_10, s3_swap_01_11, s3_swap_10_11, s3_elements,
    enumerate_a4_z2_elements, enumerate_s4_elements,
    compute_order_distribution, compute_group_center,
    _element_order,
    verify_a4_z2_has_24_distinct_elements,
    verify_s4_has_24_distinct_elements,
    verify_a4_z2_order_distribution,
    verify_s4_order_distribution,
    verify_a4_z2_no_order_4_elements,
    verify_s4_has_order_4_elements,
    verify_a4_z2_center_order_is_2,
    verify_s4_center_is_trivial,
    verify_a4_z2_not_isomorphic_to_s4,
    verify_s3_transpositions_are_involutions,
    verify_s3_has_6_elements,
    verify_s3_fixes_dc,
    # v4 additions
    A4Z2_IDENTITY, a4z2_all_elements, a4z2_compose, a4z2_inverse, a4z2_act, a4z2_name,
    S4_IDENTITY, s4_all_elements, s4_compose, s4_inverse, s4_act, s4_name,
    S3_ALL, S3_I, S3_Z, S3_Z2, S3_SWAP_0110, s3_compose, s3_inverse,
    algebraic_order, algebraic_order_distribution, algebraic_center,
    generate_group_by_action, architectural_primitives_level_2,
    verify_architectural_primitives_generate_a4z2,
    verify_adding_transposition_extends_to_48,
    verify_pure_s4_primitives_generate_s4,
    verify_algebraic_a4z2_has_24_distinct,
    verify_algebraic_s4_has_24_distinct,
    verify_a4z2_algebraic_orders_match_expected,
    verify_s4_algebraic_orders_match_expected,
    verify_a4z2_algebraic_center_is_2,
    verify_s4_algebraic_center_is_trivial,
    verify_a4z2_algebra_matches_vector,
    verify_s4_algebra_matches_vector,
    verify_a4z2_compose_is_associative,
    verify_s4_compose_is_associative,
    verify_a4z2_inverse_is_correct,
    verify_s4_inverse_is_correct,
    verify_a4z2_closure_disjoint_from_extra_transposition,
    verify_m40_group_is_a4z2_not_s4,
)


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.records = []

    def run(self, name, fn):
        try:
            result = fn()
            if result is True:
                self.passed += 1
                self.records.append(('✓', name))
            else:
                self.failed += 1
                self.records.append(('✗', f"{name}: {result}"))
        except Exception as e:
            self.failed += 1
            self.records.append(('✗', f"{name}: {type(e).__name__}: {e}"))

    def summary(self):
        for marker, line in self.records:
            print(f"  {marker} {line}")
        print()
        total = self.passed + self.failed
        verdict = '✓✓✓' if self.failed == 0 else f'({self.failed} failures)'
        print(f"  {self.passed}/{total} pass  {verdict}")


# ============================================================
# Hadamard matrix properties
# ============================================================

def test_hadamard_n2():
    return verify_hadamard_property(2)

def test_hadamard_n3():
    return verify_hadamard_property(3)

def test_hadamard_n4():
    return verify_hadamard_property(4)


def test_hadamard_dc_row_is_all_ones():
    """Row k=0 of H is the constant +1 vector (DC character)."""
    H = hadamard_matrix(2)
    return all(H[0][x] == 1 for x in range(4))


def test_hadamard_first_col_is_all_ones():
    """Column x=0 of H is all +1 (χ_k(0) = 1 for any k)."""
    H = hadamard_matrix(2)
    return all(H[k][0] == 1 for k in range(4))


# ============================================================
# WHT round-trip
# ============================================================

def test_wht_involutory_n2():
    return verify_wht_is_involutory(2)

def test_wht_involutory_n3():
    return verify_wht_is_involutory(3)


# ============================================================
# FWHT correctness
# ============================================================

def test_fwht_matches_direct_n2():
    return verify_fwht_matches_direct(2)

def test_fwht_matches_direct_n3():
    return verify_fwht_matches_direct(3)

def test_fwht_matches_direct_n4():
    return verify_fwht_matches_direct(4)


def test_fwht_arbitrary_vector_n3():
    """FWHT of an arbitrary vector matches direct H · v."""
    H = hadamard_matrix(3)
    v = [3, 1, 4, 1, 5, 9, 2, 6]
    direct = matvec(H, v)
    fast = fwht(v)
    return direct == fast


# ============================================================
# V_4 translation as frequency translation
# ============================================================

def test_v4_translation_composes_by_xor_n2():
    return verify_v4_composition(2)


def test_v4_translation_is_self_inverse():
    """v4_translation by m is self-inverse: applying it twice returns the original."""
    F = [1, 2, 3, 4]
    for m in range(4):
        if v4_translation(v4_translation(F, m), m) != F:
            return f"m={m}: not self-inverse"
    return True


def test_v4_translation_identity_is_no_op():
    """v4_translation by m=0 is the identity."""
    F = [10, 20, 30, 40]
    return v4_translation(F, 0) == F


# ============================================================
# Chirality flip
# ============================================================

def test_chirality_involutive():
    return verify_chirality_is_involutive(2)


def test_chirality_negates():
    F = [1, -2, 3, -4]
    return chirality_flip(F) == [-1, 2, -3, 4]


# ============================================================
# Commutativity
# ============================================================

def test_v4_commutes_with_chirality():
    return verify_v4_commutes_with_chirality(2)


# ============================================================
# Spectral matrix composition mirrors V_4 algebra
# ============================================================

def test_v_alpha_times_v_beta_is_v_gamma():
    """V_α · V_β = V_γ (matrix product realization of V_4 group operation)."""
    Va = v4_translation_matrix(0b01, n=2)
    Vb = v4_translation_matrix(0b10, n=2)
    Vg = v4_translation_matrix(0b11, n=2)
    return matmat(Va, Vb) == Vg


def test_v_alpha_squared_is_identity():
    """V_α^2 = I (V_4 element of order 2)."""
    Va = v4_translation_matrix(0b01, n=2)
    I = identity(4)
    return matmat(Va, Va) == I


def test_v4_matrices_are_permutations():
    """Each V_4 matrix has exactly one +1 per row and per column."""
    for m in range(4):
        P = v4_translation_matrix(m, n=2)
        for i in range(4):
            row_sum = sum(P[i])
            col_sum = sum(P[j][i] for j in range(4))
            if row_sum != 1 or col_sum != 1:
                return f"m={m}: not a permutation matrix"
    return True


def test_chirality_matrix_is_minus_I():
    """Chirality flip matrix is -I."""
    C = chirality_flip_matrix(2)
    expected = [[-1 if i == j else 0 for j in range(4)] for i in range(4)]
    return C == expected


def test_chirality_squared_is_identity():
    """C^2 = I."""
    C = chirality_flip_matrix(2)
    I = identity(4)
    return matmat(C, C) == I


# ============================================================
# v2: DC normalization
# ============================================================

def test_dc_is_sum_n2():
    return verify_dc_is_sum_not_mean(2)


def test_dc_is_sum_n3():
    return verify_dc_is_sum_not_mean(3)


def test_dc_explicit_value():
    """For f = [1,2,3,4], F[0] should be 10 = sum(f), not 2.5 = mean(f)."""
    F = fwht([1, 2, 3, 4])
    if F[0] != 10:
        return f"expected F[0]=10, got {F[0]}"
    return True


# ============================================================
# v2: character function
# ============================================================

def test_chi_dc_is_one():
    """χ_0(x) = 1 for all x; χ_a(0) = 1 for all a."""
    for x in range(8):
        if chi(0, x) != 1:
            return f"χ_0({x}) = {chi(0, x)}"
    for a in range(8):
        if chi(a, 0) != 1:
            return f"χ_{a}(0) = {chi(a, 0)}"
    return True


def test_chi_symmetric():
    """χ_a(x) = χ_x(a)."""
    for a in range(4):
        for x in range(4):
            if chi(a, x) != chi(x, a):
                return f"χ_{a}({x}) ≠ χ_{x}({a})"
    return True


def test_chi_multiplicative_in_first_arg():
    """χ_{a ⊕ b}(x) = χ_a(x) · χ_b(x)."""
    for a in range(4):
        for b in range(4):
            for x in range(4):
                if chi(a ^ b, x) != chi(a, x) * chi(b, x):
                    return f"failed at a={a}, b={b}, x={x}"
    return True


# ============================================================
# v2: point/spectral duality
# ============================================================

def test_point_translation_to_spectral_modulation_n2():
    return verify_point_translation_to_spectral_modulation(2)


def test_point_translation_to_spectral_modulation_n3():
    return verify_point_translation_to_spectral_modulation(3)


def test_point_modulation_to_spectral_translation_n2():
    return verify_point_modulation_to_spectral_translation(2)


def test_point_modulation_to_spectral_translation_n3():
    return verify_point_modulation_to_spectral_translation(3)


def test_point_translation_composes_by_xor():
    f = [1, 2, 3, 4]
    for a1 in range(4):
        for a2 in range(4):
            composed = point_translation(point_translation(f, a1), a2)
            direct = point_translation(f, a1 ^ a2)
            if composed != direct:
                return f"failed at a1={a1}, a2={a2}"
    return True


def test_point_modulation_self_inverse():
    """point_modulation(point_modulation(f, m), m) = f."""
    f = [1, 2, 3, 4]
    for m in range(4):
        if point_modulation(point_modulation(f, m), m) != f:
            return f"failed at m={m}"
    return True


def test_spectral_modulation_self_inverse():
    F = [10, -2, -4, 0]
    for a in range(4):
        if spectral_modulation(spectral_modulation(F, a), a) != F:
            return f"failed at a={a}"
    return True


# ============================================================
# v2: Z_3 cycle
# ============================================================

def test_z3_cubed_is_identity():
    return verify_z3_cubed_is_identity()


def test_z3_inverse_correct():
    return verify_z3_inverse_correct()


def test_z3_inverse_equals_z_squared():
    return verify_z3_inverse_equals_z_squared()


def test_z3_fixes_dc():
    return verify_z3_fixes_dc()


def test_z3_permutes_nonzero_masks():
    return verify_z3_permutes_nonzero_masks()


def test_z3_conjugates_v4_by_cycle():
    """Z T_m Z^{-1} = T_{cycle(m)} — the semidirect relation."""
    return verify_z3_conjugates_v4_by_cycle()


def test_z3_commutes_with_chirality():
    return verify_z3_commutes_with_chirality()


def test_z3_cycle_matrix_is_permutation():
    """The Z_3 matrix has exactly one 1 in each row and column."""
    P = z3_cycle_matrix()
    for row in P:
        if sum(row) != 1 or any(v not in (0, 1) for v in row):
            return f"row not a permutation: {row}"
    for j in range(4):
        col_sum = sum(P[i][j] for i in range(4))
        if col_sum != 1:
            return f"column {j} sum {col_sum} != 1"
    return True


def test_z3_rejects_non_level_2():
    """z3_cycle is only defined at level 2."""
    try:
        z3_cycle([1, 2])  # level 1
        return "should have raised"
    except ValueError:
        return True


# ============================================================
# v2: A_4 = V_4 ⋊ Z_3
# ============================================================

def test_a4_order_is_12():
    return verify_a4_order_is_12()


def test_a4_closure_under_composition():
    return verify_a4_closure_under_composition()


def test_a4_times_z2_order_is_24():
    """A_4 × Z_2 has order 24 — matches M38 codeword count."""
    return verify_a4_times_z2_order_is_24()


def test_a4_identity_is_in_set():
    """T_0 · Z^0 = I; applying to any F returns F."""
    F = [10, 20, 30, 40]
    result = _apply_a4_element(F, 0, 0)
    if result != F:
        return f"identity should fix F, got {result}"
    return True


# ============================================================
# v2: operator conjugation
# ============================================================

def test_spectral_of_point_translation_is_modulation():
    return verify_spectral_of_point_translation_is_spectral_modulation()


def test_chirality_in_point_view_is_minus_I_in_spectral():
    """Chirality is -I in both views (it commutes with H)."""
    n = 2
    N = 4
    H = hadamard_matrix(n)
    neg_I = [[-1 if i == j else 0 for j in range(N)] for i in range(N)]
    # H · (-I) · H^{-1} = -I
    H_neg = matmat(H, neg_I)
    H_neg_H = matmat(H_neg, H)
    # H · (-I) · H = -H · H = -N · I
    for i in range(N):
        for j in range(N):
            expected = -N if i == j else 0
            if H_neg_H[i][j] != expected:
                return f"failed at ({i}, {j}): expected {expected}, got {H_neg_H[i][j]}"
    return True


# ============================================================
# v3: S_3 transpositions
# ============================================================

def test_s3_transpositions_involutive():
    return verify_s3_transpositions_are_involutions()


def test_s3_has_6_elements():
    return verify_s3_has_6_elements()


def test_s3_fixes_dc():
    return verify_s3_fixes_dc()


def test_s3_swap_01_10_fixes_11():
    F = [10, 20, 30, 40]
    result = s3_swap_01_10(F)
    return result[3] == F[3]  # F[11] is fixed


def test_s3_swap_01_11_fixes_10():
    F = [10, 20, 30, 40]
    result = s3_swap_01_11(F)
    return result[2] == F[2]  # F[10] is fixed


def test_s3_swap_10_11_fixes_01():
    F = [10, 20, 30, 40]
    result = s3_swap_10_11(F)
    return result[1] == F[1]  # F[01] is fixed


# ============================================================
# v3: A_4 × Z_2 vs S_4 — both order 24, non-isomorphic
# ============================================================

def test_a4_z2_has_24_distinct():
    return verify_a4_z2_has_24_distinct_elements()


def test_s4_has_24_distinct():
    return verify_s4_has_24_distinct_elements()


def test_a4_z2_order_distribution():
    """{1: 1, 2: 7, 3: 8, 6: 8}."""
    return verify_a4_z2_order_distribution()


def test_s4_order_distribution():
    """{1: 1, 2: 9, 3: 8, 4: 6}."""
    return verify_s4_order_distribution()


def test_a4_z2_no_order_4():
    return verify_a4_z2_no_order_4_elements()


def test_s4_has_order_4():
    return verify_s4_has_order_4_elements()


def test_a4_z2_center_is_2():
    return verify_a4_z2_center_order_is_2()


def test_s4_center_is_1():
    return verify_s4_center_is_trivial()


def test_a4_z2_not_iso_s4():
    """Both have order 24 but are NOT isomorphic (different order distributions)."""
    return verify_a4_z2_not_isomorphic_to_s4()


def test_a4_z2_total_orders_sum_to_24():
    """Order distribution sums to 24."""
    from spectral_view import compute_order_distribution, enumerate_a4_z2_elements
    dist = compute_order_distribution(enumerate_a4_z2_elements(), [10, 20, 30, 40])
    return sum(dist.values()) == 24


def test_s4_total_orders_sum_to_24():
    from spectral_view import compute_order_distribution, enumerate_s4_elements
    dist = compute_order_distribution(enumerate_s4_elements(), [10, 20, 30, 40])
    return sum(dist.values()) == 24


# ============================================================
# v3: code-level hardening
# ============================================================

def test_inverse_wht_rejects_non_power_of_2():
    try:
        inverse_wht([1, 2, 3])  # length 3, not power of 2
        return "should raise"
    except ValueError:
        return True


def test_inverse_wht_rejects_non_divisible():
    """If F is not exactly N·f for integer f, inverse_wht should raise."""
    try:
        # F = [1, 0, 0, 0] is the WHT of f = [1/4, 1/4, 1/4, 1/4] (not integer)
        inverse_wht([1, 0, 0, 0])
        return "should raise"
    except ValueError:
        return True


def test_inverse_wht_round_trip():
    """For F = WHT(f) with integer f, inverse_wht(F) should return f."""
    f = [1, 2, 3, 4]
    F = fwht(f)
    f_back = inverse_wht(F)
    return f_back == f


def test_spectral_of_rejects_non_power_of_2():
    try:
        # 3x3 matrix — not a power-of-2 size
        from spectral_view import spectral_of
        spectral_of([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        return "should raise"
    except ValueError:
        return True


def test_spectral_of_rejects_non_square():
    try:
        from spectral_view import spectral_of
        spectral_of([[1, 0, 0, 0], [0, 1, 0, 0]])  # 2x4 not square
        return "should raise"
    except ValueError:
        return True


def test_element_order_helper():
    """_element_order should return 3 for z3_cycle, 2 for chirality_flip."""
    F = [10, 20, 30, 40]
    if _element_order(z3_cycle, F) != 3:
        return f"z3_cycle order should be 3"
    if _element_order(chirality_flip, F) != 2:
        return f"chirality_flip order should be 2"
    if _element_order(lambda x: list(x), F) != 1:
        return f"identity order should be 1"
    return True


# ============================================================
# v4: Algebraic representation as proof spine
# ============================================================

def test_fwht_rejects_non_power_of_2():
    try:
        fwht([1, 2, 3])
        return "should raise"
    except ValueError:
        return True


def test_a4z2_24_distinct_algebraic():
    return verify_algebraic_a4z2_has_24_distinct()


def test_s4_24_distinct_algebraic():
    return verify_algebraic_s4_has_24_distinct()


def test_a4z2_order_dist_algebraic():
    return verify_a4z2_algebraic_orders_match_expected()


def test_s4_order_dist_algebraic():
    return verify_s4_algebraic_orders_match_expected()


def test_a4z2_center_algebraic_is_2():
    return verify_a4z2_algebraic_center_is_2()


def test_s4_center_algebraic_is_trivial():
    return verify_s4_algebraic_center_is_trivial()


def test_a4z2_algebra_matches_vector():
    return verify_a4z2_algebra_matches_vector()


def test_s4_algebra_matches_vector():
    return verify_s4_algebra_matches_vector()


def test_a4z2_compose_associative():
    """Exhaustive over 24³ = 13,824 triples."""
    return verify_a4z2_compose_is_associative()


def test_s4_compose_associative():
    """Exhaustive over 24³ = 13,824 triples."""
    return verify_s4_compose_is_associative()


def test_a4z2_closure_excludes_transposition():
    """The architectural closure does NOT contain odd mask permutations."""
    return verify_a4z2_closure_disjoint_from_extra_transposition()


def test_m40_main_theorem():
    """v6 aggregator: M40 level-2 group is A_4 × Z_2, not S_4.

    The full chain in one verifier — see verify_m40_group_is_a4z2_not_s4
    docstring for the chain.
    """
    return verify_m40_group_is_a4z2_not_s4()


def test_a4z2_inverse_correct():
    return verify_a4z2_inverse_is_correct()


def test_s4_inverse_correct():
    return verify_s4_inverse_is_correct()


def test_a4z2_identity_is_unit():
    """A4Z2_IDENTITY is the identity element."""
    for g in a4z2_all_elements():
        if a4z2_compose(A4Z2_IDENTITY, g) != g:
            return f"left identity failed for {g}"
        if a4z2_compose(g, A4Z2_IDENTITY) != g:
            return f"right identity failed for {g}"
    return True


def test_s4_identity_is_unit():
    for g in s4_all_elements():
        if s4_compose(S4_IDENTITY, g) != g:
            return f"left identity failed for {g}"
        if s4_compose(g, S4_IDENTITY) != g:
            return f"right identity failed for {g}"
    return True


def test_a4z2_chirality_is_central_algebraic():
    """The chirality element (-1, 0, 0) commutes with everything."""
    chirality_alg = (-1, 0, 0)
    for g in a4z2_all_elements():
        if a4z2_compose(chirality_alg, g) != a4z2_compose(g, chirality_alg):
            return f"chirality doesn't commute with {g}"
    return True


def test_s3_composition_associative():
    """S_3 composition (used inside S_4) is associative."""
    samples = [
        (S3_I, S3_Z, S3_Z2),
        (S3_Z, S3_SWAP_0110, S3_Z2),
        (S3_SWAP_0110, S3_Z, S3_SWAP_0110),
    ]
    for a, b, c in samples:
        if s3_compose(s3_compose(a, b), c) != s3_compose(a, s3_compose(b, c)):
            return f"not associative on {a}, {b}, {c}"
    return True


def test_s3_z_has_order_3():
    """S_3 Z element has order 3."""
    return algebraic_order(S3_Z, s3_compose, S3_I) == 3


def test_s3_swap_has_order_2():
    """S_3 transposition has order 2."""
    return algebraic_order(S3_SWAP_0110, s3_compose, S3_I) == 2


# ============================================================
# v4: Architectural derivation by closure
# ============================================================

def test_architectural_primitives_generate_a4z2():
    """Closure of {T_m, Z, chirality} is order 24."""
    return verify_architectural_primitives_generate_a4z2()


def test_pure_s4_primitives_generate_s4():
    """Closure of {T_m, S_3 generators} is order 24 (S_4)."""
    return verify_pure_s4_primitives_generate_s4()


def test_adding_transposition_extends_to_48():
    """Closure of {T_m, Z, chirality} ∪ {one S_3 transposition} is order 48."""
    return verify_adding_transposition_extends_to_48()


def test_closure_without_z3_is_only_v4_z2():
    """{T_m, chirality} alone (no Z_3) generates V_4 × Z_2 of order 8."""
    F = [10, 20, 30, 40]
    generators = [
        ('T_1', lambda F: spectral_translation(F, 1)),
        ('T_2', lambda F: spectral_translation(F, 2)),
        ('T_3', lambda F: spectral_translation(F, 3)),
        ('chirality', chirality_flip),
    ]
    group = generate_group_by_action(generators, F, max_size=20)
    return len(group) == 8


# ============================================================
# Run
# ============================================================

def main():
    print("=" * 78)
    print("  verify_spectral.py — M40 spectral identifications")
    print("=" * 78)

    runner = TestRunner()

    print("\n[Hadamard matrix properties]")
    runner.run('hadamard_HHT_eq_NI_n2', test_hadamard_n2)
    runner.run('hadamard_HHT_eq_NI_n3', test_hadamard_n3)
    runner.run('hadamard_HHT_eq_NI_n4', test_hadamard_n4)
    runner.run('hadamard_dc_row_is_all_ones', test_hadamard_dc_row_is_all_ones)
    runner.run('hadamard_first_col_is_all_ones', test_hadamard_first_col_is_all_ones)

    print("\n[WHT round-trip]")
    runner.run('wht_involutory_n2', test_wht_involutory_n2)
    runner.run('wht_involutory_n3', test_wht_involutory_n3)

    print("\n[FWHT correctness]")
    runner.run('fwht_matches_direct_n2', test_fwht_matches_direct_n2)
    runner.run('fwht_matches_direct_n3', test_fwht_matches_direct_n3)
    runner.run('fwht_matches_direct_n4', test_fwht_matches_direct_n4)
    runner.run('fwht_arbitrary_vector_n3', test_fwht_arbitrary_vector_n3)

    print("\n[V_4 as frequency translation]")
    runner.run('v4_composes_by_xor', test_v4_translation_composes_by_xor_n2)
    runner.run('v4_self_inverse', test_v4_translation_is_self_inverse)
    runner.run('v4_identity_no_op', test_v4_translation_identity_is_no_op)

    print("\n[Z_2 as phase inversion]")
    runner.run('chirality_involutive', test_chirality_involutive)
    runner.run('chirality_negates', test_chirality_negates)

    print("\n[Commutativity]")
    runner.run('v4_commutes_with_chirality', test_v4_commutes_with_chirality)

    print("\n[Spectral matrix composition = V_4 algebra]")
    runner.run('V_alpha_x_V_beta_eq_V_gamma', test_v_alpha_times_v_beta_is_v_gamma)
    runner.run('V_alpha_squared_eq_I', test_v_alpha_squared_is_identity)
    runner.run('v4_matrices_are_permutations', test_v4_matrices_are_permutations)
    runner.run('chirality_matrix_is_minus_I', test_chirality_matrix_is_minus_I)
    runner.run('chirality_squared_eq_I', test_chirality_squared_is_identity)

    print("\n[v2: DC normalization]")
    runner.run('dc_is_sum_n2', test_dc_is_sum_n2)
    runner.run('dc_is_sum_n3', test_dc_is_sum_n3)
    runner.run('dc_explicit_value', test_dc_explicit_value)

    print("\n[v2: character function]")
    runner.run('chi_dc_is_one', test_chi_dc_is_one)
    runner.run('chi_symmetric', test_chi_symmetric)
    runner.run('chi_multiplicative', test_chi_multiplicative_in_first_arg)

    print("\n[v2: point/spectral duality]")
    runner.run('point_trans_to_spec_mod_n2', test_point_translation_to_spectral_modulation_n2)
    runner.run('point_trans_to_spec_mod_n3', test_point_translation_to_spectral_modulation_n3)
    runner.run('point_mod_to_spec_trans_n2', test_point_modulation_to_spectral_translation_n2)
    runner.run('point_mod_to_spec_trans_n3', test_point_modulation_to_spectral_translation_n3)
    runner.run('point_translation_composes_xor', test_point_translation_composes_by_xor)
    runner.run('point_modulation_self_inverse', test_point_modulation_self_inverse)
    runner.run('spectral_modulation_self_inverse', test_spectral_modulation_self_inverse)

    print("\n[v2: Z_3 cycle on nonzero spectral masks]")
    runner.run('z3_cubed_is_identity', test_z3_cubed_is_identity)
    runner.run('z3_inverse_correct', test_z3_inverse_correct)
    runner.run('z3_inverse_equals_z_squared', test_z3_inverse_equals_z_squared)
    runner.run('z3_fixes_dc', test_z3_fixes_dc)
    runner.run('z3_permutes_nonzero_masks', test_z3_permutes_nonzero_masks)
    runner.run('z3_conjugates_v4_by_cycle', test_z3_conjugates_v4_by_cycle)
    runner.run('z3_commutes_with_chirality', test_z3_commutes_with_chirality)
    runner.run('z3_cycle_matrix_is_permutation', test_z3_cycle_matrix_is_permutation)
    runner.run('z3_rejects_non_level_2', test_z3_rejects_non_level_2)

    print("\n[v2: A_4 = V_4 ⋊ Z_3 group structure]")
    runner.run('a4_order_is_12', test_a4_order_is_12)
    runner.run('a4_closure_under_composition', test_a4_closure_under_composition)
    runner.run('a4_times_z2_order_is_24', test_a4_times_z2_order_is_24)
    runner.run('a4_identity_in_set', test_a4_identity_is_in_set)

    print("\n[v2: operator conjugation]")
    runner.run('spectral_of_point_trans_is_mod', test_spectral_of_point_translation_is_modulation)
    runner.run('chirality_is_minus_I_in_both', test_chirality_in_point_view_is_minus_I_in_spectral)

    print("\n[v3: S_3 transpositions (the odd elements M40 excludes)]")
    runner.run('s3_transpositions_involutive', test_s3_transpositions_involutive)
    runner.run('s3_has_6_elements', test_s3_has_6_elements)
    runner.run('s3_fixes_dc', test_s3_fixes_dc)
    runner.run('s3_swap_01_10_fixes_11', test_s3_swap_01_10_fixes_11)
    runner.run('s3_swap_01_11_fixes_10', test_s3_swap_01_11_fixes_10)
    runner.run('s3_swap_10_11_fixes_01', test_s3_swap_10_11_fixes_01)

    print("\n[v3: A_4 × Z_2 vs S_4 — both order 24, NON-isomorphic]")
    runner.run('a4_z2_has_24_distinct', test_a4_z2_has_24_distinct)
    runner.run('s4_has_24_distinct', test_s4_has_24_distinct)
    runner.run('a4_z2_order_dist_correct', test_a4_z2_order_distribution)
    runner.run('s4_order_dist_correct', test_s4_order_distribution)
    runner.run('a4_z2_no_order_4', test_a4_z2_no_order_4)
    runner.run('s4_has_order_4', test_s4_has_order_4)
    runner.run('a4_z2_center_is_2', test_a4_z2_center_is_2)
    runner.run('s4_center_is_1', test_s4_center_is_1)
    runner.run('a4_z2_not_iso_s4', test_a4_z2_not_iso_s4)
    runner.run('a4_z2_orders_sum_to_24', test_a4_z2_total_orders_sum_to_24)
    runner.run('s4_orders_sum_to_24', test_s4_total_orders_sum_to_24)

    print("\n[v3: code-level hardening]")
    runner.run('inverse_wht_rejects_non_pow_2', test_inverse_wht_rejects_non_power_of_2)
    runner.run('inverse_wht_rejects_non_divisible', test_inverse_wht_rejects_non_divisible)
    runner.run('inverse_wht_round_trip', test_inverse_wht_round_trip)
    runner.run('spectral_of_rejects_non_pow_2', test_spectral_of_rejects_non_power_of_2)
    runner.run('spectral_of_rejects_non_square', test_spectral_of_rejects_non_square)
    runner.run('element_order_helper', test_element_order_helper)
    runner.run('fwht_rejects_non_power_of_2', test_fwht_rejects_non_power_of_2)

    print("\n[v4: Algebraic representation as proof spine]")
    runner.run('a4z2_24_distinct_algebraic', test_a4z2_24_distinct_algebraic)
    runner.run('s4_24_distinct_algebraic', test_s4_24_distinct_algebraic)
    runner.run('a4z2_order_dist_algebraic', test_a4z2_order_dist_algebraic)
    runner.run('s4_order_dist_algebraic', test_s4_order_dist_algebraic)
    runner.run('a4z2_center_algebraic_is_2', test_a4z2_center_algebraic_is_2)
    runner.run('s4_center_algebraic_is_trivial', test_s4_center_algebraic_is_trivial)
    runner.run('a4z2_algebra_matches_vector', test_a4z2_algebra_matches_vector)
    runner.run('s4_algebra_matches_vector', test_s4_algebra_matches_vector)
    runner.run('a4z2_compose_associative', test_a4z2_compose_associative)
    runner.run('s4_compose_associative', test_s4_compose_associative)
    runner.run('a4z2_inverse_correct', test_a4z2_inverse_correct)
    runner.run('s4_inverse_correct', test_s4_inverse_correct)
    runner.run('a4z2_identity_is_unit', test_a4z2_identity_is_unit)
    runner.run('s4_identity_is_unit', test_s4_identity_is_unit)
    runner.run('a4z2_chirality_central_alg', test_a4z2_chirality_is_central_algebraic)
    runner.run('s3_composition_associative', test_s3_composition_associative)
    runner.run('s3_z_has_order_3', test_s3_z_has_order_3)
    runner.run('s3_swap_has_order_2', test_s3_swap_has_order_2)

    print("\n[v4: Architectural derivation by closure]")
    runner.run('arch_primitives_gen_a4z2', test_architectural_primitives_generate_a4z2)
    runner.run('pure_s4_primitives_gen_s4', test_pure_s4_primitives_generate_s4)
    runner.run('adding_transposition_to_48', test_adding_transposition_extends_to_48)
    runner.run('no_z3_gives_v4_z2_order_8', test_closure_without_z3_is_only_v4_z2)
    runner.run('a4z2_closure_excludes_transposition', test_a4z2_closure_excludes_transposition)

    print("\n[v6: M40 main theorem (aggregator)]")
    runner.run('M40_GROUP_IS_A4Z2_NOT_S4', test_m40_main_theorem)

    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print()
    runner.summary()
    print()


if __name__ == "__main__":
    main()
