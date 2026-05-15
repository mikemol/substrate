"""
rm_in_tier1.py — Reed-Muller structure inside the tier-1 instruction table.

The combinators I, K, S, when viewed as Boolean functions (treating
application as Boolean multiplication, i.e., AND, with F_2 arithmetic),
have specific Reed-Muller polynomial signatures.

I(x)     = x                        — RM(1, 1) generator (linear)
K(x, y)  = x                        — RM(1, 2) projection generator
S(x,y,z) = (x z)(y z) = xyz in F_2  — RM(3, 3) top-degree monomial

The table spans I/K/S = generators for distinct Reed-Muller code levels.
Without S, the table generates only LINEAR Boolean functions (RM(1, m)).
With S, it lifts to the FULL Boolean function hierarchy.

This is the precise structural meaning of "S makes combinatory logic
Turing-complete": S is the generator that adds nonlinearity (degree > 1)
to the otherwise affine-only K + I basis.
"""

from itertools import product


def eval_boolean(poly_terms, point):
    """Evaluate a Boolean polynomial in ANF on a point in F_2^n.

    poly_terms: list of tuples representing monomials. Each tuple is the
    set of variable indices in the monomial. Empty tuple = constant 1.
    point: tuple of n F_2 values.

    Returns: F_2 value (0 or 1).
    """
    result = 0
    for monomial in poly_terms:
        term = 1
        for var_idx in monomial:
            term &= point[var_idx]
        result ^= term
    return result


def anf_truth_table(poly_terms, n):
    """Truth table of a Boolean polynomial as a tuple over F_2^n."""
    return tuple(
        eval_boolean(poly_terms, p)
        for p in product([0, 1], repeat=n)
    )


def compute_anf(truth_table, n):
    """Compute the ANF (algebraic normal form) of a Boolean function from
    its truth table. Returns a set of monomials (each a frozenset of var indices).

    Uses the Möbius transform over F_2.
    """
    coefficients = list(truth_table)
    # Möbius transform
    for i in range(n):
        for j in range(2 ** n):
            if j & (1 << i):
                coefficients[j] ^= coefficients[j ^ (1 << i)]
    # Extract monomials with coefficient 1
    monomials = set()
    for j, c in enumerate(coefficients):
        if c:
            vars_in_monomial = frozenset(
                i for i in range(n) if j & (1 << i)
            )
            monomials.add(vars_in_monomial)
    return monomials


def degree(monomials):
    """Degree of the polynomial = max degree of any monomial."""
    return max((len(m) for m in monomials), default=0)


def reed_muller_class(monomials, n):
    """Which RM(r, n) does this polynomial belong to? Returns smallest r."""
    return degree(monomials), n


def format_monomial(m, var_names):
    if not m:
        return "1"
    return "".join(var_names[i] for i in sorted(m))


def format_polynomial(monomials, var_names):
    if not monomials:
        return "0"
    return " + ".join(format_monomial(m, var_names) for m in sorted(monomials, key=lambda x: (len(x), tuple(sorted(x)))))


# ============================================================
# I, K, S as Boolean polynomials
# ============================================================

def boolean_truth_table(f, n):
    """Truth table where tt[j] = f(x_0, x_1, ..., x_{n-1}) with x_i = bit_i(j).

    This is the standard ANF convention: bit i of the index = variable i.
    """
    return tuple(
        f(*[(j >> i) & 1 for i in range(n)])
        for j in range(2**n)
    )


def analyze_I():
    """I(x) = x."""
    print("\n" + "─" * 72)
    print("  I(x) = x")
    print("─" * 72)
    n = 1
    tt = boolean_truth_table(lambda x: x, n)
    monomials = compute_anf(tt, n)
    r, _ = reed_muller_class(monomials, n)
    print(f"  Arity:        {n}")
    print(f"  Truth table:  {tt}  (indexed by point in F_2^{n})")
    print(f"  ANF:          {format_polynomial(monomials, ['x'])}")
    print(f"  Degree:       {degree(monomials)}")
    print(f"  RM class:     RM({r}, {n}) — identity generator")
    print(f"  Weight:       {sum(tt)} / {2**n}")
    return monomials


def analyze_K():
    """K(x, y) = x — projection π_1."""
    print("\n" + "─" * 72)
    print("  K(x, y) = x")
    print("─" * 72)
    n = 2
    tt = boolean_truth_table(lambda x, y: x, n)
    monomials = compute_anf(tt, n)
    r, _ = reed_muller_class(monomials, n)
    print(f"  Arity:        {n}")
    print(f"  Truth table:  {tt}")
    print(f"  ANF:          {format_polynomial(monomials, ['x', 'y'])}")
    print(f"  Degree:       {degree(monomials)}")
    print(f"  RM class:     RM({r}, {n}) — projection π_1")
    print(f"  Weight:       {sum(tt)} / {2**n}")
    return monomials


def analyze_S():
    """S(x, y, z) = (x z)(y z) which is xyz in F_2."""
    print("\n" + "─" * 72)
    print("  S(x, y, z) = (x z)(y z) → x∧y∧z (in F_2 Boolean algebra)")
    print("─" * 72)
    n = 3
    tt = boolean_truth_table(lambda x, y, z: (x & z) & (y & z), n)
    monomials = compute_anf(tt, n)
    r, _ = reed_muller_class(monomials, n)
    print(f"  Arity:        {n}")
    print(f"  Truth table:  {tt}")
    print(f"  ANF:          {format_polynomial(monomials, ['x', 'y', 'z'])}")
    print(f"  Degree:       {degree(monomials)}")
    print(f"  RM class:     RM({r}, {n}) — top-degree monomial xyz")
    print(f"  Weight:       {sum(tt)} / {2**n}")
    return monomials


def reed_muller_dim(r, m):
    """Dimension of RM(r, m)."""
    from math import comb
    return sum(comb(m, i) for i in range(r + 1))


def code_hierarchy():
    """Show the Reed-Muller hierarchy at m = 1, 2, 3 and where I, K, S sit."""
    print("\n" + "=" * 72)
    print("  Reed-Muller hierarchy and I/K/S placement")
    print("=" * 72)
    print()
    print(f"  RM(r, m) has dimension = C(m,0) + C(m,1) + ... + C(m,r).")
    print()
    print(f"  {'m':>3}  {'r':>3}  {'dim':>5}  {'2^dim':>10}  {'name':>20}  {'I/K/S':>10}")
    for m in [1, 2, 3]:
        for r in range(m + 1):
            d = reed_muller_dim(r, m)
            num_codewords = 2 ** d
            name = f"RM({r}, {m})"
            ix = ""
            if (m, r) == (1, 1):
                ix = "I lives here"
            elif (m, r) == (2, 1):
                ix = "K lives here"
            elif (m, r) == (3, 3):
                ix = "S top-monomial"
            print(f"  {m:>3}  {r:>3}  {d:>5}  {num_codewords:>10}  {name:>20}  {ix:>10}")


def hierarchy_observation():
    print("\n" + "=" * 72)
    print("  Structural observation: I/K/S as RM hierarchy generators")
    print("=" * 72)
    print(f"""
  The three combinators occupy distinct positions in the RM hierarchy:

  I:  Generator of RM(1, 1) — the LINEAR part of 1-variable space.
      Adds x to {{0, 1}} (constants RM(0, 1)).

  K:  Lives in RM(1, 2), specifically the projection π_1.
      Linear (degree 1), but in a 2-variable space.

  S:  TOP-DEGREE monomial xyz in RM(3, 3).
      Degree 3. Adds xyz to RM(2, 3) to span the full Boolean function
      space on 3 variables.

  WITHOUT S:
    K + I alone generate only AFFINE Boolean functions (RM(1, m)).
    These are too weak for general computation; they cannot express
    nonlinearity like AND of two distinct variables (xy).

  WITH S:
    The basis becomes Turing-complete. S contributes the multiplicative
    structure that lifts RM(1, m) toward RM(m, m) = full Boolean space.

  This is the RM-coding interpretation of Schönfinkel's original SKI
  result: SKI is sufficient because S provides the degree-lifting
  generator that K + I lack.

  The tier-1 instruction table IS the RM-hierarchy basis:
    - Constants: NIL, TRUE, FALSE (degree 0 generators)
    - Linear (I, K): degree-1 generators
    - Nonlinear (S): degree-3 generator (highest in 3-var space)

  Reed-Muller is structurally present at the level of WHICH POLYNOMIAL
  STRUCTURES the combinators express, not just at the meta-architecture
  (Fano plane / axis-signatures). Both layers carry RM structure; they
  do so independently and at different scales.
""")


def kleene_table():
    """Show the Boolean truth tables for I, K, S side by side as RM codewords."""
    print("\n" + "=" * 72)
    print("  Truth tables as RM codewords")
    print("=" * 72)
    print()
    # Embed everything in F_2^3 = 8-bit codewords for comparison.
    # I(x) extended: f(x, y, z) = x, evaluated at all 8 points
    # K(x, y) extended: f(x, y, z) = x
    # S(x, y, z) = xyz
    points_8 = list(product([0, 1], repeat=3))

    I_extended = tuple(p[0] for p in points_8)  # f = x
    K_extended = tuple(p[0] for p in points_8)  # f = x (same as I extended)
    S_func = tuple(p[0] & p[1] & p[2] for p in points_8)  # f = xyz

    print(f"  All viewed as codewords of length 8 = 2^3:")
    print()
    print(f"  Position:        000 001 010 011 100 101 110 111")
    print(f"  I extended (x):  {' '.join(str(b) for b in I_extended).rjust(31)}  weight {sum(I_extended)}")
    print(f"  K extended (x):  {' '.join(str(b) for b in K_extended).rjust(31)}  weight {sum(K_extended)}")
    print(f"  S native (xyz):  {' '.join(str(b) for b in S_func).rjust(31)}  weight {sum(S_func)}")
    print()
    print(f"  I and K extended both have weight 4 (half-zero, half-one).")
    print(f"  S has weight 1 (the single point 111).")
    print()
    print(f"  In RM(1, 3) (affine functions, length 8, dim 4): both x-functions")
    print(f"  have weight 4, matching the RM(1, 3) minimum distance d = 4.")
    print(f"  S has weight 1, the minimum-weight nonzero codeword of RM(3, 3).")


def main():
    print("=" * 72)
    print("  Reed-Muller structure within the tier-1 instruction table")
    print("=" * 72)

    I_anf = analyze_I()
    K_anf = analyze_K()
    S_anf = analyze_S()

    code_hierarchy()
    kleene_table()
    hierarchy_observation()


if __name__ == "__main__":
    main()
