"""
search_k_variants.py — Exhaustive K-rule variable-assignment grid search.

Investigates the structure of the K-rule's variable choices. The K-rule
pattern is `((K ?a) ?b) → ?a` where ?a and ?b are pattern variables. The
question: how do different choices of variables for the two slots affect
fitness, and why?

For an n-variable basis V = {v1, ..., vn}, the search space of variable
assignments is V × V (an n×n grid). We test each (vx, vy) ∈ V × V as the
K-rule's slots and measure fitness against a corpus.

Findings:
- The grid partitions into two gauge orbits under S_n (variable renaming):
  diagonal (vx = vy) and off-diagonal (vx ≠ vy).
- Off-diagonal entries are gauge-equivalent: any pair of distinct
  variables produces the same fitness.
- Diagonal entries are strictly worse: forcing the same variable on both
  slots restricts the K-rule to matching only terms (K a b) where a == b.
"""

from chart import Chart


def make_corpus(c):
    return [
        c.NIL, c.TRUE, c.FALSE, c.S, c.K, c.I,
        c.cons(c.I, c.TRUE),
        c.cons(c.I, c.FALSE),
        c.cons(c.cons(c.K, c.TRUE), c.FALSE),  # K-redex with distinct args
        c.cons(c.cons(c.K, c.S), c.K),         # K-redex with distinct args
        c.cons(c.cons(c.K, c.TRUE), c.TRUE),   # K-redex with EQUAL args (diagonal hits this)
        c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE),
        c.cons(c.S, c.K),
        c.cons(c.K, c.I),
        c.cons(c.cons(c.K, c.TRUE), c.cons(c.I, c.FALSE)),
    ]


def build_table(c, rules):
    table = c.NIL
    for pat, repl in reversed(rules):
        table = c.cons(c.cons(pat, repl), table)
    return table


def fitness(c, table, corpus):
    matches = 0
    for k in corpus:
        a = c.apply(k)
        i = c.interp(table, k)
        if a == i:
            matches += 1
    return matches


def make_K_only_table(c, vx, vy):
    """K-rule alone with given variable assignment."""
    pat = c.cons(c.cons(c.K, vx), vy)
    return build_table(c, [(pat, vx)])


def make_IKS_table(c, vx_k, vy_k):
    """Full I + K + S table, varying only the K-rule's variable assignment.

    I and S rules use canonical variable choices; K-rule slots are (vx_k, vy_k).
    """
    v1, v2, v3 = c.VAR1, c.VAR2, c.VAR3
    # I rule
    i_pat = c.cons(c.I, v1)
    i_rule = (i_pat, v1)
    # K rule with parameterized variables
    k_pat = c.cons(c.cons(c.K, vx_k), vy_k)
    # Replacement: vx_k (the kept slot)
    k_rule = (k_pat, vx_k)
    # S rule
    s_pat = c.cons(c.cons(c.cons(c.S, v1), v2), v3)
    s_repl = c.cons(c.cons(v1, v3), c.cons(v2, v3))
    s_rule = (s_pat, s_repl)
    return build_table(c, [i_rule, k_rule, s_rule])


def label(c, v):
    return c.show(v).replace("?", "")


def k_grid_search(c, corpus, basis):
    """Test every (vx, vy) ∈ basis × basis as K-rule slots; report fitness."""
    print("=" * 72)
    print(f"  K-rule variable-grid search over basis {[label(c, v) for v in basis]}")
    print("=" * 72)
    n = len(basis)

    # K-rule alone (single-rule test)
    print(f"\n  Single-rule K test (other rules absent):")
    print(f"  {'':>10}", end="")
    for vy in basis:
        print(f"  vy={label(c, vy):>6}", end="")
    print()
    grid_single = {}
    for vx in basis:
        print(f"  vx={label(c, vx):>6}  ", end="")
        for vy in basis:
            table = make_K_only_table(c, vx, vy)
            f = fitness(c, table, corpus)
            grid_single[(vx, vy)] = f
            mark = "★" if vx == vy else " "
            print(f"  {f:>2}/{len(corpus)}{mark}", end="")
        print()

    # K-rule embedded in full I+K+S
    print(f"\n  Triple-rule test (I + K(vx,vy) + S):")
    print(f"  {'':>10}", end="")
    for vy in basis:
        print(f"  vy={label(c, vy):>6}", end="")
    print()
    grid_triple = {}
    for vx in basis:
        print(f"  vx={label(c, vx):>6}  ", end="")
        for vy in basis:
            table = make_IKS_table(c, vx, vy)
            f = fitness(c, table, corpus)
            grid_triple[(vx, vy)] = f
            mark = "★" if vx == vy else " "
            print(f"  {f:>2}/{len(corpus)}{mark}", end="")
        print()

    print(f"\n  ★ = diagonal entry (vx = vy)")

    # Gauge analysis
    print("\n" + "─" * 72)
    print("  Gauge orbit analysis")
    print("─" * 72)
    diag = [grid_triple[(v, v)] for v in basis]
    off = [grid_triple[(vx, vy)] for vx in basis for vy in basis if vx != vy]
    print(f"  Diagonal entries (vx = vy):     fitnesses = {diag}")
    print(f"  Off-diagonal entries (vx ≠ vy): fitnesses = {off}")
    print(f"  Diagonal orbit uniform: {len(set(diag)) == 1}")
    print(f"  Off-diagonal orbit uniform: {len(set(off)) == 1}")

    return grid_single, grid_triple


def explain_diagonal(c, corpus):
    """Show WHY diagonal K-rule fails: it matches ((K a) b) only when a == b."""
    print("\n" + "=" * 72)
    print("  Structural explanation: why diagonal K-rules are restrictive")
    print("=" * 72)
    v1 = c.VAR1
    diag_pat = c.cons(c.cons(c.K, v1), v1)
    print(f"\n  Diagonal K-pattern: {c.show(diag_pat)} = ((K ?n) ?n)")
    print(f"  This matches ((K a) b) ONLY when a structurally equals b.")
    print()

    test_K_terms = [
        c.cons(c.cons(c.K, c.TRUE), c.FALSE),
        c.cons(c.cons(c.K, c.S), c.K),
        c.cons(c.cons(c.K, c.TRUE), c.TRUE),   # equal args
        c.cons(c.cons(c.K, c.FALSE), c.FALSE), # equal args
    ]
    for k in test_K_terms:
        binding = c._match(diag_pat, k, {})
        result = "match" if binding is not None else "FAIL"
        print(f"  {c.show(k):28s} → {result}")

    print(f"\n  In the corpus of {len(corpus)} terms, K-redexes appear with both")
    print(f"  equal and distinct arguments. The off-diagonal pattern handles all;")
    print(f"  the diagonal pattern handles only the (K a a) sub-case.")


def cohomological_reading(c, corpus, basis):
    """Frame the result in M8 cohomological terms."""
    print("\n" + "=" * 72)
    print("  Cohomological reading (M8: cocycle invariance)")
    print("=" * 72)
    print()
    print("  The variable-assignment grid V × V partitions into orbits under")
    print("  the action of S_n (permuting variable names). For the K-rule:")
    print()
    print("  - Off-diagonal orbit {(vx, vy) : vx ≠ vy} is one gauge class.")
    print("    All n(n-1) entries are operationally equivalent — the choice")
    print("    of which variable goes where is gauge, not semantics.")
    print()
    print("  - Diagonal orbit {(v, v)} is a different gauge class.")
    print("    All n entries are operationally equivalent to each other,")
    print("    but structurally distinct from off-diagonal (different pattern).")
    print()
    print("  The two orbits are NOT gauge-equivalent because they have")
    print("  different structural shape: off-diagonal patterns have two")
    print("  free pattern positions; diagonal patterns have one (with a")
    print("  consistency constraint).")
    print()
    print("  This is a real cohomological distinction: a 0-cocycle (gauge")
    print("  orbit) versus a different 0-cocycle, observable empirically as")
    print("  uniformly-different fitness within each orbit.")


def main():
    c = Chart()
    corpus = make_corpus(c)
    print(f"Test corpus: {len(corpus)} terms")

    # 2-variable basis
    print("\n" + "█" * 72)
    print("  Phase 1: 2-variable basis (2×2 grid)")
    print("█" * 72)
    basis2 = [c.VAR1, c.VAR2]
    k_grid_search(c, corpus, basis2)

    # 3-variable basis
    print("\n" + "█" * 72)
    print("  Phase 2: 3-variable basis (3×3 grid)")
    print("█" * 72)
    basis3 = [c.VAR1, c.VAR2, c.VAR3]
    k_grid_search(c, corpus, basis3)

    # Structural explanation
    explain_diagonal(c, corpus)
    cohomological_reading(c, corpus, basis2)


if __name__ == "__main__":
    main()
