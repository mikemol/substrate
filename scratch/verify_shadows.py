"""
verify_shadows.py — Regroup pass (M10, axis 010).

Reconstructs the shadow specifications S1–S7 and the cross-cutting M-move
invariants from the artefact chart.py via behavior preservation. Each
claim recorded in the cotype becomes a test that exercises the artefact
and verifies the invariant operationally.

With M1–M8 at 100 and M9 at 110, this populates 010 — completing L₁
(positive-closure: {100, 010, 110} all populated). The test suite IS
the regroup: shadows extracted from artefact behavior, audited against
the cotype's prior claims.
"""

import sys
import time
from chart import Chart


# Test registry
TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


# ============================================================
# S1 — nil
# ============================================================

@test
def S1_nil_is_designated_at_index_0():
    c = Chart()
    assert c.NIL == 0


@test
def S1_nil_has_no_proper_structure():
    c = Chart()
    assert c._cells[0] is None  # No (l, q) stored at index 0


# ============================================================
# S2 — cons (hash-consing binary constructor)
# ============================================================

@test
def S2_cons_is_hashconsed():
    c = Chart()
    a = c.cons(c.TRUE, c.FALSE)
    b = c.cons(c.TRUE, c.FALSE)
    assert a == b
    d = c.cons(c.FALSE, c.TRUE)
    assert d != a  # Distinct pairs → distinct indices


@test
def S2_cons_is_acyclic():
    c = Chart()
    for _ in range(20):
        c.cons(c.TRUE, c.FALSE)
        c.cons(c.S, c.K)
        c.cons(c.cons(c.I, c.TRUE), c.FALSE)
    for k in range(1, c.size()):
        l, q = c._cells[k]
        assert l < k, f"rule {k}: left child {l} not < {k}"
        assert q < k, f"rule {k}: right child {q} not < {k}"


@test
def S2_cons_is_monotonic():
    c = Chart()
    n0 = c.size()
    c.cons(c.TRUE, c.FALSE)
    assert c.size() == n0 + 1
    c.cons(c.TRUE, c.FALSE)  # Hash-cons hit
    assert c.size() == n0 + 1
    c.cons(c.FALSE, c.TRUE)
    assert c.size() == n0 + 2


# ============================================================
# S3 — left, right (projections)
# ============================================================

@test
def S3_projections_recover_children():
    c = Chart()
    k = c.cons(c.TRUE, c.FALSE)
    assert c.left(k) == c.TRUE
    assert c.right(k) == c.FALSE


@test
def S3_projections_invert_cons():
    c = Chart()
    for l in [c.NIL, c.TRUE, c.FALSE, c.S]:
        for q in [c.NIL, c.TRUE, c.K, c.I]:
            k = c.cons(l, q)
            assert c.left(k) == l
            assert c.right(k) == q


# ============================================================
# S4 — eq (reference equality)
# ============================================================

@test
def S4_eq_reflects_hashcons():
    c = Chart()
    a = c.cons(c.TRUE, c.FALSE)
    b = c.cons(c.TRUE, c.FALSE)
    assert c.eq(a, b)
    assert not c.eq(a, c.NIL)


@test
def S4_eq_is_equivalence_relation():
    c = Chart()
    rules = [c.NIL, c.TRUE, c.FALSE, c.S, c.K, c.I,
             c.cons(c.TRUE, c.FALSE)]
    # Reflexivity
    for k in rules:
        assert c.eq(k, k)
    # Symmetry
    for a in rules:
        for b in rules:
            assert c.eq(a, b) == c.eq(b, a)
    # Transitivity (trivially true for integer equality)
    a = c.cons(c.TRUE, c.FALSE)
    b = c.cons(c.TRUE, c.FALSE)
    d = c.cons(c.TRUE, c.FALSE)
    assert c.eq(a, b) and c.eq(b, d) and c.eq(a, d)


# ============================================================
# S5 — apply (single-step under CBNeed)
# ============================================================

@test
def S5_apply_on_atoms_is_identity():
    c = Chart()
    for k in [c.NIL, c.TRUE, c.FALSE, c.FAILURE, c.S, c.K, c.I]:
        assert c.apply(k) == k


@test
def S5_apply_reduces_I_redex():
    c = Chart()
    Ix = c.cons(c.I, c.TRUE)
    assert c.apply(Ix) == c.TRUE


@test
def S5_apply_reduces_K_redex():
    c = Chart()
    Kxy = c.cons(c.cons(c.K, c.TRUE), c.FALSE)
    assert c.apply(Kxy) == c.TRUE


@test
def S5_apply_reduces_S_redex():
    c = Chart()
    SKKx = c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE)
    one_step = c.apply(SKKx)
    expected = c.cons(c.cons(c.K, c.FALSE), c.cons(c.K, c.FALSE))
    assert one_step == expected


@test
def S5_apply_partial_application_is_normal_form():
    c = Chart()
    # S with 1 arg (needs 3): normal form
    assert c.apply(c.cons(c.S, c.K)) == c.cons(c.S, c.K)
    # K with 1 arg (needs 2): normal form
    assert c.apply(c.cons(c.K, c.TRUE)) == c.cons(c.K, c.TRUE)


@test
def S5_apply_is_cbneed_outer_first():
    """M3 C3: outer redex reduces before inner subterms."""
    c = Chart()
    # K true (I false): K-redex outer, I-redex inner.
    # Outer-first reduces K, discarding the I-redex unevaluated.
    Iy = c.cons(c.I, c.FALSE)
    KxIy = c.cons(c.cons(c.K, c.TRUE), Iy)
    assert c.apply(KxIy) == c.TRUE


# ============================================================
# S6 — parse
# ============================================================

@test
def S6_parse_handles_atoms():
    c = Chart()
    assert c.parse(c.NIL, "true") == c.TRUE
    assert c.parse(c.NIL, "K") == c.K
    assert c.parse(c.NIL, "nil") == c.NIL


@test
def S6_parse_is_left_associative():
    c = Chart()
    # "S K K" parses as ((S K) K)
    parsed = c.parse(c.NIL, "S K K")
    expected = c.cons(c.cons(c.S, c.K), c.K)
    assert parsed == expected


@test
def S6_parse_handles_parentheses():
    c = Chart()
    # "S (K K)" parses as (S (K K))
    parsed = c.parse(c.NIL, "S (K K)")
    expected = c.cons(c.S, c.cons(c.K, c.K))
    assert parsed == expected


@test
def S6_parse_hashcons_consistent():
    c = Chart()
    a = c.parse(c.NIL, "S K K true")
    b = c.parse(c.NIL, "S K K true")
    assert a == b


@test
def S6_parse_normalizes_correctly():
    c = Chart()
    assert c.normalize(c.parse(c.NIL, "I true")) == c.TRUE
    assert c.normalize(c.parse(c.NIL, "K true false")) == c.TRUE
    assert c.normalize(c.parse(c.NIL, "S K K true")) == c.TRUE


# ============================================================
# S7 — transform (representation rotation)
# ============================================================

@test
def S7_transform_identity():
    c = Chart()
    assert c.transform(c.TRUE, "integer", "integer") == c.TRUE


@test
def S7_transform_integer_trace_roundtrip():
    c = Chart()
    expr = c.parse(c.NIL, "S (K I) (K K)")
    trace = c.transform(expr, "integer", "trace")
    back = c.transform(trace, "trace", "integer")
    assert c.eq(expr, back)


@test
def S7_transform_integer_function_roundtrip():
    c = Chart()
    expr = c.parse(c.NIL, "S (K I) (K K)")
    fn = c.transform(expr, "integer", "function")
    back = c.transform(fn, "function", "integer")
    assert c.eq(expr, back)


# ============================================================
# M3 — constraint resolution invariants
# ============================================================

@test
def M3_C1_left_right_of_nil_defined():
    c = Chart()
    assert c.left(c.NIL) == c.NIL
    assert c.right(c.NIL) == c.NIL


@test
def M3_C2_designated_indices_correct():
    c = Chart()
    assert c.NIL == 0
    assert c.TRUE == 1
    assert c.FALSE == 2
    assert c.FAILURE == 3


@test
def M3_C2_designated_rules_all_distinct():
    c = Chart()
    designated = {c.NIL, c.TRUE, c.FALSE, c.FAILURE, c.S, c.K, c.I}
    assert len(designated) == 7


@test
def M3_C5_failure_is_value_not_exception():
    """Failure composes through eq; no exception machinery needed."""
    c = Chart()
    result = c.parse(c.NIL, "totally malformed )))")
    assert result == c.FAILURE
    assert c.eq(result, c.FAILURE)
    # Failure passes through further operations without raising
    k = c.cons(result, c.TRUE)  # cons(FAILURE, TRUE) is well-defined
    assert c.left(k) == c.FAILURE


# ============================================================
# M4 — single-step apply, termination
# ============================================================

@test
def M4_apply_always_terminates_quickly():
    c = Chart()
    exprs = [
        c.NIL, c.TRUE, c.S,
        c.cons(c.S, c.K),
        c.parse(c.NIL, "S K K true"),
        c.parse(c.NIL, "S (S K K) (S K K) true"),
    ]
    for e in exprs:
        start = time.perf_counter()
        c.apply(e)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.1, f"apply on {c.show(e)} took {elapsed:.3f}s"


@test
def M4_normalize_is_derived_from_apply():
    """Normalize is iterated apply; not a founding micro-op."""
    c = Chart()
    expr = c.parse(c.NIL, "S K K true")
    # Manual iteration matches the built-in
    k = expr
    for _ in range(100):
        k_next = c.apply(k)
        if k_next == k:
            break
        k = k_next
    assert k == c.TRUE
    assert c.normalize(expr) == c.TRUE


# ============================================================
# M5 — chart as memoization substrate
# ============================================================

@test
def M5_apply_memoizes():
    c = Chart()
    expr = c.parse(c.NIL, "S K K (S K K true)")
    c.normalize(expr)
    n1 = len(c._apply_memo)
    c.normalize(expr)
    n2 = len(c._apply_memo)
    assert n1 == n2, "second normalize added memo entries; memoization broken"


@test
def M5_hashconsing_is_structural_memoization():
    """Distinct construction paths to the same structure share storage."""
    c = Chart()
    # Build cons(cons(T,F), cons(T,F)) two ways
    x = c.cons(c.cons(c.TRUE, c.FALSE), c.cons(c.TRUE, c.FALSE))
    inner = c.cons(c.TRUE, c.FALSE)
    y = c.cons(inner, inner)
    assert x == y


# ============================================================
# M8 — cohomological / cocycle invariants
# ============================================================

@test
def M8_K_reduction_invariant_across_rotations():
    """The K-reduction property holds at every representation vertex."""
    c = Chart()
    expr = c.parse(c.NIL, "K true false")

    int_result = c.normalize(expr)
    trace = c.transform(expr, "integer", "trace")
    trace_result = c.normalize(c.transform(trace, "trace", "integer"))
    fn = c.transform(expr, "integer", "function")
    fn_result = c.normalize(c.transform(fn, "function", "integer"))

    assert int_result == trace_result == fn_result == c.TRUE


@test
def M8_structural_equality_invariant_across_rotations():
    c = Chart()
    a = c.parse(c.NIL, "S K K true")
    b = c.parse(c.NIL, "S K K true")
    assert c.eq(a, b)
    a_via_trace = c.transform(c.transform(a, "integer", "trace"), "trace", "integer")
    b_via_trace = c.transform(c.transform(b, "integer", "trace"), "trace", "integer")
    assert c.eq(a_via_trace, b_via_trace)


@test
def M8_normalize_invariant_across_rotations():
    c = Chart()
    # I (K true false) should normalize to true regardless of rotation
    expr = c.parse(c.NIL, "I (K true false)")
    expected = c.normalize(expr)

    fn = c.transform(expr, "integer", "function")
    back = c.transform(fn, "function", "integer")
    assert c.normalize(back) == expected


# ============================================================
# Realizability charter (per user preferences)
# ============================================================

@test
def charter_constructible_every_op_returns_witness():
    c = Chart()
    assert isinstance(c.cons(c.TRUE, c.FALSE), int)
    k = c.cons(c.TRUE, c.FALSE)
    assert isinstance(c.left(k), int)
    assert isinstance(c.right(k), int)
    assert isinstance(c.eq(c.TRUE, c.FALSE), bool)
    assert isinstance(c.apply(c.cons(c.I, c.TRUE)), int)
    assert isinstance(c.parse(c.NIL, "true"), int)


@test
def charter_reachable_every_rule_has_construction():
    c = Chart()
    for _ in range(5):
        c.parse(c.NIL, "S K K true")
        c.cons(c.parse(c.NIL, "K true"), c.NIL)
    for k in range(1, c.size()):
        l, q = c._cells[k]
        assert c.cons(l, q) == k  # cons(l,q) deterministically rebuilds k


@test
def charter_observable_outcomes_detectable():
    c = Chart()
    e = c.cons(c.I, c.TRUE)
    result = c.apply(e)
    # Outcome is detectable: eq distinguishes it from any other rule
    assert c.eq(result, c.TRUE)
    assert not c.eq(result, c.FALSE)


@test
def charter_coverable_chart_is_finite_and_enumerable():
    c = Chart()
    for _ in range(10):
        c.parse(c.NIL, "S K K true")
    n = c.size()
    # Every index from 0 to n-1 is valid and addressable
    for k in range(n):
        c.left(k)
        c.right(k)


# ============================================================
# M11 — operational meta-circularity (T1–T8)
# ============================================================

@test
def M11_T1_rules_are_chart_data():
    """T1: reduction rules are cons(pattern, replacement) — chart rules."""
    c = Chart()
    table = c.default_table
    # Walk the table; each entry must be a cons cell with a pattern and replacement.
    while not c.eq(table, c.NIL):
        rule = c.left(table)
        assert rule not in c._atoms, "rule should be a cons cell, not an atom"
        # rule = cons(pattern, replacement); both are chart rules (ints)
        pattern, replacement = c.left(rule), c.right(rule)
        assert isinstance(pattern, int) and isinstance(replacement, int)
        table = c.right(table)


@test
def M11_T2_variables_are_structural():
    """T2 (refactored M14): variables are structural cons(VAR_MARK, NAME) cells,
    NOT designated atoms. Discrimination via is_var (left == VAR_MARK)."""
    c = Chart()
    # Variables are NOT in _atoms (they're cons cells under apply):
    assert c.VAR1 not in c._atoms
    assert c.VAR2 not in c._atoms
    assert c.VAR3 not in c._atoms
    # is_var recognizes them structurally:
    assert c.is_var(c.VAR1)
    assert c.is_var(c.VAR2)
    assert c.is_var(c.VAR3)
    # Distinct (different names):
    assert len({c.VAR1, c.VAR2, c.VAR3}) == 3
    # apply still treats them as normal forms (cons(VAR_MARK, _) is opaque):
    assert c.apply(c.VAR1) == c.VAR1
    assert c.apply(c.VAR2) == c.VAR2
    assert c.apply(c.VAR3) == c.VAR3
    # Structural marker check:
    assert c.left(c.VAR1) == c.VAR_MARK
    assert c.left(c.VAR2) == c.VAR_MARK
    assert c.left(c.VAR3) == c.VAR_MARK


@test
def M11_T3_match_binds_variables():
    """T3: pattern matching produces a binding (keyed by name in M14)."""
    c = Chart()
    # Pattern (I VAR1) against term (I true): binding name(VAR1) -> true
    pat = c.cons(c.I, c.VAR1)
    term = c.cons(c.I, c.TRUE)
    binding = c._match(pat, term, {})
    # M14 refactor: binding keys are variable names, not wrappers.
    name = c.right(c.VAR1)
    assert binding == {name: c.TRUE}


@test
def M11_T3_match_enforces_consistency():
    """T3: a variable appearing twice must match the same subterm."""
    c = Chart()
    val = c.cons(c.I, c.TRUE)
    pat = c.cons(c.VAR1, c.VAR1)
    # Consistent: both occurrences see the same value
    term_good = c.cons(val, val)
    name = c.right(c.VAR1)
    assert c._match(pat, term_good, {}) == {name: val}
    # Inconsistent: name would need to bind to two different values
    other = c.cons(c.K, c.TRUE)
    term_bad = c.cons(val, other)
    assert c._match(pat, term_bad, {}) is None


@test
def M11_T3_match_fails_on_atom_mismatch():
    """T3: atom in pattern requires exact term match."""
    c = Chart()
    pat = c.cons(c.I, c.VAR1)
    term = c.cons(c.K, c.TRUE)
    assert c._match(pat, term, {}) is None


@test
def M11_T4_substitute_replaces_variables():
    """T4: substitution walks template, replacing variables (keyed by name)."""
    c = Chart()
    template = c.cons(c.VAR1, c.VAR2)
    n1, n2 = c.right(c.VAR1), c.right(c.VAR2)
    binding = {n1: c.TRUE, n2: c.FALSE}
    expected = c.cons(c.TRUE, c.FALSE)
    assert c._substitute(template, binding) == expected


@test
def M11_T4_substitute_leaves_atoms():
    """T4: non-variable atoms pass through substitution unchanged."""
    c = Chart()
    n1 = c.right(c.VAR1)
    binding = {n1: c.TRUE}
    assert c._substitute(c.I, binding) == c.I
    assert c._substitute(c.NIL, binding) == c.NIL


@test
def M11_T5_interp_reduces_I_redex():
    c = Chart()
    Ix = c.cons(c.I, c.TRUE)
    assert c.interp(c.default_table, Ix) == c.TRUE


@test
def M11_T5_interp_reduces_K_redex():
    c = Chart()
    Kxy = c.cons(c.cons(c.K, c.TRUE), c.FALSE)
    assert c.interp(c.default_table, Kxy) == c.TRUE


@test
def M11_T5_interp_reduces_S_redex():
    c = Chart()
    SKKx = c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE)
    expected = c.cons(c.cons(c.K, c.FALSE), c.cons(c.K, c.FALSE))
    assert c.interp(c.default_table, SKKx) == expected


@test
def M11_T5_interp_normal_form_unchanged():
    c = Chart()
    for k in [c.NIL, c.TRUE, c.S, c.K, c.I, c.cons(c.S, c.K)]:
        assert c.interp(c.default_table, k) == k


@test
def M11_T6_default_table_structure():
    """T6: default_table is a cons-list of three rules."""
    c = Chart()
    table = c.default_table
    rules = []
    while not c.eq(table, c.NIL):
        rules.append(c.left(table))
        table = c.right(table)
    assert len(rules) == 3, f"expected 3 rules, got {len(rules)}"


@test
def M11_T7_interp_equals_apply():
    """T7: the meta-circular fixpoint — interp(default_table, k) = apply(k)."""
    c = Chart()
    test_terms = [
        c.NIL, c.TRUE, c.FALSE, c.FAILURE, c.S, c.K, c.I,
        c.cons(c.I, c.TRUE),
        c.cons(c.cons(c.K, c.TRUE), c.FALSE),
        c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE),
        c.parse(c.NIL, "S K K true"),
        c.parse(c.NIL, "I (I (I true))"),
        c.parse(c.NIL, "K (S K K) false"),
        c.parse(c.NIL, "S (K I) (K K) true"),
        c.parse(c.NIL, "I"),
        c.parse(c.NIL, "S K"),       # Partial S
        c.parse(c.NIL, "K I"),       # Partial K
    ]
    for t in test_terms:
        a, i = c.apply(t), c.interp(c.default_table, t)
        assert a == i, f"on {c.show(t)}: apply={c.show(a)} interp={c.show(i)}"


@test
def M11_T7_full_normalization_equivalence():
    """T7 deeper: iterated interp = iterated apply (normalize)."""
    c = Chart()

    def normalize_via_interp(c, table, k, budget=1000):
        for _ in range(budget):
            k_next = c.interp(table, k)
            if c.eq(k_next, k):
                return k
            k = k_next
        return c.FAILURE

    test_terms = [
        c.parse(c.NIL, "S K K true"),
        c.parse(c.NIL, "I (I (I true))"),
        c.parse(c.NIL, "K (S K K) false"),
        c.parse(c.NIL, "S (K I) (K K) true"),
    ]
    for t in test_terms:
        via_apply = c.normalize(t)
        via_interp = normalize_via_interp(c, c.default_table, t)
        assert via_apply == via_interp, \
            f"normalize differs on {c.show(t)}: apply→{c.show(via_apply)} interp→{c.show(via_interp)}"


@test
def M11_T8_table_extension():
    """T8: extending the table adds new reduction rules; old rules still fire."""
    c = Chart()
    # Add a custom rule: (true VAR1) -> VAR1  (TRUE acts like I)
    new_pat = c.cons(c.TRUE, c.VAR1)
    new_rule = c.cons(new_pat, c.VAR1)
    extended = c.cons(new_rule, c.default_table)

    # New rule fires on (true false)
    test_new = c.cons(c.TRUE, c.FALSE)
    assert c.interp(extended, test_new) == c.FALSE
    # Default table doesn't reduce this
    assert c.interp(c.default_table, test_new) == test_new
    # Old rules still work on extended table
    Ix = c.cons(c.I, c.TRUE)
    assert c.interp(extended, Ix) == c.TRUE


@test
def M11_T8_extension_is_chart_data():
    """T8: extended table is itself a chart rule (a cons-list)."""
    c = Chart()
    new_pat = c.cons(c.TRUE, c.VAR1)
    new_rule = c.cons(new_pat, c.VAR1)
    extended = c.cons(new_rule, c.default_table)
    # Walk the extended table: first rule is new_rule, rest is default_table
    assert c.left(extended) == new_rule
    assert c.right(extended) == c.default_table


# ============================================================
# M14 — audit of K-marker → VAR_MARK refactor (011 regroup)
# ============================================================

@test
def M14_V1_var_helper_creates_marker_cell():
    """V1: var(name) produces cons(VAR_MARK, name) cell."""
    c = Chart()
    v = c.var(c.NIL)
    assert c.left(v) == c.VAR_MARK
    assert c.right(v) == c.NIL
    assert c.is_var(v)


@test
def M14_V2_distinct_names_distinct_variables():
    """V2: distinct names give distinct variables; same name hash-conses."""
    c = Chart()
    v_a = c.var(c.NIL)
    v_b = c.var(c.TRUE)
    assert v_a != v_b
    # Hash-consing: same name → same variable
    v_a2 = c.var(c.NIL)
    assert v_a == v_a2


@test
def M14_V3_VAR1_VAR2_VAR3_reinterpreted():
    """V3: M11's VAR1/VAR2/VAR3 are now structural K-marker cells."""
    c = Chart()
    assert c.VAR1 == c.var(c.NIL)
    assert c.VAR2 == c.var(c.TRUE)
    assert c.VAR3 == c.var(c.FALSE)


@test
def M14_V4_K_combinator_role_preserved():
    """V4: K's combinator role is preserved under apply.

    The M14 refactor uses VAR_MARK (not K) as variable marker specifically
    to avoid collision with K's combinator role. This test verifies the
    collision avoidance: K still reduces (K x y) → x.
    """
    c = Chart()
    Kxy = c.cons(c.cons(c.K, c.TRUE), c.FALSE)
    assert c.apply(Kxy) == c.TRUE
    # Partial K-application is NOT a variable:
    partial_K = c.cons(c.K, c.TRUE)
    assert not c.is_var(partial_K)


@test
def M14_V5_var_multiplicity_apply_normal_form():
    """V5: a variable is normal under apply (VAR_MARK is opaque)."""
    c = Chart()
    v = c.var(c.NIL)
    assert c.apply(v) == v
    # And: applying v to anything is also normal (VAR_MARK is not a combinator)
    vx = c.cons(v, c.TRUE)
    # vx = (var(NIL) TRUE). Spine: head = VAR_MARK; not I/K/S; normal form.
    assert c.apply(vx) == vx


@test
def M14_V5_var_multiplicity_match_universal():
    """V5: same variable cell is universal under match (multiplicity)."""
    c = Chart()
    v = c.var(c.NIL)
    binding = c._match(v, c.TRUE, {})
    assert binding == {c.NIL: c.TRUE}
    # Match against another term: same variable, different binding
    binding2 = c._match(v, c.FALSE, {})
    assert binding2 == {c.NIL: c.FALSE}


@test
def M14_V6_full_K_application_not_variable():
    """V6: cons(cons(K, x), y) is full K-application, NOT a variable.

    CNF-2 binarization: depth distinguishes the cases. At depth 1,
    cons(VAR_MARK, name) is a variable. cons(K, x) at depth 1 is NOT a
    variable (left is K, not VAR_MARK). At depth 2, cons(cons(K, x), y)
    is a function application, also not a variable.
    """
    c = Chart()
    # Partial K-application: not a variable (left is K, not VAR_MARK)
    partial_K = c.cons(c.K, c.TRUE)
    assert not c.is_var(partial_K)
    # Full K-application: not a variable
    full_K = c.cons(c.cons(c.K, c.TRUE), c.FALSE)
    assert not c.is_var(full_K)
    # Reduces normally:
    assert c.apply(full_K) == c.TRUE


@test
def M14_audit_no_designated_atom_is_var():
    """Audit: no designated atom is accidentally a variable."""
    c = Chart()
    for atom in [c.NIL, c.TRUE, c.FALSE, c.FAILURE,
                 c.S, c.K, c.I, c.VAR_MARK]:
        assert not c.is_var(atom), f"{c.show(atom)} mis-recognized as variable"


@test
def M14_audit_T7_preserved():
    """Audit (the 001 component): M11's T7 equivalence still holds.

    interp(default_table, k) == apply(k) for the same test terms used in
    M11. The refactor doesn't change external behavior.
    """
    c = Chart()
    test_terms = [
        c.NIL, c.TRUE, c.FALSE, c.FAILURE, c.S, c.K, c.I,
        c.cons(c.I, c.TRUE),
        c.cons(c.cons(c.K, c.TRUE), c.FALSE),
        c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE),
        c.parse(c.NIL, "S K K true"),
        c.parse(c.NIL, "I (I (I true))"),
        c.parse(c.NIL, "K (S K K) false"),
        c.parse(c.NIL, "S (K I) (K K) true"),
    ]
    for t in test_terms:
        a, i = c.apply(t), c.interp(c.default_table, t)
        assert a == i, f"on {c.show(t)}: apply={c.show(a)} interp={c.show(i)}"


@test
def M14_audit_K_rule_dispatches_correctly():
    """Audit: the K-rule in default_table correctly matches K-applications.

    This is the test that K-marker would have failed: with VAR_MARK as a
    dedicated marker, the K-rule pattern cons(cons(K, VAR1), VAR2) doesn't
    have its inner cons(K, VAR1) mistakenly interpreted as a variable.
    """
    c = Chart()
    # (K true false) should match the K-rule pattern and reduce to true
    Kxy = c.cons(c.cons(c.K, c.TRUE), c.FALSE)
    assert c.interp(c.default_table, Kxy) == c.TRUE
    # (K (S K K) false) should reduce to (S K K)
    expr = c.cons(c.cons(c.K, c.cons(c.cons(c.S, c.K), c.K)), c.FALSE)
    assert c.interp(c.default_table, expr) == c.cons(c.cons(c.S, c.K), c.K)



def categorize(name):
    if name.startswith("S1"): return "S1 (nil)"
    if name.startswith("S2"): return "S2 (cons)"
    if name.startswith("S3"): return "S3 (left, right)"
    if name.startswith("S4"): return "S4 (eq)"
    if name.startswith("S5"): return "S5 (apply)"
    if name.startswith("S6"): return "S6 (parse)"
    if name.startswith("S7"): return "S7 (transform)"
    if name.startswith("M3"): return "M3 (constraint resolutions)"
    if name.startswith("M4"): return "M4 (apply as single-step)"
    if name.startswith("M5"): return "M5 (chart as memoization)"
    if name.startswith("M8"): return "M8 (cocycle invariance)"
    if name.startswith("M11"): return "M11 (meta-circular interpreter)"
    if name.startswith("M14"): return "M14 (VAR_MARK refactor audit)"
    if name.startswith("charter"): return "Charter gates"
    return "other"


def main():
    print("=" * 72)
    print("  Regroup pass (M10, axis 010)")
    print("  Reconstructing shadow specs from chart.py via behavior preservation")
    print("=" * 72)

    grouped = {}
    for t in TESTS:
        cat = categorize(t.__name__)
        grouped.setdefault(cat, []).append(t)

    order = [
        "S1 (nil)", "S2 (cons)", "S3 (left, right)", "S4 (eq)",
        "S5 (apply)", "S6 (parse)", "S7 (transform)",
        "M3 (constraint resolutions)", "M4 (apply as single-step)",
        "M5 (chart as memoization)", "M8 (cocycle invariance)",
        "M11 (meta-circular interpreter)",
        "M14 (VAR_MARK refactor audit)",
        "Charter gates",
    ]

    passed = failed = 0
    for cat in order:
        if cat not in grouped:
            continue
        print(f"\n[{cat}]")
        for t in grouped[cat]:
            try:
                t()
                print(f"  ✓ {t.__name__}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {t.__name__}: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ {t.__name__}: {type(e).__name__}: {e}")
                failed += 1

    print("\n" + "=" * 72)
    if failed == 0:
        print(f"  All {passed} tests pass.")
        print(f"  Shadows S1–S7 verified via behavior preservation.")
        print(f"  M-move invariants (M3 C1–C5, M4, M5, M8) verified.")
        print(f"  Realizability charter gates hold at every operation.")
        print(f"  L₁ (positive-closure) completes: {{100, 010, 110}} all populated.")
    else:
        print(f"  {passed} passed, {failed} failed.")
        print(f"  L₁ completion blocked; the shadows do not match the artefact.")
    print("=" * 72)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
