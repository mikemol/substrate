"""
verify_full_v4.py — tests for the V_4-extension (M36).

Verifies:
  - 24 operations registered (full S_4 orbit)
  - Each V_4-orbit has 4 of 4 cells populated
  - Each registered op has exactly 3 V_4-twins
  - Every directed witnessed signature (s, t, w) is registered exactly once
  - V_4-rotations of any registered op are themselves registered
  - The 12 new ops run operationally
  - No regression on M34, M35, baseline tests
"""

from chart_full_v4 import ChartFullV4
from meta_protocol import chirality_of, opposite_pair, AXES


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.records = []

    def run(self, name, fn):
        try:
            result = fn()
            if result is True:
                self.passed += 1
                self.records.append(('✓', name))
            else:
                self.failed += 1
                self.records.append(('✗', f"{name}: {result}"))
        except Exception as e:
            self.failed += 1
            self.records.append(('✗', f"{name}: {type(e).__name__}: {e}"))

    def summary(self):
        for marker, line in self.records:
            print(f"  {marker} {line}")
        print()
        total = self.passed + self.failed
        verdict = '✓✓✓' if self.failed == 0 else f'({self.failed} failures)'
        print(f"  {self.passed}/{total} pass  {verdict}")


# ============================================================
# Full orbit closure
# ============================================================

def test_registry_size_is_24():
    c = ChartFullV4()
    return len(c.registry) == 24


def test_all_orbits_at_4_cells():
    c = ChartFullV4()
    for pairing in ('α', 'β', 'γ'):
        for chirality in ('even', 'odd'):
            count = len(c.registry.operations_in_orbit(pairing, chirality))
            if count != 4:
                return f"{pairing}-{chirality} has {count} ops, expected 4"
    return True


def test_every_op_has_3_v4_twins():
    """Each registered op should have exactly 3 V_4-twins (other 3 in same orbit)."""
    c = ChartFullV4()
    for op in c.registry.all():
        twins = c.registry.find_v4_twins(op)
        # twins is dict[swap_name] -> list of ops; flatten and count distinct
        all_twin_ops = []
        for twin_list in twins.values():
            for t in twin_list:
                if t.name != op.name and t.name not in [a.name for a in all_twin_ops]:
                    all_twin_ops.append(t)
        if len(all_twin_ops) != 3:
            return f"{op.name}: found {len(all_twin_ops)} distinct V_4-twins (expected 3)"
    return True


def test_every_signature_registered_once():
    """All 24 directed witnessed signatures should be uniquely registered."""
    c = ChartFullV4()
    all_signatures = []
    for s in AXES:
        for t in AXES:
            if s == t:
                continue
            opp, _ = opposite_pair(s, t)
            for w in opp:
                all_signatures.append((s, t, w))

    for sig in all_signatures:
        ops_at_sig = c.registry.at_signature(*sig)
        if len(ops_at_sig) != 1:
            return f"signature {sig}: {len(ops_at_sig)} ops (expected 1)"
    return True


def test_v4_rotations_remain_in_registry():
    """V_4-rotating any registered op must produce a signature also in the registry."""
    c = ChartFullV4()
    for op in c.registry.all():
        for swap in ('α', 'β', 'γ'):
            rotated = op.v4_rotate_signature(swap)
            if not c.registry.at_signature(*rotated):
                return f"V_4-{swap} of {op.name} → {rotated}: not registered"
    return True


def test_inverse_signatures_all_registered():
    """Every op's inverse signature must be registered."""
    c = ChartFullV4()
    for op in c.registry.all():
        inv_sig = op.invert_signature()
        if not c.registry.at_signature(*inv_sig):
            return f"inverse of {op.name} → {inv_sig}: not registered"
    return True


# ============================================================
# The 12 new operations run correctly
# ============================================================

def test_state_to_workspace_via_data():
    c = ChartFullV4()
    c._history.append(('seed', (c.TRUE,), c.TRUE))
    idx = len(c._history) - 1  # capture before workspace_alloc
    w = c.workspace_alloc()
    result = c.state_to_workspace_via_data(idx, w, c.TRUE)
    if result != c.TRUE:
        return f"got {c.show(result)}"
    entry = c._workspace[w]
    if entry is None or entry[0] != 'snapshot':
        return f"workspace entry: {entry}"
    return True


def test_workspace_to_state_via_compute():
    c = ChartFullV4()
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    result = c.workspace_to_state_via_compute(w, c.I)  # I(TRUE)→TRUE, passes
    return result == c.TRUE


def test_state_to_workspace_via_compute():
    c = ChartFullV4()
    c._history.append(('seed', (c.TRUE,), c.TRUE))
    idx = len(c._history) - 1  # capture before workspace_alloc
    w = c.workspace_alloc()
    result = c.state_to_workspace_via_compute(idx, w, c.I)  # I(TRUE)→TRUE
    return result == c.TRUE


def test_workspace_to_state_via_data():
    c = ChartFullV4()
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    result = c.workspace_to_state_via_data(w, c.TRUE)  # invariant TRUE == TRUE
    return result == c.TRUE


def test_compute_to_workspace_via_state():
    c = ChartFullV4()
    w = c.workspace_alloc()
    result = c.compute_to_workspace_via_state(c.TRUE, w)
    if result != c.TRUE:
        return f"got {c.show(result)}"
    return c._workspace[w][0] == 'compute_result'


def test_workspace_to_compute_via_data():
    c = ChartFullV4()
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    # Apply I (identity) to workspace contents: I(TRUE) → TRUE
    result = c.workspace_to_compute_via_data(w, c.I)
    return result == c.TRUE


def test_compute_to_workspace_via_data():
    c = ChartFullV4()
    w = c.workspace_alloc()
    # (I TRUE) → TRUE, so check passes
    result = c.compute_to_workspace_via_data(c.TRUE, w, c.I)
    return result == c.TRUE


def test_workspace_to_compute_via_state():
    c = ChartFullV4()
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    h_before = len(c._history)
    result = c.workspace_to_compute_via_state(w)
    h_after = len(c._history)
    if h_after <= h_before:
        return f"history did not grow: {h_before} → {h_after}"
    return True


def test_compute_to_state_via_data():
    c = ChartFullV4()
    result = c.compute_to_state_via_data(c.TRUE, c.I)
    if result != c.TRUE:
        return f"got {c.show(result)}"
    # Operation engages C (witness via cons+normalize → extra log entries) and S (sink)
    # Check that the operation's own state-write was performed (last history entry)
    last = c._history[-1]
    if last[0] != 'compute_state':
        return f"last history entry: {last[0]}, expected 'compute_state'"
    return True


def test_state_to_compute_via_workspace():
    c = ChartFullV4()
    c._history.append(('seed', (c.TRUE,), c.TRUE))
    idx = len(c._history) - 1  # capture before workspace_alloc
    w = c.workspace_alloc()
    result = c.state_to_compute_via_workspace(idx, w)
    if c._workspace[w] is None or c._workspace[w][0] != 'replay':
        return f"workspace: {c._workspace[w]}"
    return True


def test_compute_to_state_via_workspace():
    c = ChartFullV4()
    w = c.workspace_alloc()
    h_before = len(c._history)
    result = c.compute_to_state_via_workspace(c.TRUE, w)
    h_after = len(c._history)
    return h_after == h_before + 1 and result == c.TRUE


def test_state_to_compute_via_data():
    c = ChartFullV4()
    c._history.append(('seed', (c.TRUE,), c.TRUE))
    idx = len(c._history) - 1
    result = c.state_to_compute_via_data(idx, c.TRUE)  # invariant matches result
    return result == c.TRUE


# ============================================================
# No regression
# ============================================================

def test_m35_operations_still_work():
    c = ChartFullV4()
    # apply, store, validated_store, evolve_with_receipt, interp
    # quote_via_state, validated_load, restore_from_receipt
    assert c.normalize(c.cons(c.I, c.TRUE)) == c.TRUE
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    assert c.load(w) == c.TRUE
    w2 = c.workspace_alloc()
    c.validated_store(c.TRUE, w2, c.I)
    assert c.validated_load(w2, c.I) == c.TRUE
    w3 = c.workspace_alloc()
    c.evolve_with_receipt(c.TRUE, w3)
    assert c.restore_from_receipt(w3) == c.TRUE
    return True


def test_baseline_still_works():
    c = ChartFullV4()
    pair = c.cons(c.TRUE, c.FALSE)
    assert c._cells[pair] == (c.TRUE, c.FALSE)
    # Term composition still reduces
    expr = c.cons(c.I, c.TRUE)
    assert c.normalize(expr) == c.TRUE
    return True


# ============================================================
# Run all
# ============================================================

def main():
    print("=" * 78)
    print("  verify_full_v4.py — M36 V_4-extension verification")
    print("=" * 78)

    runner = TestRunner()

    print("\n[full orbit closure]")
    runner.run('registry_size_is_24', test_registry_size_is_24)
    runner.run('all_orbits_at_4_cells', test_all_orbits_at_4_cells)
    runner.run('every_op_has_3_v4_twins', test_every_op_has_3_v4_twins)
    runner.run('every_signature_registered_once', test_every_signature_registered_once)
    runner.run('v4_rotations_remain_in_registry', test_v4_rotations_remain_in_registry)
    runner.run('inverse_signatures_all_registered', test_inverse_signatures_all_registered)

    print("\n[12 new operations run]")
    runner.run('state_to_workspace_via_data', test_state_to_workspace_via_data)
    runner.run('workspace_to_state_via_compute', test_workspace_to_state_via_compute)
    runner.run('state_to_workspace_via_compute', test_state_to_workspace_via_compute)
    runner.run('workspace_to_state_via_data', test_workspace_to_state_via_data)
    runner.run('compute_to_workspace_via_state', test_compute_to_workspace_via_state)
    runner.run('workspace_to_compute_via_data', test_workspace_to_compute_via_data)
    runner.run('compute_to_workspace_via_data', test_compute_to_workspace_via_data)
    runner.run('workspace_to_compute_via_state', test_workspace_to_compute_via_state)
    runner.run('compute_to_state_via_data', test_compute_to_state_via_data)
    runner.run('state_to_compute_via_workspace', test_state_to_compute_via_workspace)
    runner.run('compute_to_state_via_workspace', test_compute_to_state_via_workspace)
    runner.run('state_to_compute_via_data', test_state_to_compute_via_data)

    print("\n[no regression]")
    runner.run('m35_operations_still_work', test_m35_operations_still_work)
    runner.run('baseline_still_works', test_baseline_still_works)

    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print()
    runner.summary()
    print()


if __name__ == "__main__":
    main()
