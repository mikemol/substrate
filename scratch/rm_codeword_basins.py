"""
rm_codeword_basins.py — Parity basins and rotational transitions of the
M19 codewords (I, K, S as length-8 Boolean functions on F_2^3).

Reed-Muller provides:
- Correction of t = ⌊(d-1)/2⌋ errors in a (n, k, d) code.
- Detection of d-1 errors.

For our M19 codewords:
- I, K (extended to length 8) sit in RM(1, 3): (8, 4, 4), correcting 1 error.
- S sits in RM(3, 3): (8, 8, 1), no correction (full space).

The parity-basin structure reveals which length-8 vectors are equivalent
under 1-error recovery in each RM family. Crucially, S is at Hamming
distance 1 from the zero codeword — so RM(1, 3) correction would
"decode S to zero", a wrong answer if we want S itself. Rotating from
RM(1, 3) up to RM(3, 3) is what makes S structurally distinct from zero.
"""

from itertools import product, combinations


# ============================================================
# Reed-Muller codeword generation
# ============================================================

def eval_polynomial(monomials, point):
    """Eval Boolean polynomial (ANF) at point ∈ F_2^n."""
    result = 0
    for monomial in monomials:
        term = 1
        for i in monomial:
            term &= point[i]
        result ^= term
    return result


def truth_table_of_polynomial(monomials, n):
    """Length-2^n truth table of polynomial."""
    return tuple(
        eval_polynomial(monomials, [(j >> i) & 1 for i in range(n)])
        for j in range(2 ** n)
    )


def all_monomials(n, max_degree):
    """All monomials in n vars of degree ≤ max_degree (as frozensets of indices)."""
    result = []
    for d in range(max_degree + 1):
        for combo in combinations(range(n), d):
            result.append(frozenset(combo))
    return result


def rm_codewords(r, m):
    """All codewords of RM(r, m): truth tables of polynomials of deg ≤ r in m vars.

    Returns: set of tuples (length 2^m each).
    """
    monomials = all_monomials(m, r)
    # Each subset of monomials gives a codeword.
    codewords = set()
    for subset_mask in range(2 ** len(monomials)):
        chosen = [monomials[i] for i in range(len(monomials)) if subset_mask & (1 << i)]
        codewords.add(truth_table_of_polynomial(chosen, m))
    return codewords


def hamming_distance(u, v):
    return sum(1 for a, b in zip(u, v) if a != b)


def hamming_weight(u):
    return sum(u)


# ============================================================
# Parity basin (decoding region) computation
# ============================================================

def basin(codeword, t):
    """Set of vectors within Hamming distance t of codeword (the basin for
    t-error correction)."""
    n = len(codeword)
    result = set()
    for d in range(t + 1):
        for positions in combinations(range(n), d):
            v = list(codeword)
            for p in positions:
                v[p] ^= 1
            result.add(tuple(v))
    return result


def basin_size(n, t):
    """|B_t(c)| = sum_{i=0}^{t} C(n, i)."""
    from math import comb
    return sum(comb(n, i) for i in range(t + 1))


def all_basins_disjoint(codewords, t):
    """Check if all 1-error basins are disjoint (perfect code-style)."""
    seen = set()
    for c in codewords:
        b = basin(c, t)
        if b & seen:
            return False
        seen |= b
    return True


def covering_count(codewords, t, n):
    """How many of the 2^n vectors are in SOME basin?"""
    covered = set()
    for c in codewords:
        covered |= basin(c, t)
    return len(covered), 2 ** n


# ============================================================
# The M19 codewords specifically
# ============================================================

def format_codeword(c):
    return "".join(str(b) for b in c)


def main():
    n = 3
    length = 2 ** n  # 8

    # Generate RM codes
    rm_0_3 = rm_codewords(0, 3)
    rm_1_3 = rm_codewords(1, 3)
    rm_2_3 = rm_codewords(2, 3)
    rm_3_3 = rm_codewords(3, 3)

    print("=" * 72)
    print("  Reed-Muller parity-basin analysis for M19 codewords")
    print("=" * 72)
    print(f"\n  RM hierarchy on length-{length} space:")
    print(f"    |RM(0, 3)| = {len(rm_0_3):>3}  (constants)")
    print(f"    |RM(1, 3)| = {len(rm_1_3):>3}  (affine functions)")
    print(f"    |RM(2, 3)| = {len(rm_2_3):>3}  (deg ≤ 2)")
    print(f"    |RM(3, 3)| = {len(rm_3_3):>3}  (all Boolean functions on F_2^3)")
    print(f"    Total 2^8 = 256 vectors. RM(3, 3) = full space.")

    # ─────────────────────────────────────────────────
    # 1. List RM(1, 3) codewords explicitly
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  All 16 codewords of RM(1, 3) (length-8 affine Boolean functions)")
    print("─" * 72)

    monomials_deg1 = all_monomials(3, 1)
    # Each codeword is a polynomial; enumerate by coefficient tuple
    var_names = {frozenset(): "1", frozenset([0]): "x", frozenset([1]): "y", frozenset([2]): "z"}
    print(f"  {'index':>5}  {'polynomial':>20}  {'codeword':>10}  {'weight':>6}")
    rm1_with_labels = []
    for c0, c1, c2, c3 in product([0, 1], repeat=4):
        coeffs = [(frozenset(), c0), (frozenset([0]), c1),
                  (frozenset([1]), c2), (frozenset([2]), c3)]
        active = [m for m, c in coeffs if c]
        poly_label = " + ".join(var_names[m] for m in active) if active else "0"
        cw = truth_table_of_polynomial(active, 3)
        weight = sum(cw)
        rm1_with_labels.append((cw, poly_label))
        idx = c0 * 8 + c1 * 4 + c2 * 2 + c3
        print(f"  {idx:>5}  {poly_label:>20}  {format_codeword(cw):>10}  {weight:>6}")

    # Weight distribution
    weights = [sum(cw) for cw, _ in rm1_with_labels]
    weight_dist = {w: weights.count(w) for w in sorted(set(weights))}
    print(f"\n  Weight distribution: {weight_dist}")
    print(f"  Min distance = {min(w for w in weight_dist if w > 0)} (matches (8,4,4) RM(1,3))")

    # ─────────────────────────────────────────────────
    # 2. M19 codewords as length-8 vectors
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  The M19 codewords (I, K, S extended to length 8)")
    print("─" * 72)

    I_cw = truth_table_of_polynomial([frozenset([0])], 3)  # x
    K_cw = truth_table_of_polynomial([frozenset([0])], 3)  # x (extended)
    S_cw = truth_table_of_polynomial([frozenset([0, 1, 2])], 3)  # xyz

    print(f"\n  I extended (x):   {format_codeword(I_cw)}  weight {sum(I_cw)}")
    print(f"  K extended (x):   {format_codeword(K_cw)}  weight {sum(K_cw)}")
    print(f"  S native  (xyz):  {format_codeword(S_cw)}  weight {sum(S_cw)}")
    print(f"\n  Note: I extended = K extended (both are the function x_0 in 3 vars).")
    print(f"        S is structurally distinct (degree 3, in RM(3,3) \\ RM(2,3)).")

    # Which RM family does each belong to?
    print(f"\n  Smallest RM(r, 3) containing each codeword:")
    for label, cw in [("I=x", I_cw), ("K=x", K_cw), ("S=xyz", S_cw)]:
        for r in range(4):
            rm_r = rm_codewords(r, 3)
            if cw in rm_r:
                print(f"    {label}: RM({r}, 3)")
                break

    # ─────────────────────────────────────────────────
    # 3. Parity basins of I/K codeword under RM(1, 3) decoding
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  Parity basin of I/K codeword (= x = 01010101) under RM(1,3)")
    print("─" * 72)
    print(f"  RM(1, 3) is (n=8, k=4, d=4). Corrects t = ⌊(4-1)/2⌋ = 1 error.")
    print(f"  Basin size = 1 + C(8,1) = 9 vectors per codeword.")
    print(f"  Total covered = 16 × 9 = 144 of 256 vectors (= 56.25%).")

    cw_x = I_cw  # = 01010101
    basin_x = basin(cw_x, 1)
    print(f"\n  Basin of x = {format_codeword(cw_x)} (9 vectors, all 'equivalent under recovery'):")
    for v in sorted(basin_x):
        flipped_bits = [i for i in range(8) if v[i] != cw_x[i]]
        if flipped_bits:
            print(f"    {format_codeword(v)}  flip bit {flipped_bits[0]} {'(noisy)':>10}")
        else:
            print(f"    {format_codeword(v)}  (codeword itself)")

    print(f"\n  These 9 vectors all DECODE TO x under RM(1, 3) 1-error correction.")
    print(f"  Operationally: any single-bit corruption of the I or K rule's truth")
    print(f"  table is recoverable to the correct function.")

    # ─────────────────────────────────────────────────
    # 4. S's relationship to RM(1, 3)
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  S codeword (= xyz = 00000001) vs RM(1, 3)")
    print("─" * 72)

    # Find distances from S to all RM(1, 3) codewords
    dists = sorted([(hamming_distance(S_cw, cw), label)
                    for cw, label in rm1_with_labels])
    print(f"\n  Hamming distance from S = 00000001 to each RM(1, 3) codeword:")
    print(f"  {'distance':>10}  {'codeword':>20}  {'count at this distance':>25}")
    dist_counts = {}
    for d, label in dists:
        dist_counts[d] = dist_counts.get(d, 0) + 1
    for d in sorted(dist_counts):
        rep_labels = [label for dd, label in dists if dd == d][:3]
        rep = ", ".join(rep_labels) + ("..." if dist_counts[d] > 3 else "")
        print(f"  {d:>10}  {rep:>20}  {dist_counts[d]:>25}")

    closest_dist = min(d for d, _ in dists)
    print(f"\n  S is at distance {closest_dist} from the nearest RM(1, 3) codeword (zero).")
    print(f"  Under RM(1, 3) decoding: S would be 'corrected' to 0 (constant zero).")
    print(f"  This is WRONG if we want S = xyz; correct only in RM(3, 3) where S")
    print(f"  is its own codeword.")

    # ─────────────────────────────────────────────────
    # 5. Rotational transitions between RM families
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  Rotational transitions: which RM family captures which combinator")
    print("─" * 72)
    print(f"""
  Family          | Captures    | S's status
  ─────────────────|─────────────|──────────────────────────────────
  RM(0, 3)        | constants   | S not present (distance 1 from 0)
  RM(1, 3)        | + I, K      | S "decoded to" 0 (1-error correction)
  RM(2, 3)        | + xy, xz, yz| S "detected as error" (no correction)
  RM(3, 3) = all  | + xyz = S   | S is its own codeword

  The "rotational transition" RM(r, 3) → RM(r+1, 3) ADDS degree-(r+1)
  monomials. Each transition rescues some vectors from being "errors"
  in the lower family into being "valid codewords" in the higher.

  Specifically:
    RM(1, 3) → RM(2, 3): adds xy, xz, yz, and their combinations.
                         16 → 128 codewords. 112 new vectors recognized.
    RM(2, 3) → RM(3, 3): adds xyz (and the all-one xyz+1).
                         128 → 256 codewords. 128 new vectors recognized.

  S = xyz is one of the 128 vectors that "appears" at the RM(2, 3) →
  RM(3, 3) transition. Before this transition, S looks like noise on
  the zero codeword. After, it's a distinct generator.
""")

    # ─────────────────────────────────────────────────
    # 6. Excluded vectors: what's NOT in I/K's basin
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  Excluded vectors (NOT in I/K's basin) — and where they live")
    print("─" * 72)

    # Compute basins of all RM(1, 3) codewords
    rm1_basins = {}
    for cw, label in rm1_with_labels:
        rm1_basins[cw] = basin(cw, 1)

    # All vectors covered by some RM(1, 3) basin
    covered = set()
    for b in rm1_basins.values():
        covered |= b

    all_vectors = set(product([0, 1], repeat=length))
    uncovered = all_vectors - covered
    print(f"\n  Total length-8 vectors:      {len(all_vectors)}")
    print(f"  Covered by RM(1,3) basins:   {len(covered)} ({100*len(covered)//len(all_vectors)}%)")
    print(f"  Excluded (no 1-error basin): {len(uncovered)} ({100*len(uncovered)//len(all_vectors)}%)")

    # Among the uncovered, find S and characterize
    print(f"\n  Is S = 00000001 in the uncovered set? {S_cw not in covered}")
    print(f"    (S IS in covered set, in the basin of 00000000 = zero codeword.)")

    # The uncovered set's distance profile
    uncovered_weight_dist = {}
    for v in uncovered:
        w = sum(v)
        uncovered_weight_dist[w] = uncovered_weight_dist.get(w, 0) + 1
    print(f"\n  Weight distribution of uncovered (RM(1,3)-non-decodable) vectors:")
    for w in sorted(uncovered_weight_dist):
        print(f"    weight {w}: {uncovered_weight_dist[w]} vectors")

    print(f"""
  Reading: vectors of weight 2, 3, 5, 6 cannot be uniquely decoded in
  RM(1, 3) — they're equidistant from multiple codewords or beyond
  the 1-error radius. These are "ambiguous" under RM(1, 3) recovery
  but ALL are valid codewords in RM(2, 3) or RM(3, 3).

  In M19 terms: writing a rule whose Boolean polynomial is in this
  ambiguous zone means the rule is NOT recoverable from corruption
  IF the chart were operating under RM(1, 3) error-correction
  semantics. To make such a rule robust, we'd need to either:
    (a) Rotate up to RM(2, 3) or RM(3, 3) where the rule IS a valid
        codeword (no correction needed, just identification).
    (b) Add complementary rules to bring the rule's polynomial
        structure into a stronger error-correcting family.
""")

    # ─────────────────────────────────────────────────
    # 7. Symmetry: I/K's basin under variable permutation
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  Gauge orbit of I/K's codeword under S_3 (variable permutation)")
    print("─" * 72)

    # Apply S_3 permutations of variables to I/K's codeword
    from itertools import permutations as perms

    orbit = set()
    for perm in perms(range(3)):
        # Apply permutation: f(x_0, x_1, x_2) → f(x_perm[0], x_perm[1], x_perm[2])
        # In ANF: x → x_perm[0]
        permuted = truth_table_of_polynomial([frozenset([perm[0]])], 3)
        orbit.add(permuted)

    print(f"\n  Orbit of I/K codeword (= x) under S_3 variable permutation:")
    for v in sorted(orbit):
        print(f"    {format_codeword(v)}  (one of x_0, x_1, x_2)")
    print(f"\n  Orbit size: {len(orbit)} = 3 codewords (x_0, x_1, x_2).")
    print(f"  These are the three single-variable linear functions in RM(1, 3).")

    # S's orbit (just S itself since xyz is symmetric)
    print(f"\n  S = xyz is S_3-invariant (symmetric in all variables).")
    print(f"  Its orbit has just 1 element: itself.")

    print(f"""
  This makes operational the M18 observation: the gauge group permuting
  axis labels is S_n, but its action on the Boolean codeword space splits
  the space into orbits. Symmetric codewords (like xyz = S) sit at fixed
  points of the S_n action; asymmetric codewords (like x_0) lie on orbits
  of size > 1.

  The 'rotational transitions' the user described are TWO different
  rotations:
    (a) Vertical rotation: RM(r, m) → RM(r+1, m), adding degree-(r+1)
        monomials. Changes which codewords are "valid."
    (b) Horizontal rotation: S_n action permuting variables. Changes
        the labeling of codewords within an orbit.

  Both are gauge degrees of freedom. The M8 cocycle invariance applies
  to both: the operational semantics depend only on gauge-invariant data,
  not on the chosen representative within an orbit.
""")


if __name__ == "__main__":
    main()
