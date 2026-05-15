"""
search_table2.py — Beam search over candidate table₂ rule sets.

The question: what is the minimal set of chart rules that, under interp,
reproduces apply's behavior on the I/K/S combinator semantics?

Approach: enumerate candidate rule sets at increasing complexity (number
of rules, pattern depth, variable count). For each, run interp on a test
corpus and check equivalence with apply. Beam search keeps top-N candidates
at each complexity tier.

Constraints (per M12-M14):
- Only existing primitives (cons, left, right, eq, apply, interp).
- Variables via VAR_MARK structure.
- No new Python-level primitives.
"""

from chart import Chart
from itertools import product
import time


def make_test_corpus(c):
    """Test terms covering I, K, S reductions plus atoms and nested."""
    return [
        # Atoms (should be normal forms)
        c.NIL, c.TRUE, c.FALSE, c.S, c.K, c.I,
        # Single-step I redex
        c.cons(c.I, c.TRUE),
        c.cons(c.I, c.FALSE),
        # Single-step K redex
        c.cons(c.cons(c.K, c.TRUE), c.FALSE),
        c.cons(c.cons(c.K, c.S), c.K),
        # Single-step S redex
        c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE),
        c.cons(c.cons(c.cons(c.S, c.I), c.K), c.TRUE),
        # Partial applications (normal forms)
        c.cons(c.S, c.K),
        c.cons(c.K, c.I),
        # Nested (CBNeed: outer reduces first)
        c.cons(c.cons(c.K, c.TRUE), c.cons(c.I, c.FALSE)),
    ]


def fitness(c, table, corpus):
    """How many corpus terms does interp(table, ·) reduce identically to apply?"""
    matches = 0
    for k in corpus:
        try:
            a = c.apply(k)
            i = c.interp(table, k)
            if a == i:
                matches += 1
        except Exception:
            pass
    return matches


def build_table(c, rules):
    """Convert list of (pattern, replacement) pairs to a chart cons-list."""
    table = c.NIL
    for pat, repl in reversed(rules):
        rule = c.cons(pat, repl)
        table = c.cons(rule, table)
    return table


def enumerate_single_rules(c):
    """Generate candidate single-rule sets (rule_count = 1).

    Each rule is (pattern, replacement). Vary:
    - Head combinator: I, K, S
    - Variable structure in pattern
    - Replacement structure
    """
    v1, v2, v3 = c.VAR1, c.VAR2, c.VAR3
    candidates = []

    # I-like rules: pattern (I ?v), replacement ?v or ?something
    for v in [v1, v2, v3]:
        pat = c.cons(c.I, v)
        candidates.append(("I-rule", [(pat, v)]))

    # K-like rules: pattern ((K ?v1) ?v2), replacement ?v1
    for vx, vy in [(v1, v2), (v2, v1), (v1, v3)]:
        pat = c.cons(c.cons(c.K, vx), vy)
        candidates.append((f"K-rule({c.show(vx)},{c.show(vy)})", [(pat, vx)]))

    # S-like rules: pattern (((S ?v1) ?v2) ?v3), replacement ((v1 v3) (v2 v3))
    vx, vy, vz = v1, v2, v3
    pat = c.cons(c.cons(c.cons(c.S, vx), vy), vz)
    repl = c.cons(c.cons(vx, vz), c.cons(vy, vz))
    candidates.append(("S-rule", [(pat, repl)]))

    return candidates


def enumerate_pairs(c, single_candidates):
    """Pairs of rules: every combination of two single-rule candidates."""
    pairs = []
    for i, (n1, rs1) in enumerate(single_candidates):
        for j, (n2, rs2) in enumerate(single_candidates):
            if i >= j:  # avoid duplicates; order matters for interp
                continue
            pairs.append((f"{n1} + {n2}", rs1 + rs2))
    return pairs


def enumerate_triples_canonical(c, single_candidates):
    """Triples favoring canonical combinator orderings (I, K, S)."""
    # Pick canonical I, K, S rule candidates
    i_rule = next((n, rs) for n, rs in single_candidates if n == "I-rule")
    k_rules = [(n, rs) for n, rs in single_candidates if n.startswith("K-rule")]
    s_rule = next((n, rs) for n, rs in single_candidates if n == "S-rule")

    triples = []
    for kn, kr in k_rules:
        for order_perm in [(i_rule, (kn, kr), s_rule),
                           (s_rule, (kn, kr), i_rule),
                           ((kn, kr), i_rule, s_rule)]:
            name = " + ".join(r[0] for r in order_perm)
            rules = []
            for r in order_perm:
                rules.extend(r[1])
            triples.append((name, rules))
    return triples


def search(c, corpus):
    """Beam search: try single rules, pairs, triples; report best at each tier."""
    print("=" * 72)
    print("  Beam search over table₂ candidate rule sets")
    print("=" * 72)
    print(f"\n  Test corpus: {len(corpus)} terms")
    print(f"  Fitness: number of terms where interp(table, k) == apply(k)")
    print()

    # Tier 1: single rules
    print("─" * 72)
    print(" Tier 1: single-rule candidates")
    print("─" * 72)
    singles = enumerate_single_rules(c)
    single_scored = []
    for name, rules in singles:
        table = build_table(c, rules)
        score = fitness(c, table, corpus)
        single_scored.append((score, name, rules, table))
        print(f"  fitness {score:2d}/{len(corpus)}  {name}")

    single_scored.sort(key=lambda x: -x[0])
    best_single = single_scored[0]
    print(f"\n  Best single rule: {best_single[1]} (fitness {best_single[0]}/{len(corpus)})")

    # Tier 2: pairs
    print("\n" + "─" * 72)
    print(" Tier 2: pair candidates")
    print("─" * 72)
    pairs = enumerate_pairs(c, singles)
    pair_scored = []
    for name, rules in pairs:
        table = build_table(c, rules)
        score = fitness(c, table, corpus)
        pair_scored.append((score, name, rules, table))

    pair_scored.sort(key=lambda x: -x[0])
    top_pairs = pair_scored[:5]
    print(f"  Top 5 pair candidates:")
    for score, name, rules, _ in top_pairs:
        print(f"    fitness {score:2d}/{len(corpus)}  {name}")

    # Tier 3: triples (canonical)
    print("\n" + "─" * 72)
    print(" Tier 3: canonical triple candidates (I + K + S)")
    print("─" * 72)
    triples = enumerate_triples_canonical(c, singles)
    triple_scored = []
    for name, rules in triples:
        table = build_table(c, rules)
        score = fitness(c, table, corpus)
        triple_scored.append((score, name, rules, table))

    triple_scored.sort(key=lambda x: -x[0])
    top_triples = triple_scored[:5]
    print(f"  Top 5 triple candidates:")
    for score, name, rules, _ in top_triples:
        print(f"    fitness {score:2d}/{len(corpus)}  {name}")

    # Report best overall
    best = max([best_single] + top_pairs[:1] + top_triples[:1], key=lambda x: x[0])
    print("\n" + "=" * 72)
    print(f"  Best fitness: {best[0]}/{len(corpus)}  ({best[1]})")
    print(f"  Rule count: {len(best[2])}")
    print(f"  table = {c.show(best[3])}")

    # Detailed diagnostic on the best table
    print(f"\n  Per-term diagnostic for best table:")
    for k in corpus:
        a = c.apply(k)
        i = c.interp(best[3], k)
        mark = "✓" if a == i else "✗"
        print(f"    {mark} {c.show(k):28s} apply→{c.show(a):20s} interp→{c.show(i)}")
    print("=" * 72)

    return best


def find_minimal_complete(c, corpus):
    """Find the minimal rule count that achieves perfect fitness."""
    print("\n" + "=" * 72)
    print("  Finding minimal complete table (fitness = corpus size)")
    print("=" * 72)

    singles = enumerate_single_rules(c)

    # Try size-1 first
    for name, rules in singles:
        table = build_table(c, rules)
        if fitness(c, table, corpus) == len(corpus):
            print(f"\n  Size 1 sufficient: {name}")
            return ("size 1", rules)

    # Size-2
    for name, rules in enumerate_pairs(c, singles):
        table = build_table(c, rules)
        if fitness(c, table, corpus) == len(corpus):
            print(f"\n  Size 2 sufficient: {name}")
            return ("size 2", rules)

    # Size-3
    for name, rules in enumerate_triples_canonical(c, singles):
        table = build_table(c, rules)
        if fitness(c, table, corpus) == len(corpus):
            print(f"\n  Size 3 sufficient: {name}")
            print(f"  This is the canonical default_table structure.")
            return ("size 3", rules)

    print("\n  No table of size ≤ 3 achieves perfect fitness on this corpus.")
    print("  The corpus may include reductions requiring deeper tables, or")
    print("  the search space is too restricted.")
    return None


if __name__ == "__main__":
    c = Chart()
    corpus = make_test_corpus(c)
    best = search(c, corpus)
    minimal = find_minimal_complete(c, corpus)
