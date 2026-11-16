# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""
spectral_view.py — M40 (v6): closure-equals-algebraic, exhaustive
associativity, theorem-style aggregator, refined architectural framing.

v1 — Hadamard substrate, FWHT, V_4 translation, chirality flip
v2 — three-view discipline (point/spectral/operator), point/spectral
     duality, Z_3 implementation, A_4 group structure, A_4 × Z_2 =
     architectural 24-op symmetry group
v3 — distinguish A_4 × Z_2 from S_4; both order 24 at level 2 but
     non-isomorphic. Code-level hardening (divisibility assertions,
     power-of-2 checks, ordering conventions)
v4 — algebraic tuple representations as proof spine; vector action as
     visualization. Architectural derivation as conditional claim
     via closure under composition
v5 — closure-equals-algebraic verification (which 24, constructively),
     exhaustive associativity over all 24³ triples, dead code cleanup
v6 — theorem-style aggregator (verify_m40_group_is_a4z2_not_s4),
     refined architectural framing, header alignment

═══════════════════════════════════════════════════════════════════════════════
  TWO 24-ELEMENT GROUPS AT LEVEL 2 (v6 — refined framing)
═══════════════════════════════════════════════════════════════════════════════

At level 2, the linear action on the three nonzero spectral masks
{01, 10, 11} is governed by GL_2(F_2) ≅ S_3 (6 elements: identity,
3 transpositions, 2 cycles). The contrast between M40's group and
the full affine alternative is NOT "two ways of choosing 6 vs 3
extensions of V_4." It is:

  (A) M40's choice:    ORIENTED AFFINE-EVEN CLOSURE
                       PLUS EXTERNAL CENTRAL CHIRALITY

      V_4 ⋊ Z_3 ≅ A_4                                (order 12)
      A_4 × Z_2 = (V_4 ⋊ Z_3) × Z_2                  (order 24)

      The Z_3 is the EVEN subgroup of GL_2(F_2) — the oriented cycle
      action on nonzero masks. The Z_2 is a SEPARATE external factor
      (chirality / global sign), placed in the CENTER of the group.

  (B) Full affine choice: ALL OF GL_2(F_2), NO CHIRALITY

      V_4 ⋊ GL_2(F_2) ≅ V_4 ⋊ S_3 ≅ S_4              (order 24)
      Equivalently AGL_2(F_2).

      All 6 of GL_2(F_2)'s elements are admissible, including the 3
      odd transpositions. No external sign factor.

The two reach 24 from V_4 via different structural moves:
  (A) doubles 12 by an external central factor
  (B) extends V_4 by a larger linear action

Their non-isomorphism is witnessed by:

      |Z(A_4 × Z_2)|  =  2   (chirality is central)
      |Z(S_4)|        =  1   (trivial center)

The center order is the architecturally meaningful invariant: it
directly captures M40's design intent that CHIRALITY IS CENTRAL.
Element-order distribution provides an independent witness:

      A_4 × Z_2:   {1: 1,  2: 7,  3: 8,  6: 8}    no order-4 elements
      S_4:         {1: 1,  2: 9,  3: 8,  4: 6}    has 6 order-4

M40 selects option (A) by intentional architectural choice. The
admissibility rule "odd mask permutations are excluded from level-2
operations" is an architectural axiom — observable in this module
(the closure of admissible generators does not contain any swap
action) but not derived here. The derivation would require an audit
of the M30-M37 operation registry.

═══════════════════════════════════════════════════════════════════════════════
  THREE-VIEW DISCIPLINE (M40 v2 — preserved)
═══════════════════════════════════════════════════════════════════════════════

This module distinguishes three coordinate systems and keeps them separate:

  (1) POINT view
      f[x] is a function on F_2^n, x ∈ {0, ..., 2^n - 1}.

  (2) SPECTRAL view
      F[k] = Σ_x (-1)^{k·x} f[x]
      where k·x is the bit-parity of (k AND x) — the character χ_k(x).
      This is the unnormalized Walsh-Hadamard transform.

  (3) OPERATOR view
      A linear map M on point-space has a spectral image:
          spectral(M) = H · M · H^{-1}
      where H^{-1} = (1/N) · H under the unnormalized convention
      (since H · H = N · I).

  DUALITIES under WHT:

      Point translation:    f'[x] = f[x ⊕ a]
        ⇔ Spectral modulation:  F'[k] = χ_a(k) · F[k]

      Point modulation:     f'[x] = χ_m(x) · f[x]
        ⇔ Spectral translation: F'[k] = F[k ⊕ m]

  NORMALIZATION NOTE:
      Under the unnormalized WHT used here:
          F[0] = Σ_x f[x]   (the DC SUM, not the mean)
          mean(f) = F[0] / N
      Recovery: f = (1/N) · H · F.
"""

from typing import List, Tuple


# ============================================================
# Hadamard matrix and (Fast) Walsh-Hadamard Transform
# ============================================================


def hadamard_matrix(n: int) -> List[List[int]]:
    """Build the 2^n × 2^n Hadamard matrix. H[k][x] = (-1)^{k·x}."""
    N = 2**n
    H = [[0] * N for _ in range(N)]
    for k in range(N):
        for x in range(N):
            H[k][x] = -1 if (bin(k & x).count("1") % 2) else 1
    return H


def matvec(M: List[List[int]], v: List[int]) -> List[int]:
    N = len(v)
    return [sum(M[i][j] * v[j] for j in range(N)) for i in range(N)]


def matmat(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    N = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(N)) for j in range(N)] for i in range(N)]


def transpose(M: List[List[int]]) -> List[List[int]]:
    N = len(M)
    return [[M[j][i] for j in range(N)] for i in range(N)]


def identity(N: int) -> List[List[int]]:
    return [[1 if i == j else 0 for j in range(N)] for i in range(N)]


def fwht(f: List[int]) -> List[int]:
    """Fast Walsh-Hadamard Transform via butterfly. O(N log N).

    Unnormalized convention: F[0] = sum(f). Inverse needs ÷ N.

    v4: Validates that len(f) is a power of 2.
    """
    f = list(f)
    N = len(f)
    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError(f"fwht requires length 2^n; got N={N}")
    h = 1
    while h < N:
        for i in range(0, N, h * 2):
            for j in range(i, i + h):
                x, y = f[j], f[j + h]
                f[j] = x + y
                f[j + h] = x - y
        h *= 2
    return f


def inverse_wht(F: List[int]) -> List[int]:
    """Inverse WHT under unnormalized convention: f = (1/N) · H · F.

    v3: Asserts that the result is exactly divisible by N. Raises
    ValueError if not — callers must ensure F is a valid WHT output
    (or use rationals/floats for general F).
    """
    N = len(F)
    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError(f"inverse_wht requires length 2^n; got N={N}")
    raw = fwht(F)
    bad = [v for v in raw if v % N != 0]
    if bad:
        raise ValueError(
            f"inverse_wht: H·F not exactly divisible by N={N}; "
            f"non-divisible entries: {bad[:5]}{'...' if len(bad) > 5 else ''}"
        )
    return [v // N for v in raw]


# ============================================================
# Characters
# ============================================================


def chi(a: int, x: int) -> int:
    """The character χ_a(x) = (-1)^{a·x}, where a·x is bit-AND parity."""
    return -1 if bin(a & x).count("1") % 2 else 1


# ============================================================
# POINT VIEW operations (v2)
# ============================================================


def point_translation(f: List[int], a: int) -> List[int]:
    """Point-domain translation: f'[x] = f[x ⊕ a].

    Under WHT, this is dual to spectral_modulation by χ_a:
        WHT(point_translation(f, a)) = spectral_modulation(WHT(f), a)
    """
    N = len(f)
    return [f[x ^ a] for x in range(N)]


def point_modulation(f: List[int], m: int) -> List[int]:
    """Pointwise multiplication by character: f'[x] = χ_m(x) · f[x].

    Under WHT, this is dual to spectral_translation by m:
        WHT(point_modulation(f, m)) = spectral_translation(WHT(f), m)
    """
    N = len(f)
    return [f[x] * chi(m, x) for x in range(N)]


# ============================================================
# SPECTRAL VIEW operations (v2 — explicit naming)
# ============================================================


def spectral_translation(F: List[int], m: int) -> List[int]:
    """Spectral translation: F'[k] = F[k ⊕ m].

    Dual of point_modulation under WHT. This is the operation v1 called
    `v4_translation`; preserved here under both names.
    """
    N = len(F)
    return [F[k ^ m] for k in range(N)]


# v1 alias preserved for backward compatibility
v4_translation = spectral_translation


def spectral_modulation(F: List[int], a: int) -> List[int]:
    """Spectral modulation: F'[k] = χ_a(k) · F[k].

    Dual of point_translation under WHT.
    """
    N = len(F)
    return [F[k] * chi(a, k) for k in range(N)]


def chirality_flip(F: List[int]) -> List[int]:
    """Z_2 chirality: F ↦ -F. Global sign inversion.

    OBSERVABILITY NOTE: This is a real Z_2 action only if global sign is
    observable in the architecture. If the architecture quotients global
    sign (e.g. only cares about |F[k]| or F[k]²), chirality is trivial.
    The M38/M40 architecture treats signed F as observable, so chirality
    is a real Z_2 here and contributes the Z_2 factor in A_4 × Z_2.
    """
    return [-x for x in F]


# ============================================================
# Z_3 cycle (NEW v2 — actually implemented)
# ============================================================


def z3_cycle(F: List[int]) -> List[int]:
    """Z_3 permutation on level-2 spectral coefficients.

    Cycle on nonzero masks: 01 → 10 → 11 → 01 (00 fixed).

    Pullback convention: (Z F)[k] = F[cycle^{-1}(k)].
    With cycle: 01→10, 10→11, 11→01, the inverse permutation
    sends 01→11, 10→01, 11→10. So:
        (Z F)[00] = F[00]
        (Z F)[01] = F[11]
        (Z F)[10] = F[01]
        (Z F)[11] = F[10]

    Only defined at level 2 currently. Higher-level Z_3 would require
    selecting a specific 3-cycle within GL_n(F_2)'s action on F_2^n \\ {0}.
    """
    if len(F) != 4:
        raise ValueError(f"z3_cycle requires level 2 (N=4), got N={len(F)}")
    return [F[0], F[3], F[1], F[2]]


def z3_cycle_inverse(F: List[int]) -> List[int]:
    """Inverse Z_3: cycle on nonzero masks is 01 → 11 → 10 → 01.

    Equals Z² since Z is order 3.
    """
    if len(F) != 4:
        raise ValueError(f"z3_cycle_inverse requires level 2, got N={len(F)}")
    return [F[0], F[2], F[3], F[1]]


# ============================================================
# S_3 transpositions on nonzero spectral masks (v3)
# ============================================================
#
# GL_2(F_2) ≅ S_3 has 6 elements: identity, 3 transpositions, 2 cycles.
# The transpositions are the odd elements that M40 does NOT include in
# its architectural Z_3 — they would extend the level-2 group from
# A_4 × Z_2 (current choice) to S_4 (full affine choice).
#
# Each transposition is the linear map on F_2^2 swapping two nonzero
# masks while fixing the third (and 00).


def s3_swap_01_10(F: List[int]) -> List[int]:
    """Transposition swap(01, 10) on nonzero masks. Fixes 11 (since 01⊕10=11).

    As a linear map L: 01 ↦ 10, 10 ↦ 01, hence 11 = 01⊕10 ↦ 10⊕01 = 11. ✓
    """
    if len(F) != 4:
        raise ValueError(f"requires level 2, got N={len(F)}")
    return [F[0], F[2], F[1], F[3]]


def s3_swap_01_11(F: List[int]) -> List[int]:
    """Transposition swap(01, 11). Fixes 10.

    As a linear map: 01 ↦ 11, then 11 ↦ 01, and 10 = 01⊕11 ↦ 11⊕01 = 10. ✓
    """
    if len(F) != 4:
        raise ValueError(f"requires level 2, got N={len(F)}")
    return [F[0], F[3], F[2], F[1]]


def s3_swap_10_11(F: List[int]) -> List[int]:
    """Transposition swap(10, 11). Fixes 01."""
    if len(F) != 4:
        raise ValueError(f"requires level 2, got N={len(F)}")
    return [F[0], F[1], F[3], F[2]]


def s3_elements():
    """Return the 6 elements of S_3 = GL_2(F_2) as (name, callable) pairs."""
    return [
        ("I", lambda F: list(F)),
        ("Z", z3_cycle),
        ("Z^2", z3_cycle_inverse),
        ("(01 10)", s3_swap_01_10),
        ("(01 11)", s3_swap_01_11),
        ("(10 11)", s3_swap_10_11),
    ]


# ============================================================
# OPERATOR VIEW: matrices
# ============================================================


def v4_translation_matrix(m: int, n: int) -> List[List[int]]:
    """Permutation matrix for spectral_translation by mask m."""
    N = 2**n
    P = [[0] * N for _ in range(N)]
    for k in range(N):
        P[k][k ^ m] = 1
    return P


def chirality_flip_matrix(n: int) -> List[List[int]]:
    """-I matrix for chirality."""
    N = 2**n
    return [[-1 if i == j else 0 for j in range(N)] for i in range(N)]


def z3_cycle_matrix() -> List[List[int]]:
    """Permutation matrix for z3_cycle at level 2.

    P[k][j] = 1 iff (P F)[k] = F[j].
    Here: P[0][0]=1, P[1][3]=1, P[2][1]=1, P[3][2]=1.
    """
    P = [[0] * 4 for _ in range(4)]
    P[0][0] = 1  # 00 fixed
    P[1][3] = 1  # 01 ← 11
    P[2][1] = 1  # 10 ← 01
    P[3][2] = 1  # 11 ← 10
    return P


def spectral_modulation_matrix(a: int, n: int) -> List[List[int]]:
    """Diagonal matrix with χ_a(k) on the diagonal."""
    N = 2**n
    D = [[0] * N for _ in range(N)]
    for k in range(N):
        D[k][k] = chi(a, k)
    return D


def point_modulation_matrix(m: int, n: int) -> List[List[int]]:
    """Diagonal matrix with χ_m(x) on the diagonal."""
    N = 2**n
    D = [[0] * N for _ in range(N)]
    for x in range(N):
        D[x][x] = chi(m, x)
    return D


# ============================================================
# OPERATOR VIEW: spectral image of a point-domain operator
# ============================================================


def spectral_of(M: List[List[int]]) -> List[List[int]]:
    """Spectral image: H · M · H^{-1} = (1/N) · H · M · H.

    v3: Validates that N = len(M) is a power of 2, and that the
    intermediate product H·M·H is exactly divisible by N. Otherwise
    raises ValueError.
    """
    N = len(M)
    if N <= 0 or (N & (N - 1)) != 0:
        raise ValueError(f"spectral_of requires square matrix of size 2^n; got N={N}")
    if any(len(row) != N for row in M):
        raise ValueError(f"spectral_of: matrix not square")
    n = N.bit_length() - 1
    H = hadamard_matrix(n)
    HM = matmat(H, M)
    HMH = matmat(HM, H)
    for i in range(N):
        for j in range(N):
            if HMH[i][j] % N != 0:
                raise ValueError(
                    f"spectral_of: H·M·H not exactly divisible by N={N} "
                    f"at ({i},{j}): value {HMH[i][j]}"
                )
    return [[v // N for v in row] for row in HMH]


# ============================================================
# Verification — Hadamard / WHT
# ============================================================


def verify_hadamard_property(n: int) -> bool:
    H = hadamard_matrix(n)
    HHT = matmat(H, transpose(H))
    N = 2**n
    for i in range(N):
        for j in range(N):
            expected = N if i == j else 0
            if HHT[i][j] != expected:
                return False
    return True


def verify_wht_is_involutory(n: int) -> bool:
    """H · H · f = N · f (under unnormalized convention)."""
    H = hadamard_matrix(n)
    N = 2**n
    f = list(range(N))
    Ff = matvec(H, f)
    f_recovered = matvec(H, Ff)
    for i in range(N):
        if f_recovered[i] != N * f[i]:
            return False
    return True


def verify_fwht_matches_direct(n: int) -> bool:
    H = hadamard_matrix(n)
    N = 2**n
    for k in range(min(N, 8)):
        e_k = [1 if i == k else 0 for i in range(N)]
        direct = matvec(H, e_k)
        fast = fwht(e_k)
        if direct != fast:
            return False
    return True


def verify_dc_is_sum_not_mean(n: int) -> bool:
    """F[0] = sum(f), not mean(f). The mean is F[0] / N."""
    N = 2**n
    f = [1, 2, 3, 4, 5, 6, 7, 8][:N]
    F = fwht(f)
    return F[0] == sum(f)


# ============================================================
# Verification — point/spectral dualities (NEW v2)
# ============================================================


def verify_point_translation_to_spectral_modulation(n: int) -> bool:
    """WHT(point_translation(f, a)) = spectral_modulation(WHT(f), a) for all a."""
    N = 2**n
    f = [i + 1 for i in range(N)]
    Ff = fwht(f)
    for a in range(N):
        lhs = fwht(point_translation(f, a))
        rhs = spectral_modulation(Ff, a)
        if lhs != rhs:
            return False
    return True


def verify_point_modulation_to_spectral_translation(n: int) -> bool:
    """WHT(point_modulation(f, m)) = spectral_translation(WHT(f), m) for all m."""
    N = 2**n
    f = [i + 1 for i in range(N)]
    Ff = fwht(f)
    for m in range(N):
        lhs = fwht(point_modulation(f, m))
        rhs = spectral_translation(Ff, m)
        if lhs != rhs:
            return False
    return True


# ============================================================
# Verification — V_4 group structure
# ============================================================


def verify_v4_composition(n: int) -> bool:
    """V_4: T_{m1} ∘ T_{m2} = T_{m1 ⊕ m2}."""
    N = 2**n
    test_F = list(range(N))
    for m1 in range(N):
        for m2 in range(N):
            composed = spectral_translation(spectral_translation(test_F, m1), m2)
            direct = spectral_translation(test_F, m1 ^ m2)
            if composed != direct:
                return False
    return True


def verify_chirality_is_involutive(n: int) -> bool:
    N = 2**n
    test_F = list(range(N))
    return chirality_flip(chirality_flip(test_F)) == test_F


def verify_v4_commutes_with_chirality(n: int) -> bool:
    """Chirality is central: commutes with V_4."""
    N = 2**n
    test_F = list(range(N))
    for m in range(N):
        a = spectral_translation(chirality_flip(test_F), m)
        b = chirality_flip(spectral_translation(test_F, m))
        if a != b:
            return False
    return True


# ============================================================
# Verification — Z_3 cycle (NEW v2)
# ============================================================


def verify_z3_cubed_is_identity() -> bool:
    """Z³ = I at level 2."""
    F = [1, 2, 3, 4]
    return z3_cycle(z3_cycle(z3_cycle(F))) == F


def verify_z3_inverse_correct() -> bool:
    """z3_cycle_inverse undoes z3_cycle."""
    F = [1, 2, 3, 4]
    return z3_cycle_inverse(z3_cycle(F)) == F and z3_cycle(z3_cycle_inverse(F)) == F


def verify_z3_inverse_equals_z_squared() -> bool:
    """Z² = Z^{-1}."""
    F = [1, 2, 3, 4]
    return z3_cycle(z3_cycle(F)) == z3_cycle_inverse(F)


def verify_z3_fixes_dc() -> bool:
    """Z fixes the DC component F[0]."""
    F = [1, 2, 3, 4]
    return z3_cycle(F)[0] == F[0]


def verify_z3_permutes_nonzero_masks() -> bool:
    """Z permutes the 3 nonzero spectral indices in a 3-cycle.

    Verified via the operator: applying Z to the indicator vector e_m
    should give e_{cycle(m)}.
    """
    cycle = {1: 2, 2: 3, 3: 1}  # 01 → 10, 10 → 11, 11 → 01
    for m, m_next in cycle.items():
        e_m = [1 if i == m else 0 for i in range(4)]
        e_next_expected = [1 if i == m_next else 0 for i in range(4)]
        if z3_cycle(e_m) != e_next_expected:
            return False
    return True


def verify_z3_conjugates_v4_by_cycle() -> bool:
    """Semidirect relation: Z · T_m · Z^{-1} = T_{cycle(m)}.

    This is THE relation that makes V_4 ⋊ Z_3 = A_4 work.
    """
    cycle = {0b00: 0b00, 0b01: 0b10, 0b10: 0b11, 0b11: 0b01}
    F = [1, 2, 3, 4]
    for m, m_cycled in cycle.items():
        lhs = z3_cycle(spectral_translation(z3_cycle_inverse(F), m))
        rhs = spectral_translation(F, m_cycled)
        if lhs != rhs:
            return False
    return True


def verify_z3_commutes_with_chirality() -> bool:
    """Chirality (-I) commutes with Z (permutation)."""
    F = [1, 2, 3, 4]
    a = z3_cycle(chirality_flip(F))
    b = chirality_flip(z3_cycle(F))
    return a == b


# ============================================================
# Verification — A_4 = V_4 ⋊ Z_3 (NEW v2)
# ============================================================


def _apply_a4_element(F: List[int], m: int, j: int) -> List[int]:
    """Apply the A_4 element T_m · Z^j to F.

    ORDERING CONVENTION: Z^j is applied FIRST, then T_m. So
        _apply_a4_element(F, m, j)  =  T_m(Z^j(F))  =  (T_m · Z^j)(F)
    where composition is right-to-left as is standard for operators
    acting on the left.
    """
    result = F
    for _ in range(j):
        result = z3_cycle(result)
    result = spectral_translation(result, m)
    return result


def verify_a4_order_is_12() -> bool:
    """The group V_4 ⋊ Z_3 has order 12 at level 2.

    Enumerate T_m · Z^j for m ∈ {0,1,2,3}, j ∈ {0,1,2}. These 12 elements,
    when applied to a generic test vector, should produce 12 distinct outputs.
    """
    F = [10, 20, 30, 40]  # distinct entries → distinct permutations distinguishable
    outputs = set()
    for j in range(3):
        for m in range(4):
            out = tuple(_apply_a4_element(F, m, j))
            outputs.add(out)
    return len(outputs) == 12


def verify_a4_closure_under_composition() -> bool:
    """Composition of any two elements of {T_m · Z^j : m, j} lies in the set."""
    F = [10, 20, 30, 40]
    # Build the 12 elements as permutation tuples
    elements = {}  # output tuple → (m, j) for identification
    for j in range(3):
        for m in range(4):
            out = tuple(_apply_a4_element(F, m, j))
            elements[out] = (m, j)

    # Verify closure: for each pair (g, h), g∘h ∈ elements
    for g_out, (g_m, g_j) in elements.items():
        for h_out, (h_m, h_j) in elements.items():
            # Apply h first, then g
            after_h = _apply_a4_element(F, h_m, h_j)
            after_g = _apply_a4_element(after_h, g_m, g_j)
            if tuple(after_g) not in elements:
                return False
    return True


def verify_a4_times_z2_order_is_24() -> bool:
    """A_4 × Z_2 has 24 elements; matches M38 architectural codeword count."""
    F = [10, 20, 30, 40]
    outputs = set()
    for sign in (1, -1):
        for j in range(3):
            for m in range(4):
                out = _apply_a4_element(F, m, j)
                if sign == -1:
                    out = chirality_flip(out)
                outputs.add(tuple(out))
    return len(outputs) == 24


# ============================================================
# Verification — operator conjugation (NEW v2)
# ============================================================


def verify_spectral_of_point_translation_is_spectral_modulation() -> bool:
    """spectral(point_translation_op_a) = spectral_modulation_op_a (diagonal).

    Equivalently: H · T_a^{point} · H^{-1} = D_{χ_a}^{spectral}.
    """
    n = 2
    N = 4
    H = hadamard_matrix(n)
    for a in range(N):
        # Point translation operator: T_a maps x ↦ x ⊕ a, so e_x ↦ e_{x⊕a}.
        # As a matrix on point space: T[y][x] = 1 if y = x ⊕ a.
        T_point = [[0] * N for _ in range(N)]
        for x in range(N):
            T_point[x ^ a][x] = 1
        # Spectral image: H · T · H^{-1} = (1/N) · H · T · H
        HT = matmat(H, T_point)
        HTH = matmat(HT, H)
        # Compare with the diagonal spectral_modulation matrix
        D = spectral_modulation_matrix(a, n)
        for i in range(N):
            for j in range(N):
                if HTH[i][j] != N * D[i][j]:
                    return False
    return True


# ============================================================
# v3: The two 24-element groups at level 2
# ============================================================


def enumerate_a4_z2_elements():
    """Return the 24 elements of A_4 × Z_2 as (name, callable) pairs.

    Construction: T_m · Z^j × sign for m ∈ {0..3}, j ∈ {0..2}, sign ∈ {+,-}.
    The sign factor is the central chirality (commutes with everything).
    """
    elements = []
    for sign in (1, -1):
        for j in range(3):
            for m in range(4):

                def make_op(m=m, j=j, sign=sign):
                    def op(F):
                        out = _apply_a4_element(F, m, j)
                        if sign == -1:
                            out = chirality_flip(out)
                        return out

                    return op

                name = f"{'+' if sign == 1 else '-'} T_{m} Z^{j}"
                elements.append((name, make_op()))
    return elements


def enumerate_s4_elements():
    """Return the 24 elements of V_4 ⋊ S_3 ≅ S_4 ≅ AGL_2(F_2).

    Construction: T_m · σ for m ∈ {0..3}, σ ∈ S_3 (6 elements).
    No chirality factor — the 24 come entirely from mask permutations.
    """
    elements = []
    for sigma_name, sigma in s3_elements():
        for m in range(4):

            def make_op(m=m, sigma=sigma):
                def op(F):
                    return spectral_translation(sigma(F), m)

                return op

            name = f"T_{m} · {sigma_name}"
            elements.append((name, make_op()))
    return elements


def _element_order(op, test_F: List[int], max_order: int = 30) -> int:
    """Compute the order of a group element by repeated application.

    Uses a test vector whose entries are all distinct (so the action
    determines the permutation). Returns -1 if order exceeds max_order.
    """
    current = list(test_F)
    for k in range(1, max_order + 1):
        current = op(current)
        if current == test_F:
            return k
    return -1


def compute_order_distribution(elements, test_F: List[int]) -> dict:
    """Return {order: count} dict for the group elements."""
    from collections import Counter

    orders = []
    for name, op in elements:
        orders.append(_element_order(op, test_F))
    return dict(Counter(orders))


def compute_group_center(elements, test_F: List[int]) -> List[str]:
    """Return the names of central elements (commuting with all others).

    For test_F with all entries distinct (e.g. [10, 20, 30, 40]),
    chirality (negation) produces values disjoint from the positives,
    so the set {±a, ±b, ±c, ±d} has 8 distinct values. Any element
    of A_4 × Z_2 is then uniquely determined by its action on test_F,
    making commutation on test_F equivalent to commutation in the group.

    For pure S_4 (no sign-flipping), the 4 positive distinct entries
    alone suffice to distinguish the 24 permutations.

    v4 preserves this as a compatibility/visualization layer; the
    proof spine is the algebraic compute_group_center_algebraic.
    """
    central_names = []
    for i, (name_g, g) in enumerate(elements):
        is_central = True
        for j, (name_h, h) in enumerate(elements):
            if i == j:
                continue
            lhs = g(h(test_F))
            rhs = h(g(test_F))
            if lhs != rhs:
                is_central = False
                break
        if is_central:
            central_names.append(name_g)
    return central_names


# Test vector with all 8 (4 positive, 4 negative) entries distinct,
# so commutation on it implies commutation as group elements
_GROUP_TEST_VECTOR = [10, 20, 30, 40]


def verify_a4_z2_has_24_distinct_elements() -> bool:
    elements = enumerate_a4_z2_elements()
    outputs = set()
    for name, op in elements:
        outputs.add(tuple(op(_GROUP_TEST_VECTOR)))
    return len(outputs) == 24


def verify_s4_has_24_distinct_elements() -> bool:
    elements = enumerate_s4_elements()
    outputs = set()
    for name, op in elements:
        outputs.add(tuple(op(_GROUP_TEST_VECTOR)))
    return len(outputs) == 24


def verify_a4_z2_order_distribution() -> bool:
    """A_4 × Z_2: orders {1: 1, 2: 7, 3: 8, 6: 8} — no order-4 elements."""
    dist = compute_order_distribution(enumerate_a4_z2_elements(), _GROUP_TEST_VECTOR)
    expected = {1: 1, 2: 7, 3: 8, 6: 8}
    return dist == expected


def verify_s4_order_distribution() -> bool:
    """S_4: orders {1: 1, 2: 9, 3: 8, 4: 6} — has order-4 elements."""
    dist = compute_order_distribution(enumerate_s4_elements(), _GROUP_TEST_VECTOR)
    expected = {1: 1, 2: 9, 3: 8, 4: 6}
    return dist == expected


def verify_a4_z2_no_order_4_elements() -> bool:
    """A_4 × Z_2 has NO elements of order 4."""
    dist = compute_order_distribution(enumerate_a4_z2_elements(), _GROUP_TEST_VECTOR)
    return 4 not in dist


def verify_s4_has_order_4_elements() -> bool:
    """S_4 has elements of order 4 (the 4-cycles)."""
    dist = compute_order_distribution(enumerate_s4_elements(), _GROUP_TEST_VECTOR)
    return dist.get(4, 0) == 6


def verify_a4_z2_center_order_is_2() -> bool:
    """Z(A_4 × Z_2) = {identity, chirality}, order 2."""
    central = compute_group_center(enumerate_a4_z2_elements(), _GROUP_TEST_VECTOR)
    return len(central) == 2


def verify_s4_center_is_trivial() -> bool:
    """Z(S_4) = {identity}, order 1."""
    central = compute_group_center(enumerate_s4_elements(), _GROUP_TEST_VECTOR)
    return len(central) == 1


def verify_a4_z2_not_isomorphic_to_s4() -> bool:
    """The two 24-element groups have different order distributions.

    Sufficient to prove non-isomorphism: isomorphic groups have
    identical order distributions.
    """
    dist_a4z2 = compute_order_distribution(enumerate_a4_z2_elements(), _GROUP_TEST_VECTOR)
    dist_s4 = compute_order_distribution(enumerate_s4_elements(), _GROUP_TEST_VECTOR)
    return dist_a4z2 != dist_s4


def verify_s3_transpositions_are_involutions() -> bool:
    """Each transposition has order 2."""
    F = _GROUP_TEST_VECTOR
    for swap in (s3_swap_01_10, s3_swap_01_11, s3_swap_10_11):
        if swap(swap(F)) != F:
            return False
        if swap(F) == F:
            return False  # transposition shouldn't be identity
    return True


def verify_s3_has_6_elements() -> bool:
    """S_3 has 6 distinct elements as functions."""
    outputs = set()
    for name, op in s3_elements():
        outputs.add(tuple(op(_GROUP_TEST_VECTOR)))
    return len(outputs) == 6


def verify_s3_fixes_dc() -> bool:
    """All S_3 elements fix F[0] (act trivially on the 00 mask)."""
    F = _GROUP_TEST_VECTOR
    for name, op in s3_elements():
        if op(F)[0] != F[0]:
            return False
    return True


# ============================================================
# v4: ALGEBRAIC group representations
# ============================================================
#
# Per v3 audit point 7: replace the test-vector trick with canonical
# algebraic representations. Elements are tuples; multiplication is
# defined by composition law derived from the semidirect product
# structure. Vector action becomes visualization, not the proof spine.
#
# Order distribution and center are computed from algebra alone,
# independent of any test data.

# S_3 = GL_2(F_2) as 4-tuple permutations of {00, 01, 10, 11}.
# σ[i] = where mask i maps. All elements fix 00 (linear maps).
S3_I = (0, 1, 2, 3)  # identity
S3_Z = (0, 2, 3, 1)  # 3-cycle 01→10→11→01
S3_Z2 = (0, 3, 1, 2)  # 3-cycle 01→11→10→01 (Z^2)
S3_SWAP_0110 = (0, 2, 1, 3)  # transposition (01 10), fixes 11
S3_SWAP_0111 = (0, 3, 2, 1)  # transposition (01 11), fixes 10
S3_SWAP_1011 = (0, 1, 3, 2)  # transposition (10 11), fixes 01

S3_ALL = [S3_I, S3_Z, S3_Z2, S3_SWAP_0110, S3_SWAP_0111, S3_SWAP_1011]
S3_NAMES = {
    S3_I: "I",
    S3_Z: "Z",
    S3_Z2: "Z^2",
    S3_SWAP_0110: "(01 10)",
    S3_SWAP_0111: "(01 11)",
    S3_SWAP_1011: "(10 11)",
}

# A_3 ⊂ S_3 — even permutations (the oriented Z_3 cycle)
S3_EVEN = [S3_I, S3_Z, S3_Z2]


def s3_compose(sigma1: Tuple[int, ...], sigma2: Tuple[int, ...]) -> Tuple[int, ...]:
    """(σ1 ∘ σ2)(x) = σ1(σ2(x))."""
    return tuple(sigma1[sigma2[i]] for i in range(4))


def s3_inverse(sigma: Tuple[int, ...]) -> Tuple[int, ...]:
    """Inverse permutation."""
    inv = [0] * 4
    for i in range(4):
        inv[sigma[i]] = i
    return tuple(inv)


# A_4 × Z_2 element: (sign, m, j)
# Represents:  chirality^{(1-sign)/2} · T_m · Z^j
# where sign ∈ {+1, -1}, m ∈ {0,1,2,3}, j ∈ {0,1,2}.

A4Z2Element = Tuple[int, int, int]  # (sign, m, j)

A4Z2_IDENTITY: A4Z2Element = (1, 0, 0)

# Cycle table: σ_Z permutation of nonzero masks (00 fixed)
_CYCLE_TABLE = {0: 0, 1: 2, 2: 3, 3: 1}  # 01→10→11→01


def _apply_cycle(m: int, times: int) -> int:
    for _ in range(times):
        m = _CYCLE_TABLE[m]
    return m


def a4z2_compose(g: A4Z2Element, h: A4Z2Element) -> A4Z2Element:
    """g · h.

    Derivation: g · h = (chir^{a_g} T_{m_g} Z^{j_g}) (chir^{a_h} T_{m_h} Z^{j_h})
                      = chir^{a_g + a_h} T_{m_g} (Z^{j_g} T_{m_h} Z^{-j_g}) Z^{j_g + j_h}
                      = chir^{a_g + a_h} T_{m_g ⊕ σ^{j_g}(m_h)} Z^{j_g + j_h}
    where σ is the Z_3 cycle on masks and chirality is central.
    """
    s_g, m_g, j_g = g
    s_h, m_h, j_h = h
    return (s_g * s_h, m_g ^ _apply_cycle(m_h, j_g), (j_g + j_h) % 3)


def a4z2_inverse(g: A4Z2Element) -> A4Z2Element:
    """Inverse element: a4z2_compose(g, a4z2_inverse(g)) = identity."""
    s, m, j = g
    j_inv = (3 - j) % 3
    # Need: m ⊕ σ^j(m_inv) = 0 → m_inv = σ^{-j}(m)
    m_inv = _apply_cycle(m, j_inv)
    return (s, m_inv, j_inv)


def a4z2_all_elements() -> List[A4Z2Element]:
    return [(s, m, j) for s in (1, -1) for j in range(3) for m in range(4)]


def a4z2_name(g: A4Z2Element) -> str:
    s, m, j = g
    sign_str = "+" if s == 1 else "-"
    return f"{sign_str}T_{m}·Z^{j}"


def a4z2_act(g: A4Z2Element, F: List[int]) -> List[int]:
    """Apply algebraic element to vector F (for visualization)."""
    s, m, j = g
    result = list(F)
    for _ in range(j):
        result = z3_cycle(result)
    result = spectral_translation(result, m)
    if s == -1:
        result = chirality_flip(result)
    return result


# S_4 = V_4 ⋊ S_3 element: (m, sigma)
# Represents:  T_m · σ
# where m ∈ {0,1,2,3}, σ ∈ S_3 (one of S3_ALL).

S4Element = Tuple[int, Tuple[int, ...]]  # (m, sigma)

S4_IDENTITY: S4Element = (0, S3_I)


def s4_compose(g: S4Element, h: S4Element) -> S4Element:
    """g · h.

    Derivation: (T_{m_g} σ_g)(T_{m_h} σ_h)
              = T_{m_g} (σ_g T_{m_h} σ_g^{-1}) σ_g σ_h
              = T_{m_g ⊕ σ_g(m_h)} (σ_g σ_h)
    """
    m_g, sigma_g = g
    m_h, sigma_h = h
    return (m_g ^ sigma_g[m_h], s3_compose(sigma_g, sigma_h))


def s4_inverse(g: S4Element) -> S4Element:
    """Inverse element."""
    m, sigma = g
    sigma_inv = s3_inverse(sigma)
    m_inv = sigma_inv[m]
    return (m_inv, sigma_inv)


def s4_all_elements() -> List[S4Element]:
    return [(m, sigma) for sigma in S3_ALL for m in range(4)]


def s4_name(g: S4Element) -> str:
    m, sigma = g
    return f"T_{m}·{S3_NAMES[sigma]}"


def s4_act(g: S4Element, F: List[int]) -> List[int]:
    """Apply algebraic element to vector F (for visualization)."""
    m, sigma = g
    # Apply sigma (pullback convention: (σF)[k] = F[σ^{-1}(k)])
    sigma_inv = s3_inverse(sigma)
    sigma_F = [F[sigma_inv[i]] for i in range(4)]
    return spectral_translation(sigma_F, m)


# ============================================================
# v4: Algebraic invariants (independent of test vector)
# ============================================================


def algebraic_order(g, compose, identity, max_order: int = 30) -> int:
    """Compute order of g by repeated composition: smallest k with g^k = identity."""
    if g == identity:
        return 1
    current = g
    for k in range(2, max_order + 1):
        current = compose(current, g)
        if current == identity:
            return k
    return -1


def algebraic_order_distribution(elements, compose, identity) -> dict:
    """Compute {order: count} from algebra alone."""
    from collections import Counter

    return dict(Counter(algebraic_order(g, compose, identity) for g in elements))


def algebraic_center(elements, compose) -> list:
    """Compute group center {g : g·h = h·g for all h} from algebra alone."""
    central = []
    for g in elements:
        if all(compose(g, h) == compose(h, g) for h in elements):
            central.append(g)
    return central


# ============================================================
# v4: Architectural derivation by closure
# ============================================================
#
# The architectural claim "M40 selects A_4 × Z_2, not S_4" depends on
# admissibility: which generators is the architecture allowed to use?
# This module proves the CONDITIONAL claim: GIVEN primitives
# {V_4 translations, z3_cycle, chirality_flip}, the group generated is
# A_4 × Z_2 (order 24). Adding any S_3 transposition extends it to
# S_4 × Z_2 (order 48). The architecture chooses the smaller closure.


def generate_group_by_action(generators, test_F: List[int], max_size: int = 100) -> dict:
    """Compute the closure of generators under composition.

    Each generator is a callable F → F. Two elements are identified
    by their action on test_F (which must have distinct entries that
    remain distinct under negation, so this distinguishes all 24/48
    relevant actions).

    Returns a dict mapping action-tuples to the callables that produce them.
    """
    identity_action = tuple(test_F)
    group = {identity_action: lambda F: list(F)}
    frontier = [identity_action]

    while frontier and len(group) < max_size:
        new_frontier = []
        for g_action in frontier:
            g_func = group[g_action]
            for gen_name, gen_func in generators:

                def make_product(gg, gf):
                    return lambda F: gf(gg(F))

                product_func = make_product(g_func, gen_func)
                product_action = tuple(product_func(test_F))
                if product_action not in group:
                    group[product_action] = product_func
                    new_frontier.append(product_action)
        frontier = new_frontier

    return group


def architectural_primitives_level_2():
    """The architectural primitives M40 admits at level 2.

    Excludes: S_3 transpositions (s3_swap_*) — odd mask permutations.
    """
    return [
        ("T_1", lambda F: spectral_translation(F, 1)),
        ("T_2", lambda F: spectral_translation(F, 2)),
        ("T_3", lambda F: spectral_translation(F, 3)),
        ("Z", z3_cycle),
        ("chirality", chirality_flip),
    ]


def verify_architectural_primitives_generate_a4z2() -> bool:
    """The closure of architectural primitives EQUALS the algebraic A_4 × Z_2.

    This proves WHICH 24 — not just "24 elements," but specifically the
    24 elements of A_4 × Z_2 in their action representation.
    """
    F = [10, 20, 30, 40]
    group = generate_group_by_action(architectural_primitives_level_2(), F, max_size=50)

    if len(group) != 24:
        return False

    # The closure's action set must equal the algebraic A_4 × Z_2's action set
    expected_actions = {tuple(a4z2_act(g, F)) for g in a4z2_all_elements()}

    return set(group.keys()) == expected_actions


def verify_pure_s4_primitives_generate_s4() -> bool:
    """Closure of pure S_4 primitives EQUALS the algebraic S_4.

    Parallel to verify_architectural_primitives_generate_a4z2 — proves
    which 24, not just that there are 24.
    """
    F = [10, 20, 30, 40]
    generators = [
        ("T_1", lambda F: spectral_translation(F, 1)),
        ("T_2", lambda F: spectral_translation(F, 2)),
        ("T_3", lambda F: spectral_translation(F, 3)),
        ("Z", z3_cycle),
        ("(01 10)", s3_swap_01_10),
        ("(01 11)", s3_swap_01_11),
        ("(10 11)", s3_swap_10_11),
    ]
    group = generate_group_by_action(generators, F, max_size=50)

    if len(group) != 24:
        return False

    expected_actions = {tuple(s4_act(g, F)) for g in s4_all_elements()}

    return set(group.keys()) == expected_actions


def verify_a4z2_closure_disjoint_from_extra_transposition() -> bool:
    """The 24-element architectural closure does NOT contain any odd
    mask permutation. Adding one expands to 48."""
    F = [10, 20, 30, 40]
    arch_group = generate_group_by_action(architectural_primitives_level_2(), F, max_size=50)
    # Apply the transposition (01 10) to F — this is the action of an
    # odd mask permutation. It must NOT be in arch_group's action set.
    swap_action = tuple(s3_swap_01_10(F))
    return swap_action not in arch_group


def verify_adding_transposition_extends_to_48() -> bool:
    """Adding ANY S_3 transposition to architectural primitives extends
    the closure to 48 elements (S_4 × Z_2)."""
    F = [10, 20, 30, 40]
    generators = architectural_primitives_level_2() + [
        ("(01 10)", s3_swap_01_10),
    ]
    group = generate_group_by_action(generators, F, max_size=100)
    return len(group) == 48


# ============================================================
# v6: theorem-style aggregator
# ============================================================


def verify_m40_group_is_a4z2_not_s4() -> bool:
    """The M40 main theorem, in one verifier.

    Asserts the full chain:

        admissible generators {V_4, Z_3, chirality}
          ↓ closure under composition
        action set = algebraic A_4 × Z_2
          ↓ algebraic invariants
        order distribution = {1:1, 2:7, 3:8, 6:8}    (≠ S_4's {1:1, 2:9, 3:8, 4:6})
        center order = 2                              (≠ S_4's 1)
          ↓ structural witness
        A_4 × Z_2 ≇ S_4
          ↓ admissibility-rule sensitivity
        adding any S_3 transposition collapses the equality
        (closure becomes S_4 × Z_2, order 48)

    Each sub-claim is verified by an independent test; this aggregator
    asserts the conjunction. Returns True iff every sub-claim holds.
    """
    return (
        # Architectural generators produce A_4 × Z_2 specifically
        verify_architectural_primitives_generate_a4z2()
        # A_4 × Z_2's algebraic invariants
        and verify_a4z2_algebraic_orders_match_expected()
        and verify_a4z2_algebraic_center_is_2()
        # S_4's algebraic invariants (the contrasting alternative)
        and verify_s4_algebraic_orders_match_expected()
        and verify_s4_algebraic_center_is_trivial()
        # Pure S_4 generators (no chirality) produce S_4 specifically
        and verify_pure_s4_primitives_generate_s4()
        # The two groups are non-isomorphic
        and verify_a4_z2_not_isomorphic_to_s4()
        # Architectural closure excludes odd mask permutations
        and verify_a4z2_closure_disjoint_from_extra_transposition()
        # Adding any odd permutation collapses A_4 × Z_2 to S_4 × Z_2
        and verify_adding_transposition_extends_to_48()
    )


# ============================================================
# v4: Consistency between algebraic and vector representations
# ============================================================


def verify_algebraic_a4z2_has_24_distinct() -> bool:
    elements = a4z2_all_elements()
    if len(elements) != 24:
        return False
    return len(set(elements)) == 24


def verify_algebraic_s4_has_24_distinct() -> bool:
    elements = s4_all_elements()
    if len(elements) != 24:
        return False
    return len(set(elements)) == 24


def verify_a4z2_algebraic_orders_match_expected() -> bool:
    """Algebraic order distribution for A_4 × Z_2 is {1:1, 2:7, 3:8, 6:8}."""
    dist = algebraic_order_distribution(a4z2_all_elements(), a4z2_compose, A4Z2_IDENTITY)
    return dist == {1: 1, 2: 7, 3: 8, 6: 8}


def verify_s4_algebraic_orders_match_expected() -> bool:
    """Algebraic order distribution for S_4 is {1:1, 2:9, 3:8, 4:6}."""
    dist = algebraic_order_distribution(s4_all_elements(), s4_compose, S4_IDENTITY)
    return dist == {1: 1, 2: 9, 3: 8, 4: 6}


def verify_a4z2_algebraic_center_is_2() -> bool:
    """Algebraic center of A_4 × Z_2: identity and chirality (-I)."""
    center = algebraic_center(a4z2_all_elements(), a4z2_compose)
    if len(center) != 2:
        return False
    # The two central elements should be (+1, 0, 0) and (-1, 0, 0)
    expected = {(1, 0, 0), (-1, 0, 0)}
    return set(center) == expected


def verify_s4_algebraic_center_is_trivial() -> bool:
    center = algebraic_center(s4_all_elements(), s4_compose)
    return len(center) == 1 and center[0] == S4_IDENTITY


def verify_a4z2_algebra_matches_vector() -> bool:
    """The algebraic and vector representations agree on all 24 elements."""
    F = [10, 20, 30, 40]
    for g in a4z2_all_elements():
        # Algebraic action
        alg = a4z2_act(g, F)
        # Vector enumeration: g = (s, m, j) corresponds to chir^{1 if s=-1} T_m Z^j
        s, m, j = g
        vec = _apply_a4_element(F, m, j)
        if s == -1:
            vec = chirality_flip(vec)
        if alg != vec:
            return False
    return True


def verify_s4_algebra_matches_vector() -> bool:
    """The algebraic and vector representations of S_4 agree."""
    F = [10, 20, 30, 40]
    sigma_funcs = dict(s3_elements())
    for g in s4_all_elements():
        m, sigma_tuple = g
        sigma_name = S3_NAMES[sigma_tuple]
        sigma_func = sigma_funcs[sigma_name]
        # Vector: T_m(σ(F))
        vec = spectral_translation(sigma_func(F), m)
        # Algebraic
        alg = s4_act(g, F)
        if alg != vec:
            return False
    return True


def verify_a4z2_compose_is_associative() -> bool:
    """Algebraic composition is associative. Exhaustive over all 24³ = 13,824 triples."""
    elements = a4z2_all_elements()
    for g in elements:
        for h in elements:
            for k in elements:
                lhs = a4z2_compose(a4z2_compose(g, h), k)
                rhs = a4z2_compose(g, a4z2_compose(h, k))
                if lhs != rhs:
                    return False
    return True


def verify_s4_compose_is_associative() -> bool:
    """S_4 composition is associative. Exhaustive over all 24³ = 13,824 triples."""
    elements = s4_all_elements()
    for g in elements:
        for h in elements:
            for k in elements:
                lhs = s4_compose(s4_compose(g, h), k)
                rhs = s4_compose(g, s4_compose(h, k))
                if lhs != rhs:
                    return False
    return True


def verify_a4z2_inverse_is_correct() -> bool:
    """g · g^{-1} = identity for all g ∈ A_4 × Z_2."""
    for g in a4z2_all_elements():
        if a4z2_compose(g, a4z2_inverse(g)) != A4Z2_IDENTITY:
            return False
        if a4z2_compose(a4z2_inverse(g), g) != A4Z2_IDENTITY:
            return False
    return True


def verify_s4_inverse_is_correct() -> bool:
    for g in s4_all_elements():
        if s4_compose(g, s4_inverse(g)) != S4_IDENTITY:
            return False
        if s4_compose(s4_inverse(g), g) != S4_IDENTITY:
            return False
    return True


# ============================================================
# v3 vector-based verifiers (preserved as compatibility / visualization)
# ============================================================


# ============================================================
# Demo — RELOCATED to spectral_view_demo.py, re-exported here
# ============================================================
#
# ⚑ SPLIT 2026-08-11 (size rule: 1200 code lines; this module measured
#   1233 code lines / 105 defs, 33 over).  The seam was not invented for
#   the split — it was already the only one in the file.  Of 105 defs,
#   103 are pure-arithmetic library functions with a mean body of ~11
#   lines; the two exceptions, `fmt_matrix` and `demo`, are ~330 lines of
#   `print` reachable ONLY from the `__main__` guard below (`--calls demo`
#   found zero other callers, in this repo or any other).  Moving them
#   removes the entire overage in ONE cut and leaves the library half a
#   coherent whole — the rest of this file is a single subject (WHT +
#   the level-2 group identity) whose verifiers cite each other densely,
#   so a second cut would add import indirection for no readability gain.
#
#   `fmt_matrix` and `demo` are RE-EXPORTED below so every public name
#   this module exported before the split is still importable from it,
#   and `python3 spectral_view.py` still runs the walkthrough.
#
#   The import is deferred into the guard/module tail rather than placed
#   at the top of the file because spectral_view_demo imports FROM here:
#   a module-scope import at the head would be a cycle.


def _load_demo():
    """Import the relocated demo half.  Deferred: it imports back from here."""
    from spectral_view_demo import fmt_matrix, demo

    return fmt_matrix, demo


def fmt_matrix(M, sign_only=False):
    """Re-export shim — the body lives in spectral_view_demo.fmt_matrix."""
    return _load_demo()[0](M, sign_only=sign_only)


def demo():
    """Re-export shim — the body lives in spectral_view_demo.demo."""
    return _load_demo()[1]()


if __name__ == "__main__":
    demo()
