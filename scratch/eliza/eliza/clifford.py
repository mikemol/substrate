"""Eliza.Clifford — Cl(ℝⁿ, q=+1) graded algebra for the DD-arc.

Per [[expose-generator-not-orbit]]: AA/BB/CC-arc rotation layers are
individual GRADES (orbit points) of a single ambient generator —
the Clifford algebra Cl(ℝⁿ). DD1 surfaces the generator.

The codec restriction is the F₂-linear sub-coalgebra (subset-masks
⊆ {0,...,n-1}, coefficients in {-1, 0, 1}). Signs are retained so
the wedge product satisfies e_i ∧ e_j = -e_j ∧ e_i, distinguishing
the substrate's chirality F₂ from a flat Z/2 grading.

Algebra (Euclidean signature, q(e_i) = 1):
  basis        e_S indexed by subsets S ⊆ {0,...,n-1}; bitmask
  product      e_i e_j = -e_j e_i for i ≠ j; e_i e_i = 1
  multivector  Σ c_S e_S with c_S ∈ ℤ

Grade decomposition:
  Λ⁰ = scalar      (identity emission; baseline)
  Λ¹ = vector      (single bit-flip direction)
  Λ² = bivector    (transposition; AA-arc S₄ residue subspace)
  Λᵏ = grade-k multivector
  Λⁿ = pseudoscalar (chirality F₂)

Per [[3plus1-parity-universal]] at n = 4 (bit-width 4):
  Cl(ℝ⁴) has 16 basis elements, 5 grades. The split
    (Λ⁰ ⊕ Λ⁴) ⊕ Λ² ⊕ (Λ¹ ⊕ Λ³)
  carries one 3+1 reading; the bivector axis carries the
  Coxeter/transposition content.

Hamming-neighbourhood note (per user, 2026-05-20): grade-k blades
correspond to weight-k Hamming patterns over n bits; Λ¹ is the
weight-1 single-bit-error coset, Λ² the weight-2 paired-error coset,
etc. DD2's bit-flip tracer factors through this correspondence and
DD3's grade projector is precisely the Hamming-weight syndrome
projection — recovery from a perturbation = projecting back onto
the original grade-k coset.

Multivector representation: dict[bitmask: int → coefficient: int],
canonical with no zero entries.
"""

from __future__ import annotations

from typing import Dict, Iterator, Tuple

Multivector = Dict[int, int]


# --- Constructors -----------------------------------------------------


def grade_of(mask: int) -> int:
    """Number of basis vectors in the multivector mask."""
    return bin(mask).count("1")


def scalar(c: int = 1) -> Multivector:
    """Λ⁰ element with coefficient c."""
    return {0: c} if c else {}


def vector(i: int, c: int = 1) -> Multivector:
    """Λ¹ basis blade e_i with coefficient c."""
    return {1 << i: c} if c else {}


def basis(mask: int, c: int = 1) -> Multivector:
    """Arbitrary basis blade e_{mask} with coefficient c."""
    return {mask: c} if c else {}


def pseudoscalar(n: int) -> Multivector:
    """Top blade I = e_0 ∧ ... ∧ e_{n-1} at dimension n."""
    return {(1 << n) - 1: 1}


# --- Linear ops -------------------------------------------------------


def add(a: Multivector, b: Multivector) -> Multivector:
    """Pointwise addition; zero coefficients dropped."""
    out: Multivector = dict(a)
    for mask, coef in b.items():
        new = out.get(mask, 0) + coef
        if new:
            out[mask] = new
        elif mask in out:
            del out[mask]
    return out


def neg(a: Multivector) -> Multivector:
    return {m: -c for m, c in a.items()}


def scale_mv(a: Multivector, c: int) -> Multivector:
    if c == 0:
        return {}
    return {m: c * v for m, v in a.items()}


# --- Blade products ---------------------------------------------------


def _blade_product(a_mask: int, b_mask: int) -> Tuple[int, int]:
    """Compute (sign, result_mask) for e_a · e_b under Cl(ℝⁿ, q=+1).

    Sorted-blade convention: process bits of b from low to high,
    sliding each past higher bits of the running blade; matching
    indices collapse via e_i² = 1.
    """
    sign = 1
    running = a_mask
    b = b_mask
    i = 0
    while b:
        if b & 1:
            higher = running >> (i + 1)
            if bin(higher).count("1") & 1:
                sign = -sign
            running ^= (1 << i)
        b >>= 1
        i += 1
    return sign, running


def geometric_product(a: Multivector, b: Multivector) -> Multivector:
    """Full Clifford product a * b."""
    out: Multivector = {}
    for ma, va in a.items():
        for mb, vb in b.items():
            sign, m = _blade_product(ma, mb)
            new = out.get(m, 0) + sign * va * vb
            if new:
                out[m] = new
            elif m in out:
                del out[m]
    return out


def wedge(a: Multivector, b: Multivector) -> Multivector:
    """Outer (wedge) product: contributions only when masks disjoint.

    Equivalent to grade-raised geometric product: a ∧ b is the
    component of (a * b) of grade exactly grade(a) + grade(b).
    """
    out: Multivector = {}
    for ma, va in a.items():
        for mb, vb in b.items():
            if ma & mb:
                continue
            sign, m = _blade_product(ma, mb)
            new = out.get(m, 0) + sign * va * vb
            if new:
                out[m] = new
            elif m in out:
                del out[m]
    return out


def left_contract(a: Multivector, b: Multivector) -> Multivector:
    """Left contraction a ⌟ b: blades where a ⊆ b survive.

    grade(a ⌟ b) = grade(b) - grade(a) when nonzero. This is the
    Hamming-syndrome view: a is the perturbation pattern, b ⌟ a
    extracts the higher-grade content "modulo" a.
    """
    out: Multivector = {}
    for ma, va in a.items():
        for mb, vb in b.items():
            if (ma & mb) != ma:
                continue
            sign, m = _blade_product(ma, mb)
            new = out.get(m, 0) + sign * va * vb
            if new:
                out[m] = new
            elif m in out:
                del out[m]
    return out


# --- Involutions ------------------------------------------------------


def reverse(a: Multivector) -> Multivector:
    """Reverse anti-automorphism: (e_{i_1...i_k})† = e_{i_k...i_1}.

    Sign: (-1)^(k(k-1)/2) on grade-k blades. Used in DD2/DD3 for
    bit-flip path inversion (peel a Clifford-element back to its
    reference point).
    """
    out: Multivector = {}
    for m, c in a.items():
        k = bin(m).count("1")
        sign = -1 if (k * (k - 1) // 2) & 1 else 1
        new = sign * c
        if new:
            out[m] = new
    return out


def involute(a: Multivector) -> Multivector:
    """Grade involution: (-1)^k on grade-k blades."""
    out: Multivector = {}
    for m, c in a.items():
        k = bin(m).count("1")
        new = -c if k & 1 else c
        if new:
            out[m] = new
    return out


# --- Grade ops --------------------------------------------------------


def grade_project(a: Multivector, k: int) -> Multivector:
    """Keep only blades of grade exactly k. Λᵏ-projection."""
    return {m: c for m, c in a.items() if bin(m).count("1") == k}


def grade_decomposition(a: Multivector) -> Dict[int, Multivector]:
    """Split a into {k: ⟨a⟩_k}; sum recovers a."""
    out: Dict[int, Multivector] = {}
    for m, c in a.items():
        k = bin(m).count("1")
        out.setdefault(k, {})[m] = c
    return out


def hamming_weight_profile(a: Multivector) -> Dict[int, int]:
    """Total |coefficient| per grade; Hamming-weight histogram of a.

    Per user-2026-05-20 Hamming-neighbourhood note: this IS the
    syndrome profile when a is read as a perturbation multivector.
    """
    out: Dict[int, int] = {}
    for m, c in a.items():
        k = bin(m).count("1")
        out[k] = out.get(k, 0) + abs(c)
    return out


# --- Equality & enumeration -------------------------------------------


def canonical(a: Multivector) -> Multivector:
    """Strip zero coefficients."""
    return {m: c for m, c in a.items() if c}


def equal(a: Multivector, b: Multivector) -> bool:
    return canonical(a) == canonical(b)


def all_basis(n: int) -> Iterator[int]:
    """All 2^n basis masks at dimension n."""
    return iter(range(1 << n))


def all_blades_of_grade(n: int, k: int) -> Iterator[int]:
    """All grade-k basis masks at dimension n."""
    for m in range(1 << n):
        if bin(m).count("1") == k:
            yield m


def dim_grade(n: int, k: int) -> int:
    """|Λᵏ ⊂ Cl(ℝⁿ)| = C(n, k)."""
    if k < 0 or k > n:
        return 0
    out = 1
    for i in range(k):
        out = out * (n - i) // (i + 1)
    return out


# --- Self-check -------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    ok = True

    # 1. Associativity of geometric product (sample).
    for n in (2, 3, 4):
        a = add(scalar(2), vector(0))
        b = add(vector(1 % n), wedge(vector(0), vector(1 % n)))
        c = add(scalar(-1), vector(min(n - 1, 2)))
        left = geometric_product(geometric_product(a, b), c)
        right = geometric_product(a, geometric_product(b, c))
        if not equal(left, right):
            if verbose:
                print(f"FAIL: associativity at n={n}")
            ok = False

    # 2. Wedge antisymmetry: e_i ∧ e_j = -(e_j ∧ e_i) for i ≠ j.
    for n in (2, 3, 4):
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                aw = wedge(vector(i), vector(j))
                bw = neg(wedge(vector(j), vector(i)))
                if not equal(aw, bw):
                    if verbose:
                        print(f"FAIL: wedge antisymmetry n={n} ({i},{j})")
                    ok = False

    # 3. Wedge self-annihilation: e_i ∧ e_i = 0.
    for n in (2, 3, 4):
        for i in range(n):
            if wedge(vector(i), vector(i)):
                if verbose:
                    print(f"FAIL: e_{i} ∧ e_{i} ≠ 0 at n={n}")
                ok = False

    # 4. e_i² = 1 (Euclidean).
    for n in (2, 3, 4):
        for i in range(n):
            if not equal(geometric_product(vector(i), vector(i)), scalar(1)):
                if verbose:
                    print(f"FAIL: e_{i}² ≠ 1 at n={n}")
                ok = False

    # 5. Grade decomposition completeness.
    for n in (2, 3, 4):
        a = add(scalar(3), add(vector(0), wedge(vector(0), vector(1 % n))))
        recon: Multivector = {}
        for k in range(n + 1):
            recon = add(recon, grade_project(a, k))
        if not equal(recon, a):
            if verbose:
                print(f"FAIL: grade decomp incomplete at n={n}")
            ok = False

    # 6. Pseudoscalar squares: I² = (-1)^(n(n-1)/2).
    for n in (2, 3, 4):
        I = pseudoscalar(n)
        sq = geometric_product(I, I)
        expected = -1 if (n * (n - 1) // 2) & 1 else 1
        if not equal(sq, scalar(expected)):
            if verbose:
                print(f"FAIL: I² at n={n} (expected {expected})")
            ok = False

    # 7. Reverse is involution: (a†)† = a.
    for n in (2, 3, 4):
        a = add(add(scalar(1), vector(0)),
                wedge(vector(0), vector(min(n - 1, 1))))
        if not equal(reverse(reverse(a)), a):
            if verbose:
                print(f"FAIL: reverse not involution at n={n}")
            ok = False

    # 8. Λᵏ dimension count: Σ_k C(n, k) = 2^n.
    for n in (2, 3, 4):
        total = sum(dim_grade(n, k) for k in range(n + 1))
        if total != (1 << n):
            if verbose:
                print(f"FAIL: dim count at n={n}: {total} ≠ {1 << n}")
            ok = False

    # 9. Cl(ℝ²) check: e_0 e_1 e_0 e_1 = -1 (bivector squared).
    e01 = wedge(vector(0), vector(1))
    if not equal(geometric_product(e01, e01), scalar(-1)):
        if verbose:
            print(f"FAIL: bivector square ≠ -1")
        ok = False

    # 10. Hamming-weight profile sanity.
    a = add(scalar(1), add(vector(0), wedge(vector(1), vector(2))))
    prof = hamming_weight_profile(a)
    if prof != {0: 1, 1: 1, 2: 1}:
        if verbose:
            print(f"FAIL: Hamming weight profile {prof}")
        ok = False

    if verbose:
        print(f"clifford self_check {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
