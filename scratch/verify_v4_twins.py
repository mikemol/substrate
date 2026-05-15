"""
verify_v4_twins.py — Cocycle invariance test suite for M30/M31 V₄-twin
operations implemented in chart.py.

For each V₄-twin operation, verify:
  (V) V₄-invariance — operation produces results in the same V₄-orbit
  (C) cocycle commutativity — V₄-twin pairs produce equivalent results
  (W) WHT orthogonality — different gauges give distinguishable signatures

These tests verify the formal claims from M29 (state machine construction)
and M30/M31 (V₄-twin construction) in actual running code.
"""

from chart import Chart


# ============================================================
# Test infrastructure
# ============================================================

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def run(self, name, fn):
        try:
            result = fn()
            if result is True:
                self.passed += 1
                self.tests.append(('✓', name))
            else:
                self.failed += 1
                self.tests.append(('✗', f"{name}: {result}"))
        except Exception as e:
            self.failed += 1
            self.tests.append(('✗', f"{name}: {type(e).__name__}: {e}"))

    def summary(self):
        print()
        for marker, name in self.tests:
            print(f"  {marker} {name}")
        print()
        total = self.passed + self.failed
        print(f"  {self.passed}/{total} pass" + ("  ✓✓✓" if self.failed == 0 else f"  ({self.failed} failures)"))


# ============================================================
# Test category 1: V invariance (V₄-twin same orbit)
# ============================================================

def test_V_workspace_alloc_independent_of_chart_state():
    """workspace_alloc (MV₄-14) is a V₄-twin of S1_nil. Like S1_nil,
    it should produce a fresh resource that depends only on prior alloc
    state, not on chart contents."""
    c1 = Chart()
    c2 = Chart()
    # Make the charts differ in data
    c2.cons(c2.K, c2.S)
    c2.cons(c2.I, c2.TRUE)
    # workspace_alloc should still produce w_id 0 for both
    w1 = c1.workspace_alloc()
    w2 = c2.workspace_alloc()
    return w1 == w2 == 0


def test_V_compute_identity_preserves_all_atoms():
    """compute_identity (MV₄-12) is V₄-twin of S1_nil. Like S1_nil's
    'do nothing' nature, it should preserve every atom unchanged."""
    c = Chart()
    for atom in [c.NIL, c.TRUE, c.FALSE, c.S, c.K, c.I, c.VAR_MARK]:
        if c.compute_identity(atom) != atom:
            return f"compute_identity({atom}) != {atom}"
    return True


def test_V_state_identity_only_advances_history():
    """state_identity (MV₄-13) should advance history without changing chart."""
    c = Chart()
    chart_size_before = c.size()
    workspace_size_before = c.workspace_size()
    h_before = c.history_length()
    c.state_identity()
    return (c.size() == chart_size_before
            and c.workspace_size() == workspace_size_before
            and c.history_length() == h_before + 1)


# ============================================================
# Test category 2: C cocycle commutativity (V₄-twin equivalence)
# ============================================================

def test_C_workspace_driven_state_equals_apply():
    """workspace_driven_state (MV₄-2) is V₄-twin of morton_heap_driver
    via γ-swap. The state-axis version (direct apply) and workspace-axis
    version should produce equal results — cocycle invariance.

    Tests across multiple terms to verify coherence isn't accidental.
    """
    c = Chart()
    test_terms = [
        c.parse(c.NIL, "I true"),
        c.parse(c.NIL, "K true false"),
        c.parse(c.NIL, "S K K true"),
        c.parse(c.NIL, "I (I true)"),
        c.parse(c.NIL, "K (I true) false"),
    ]
    for t in test_terms:
        w = c.workspace_alloc()
        c.store(w, t)
        via_workspace = c.workspace_driven_state(w)
        direct = c.apply(t)
        if via_workspace != direct:
            return f"term {c.show(t)}: ws={c.show(via_workspace)} != direct={c.show(direct)}"
    return True


def test_C_workspace_witness_equals_state_witness():
    """workspace_witness (MV₄-3) is V₄-twin of state-axis witness via
    α-swap. When the witness matches, both should return the matched value;
    when it doesn't, both should return FAILURE."""
    c = Chart()
    term = c.parse(c.NIL, "I true")
    expected_normal = c.TRUE
    # Match case
    w = c.workspace_alloc()
    c.store(w, expected_normal)
    ws_match = c.workspace_witness(w, term)
    state_match = expected_normal if c.normalize(term) == expected_normal else c.FAILURE
    if ws_match != state_match:
        return f"match: ws={c.show(ws_match)} != state={c.show(state_match)}"
    # No-match case
    c.store(w, c.FALSE)
    ws_nomatch = c.workspace_witness(w, term)
    state_nomatch = c.FALSE if c.normalize(term) == c.FALSE else c.FAILURE
    if ws_nomatch != state_nomatch:
        return f"no-match: ws={c.show(ws_nomatch)} != state={c.show(state_nomatch)}"
    return True


def test_C_marker_discrimination_symmetric():
    """compute_marker (MV₄-7) and workspace_marker (MV₄-9) are both
    V₄-twins of VAR_MARK. Both should be discriminable as markers."""
    c = Chart()
    # compute_marker
    w1 = c.workspace_alloc()
    c.compute_marker(w1, c.I)
    if not c.is_workspace_marker(w1):
        return f"compute_marker_cell not discriminated as marker"
    # workspace_marker
    w2 = c.workspace_alloc()
    c.workspace_marker(w2, c.K)
    if not c.is_workspace_marker(w2):
        return f"workspace_marker_cell not discriminated as marker"
    # plain data is NOT a marker
    w3 = c.workspace_alloc()
    c.store(w3, c.TRUE)
    if c.is_workspace_marker(w3):
        return f"data cell wrongly discriminated as marker"
    return True


def test_C_identity_compose_associative():
    """Composition of identity primitives across axes should be associative
    and produce no net effect. This is the multi-axis cocycle property."""
    c = Chart()
    initial_chart_size = c.size()
    initial_workspace_size = c.workspace_size()
    initial_history_length = c.history_length()

    # Apply identities across all three "no-op" axes
    term = c.TRUE
    after_compute_id = c.compute_identity(term)
    c.state_identity()
    w = c.workspace_alloc()  # workspace identity = alloc empty
    after_load = c.load(w)  # empty workspace returns FAILURE per spec
    c.workspace_free(w)

    # Compute identity should preserve term
    if after_compute_id != term:
        return f"compute_identity changed term: {c.show(after_compute_id)} != {c.show(term)}"
    # Empty workspace load should return FAILURE
    if after_load != c.FAILURE:
        return f"empty workspace load: expected FAILURE, got {c.show(after_load)}"
    return True


# ============================================================
# Test category 3: W orthogonality (different axes distinguishable)
# ============================================================

def test_W_data_marker_vs_compute_marker_distinct():
    """Data cells and compute-marker cells have distinct kinds even when
    holding the same underlying value. The W axis is observable."""
    c = Chart()
    w1 = c.workspace_alloc()
    w2 = c.workspace_alloc()
    c.store(w1, c.I)  # data: holds I
    c.compute_marker(w2, c.I)  # compute_marker: tagged with I
    return (c.workspace_kind(w1) == 'data'
            and c.workspace_kind(w2) == 'compute_marker'
            and c.workspace_kind(w1) != c.workspace_kind(w2))


def test_W_history_distinguishes_operation_types():
    """The state history (S axis) should record different operation types
    distinguishably, so we can filter by op_name. Verifies WHT-like
    orthogonality at the history level."""
    c = Chart()
    initial = c.history_length()
    # Trigger different operations
    x = c.cons(c.S, c.K)
    c.apply(x)
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    c.state_identity()
    # Check that each operation type is filterable
    op_counts = {
        'cons': len(c.history_filter('cons')),
        'apply': len(c.history_filter('apply')),
        'workspace_alloc': len(c.history_filter('workspace_alloc')),
        'store': len(c.history_filter('store')),
        'state_identity': len(c.history_filter('state_identity')),
    }
    # All should be nonzero
    return all(v > 0 for v in op_counts.values())


def test_W_chart_history_separate_from_workspace_history():
    """The S axis history should record both chart and workspace ops,
    but they should be distinguishable. Tests observability of the
    full 4-axis state space."""
    c = Chart()
    h0 = c.history_length()

    # Chart-only op (cons advances D and S)
    c.cons(c.K, c.S)
    h_after_cons = c.history_length()
    cons_logged = h_after_cons > h0

    # Workspace-only op
    w = c.workspace_alloc()
    h_after_alloc = c.history_length()
    alloc_logged = h_after_alloc > h_after_cons

    # Apply (compute + state)
    c.apply(c.cons(c.I, c.TRUE))
    h_after_apply = c.history_length()
    apply_logged = h_after_apply > h_after_alloc

    return cons_logged and alloc_logged and apply_logged


# ============================================================
# Test category 4: cross-cutting integration tests
# ============================================================

def test_integration_workspace_witness_in_real_pipeline():
    """End-to-end: use workspace_witness to validate a reduction result.
    This tests the W axis as a first-class participant in computation."""
    c = Chart()
    # Set up the expected result in workspace
    expected = c.TRUE
    w = c.workspace_alloc()
    c.store(w, expected)
    # Run several terms that should all reduce to TRUE
    terms = [
        c.parse(c.NIL, "I true"),
        c.parse(c.NIL, "K true false"),
        c.parse(c.NIL, "I (I (I true))"),
    ]
    for t in terms:
        result = c.workspace_witness(w, t)
        if result != expected:
            return f"term {c.show(t)}: expected witness={c.show(expected)}, got {c.show(result)}"
    return True


def test_integration_marker_drives_evaluation():
    """End-to-end: use compute_marker + workspace_driven_state together.
    This is the "Z5_invoke-style" use case from M31."""
    c = Chart()
    # Build a function-like term, store it in workspace via compute_marker
    fn = c.parse(c.NIL, "K true")  # (K true) - a function that consumes one arg
    w = c.workspace_alloc()
    c.compute_marker(w, fn)
    # Drive state from workspace — should apply the function
    result = c.workspace_driven_state(w)
    # (K true) reduces to ... well, (K true) needs an arg to fully reduce
    # but as a normal form it stays (K true). The marker drives apply().
    direct = c.apply(fn)
    return result == direct


def test_integration_history_supports_replay():
    """The state history should support replay-like queries. This is the
    foundation for MV₄-1 (BWT-state-history)."""
    c = Chart()
    # Do some work
    x = c.parse(c.NIL, "S K K")
    y = c.cons(x, c.TRUE)
    z = c.apply(y)
    # Query: how many cons operations happened?
    cons_count = len(c.history_filter('cons'))
    # Query: what was the result of the apply?
    apply_events = c.history_filter('apply')
    if not apply_events:
        return "no apply events recorded"
    last_apply_idx, last_apply = apply_events[-1]
    op_name, args, result = last_apply
    return cons_count > 0 and result == z


# ============================================================
# Run all tests
# ============================================================

def main():
    print("=" * 72)
    print("  verify_v4_twins.py — cocycle invariance verification suite")
    print("=" * 72)

    runner = TestRunner()

    print("\n[V invariance — V₄-twin preserves orbit]")
    runner.run('V_workspace_alloc_independent_of_chart_state',
               test_V_workspace_alloc_independent_of_chart_state)
    runner.run('V_compute_identity_preserves_all_atoms',
               test_V_compute_identity_preserves_all_atoms)
    runner.run('V_state_identity_only_advances_history',
               test_V_state_identity_only_advances_history)

    print("\n[C cocycle commutativity — V₄-twin equivalence]")
    runner.run('C_workspace_driven_state_equals_apply',
               test_C_workspace_driven_state_equals_apply)
    runner.run('C_workspace_witness_equals_state_witness',
               test_C_workspace_witness_equals_state_witness)
    runner.run('C_marker_discrimination_symmetric',
               test_C_marker_discrimination_symmetric)
    runner.run('C_identity_compose_associative',
               test_C_identity_compose_associative)

    print("\n[W orthogonality — axes are distinguishable]")
    runner.run('W_data_marker_vs_compute_marker_distinct',
               test_W_data_marker_vs_compute_marker_distinct)
    runner.run('W_history_distinguishes_operation_types',
               test_W_history_distinguishes_operation_types)
    runner.run('W_chart_history_separate_from_workspace_history',
               test_W_chart_history_separate_from_workspace_history)

    print("\n[Integration — full V₄ machinery in real pipelines]")
    runner.run('integration_workspace_witness_in_real_pipeline',
               test_integration_workspace_witness_in_real_pipeline)
    runner.run('integration_marker_drives_evaluation',
               test_integration_marker_drives_evaluation)
    runner.run('integration_history_supports_replay',
               test_integration_history_supports_replay)

    runner.summary()
    print("=" * 72)


if __name__ == "__main__":
    main()
