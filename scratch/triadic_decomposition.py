"""
triadic_decomposition.py — The three-aspect decomposition of computation.

Computation has a fundamental triadic structure:
  - DATA / OBJECTS:   what exists (stable configurations)
  - COMPUTE / MORPHISM: what changes (operations)
  - STATE / TEMPORAL: when/where it lives (sequence of evolution)

These form a structural quotient algebra:
  temporal = objects × morphism
  morphism = temporal / objects
  objects  = morphism / temporal

Each aspect is derivable from the other two. No aspect can stand alone:
  - Data without compute is inert
  - Compute without data is empty
  - State/temporal without objects-and-morphisms is contentless

This is the F_2^3 structure of our 3 axes: not arbitrary coordinates, but
the three aspects of computation itself. Each Boolean variable in
F_2[x, y, z]/(x_i² - x_i) corresponds to one aspect:
  x = DATA (object)
  y = COMPUTE (morphism)
  z = STATE (temporal)

The 8 polynomial monomials = 8 subsets of {data, compute, state} =
8 distinct "kinds of operation" the chart can express:

  1        — neither (constant, no engagement)
  x        — pure data manipulation
  y        — pure compute (operation, no object)
  z        — pure state (temporal flow, no content)
  xy       — data + compute (data manipulation by operation)
  xz       — data + state (data evolving over time)
  yz       — compute + state (operations sequenced in time)
  xyz = S  — DATA × COMPUTE × STATE (fully triadic)

S is the unique combinator that engages ALL THREE aspects. Without S,
the system has only sub-triadic operations. S realizes the full
computational triad.

This explains why S is the gauge-invariant pivot: it's the unique
generator at the apex of the triadic algebra, where all three quotient
relations converge.
"""

from itertools import product


# ============================================================
# The triadic algebra
# ============================================================

ASPECTS = {
    0: ("x", "DATA / objects"),
    1: ("y", "COMPUTE / morphism"),
    2: ("z", "STATE / temporal"),
}


def monomial_label(subset):
    """Subset of {0, 1, 2} → polynomial monomial label."""
    if not subset:
        return "1"
    return "".join(ASPECTS[i][0] for i in sorted(subset))


def monomial_aspects(subset):
    """Which aspects does this monomial engage?"""
    if not subset:
        return "(neither aspect)"
    return " × ".join(ASPECTS[i][1].split(" / ")[0] for i in sorted(subset))


def monomial_truth_table(subset):
    """Truth table on F_2^3 of the monomial Π x_i for i in subset."""
    return tuple(
        int(all((j >> i) & 1 for i in subset))
        for j in range(8)
    )


# ============================================================
# The 8 monomials and what they mean for computation
# ============================================================

def enumerate_triadic_monomials():
    print("=" * 72)
    print("  The 8 polynomial monomials = 8 subsets of {data, compute, state}")
    print("=" * 72)

    print(f"\n  Mapping: x = DATA, y = COMPUTE, z = STATE")
    print(f"  Each Boolean monomial = a 'kind of operation' the chart expresses.\n")

    print(f"  {'subset':<10}  {'monomial':<10}  {'truth table':<14}  {'meaning'}")
    print(f"  {'─' * 10}  {'─' * 10}  {'─' * 14}  {'─' * 35}")

    meanings = {
        frozenset(): "no engagement (constant)",
        frozenset([0]): "pure data manipulation",
        frozenset([1]): "pure compute (operation, no obj)",
        frozenset([2]): "pure state (temporal, no content)",
        frozenset([0, 1]): "data manipulation by operation",
        frozenset([0, 2]): "data evolving over time",
        frozenset([1, 2]): "operations sequenced in time",
        frozenset([0, 1, 2]): "★ FULLY TRIADIC (data × compute × state) ★",
    }

    for size in range(4):
        for subset in [s for s in [frozenset(c)
                                    for c in [(), (0,), (1,), (2,),
                                              (0,1), (0,2), (1,2), (0,1,2)]]
                       if len(s) == size]:
            label = monomial_label(subset)
            tt = monomial_truth_table(subset)
            tt_str = "".join(str(b) for b in tt)
            meaning = meanings[subset]
            print(f"  {str(set(subset) if subset else '{}'):<10}  {label:<10}  {tt_str:<14}  {meaning}")

    print(f"\n  Only ONE monomial (xyz = S) realizes the full triadic structure.")
    print(f"  All others engage at most 2 of the 3 aspects.")
    print(f"\n  Generic pattern:")
    print(f"    - 1 monomial of degree 0 (no axes)")
    print(f"    - 3 monomials of degree 1 (one axis each)")
    print(f"    - 3 monomials of degree 2 (pairs of axes)")
    print(f"    - 1 monomial of degree 3 (all axes) ← S")


# ============================================================
# Connection to skill axes and chart structure
# ============================================================

def skill_axis_mapping():
    print("\n" + "=" * 72)
    print("  Connection: skill's 3 axes ↔ computation's 3 aspects")
    print("=" * 72)
    print(f"""
  The shadow-engineer skill operates on 3 axes:
    e_1 = goal/shadows axis (decompose-by-entailment direction)
    e_2 = shadows/artefact axis (regroup-from-shadows direction)
    e_3 = mediation guard axis (audit / guard event direction)

  The 7 nonzero axis-signatures = 7 nonempty subsets of {{e_1, e_2, e_3}}.

  Under the triadic decomposition of computation (data/compute/state),
  these correspond to:

    e_1 (decomposition direction)  ↔  COMPUTE  (operations)
    e_2 (regroup direction)        ↔  DATA     (objects)
    e_3 (mediation guard)          ↔  STATE    (temporal)

  Reading the 7 axis-signatures as combinator domains:

    100 (decompose only)         ↔  pure compute    (x_compute)
    010 (regroup only)           ↔  pure data       (x_data)
    001 (guard only)             ↔  pure state      (x_state)
    110 (decompose + regroup)    ↔  compute + data
    101 (decompose + guard)      ↔  compute + state
    011 (regroup + guard)        ↔  data + state
    111 (triadic-full = M11)     ↔  ALL THREE = S

  M11 (triadic-full move) and S (top-degree monomial) sit at the
  SAME position because they BOTH realize the full triadic structure.

  At the META level: M11 makes the chart describe itself (all 3 axes
  engaged in one move).

  At the OBJECT level: S = xyz uses all 3 polynomial variables (all 3
  aspects of computation in one combinator).

  These aren't analogies — they're the SAME triadic structure observed
  at different scales of the meta-circular tower (M11's collapse).
""")


# ============================================================
# The quotient algebra: each from the other two
# ============================================================

def quotient_algebra():
    print("─" * 72)
    print("  The quotient algebra: each aspect from the other two")
    print("─" * 72)
    print(f"""
  The triadic relations:
    temporal = objects × morphism      (state arises from data + compute)
    morphism = temporal / objects      (compute is state-evolution / data-stability)
    objects  = morphism / temporal     (data is operation-result / time-snapshot)

  In our chart's polynomial ring F_2[x, y, z]/(x_i² - x_i):

    z (state)   = x (data) · y (compute)        in degree-2 part
    y (compute) = z (state) / x (data)          via division-by-projection
    x (data)    = y (compute) / z (state)       via division-by-projection

  The "quotient" in F_2 algebra: for variables x, y, z with x² = x,
  we have x · (1/x) = 1 only for x = 1. So strict algebraic quotients
  fail. But the STRUCTURAL relationships hold:

    - Engaging two aspects implicitly engages the third (in the cubic
      closure via xyz).
    - Removing one aspect collapses the system to a strictly smaller
      subalgebra.

  The three aspects are interlocked: any two GENERATE the third
  through the algebra's closure.

  Sub-algebras by aspect-omission:
    - Omit STATE (z = 0):    F_2[x, y]/(x² - x, y² - y)  → 4 elements (xy quadratic)
    - Omit COMPUTE (y = 0):  F_2[x, z]/(x² - x, z² - z)  → 4 elements (xz quadratic)
    - Omit DATA (x = 0):     F_2[y, z]/(y² - y, z² - z)  → 4 elements (yz quadratic)
    - Omit ALL: F_2  → 2 elements (constants 0, 1)

  The FULL triadic algebra has 8 elements (= 2³). S = xyz is its top.

  Without S, the chart can only express 2-of-3 aspect combinations.
  With S, the chart engages ALL 3 simultaneously.
""")


# ============================================================
# The category-theoretic reading
# ============================================================

def categorical_reading():
    print("─" * 72)
    print("  Categorical reading: a category is a triadic structure")
    print("─" * 72)
    print(f"""
  A category C is determined by:
    - Ob(C):     the objects (a class)
    - Hom(C):    the morphisms (between pairs of objects)
    - ∘:         composition (the temporal structure of morphism sequences)

  These three components form a triadic structure:

    For objects A, B, C and morphisms f: A→B, g: B→C:
      f ∘ g: A→C  (the composite)

    Composition is the TEMPORAL: it sequences morphisms in time.
    Morphisms are the COMPUTE: they transform objects.
    Objects are the DATA: stable identity under (id) morphisms.

  The quotient relations express category-theoretic invariants:

    - Identities  (objects):  id_A: A→A, preserved across all compositions
                              → objects = invariants under temporal flow
    - Composition (temporal): the structure that makes morphisms iterable
                              → temporal = objects × morphism iterations
    - Hom-sets    (morphism): the arrows between fixed objects
                              → morphism = temporal sequences mod object identity

  Our chart is a category in this sense:
    - Objects = cells (chart-cell indices, hash-consed structures)
    - Morphisms = apply / interp / cons operations
    - Composition = sequences of reductions

  Each can be derived from the other two via the chart's operations.
  S is the unique combinator that engages all three simultaneously in
  its reduction: S x y z = ((x z)(y z)) constructs new objects (cons),
  applies them in sequence (apply), and produces a temporally-ordered
  result (the composed term).

  I and K engage at most 2 of the 3:
    - I x = x: returns its arg unchanged (no new compute, no temporal step)
    - K x y = x: drops second arg (no temporal sequencing of both args)

  S is uniquely category-theoretically TRIADIC.
""")


def main():
    enumerate_triadic_monomials()
    skill_axis_mapping()
    quotient_algebra()
    categorical_reading()


if __name__ == "__main__":
    main()
