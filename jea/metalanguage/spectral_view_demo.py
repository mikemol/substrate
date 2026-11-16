# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""
spectral_view_demo.py — the printed walkthrough for `spectral_view`.

⚑ SPLIT FROM `spectral_view.py` (2026-08-11, size rule: 1200 code lines).
   `spectral_view.py` measured 1233 code lines / 105 defs — 33 over cap.
   The seam is exact and PRE-EXISTING, not invented for the split: every
   def in that module is a pure-arithmetic library function EXCEPT
   `fmt_matrix` and `demo`, which between them are ~330 lines of `print`
   and were reachable ONLY from the `__main__` guard.  `--calls demo`
   showed zero callers outside that guard.  Nothing below is new; it is
   the original bytes, relocated.

   `python3 spectral_view.py` still runs this walkthrough — the parent
   module re-exports `fmt_matrix`/`demo` and keeps its `__main__` guard,
   so every public name and every entry point is where it was.
"""

from spectral_view import (
    _GROUP_TEST_VECTOR,
    _apply_a4_element,
    A4Z2_IDENTITY,
    S4_IDENTITY,
    a4z2_all_elements,
    a4z2_compose,
    a4z2_name,
    algebraic_center,
    algebraic_order_distribution,
    architectural_primitives_level_2,
    chirality_flip,
    compute_group_center,
    compute_order_distribution,
    enumerate_a4_z2_elements,
    enumerate_s4_elements,
    fwht,
    generate_group_by_action,
    hadamard_matrix,
    matmat,
    point_modulation,
    point_translation,
    s3_swap_01_10,
    s3_swap_01_11,
    s3_swap_10_11,
    s4_all_elements,
    s4_compose,
    s4_name,
    spectral_modulation,
    spectral_translation,
    transpose,
    verify_m40_group_is_a4z2_not_s4,
    verify_spectral_of_point_translation_is_spectral_modulation,
    z3_cycle,
    z3_cycle_inverse,
)


# ============================================================
# Demo
# ============================================================


def fmt_matrix(M, sign_only=False):
    if sign_only:
        return "\n".join(
            "  " + " ".join("+" if x > 0 else ("-" if x < 0 else "0") for x in row) for row in M
        )
    return "\n".join("  " + " ".join(f"{x:+3d}" for x in row) for row in M)


def demo():
    print("=" * 78)
    print("  spectral_view.py — M40 (v2): three-view discipline,")
    print("                                point/spectral duality, A_4 = V_4 ⋊ Z_3")
    print("=" * 78)
    print()

    # ============================================================
    # Three-view invariant
    # ============================================================
    print("=" * 78)
    print("  Three-view discipline (load-bearing)")
    print("=" * 78)
    print("""
  POINT view       f[x]                  function on F_2^n
  SPECTRAL view    F[k] = Σ_x χ_k(x)f[x]  Hadamard coefficients
  OPERATOR view    M and spectral(M)=HMH⁻¹  linear maps with conjugation

  Dualities:
    point_translation(·, a)   ↔ spectral_modulation(·, a)
    point_modulation(·, m)    ↔ spectral_translation(·, m)
""")

    # ============================================================
    # Hadamard
    # ============================================================
    print("=" * 78)
    print("  Level 2 Hadamard matrix H_4")
    print("=" * 78)
    print()
    H = hadamard_matrix(n=2)
    print(fmt_matrix(H, sign_only=True))
    print()
    print("  Row k = 00 is all +1 — the DC character χ_00.")
    print("  H · H^T = N · I = 4 · I:")
    print()
    HHT = matmat(H, transpose(H))
    print(fmt_matrix(HHT))

    # ============================================================
    # Duality demonstration
    # ============================================================
    print()
    print("=" * 78)
    print("  Dualities under WHT (the v1 confusion, made explicit)")
    print("=" * 78)
    print()
    f = [1, 2, 3, 4]
    F = fwht(f)
    print(f"  f = {f}")
    print(f"  F = WHT(f) = {F}")
    print(f"             F[0] = {F[0]} = sum(f) = {sum(f)}   (DC SUM, not mean)")
    print(f"             mean(f) = F[0]/N = {F[0]}/4 = {F[0] // 4}")
    print()

    print("  Point translation f[x] ↦ f[x ⊕ 01]:")
    f_pt = point_translation(f, 0b01)
    print(f"    f'(x) = {f_pt}")
    print(f"    WHT(f') = {fwht(f_pt)}")
    print()
    print("  Spectral modulation F[k] ↦ χ_01(k) · F[k]:")
    F_smod = spectral_modulation(F, 0b01)
    print(f"    F'(k) = {F_smod}")
    print(f"  These are EQUAL: {fwht(f_pt) == F_smod}")
    print()

    print("  Point modulation f[x] ↦ χ_01(x) · f[x]:")
    f_pmod = point_modulation(f, 0b01)
    print(f"    f'(x) = {f_pmod}")
    print(f"    WHT(f') = {fwht(f_pmod)}")
    print()
    print("  Spectral translation F[k] ↦ F[k ⊕ 01]:")
    F_st = spectral_translation(F, 0b01)
    print(f"    F'(k) = {F_st}")
    print(f"  These are EQUAL: {fwht(f_pmod) == F_st}")

    # ============================================================
    # Z_3 cycle on nonzero masks
    # ============================================================
    print()
    print("=" * 78)
    print("  Z_3 cycle on nonzero spectral masks (NEW v2)")
    print("=" * 78)
    print()
    print(f"  Cycle:  01 → 10 → 11 → 01  (00 fixed)")
    print()
    print(f"  F        = {F}")
    print(f"  Z(F)     = {z3_cycle(F)}")
    print(f"  Z²(F)    = {z3_cycle(z3_cycle(F))}")
    print(f"  Z³(F)    = {z3_cycle(z3_cycle(z3_cycle(F)))}   (back to F)")
    print()
    print(f"  Z fixes DC:         {z3_cycle(F)[0] == F[0]}")
    print(f"  Z³ = I:             {z3_cycle(z3_cycle(z3_cycle(F))) == F}")
    print(f"  Z² = Z^{{-1}}:        {z3_cycle(z3_cycle(F)) == z3_cycle_inverse(F)}")
    print()
    print(f"  Semidirect relation: Z · T_m · Z^{{-1}} = T_{{cycle(m)}}")
    print()
    print(f"  {'m':>4} {'cycle(m)':>10}  Z T_m Z⁻¹(F) == T_cycle(m)(F)?")
    cycle_map = {0b01: 0b10, 0b10: 0b11, 0b11: 0b01}
    for m, mc in cycle_map.items():
        lhs = z3_cycle(spectral_translation(z3_cycle_inverse(F), m))
        rhs = spectral_translation(F, mc)
        ok = lhs == rhs
        print(f"  {bin(m)[2:].zfill(2):>4} {bin(mc)[2:].zfill(2):>10}  {ok}")

    # ============================================================
    # A_4 = V_4 ⋊ Z_3 group structure
    # ============================================================
    print()
    print("=" * 78)
    print("  A_4 = V_4 ⋊ Z_3 has order 12 (NEW v2)")
    print("=" * 78)
    print()
    F_test = [10, 20, 30, 40]
    outputs = []
    for j in range(3):
        for m in range(4):
            out = _apply_a4_element(F_test, m, j)
            outputs.append((j, m, out))

    print(f"  Enumerating T_m · Z^j for m ∈ {{0..3}}, j ∈ {{0..2}}:")
    print()
    print(f"  {'j':>2} {'m':>4}  {'T_m · Z^j (F_test)':>26}")
    for j, m, out in outputs:
        print(f"  {j:>2} {m:>4}  {str(out):>26}")
    print()
    distinct = set(tuple(o[2]) for o in outputs)
    print(f"  Distinct outputs: {len(distinct)}  (expected 12 = |A_4|)")
    print()
    print(f"  With chirality: A_4 × Z_2 has order 24. This matches the")
    print(f"  M38 unified-address codeword count exactly: the level-2")
    print(f"  architectural symmetry group is A_4 × Z_2.")
    print()

    chirality_outputs = set(tuple(chirality_flip(list(o))) for o in distinct)
    full = distinct | chirality_outputs
    print(f"  |A_4 × Z_2| at level 2 = {len(full)}  (expected 24)")

    # ============================================================
    # v3: Two 24-element groups at level 2
    # ============================================================
    print()
    print("=" * 78)
    print("  v3: A_4 × Z_2 vs S_4 — both order 24, NON-isomorphic")
    print("=" * 78)
    print()
    print("  GL_2(F_2) ≅ S_3 has 6 elements: identity, 3 transpositions, 2 cycles.")
    print("  Two natural 24-element extensions of V_4:")
    print()
    print("    (A) V_4 ⋊ Z_3 × Z_2  =  A_4 × Z_2     (M40's choice — implemented)")
    print("    (B) V_4 ⋊ GL_2(F_2)  =  V_4 ⋊ S_3  =  S_4  (= AGL_2(F_2))")
    print()
    print("  Both have order 24, but they are NOT isomorphic.")
    print()

    test_F = _GROUP_TEST_VECTOR
    dist_a4z2 = compute_order_distribution(enumerate_a4_z2_elements(), test_F)
    dist_s4 = compute_order_distribution(enumerate_s4_elements(), test_F)

    print(f"  Element-order distribution:")
    print(f"    A_4 × Z_2:  {dist_a4z2}")
    print(f"    S_4:        {dist_s4}")
    print()
    print(f"    → A_4 × Z_2 has NO order-4 elements")
    print(f"    → S_4 has 6 order-4 elements (the 4-cycles)")
    print()

    center_a4z2 = compute_group_center(enumerate_a4_z2_elements(), test_F)
    center_s4 = compute_group_center(enumerate_s4_elements(), test_F)

    print(f"  Center order (commuting with all elements):")
    print(f"    |Z(A_4 × Z_2)| = {len(center_a4z2)}  ({', '.join(center_a4z2)})")
    print(f"    |Z(S_4)|       = {len(center_s4)}   ({', '.join(center_s4)})")
    print()
    # ============================================================
    # v4: Algebraic representation as the proof spine
    # ============================================================
    print()
    print("=" * 78)
    print("  v4: Algebraic representation (proof spine independent of test data)")
    print("=" * 78)
    print()
    print("  A_4 × Z_2 element: (sign, m, j) ∈ {±1} × F_2² × Z_3")
    print("  S_4 element:       (m, σ)        where σ ∈ S_3 = GL_2(F_2)")
    print()
    print("  Composition laws (derived from semidirect product structure):")
    print()
    print("    (s_g, m_g, j_g) · (s_h, m_h, j_h)")
    print("       = (s_g · s_h,  m_g ⊕ σ^{j_g}(m_h),  (j_g + j_h) mod 3)")
    print()
    print("    (m_g, σ_g) · (m_h, σ_h)")
    print("       = (m_g ⊕ σ_g(m_h),  σ_g ∘ σ_h)")
    print()
    print("  Algebraic invariants (independent of any test vector):")
    print()
    alg_dist_a4z2 = algebraic_order_distribution(a4z2_all_elements(), a4z2_compose, A4Z2_IDENTITY)
    alg_dist_s4 = algebraic_order_distribution(s4_all_elements(), s4_compose, S4_IDENTITY)
    alg_cen_a4z2 = algebraic_center(a4z2_all_elements(), a4z2_compose)
    alg_cen_s4 = algebraic_center(s4_all_elements(), s4_compose)

    print(f"    A_4 × Z_2 order distribution:  {alg_dist_a4z2}")
    print(f"    S_4       order distribution:  {alg_dist_s4}")
    print()
    print(f"    A_4 × Z_2 center: {[a4z2_name(g) for g in alg_cen_a4z2]}")
    print(f"    S_4       center: {[s4_name(g) for g in alg_cen_s4]}")
    print()
    print("  These are computed from composition tables, not from vector action.")

    # ============================================================
    # v4: Architectural derivation by closure
    # ============================================================
    print()
    print("=" * 78)
    print("  v4: Architectural derivation — the conditional claim")
    print("=" * 78)
    print()
    print("  CONDITIONAL CLAIM (proven below):")
    print("    GIVEN the architectural primitives at level 2 are")
    print("        {V_4 translations T_1, T_2, T_3; Z_3 cycle Z; chirality},")
    print("    THE GROUP GENERATED is A_4 × Z_2 (order 24), not S_4.")
    print()
    print("  The architectural exclusion of S_3 transpositions is an")
    print("  ASSUMED rule, not derived here. This module proves the")
    print("  consequence under that assumption.")
    print()

    F_arch = [10, 20, 30, 40]
    g_arch = generate_group_by_action(architectural_primitives_level_2(), F_arch, max_size=50)
    g_pure_s4 = generate_group_by_action(
        [
            ("T_1", lambda F: spectral_translation(F, 1)),
            ("T_2", lambda F: spectral_translation(F, 2)),
            ("T_3", lambda F: spectral_translation(F, 3)),
            ("Z", z3_cycle),
            ("(01 10)", s3_swap_01_10),
            ("(01 11)", s3_swap_01_11),
            ("(10 11)", s3_swap_10_11),
        ],
        F_arch,
        max_size=50,
    )
    g_extended = generate_group_by_action(
        architectural_primitives_level_2() + [("(01 10)", s3_swap_01_10)], F_arch, max_size=100
    )

    print(f"  Closure tests (from V_4 translations + ...):")
    print(f"    + Z + chirality                         → |G| = {len(g_arch)}  (= A_4 × Z_2)")
    print(f"    + full S_3 (no chirality)                → |G| = {len(g_pure_s4)}  (= S_4)")
    print(f"    + Z + chirality + one S_3 transposition  → |G| = {len(g_extended)}  (= S_4 × Z_2)")
    print()
    print("  M40 selects the first closure (24 elements, A_4 × Z_2).")
    print("  An architecture admitting odd mask permutations would land")
    print("  in either the second (24, S_4) or third (48, S_4 × Z_2) row.")

    # ============================================================
    # v6: theorem-style aggregator
    # ============================================================
    print()
    print("=" * 78)
    print("  v6: M40 main theorem (one-line verification)")
    print("=" * 78)
    print()
    print("  THEOREM (M40 level-2 group identity):")
    print()
    print("    Given admissible generators {V_4 translations, Z_3 cycle,")
    print("    chirality}, the generated group is A_4 × Z_2, distinguishable")
    print("    from S_4 by both center order (2 vs 1) and element-order")
    print("    distribution. Adding any S_3 transposition collapses this")
    print("    identity by extending the closure to S_4 × Z_2 (order 48).")
    print()
    print(f"  verify_m40_group_is_a4z2_not_s4(): {verify_m40_group_is_a4z2_not_s4()}")
    print()
    print("  The architecturally meaningful invariant is the center:")
    print("    |Z(A_4 × Z_2)| = 2 captures the design intent that")
    print("    CHIRALITY IS CENTRAL. |Z(S_4)| = 1 fails this property.")

    # ============================================================
    # Operator conjugation
    # ============================================================
    print()
    print("=" * 78)
    print("  Operator-view: spectral(point_translation_a) = spectral_modulation_a")
    print("=" * 78)
    print()
    print(f"  H · T_a^{{point}} · H^{{-1}} = D_{{χ_a}}^{{spectral}}")
    print(f"  i.e. conjugation of point translation by WHT yields")
    print(f"  the diagonal sign-modulation matrix.")
    print()
    print(
        f"  Verified at level 2 for all a ∈ {{0,1,2,3}}: "
        f"{verify_spectral_of_point_translation_is_spectral_modulation()}"
    )

    # ============================================================
    # Summary
    # ============================================================
    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print("""
  v2 closes v1's three confusions:

  1. Three coordinate systems are now explicit:
     point f[x], spectral F[k], operator M↔HMH⁻¹.

  2. Dualities are stated and verified:
       point_translation ⟷ spectral_modulation
       point_modulation  ⟷ spectral_translation
     They are NOT the same operation — they are duals under WHT.

  3. F[0] is the DC SUM (= Σ_x f[x]), not the mean.
     mean(f) = F[0] / N.

  4. Z_3 is now actually implemented as a permutation of the three
     nonzero spectral indices: 01 → 10 → 11 → 01. The semidirect
     relation Z · T_m · Z⁻¹ = T_{cycle(m)} is verified.

  5. The level-2 architectural symmetry group is identified:
     V_4 ⋊ Z_3 ≅ A_4 (order 12), and with chirality:
     A_4 × Z_2 (order 24) — matching the M38 codeword count.
""")


if __name__ == "__main__":
    demo()
