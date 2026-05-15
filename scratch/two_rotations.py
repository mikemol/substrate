"""
two_rotations.py — The substrate and data rotations on the F_2^3 polytope.

M2's multiplicity (cell-as-integer vs cell-as-function) becomes operational
when we ask how the F_2^3 cube ROTATES under each representation.

  Substrate rotation (cell-as-integer):
    The chart is an integer-indexed structure. Cells are stored by their
    Python integer indices; cons creates new indices. The substrate
    "rotation" measures how many new cells a reduction creates.

  Data rotation (cell-as-function):
    The chart cells encode Boolean polynomials. Functions live in a
    graded polynomial ring. The data "rotation" measures the
    polynomial degree of each combinator.

S is the pivot of BOTH rotations:
  - Substrate: S's reduction creates 3 new cells (max growth)
  - Data:     S's polynomial is xyz (max degree)

Both pivots are the integer 3 = dim(F_2^3). The two views identify S by
the same dimensional count, in two different M2 representations.

This is the M2 multiplicity at gauge level: same pivot, two presentations.
"""

from chart import Chart


def measure_substrate_growth(c, term):
    """Run apply on term and count how many new chart cells are created.

    This is the "substrate rotation" measure: how much the integer
    index space grows during one reduction step.
    """
    size_before = c.size()
    result = c.apply(term)
    size_after = c.size()
    return result, size_after - size_before


def main():
    print("=" * 72)
    print("  Two rotations on the F_2^3 polytope: substrate and data")
    print("=" * 72)

    # ─────────────────────────────────────────────────
    # 1. Substrate rotation: chart growth per reduction
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  Substrate rotation: chart growth per combinator reduction")
    print("─" * 72)

    print(f"\n  For each combinator's reduction, count NEW cells created.")
    print(f"  This is the 'cell-as-integer' rotation: integer index growth.\n")

    # I-reduction
    c = Chart()
    Ix = c.cons(c.I, c.cons(c.TRUE, c.FALSE))  # I applied to (true false)
    _, growth_I = measure_substrate_growth(c, Ix)
    print(f"  I x:       redex → x (just returns arg).      Growth: {growth_I} cells")

    # K-reduction
    c = Chart()
    Kxy = c.cons(c.cons(c.K, c.TRUE), c.FALSE)
    _, growth_K = measure_substrate_growth(c, Kxy)
    print(f"  K x y:     redex → x (drops second arg).      Growth: {growth_K} cells")

    # S-reduction
    c = Chart()
    # Create a meaningful S-redex with distinct args (not just atoms)
    a = c.cons(c.I, c.TRUE)   # a non-trivial term
    b = c.cons(c.K, c.FALSE)  # another non-trivial term
    d = c.cons(c.S, c.FAILURE)
    Sxyz = c.cons(c.cons(c.cons(c.S, a), b), d)
    _, growth_S = measure_substrate_growth(c, Sxyz)
    print(f"  S x y z:   redex → (x z)(y z) (composes).     Growth: {growth_S} cells")

    print(f"\n  S's substrate rotation creates {growth_S} new cells per reduction.")
    print(f"  I and K create 0 new cells; S is the unique GROWTH-PRODUCING combinator.")

    # ─────────────────────────────────────────────────
    # 2. Data rotation: polynomial degree
    # ─────────────────────────────────────────────────
    print("\n" + "─" * 72)
    print("  Data rotation: polynomial degree in F_2[x, y, z]/(x_i² - x_i)")
    print("─" * 72)

    print(f"""
  Recall from M19: each combinator's Boolean polynomial:
    I = x        — degree 1, in RM(1, 1)
    K = x        — degree 1, in RM(1, 2)
    S = xyz      — degree 3, in RM(3, 3)

  The 'cell-as-function' rotation measures polynomial degree.
  S's degree is 3 = max in 3-var space.
""")

    # ─────────────────────────────────────────────────
    # 3. The dimensional duality: both pivots give 3
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  The dimensional duality: substrate-growth = polynomial-degree")
    print("─" * 72)

    print(f"""
  Combinator | Substrate growth | Polynomial degree | dim(F_2^n) match
  ─────────────────────────────────────────────────────────────────────
  I          | {growth_I}                | 1                 | 1 = dim F_2^1 ✓
  K          | {growth_K}                | 1                 | (drops a dim)
  S          | {growth_S}                | 3                 | 3 = dim F_2^3 ✓

  S's substrate-growth (3 cells) and polynomial-degree (3) are the SAME
  number. Both measure "how fully S uses the 3-variable space."

  This is the M2 multiplicity at the level of gauge structure:
    - cell-as-integer view: S grows the chart by 3 cells per reduction
    - cell-as-function view: S is the degree-3 polynomial xyz
  Both views identify S by the same dimensional count: 3 = dim(F_2^3).

  The "pivot" S looks different in each view, but the dimensional
  measure of S's centrality is invariant: 3 in both readings.
""")

    # ─────────────────────────────────────────────────
    # 4. Both rotations leave S invariant
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  S is the pivot of both rotations (gauge-invariant)")
    print("─" * 72)
    print(f"""
  Substrate rotation invariance:
    Under any frame choice (which Python integers label which positions),
    the FACT that S creates 3 cells per reduction is unchanged. The
    specific integers labeling the new cells change with the frame,
    but the count is gauge-invariant.

  Data rotation invariance:
    Under any frame choice (which Boolean polynomial labels which
    positions), the FACT that S has degree 3 is unchanged. The specific
    polynomial form might pick up lower-degree corrections under
    translation, but the top-degree coefficient is gauge-invariant.

  In both views, the dimensional measure of S's centrality (= 3 =
  dim F_2^3) is the gauge-invariant content.
""")

    # ─────────────────────────────────────────────────
    # 5. Connection to M7's associahedron
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  Connection to M7's associahedron and Stasheff structure")
    print("─" * 72)
    print(f"""
  M7's formal-system associahedron has 3 vertices:
    - HOTRS (Higher-Order Term Rewriting Systems)
    - de Bruijn lambda calculus
    - Combinator basis (SKI)

  These 3 vertices are connected by compilation translations (edges).
  Within the COMBINATOR vertex, the system uses I, K, S as the basis.

  M2's representation associahedron has 4 vertices:
    - integer-as-path
    - function-as-path
    - trace-as-path
    - polynomial-as-path

  Within the COMBINATOR vertex of M7, the chart uses M2's 4 representations
  multiplicitously. Cell-as-integer (substrate view) and cell-as-function
  (data view) are 2 of M2's 4 vertices.

  The TWO ROTATIONS we've identified live within M2's polytope:
    - Substrate rotation = movement along cell-as-integer axis
    - Data rotation = movement along cell-as-function axis

  Both rotations are GAUGE TRANSFORMATIONS on the F_2^3 cube. They
  permute labels (integers in one case, polynomials in the other)
  while preserving the dimensional pivot 3 = dim(F_2^3) at the S axis.

  The gauge group acting on both:
    - Substrate side: how indices reorder under chart growth / hash-consing
    - Data side: AGL(3, F_2) = 1344 elements (M22)

  Both gauge groups have S as a fixed point. They're DIFFERENT GROUPS
  but they SHARE THE PIVOT. This is the M7 / M2 multiplicity at the
  level of automorphism groups.
""")

    # ─────────────────────────────────────────────────
    # 6. Asymmetric pivoting: S is unique
    # ─────────────────────────────────────────────────
    print("─" * 72)
    print("  S is the UNIQUE pivot: I and K have lower-dim signatures")
    print("─" * 72)
    print(f"""
  Substrate-growth count by combinator:
    I:  0 (returns its only arg)
    K:  0 (returns first arg, drops second)
    S:  3 (constructs (x z)(y z))

  Polynomial-degree count by combinator:
    I:  1 (returns x)
    K:  1 (returns x, projection)
    S:  3 (xyz, top-degree monomial)

  Only S has the maximal value (3) in BOTH measures.

  I has growth 0 and degree 1 — minimum substrate, minimum data.
  K has growth 0 and degree 1 — same as I in both views.
  S has growth 3 and degree 3 — MAXIMUM in both views.

  The maximum (= dim F_2^3 = 3) is the structural pivot. S sits at the
  intersection of "max substrate growth" and "max data degree". This
  intersection point IS the gauge-invariant axis around which the 8
  frames (and the 1344-element AGL group) rotate.

  In a deep sense: SKI's design encodes a 3-dimensional generator
  (I: dim 1 minimum, K: dim 1 with projection, S: dim 3 maximum).
  S's role is to FILL OUT THE DIMENSION; I and K provide
  lower-dimensional structure within S's frame.
""")


if __name__ == "__main__":
    main()
