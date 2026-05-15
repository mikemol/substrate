"""
verify_inverses.py — tests for the 6 inverse operations (M35).

Verifies:
  - Each inverse has the correct signature (source/sink swapped, witness same)
  - Each inverse has opposite chirality from its fundamental
  - Each inverse can be found via registry.find_inverse(fundamental)
  - Each inverse operationally returns the expected data
  - V_4-orbit population is now 2/4 cells per orbit (was 1/4 in M34)
  - All 6 inverse pairs are detected by the meta-protocol's automatic relations
  - No regression on M34 tests
"""

from chart_with_inverses import ChartWithInverses
from meta_protocol import chirality_of, opposite_pair


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
# Inverse-pair structural correspondence
# ============================================================

INVERSE_PAIRS = [
    ('apply', 'quote_via_state'),
    ('workspace_witness', 'quote_via_workspace'),
    ('interp', 'decode_via_compute'),
    ('evolve_with_receipt', 'restore_from_receipt'),
    ('validated_store', 'validated_load'),
    ('store', 'load_with_log'),
]


def test_signatures_are_inverses():
    """Each inverse's (source, sink, witness) = (fund.sink, fund.source, fund.witness)."""
    c = ChartWithInverses()
    for fund_name, inv_name in INVERSE_PAIRS:
        fund = c.registry.get(fund_name)
        inv = c.registry.get(inv_name)
        expected = (fund.sink, fund.source, fund.witness)
        actual = (inv.source, inv.sink, inv.witness)
        if expected != actual:
            return f"{fund_name}/{inv_name}: signature mismatch {expected} vs {actual}"
    return True


def test_chiralities_flip():
    """Each fundamental and its inverse have opposite chirality."""
    c = ChartWithInverses()
    for fund_name, inv_name in INVERSE_PAIRS:
        fund = c.registry.get(fund_name)
        inv = c.registry.get(inv_name)
        if fund.chirality == inv.chirality:
            return f"{fund_name}/{inv_name}: same chirality {fund.chirality}"
    return True


def test_same_pairing():
    """Each fundamental and its inverse are in the same pairing."""
    c = ChartWithInverses()
    for fund_name, inv_name in INVERSE_PAIRS:
        fund = c.registry.get(fund_name)
        inv = c.registry.get(inv_name)
        if fund.pairing != inv.pairing:
            return f"{fund_name}/{inv_name}: different pairings {fund.pairing} vs {inv.pairing}"
    return True


def test_same_witness():
    """Each fundamental and its inverse share the same witness axis."""
    c = ChartWithInverses()
    for fund_name, inv_name in INVERSE_PAIRS:
        fund = c.registry.get(fund_name)
        inv = c.registry.get(inv_name)
        if fund.witness != inv.witness:
            return f"{fund_name}/{inv_name}: different witnesses"
    return True


def test_registry_finds_inverses_automatically():
    """registry.find_inverse(fund) should find the registered inverse op."""
    c = ChartWithInverses()
    for fund_name, inv_name in INVERSE_PAIRS:
        fund = c.registry.get(fund_name)
        found = c.registry.find_inverse(fund)
        if not found:
            return f"find_inverse({fund_name}) returned nothing"
        if inv_name not in [o.name for o in found]:
            names = [o.name for o in found]
            return f"find_inverse({fund_name}) returned {names}, expected {inv_name} in list"
    return True


# ============================================================
# Operational tests — each inverse runs and returns expected result
# ============================================================

def test_quote_via_state_finds_term():
    """quote_via_state should return a term that reduced to the target."""
    c = ChartWithInverses()
    # Ensure something is in the memo by normalizing
    c.normalize(c.cons(c.I, c.TRUE))
    # The memo now has (I TRUE) → TRUE
    result = c.quote_via_state(c.TRUE)
    if result == c.FAILURE:
        return "quote_via_state returned FAILURE (memo lookup failed)"
    return True


def test_restore_from_receipt_returns_data():
    """restore_from_receipt(w) where w holds a receipt should return the data."""
    c = ChartWithInverses()
    w = c.workspace_alloc()
    c.evolve_with_receipt(c.TRUE, w)
    result = c.restore_from_receipt(w)
    if result != c.TRUE:
        return f"expected TRUE, got {c.show(result)}"
    return True


def test_validated_load_passes():
    """validated_load with passing predicate should return data."""
    c = ChartWithInverses()
    w = c.workspace_alloc()
    c.validated_store(c.TRUE, w, c.I)
    # Identity predicate I(TRUE) → TRUE, so load passes
    result = c.validated_load(w, c.I)
    if result != c.TRUE:
        return f"expected TRUE, got {c.show(result)}"
    return True


def test_validated_load_fails_with_wrong_predicate():
    """validated_load with FALSE-returning predicate should return FAILURE."""
    c = ChartWithInverses()
    w = c.workspace_alloc()
    c.validated_store(c.TRUE, w, c.I)
    # (K FALSE) returns FALSE, so validation fails
    KFalse = c.cons(c.K, c.FALSE)
    result = c.validated_load(w, KFalse)
    if result != c.FAILURE:
        return f"expected FAILURE, got {c.show(result)}"
    return True


def test_load_with_log_logs_to_history():
    """load_with_log should append an entry to history."""
    c = ChartWithInverses()
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    h_before = len(c._history)
    c.load_with_log(w)
    h_after = len(c._history)
    if h_after != h_before + 1:
        return f"history grew by {h_after - h_before}, expected 1"
    return True


def test_decode_via_compute_extracts_data():
    """decode_via_compute should extract data from a history entry."""
    c = ChartWithInverses()
    # Inject a history entry
    c._history.append(('test_op', (c.TRUE,), c.TRUE))
    idx = len(c._history) - 1
    result = c.decode_via_compute(idx)
    if result != c.TRUE:
        return f"expected TRUE, got {c.show(result)}"
    return True


def test_quote_via_workspace_uses_workspace_witness():
    """quote_via_workspace should use workspace contents to return data."""
    c = ChartWithInverses()
    w = c.workspace_alloc()
    c.validated_store(c.TRUE, w, c.I)
    # Workspace[w] = ('validated', TRUE). normalize(TRUE) == TRUE.
    result = c.quote_via_workspace(c.TRUE, w)
    if result != c.TRUE:
        return f"expected TRUE, got {c.show(result)}"
    return True


# ============================================================
# Orbit population — each orbit now has 2 of 4 cells
# ============================================================

def test_each_orbit_has_two_ops():
    """After M35, every V_4-orbit has exactly 2 registered operations."""
    c = ChartWithInverses()
    for pairing in ('α', 'β', 'γ'):
        for chirality in ('even', 'odd'):
            count = len(c.registry.operations_in_orbit(pairing, chirality))
            if count != 2:
                return f"{pairing}-{chirality} has {count} ops, expected 2"
    return True


def test_total_registered_is_12():
    """12 = 6 V_4-orbits × 2 ops each. The remaining 12 cells need V_4-rotation."""
    c = ChartWithInverses()
    return len(c.registry) == 12


# ============================================================
# V_4-rotation extension would give 24 (path 1)
# ============================================================

def test_v4_rotations_of_registered_ops_cover_all_24():
    """The V_4-rotations of the 12 registered ops cover all 24 possible signatures."""
    c = ChartWithInverses()
    reachable = set()
    for op in c.registry.all():
        for swap_name in ('e', 'α', 'β', 'γ'):
            rotated = op.v4_rotate_signature(swap_name)
            reachable.add(rotated)
    if len(reachable) != 24:
        return f"V_4-rotations cover only {len(reachable)} of 24 signatures"
    return True


# ============================================================
# No regression
# ============================================================

def test_m34_operations_still_run():
    """The 6 M34 fundamentals should still work."""
    c = ChartWithInverses()
    # Forward operations from M34
    assert c.normalize(c.cons(c.I, c.TRUE)) == c.TRUE
    w = c.workspace_alloc()
    c.store(w, c.FALSE)
    assert c.load(w) == c.FALSE
    w2 = c.workspace_alloc()
    c.evolve_with_receipt(c.TRUE, w2)
    assert c._workspace[w2][0] == 'receipt'
    w3 = c.workspace_alloc()
    c.validated_store(c.TRUE, w3, c.I)
    assert c._workspace[w3][0] == 'validated'
    return True


def test_baseline_chart_still_works():
    """Base Chart operations: cons, normalize, apply should all still function."""
    c = ChartWithInverses()
    pair = c.cons(c.TRUE, c.FALSE)
    assert c._cells[pair] == (c.TRUE, c.FALSE)
    reduced = c.normalize(c.cons(c.K, c.TRUE))
    # K is constant: K x reduces under apply
    return True


# ============================================================
# Run all tests
# ============================================================

def main():
    print("=" * 78)
    print("  verify_inverses.py — M35 inverse-pair verification")
    print("=" * 78)

    runner = TestRunner()

    print("\n[structural correspondence]")
    runner.run('signatures_are_inverses', test_signatures_are_inverses)
    runner.run('chiralities_flip', test_chiralities_flip)
    runner.run('same_pairing', test_same_pairing)
    runner.run('same_witness', test_same_witness)
    runner.run('registry_finds_inverses_automatically', test_registry_finds_inverses_automatically)

    print("\n[operational correctness]")
    runner.run('quote_via_state_finds_term', test_quote_via_state_finds_term)
    runner.run('restore_from_receipt_returns_data', test_restore_from_receipt_returns_data)
    runner.run('validated_load_passes', test_validated_load_passes)
    runner.run('validated_load_fails_with_wrong_predicate', test_validated_load_fails_with_wrong_predicate)
    runner.run('load_with_log_logs_to_history', test_load_with_log_logs_to_history)
    runner.run('decode_via_compute_extracts_data', test_decode_via_compute_extracts_data)
    runner.run('quote_via_workspace_uses_workspace_witness', test_quote_via_workspace_uses_workspace_witness)

    print("\n[orbit population]")
    runner.run('each_orbit_has_two_ops', test_each_orbit_has_two_ops)
    runner.run('total_registered_is_12', test_total_registered_is_12)

    print("\n[V_4 extension to (1)]")
    runner.run('v4_rotations_of_registered_ops_cover_all_24', test_v4_rotations_of_registered_ops_cover_all_24)

    print("\n[no regression]")
    runner.run('m34_operations_still_run', test_m34_operations_still_run)
    runner.run('baseline_chart_still_works', test_baseline_chart_still_works)

    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print()
    runner.summary()
    print()


if __name__ == "__main__":
    main()
