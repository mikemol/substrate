"""
verify_meta_protocol.py — tests for the meta-protocol framework.

Verifies:
  - Chirality is correctly computed from (source, sink, witness)
  - All 6 V_4-orbits are populated with at least one operation
  - Inverse and V_4-twin signatures are correctly derived
  - The 2 new fundamental patterns run correctly
  - Coherence laws hold at the protocol level

This is the M34 verification — checking that we've actually closed the
6-pattern coverage gap, not just claimed to.
"""

from chart_meta import ChartWithMeta
from meta_protocol import (
    WitnessedOp, chirality_of, opposite_pair,
    PATTERN_NAMES, V4_SWAPS, AXES,
)


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
# Group 1: chirality is correctly computed
# ============================================================

def test_chirality_apply():
    """D→C w/ S should be even (M_SPPF_witness_application orbit)."""
    return chirality_of('D', 'C', 'S') == 'even'

def test_chirality_workspace_witness():
    """D→C w/ W should be odd."""
    return chirality_of('D', 'C', 'W') == 'odd'

def test_chirality_interp():
    """D→S w/ C (M11 interp) should be odd."""
    return chirality_of('D', 'S', 'C') == 'odd'

def test_chirality_evolve_with_receipt():
    """D→S w/ W (new β-even op) should be even."""
    return chirality_of('D', 'S', 'W') == 'even'

def test_chirality_validated_store():
    """D→W w/ C (new γ-even op) should be even."""
    return chirality_of('D', 'W', 'C') == 'even'

def test_chirality_store():
    """D→W w/ S (M32 store) should be odd."""
    return chirality_of('D', 'W', 'S') == 'odd'


# ============================================================
# Group 2: inverse always flips chirality
# ============================================================

def test_inverse_flips_chirality_all_24():
    """For all 24 directed ops, the inverse must have opposite chirality."""
    for source in AXES:
        for sink in AXES:
            if source == sink:
                continue
            opp, _ = opposite_pair(source, sink)
            for witness in opp:
                forward = chirality_of(source, sink, witness)
                inverse = chirality_of(sink, source, witness)  # swap source ↔ sink
                if forward == inverse:
                    return f"inverse of {source}→{sink} w/ {witness} has same chirality!"
    return True


# ============================================================
# Group 3: V_4 swaps preserve orbit
# ============================================================

def test_v4_preserves_pairing_and_chirality():
    """Applying any V_4 swap to (s, t, w) keeps the same (pairing, chirality)."""
    test_triples = [
        ('D', 'C', 'S'), ('D', 'C', 'W'),
        ('D', 'S', 'C'), ('D', 'S', 'W'),
        ('D', 'W', 'C'), ('D', 'W', 'S'),
    ]
    for source, sink, witness in test_triples:
        op = WitnessedOp(name='t', source=source, sink=sink, witness=witness, fn=lambda: None)
        for swap_name in ('α', 'β', 'γ'):
            ns, nt, nw = op.v4_rotate_signature(swap_name)
            if {ns, nt, nw} == {source, sink, witness}:
                continue  # V_4-invariant under this swap
            new_pairing = opposite_pair(ns, nt)[1]
            new_chirality = chirality_of(ns, nt, nw)
            if new_pairing != op.pairing or new_chirality != op.chirality:
                return (f"V_4-{swap_name} of {source}→{sink} w/ {witness} "
                        f"changed orbit: {op.pairing}-{op.chirality} → "
                        f"{new_pairing}-{new_chirality}")
    return True


# ============================================================
# Group 4: registry behaviors
# ============================================================

def test_registry_size():
    """The chart should have 6 operations registered (one per V_4-orbit)."""
    c = ChartWithMeta()
    return len(c.registry) == 6

def test_each_orbit_populated():
    """All 6 V_4-orbits should have at least one registered operation."""
    c = ChartWithMeta()
    report = c.coverage_report()
    empty = [k for k, v in report.items() if v == 0]
    if empty:
        return f"empty orbits: {empty}"
    return True

def test_chirality_consistent_with_orbit():
    """Each registered operation's chirality should match the V_4-orbit it lives in."""
    c = ChartWithMeta()
    for op in c.registry.all():
        expected_chir = chirality_of(op.source, op.sink, op.witness)
        if op.chirality != expected_chir:
            return f"{op.name}: chirality mismatch (op says {op.chirality}, sign says {expected_chir})"
    return True


# ============================================================
# Group 5: operational correctness of the 2 new patterns
# ============================================================

def test_evolve_with_receipt_advances_state():
    """evolve_with_receipt should grow the history by exactly one entry."""
    c = ChartWithMeta()
    w = c.workspace_alloc()
    h_before = c.history_length()
    c.evolve_with_receipt(c.TRUE, w)
    h_after = c.history_length()
    return h_after == h_before + 1

def test_evolve_with_receipt_writes_workspace():
    """evolve_with_receipt should leave a receipt tuple in the workspace."""
    c = ChartWithMeta()
    w = c.workspace_alloc()
    c.evolve_with_receipt(c.TRUE, w)
    entry = c._workspace[w]
    if entry is None or entry[0] != 'receipt':
        return f"workspace[w] = {entry}, expected receipt tuple"
    return True

def test_evolve_with_receipt_returns_data():
    """evolve_with_receipt returns its data input (data is unchanged)."""
    c = ChartWithMeta()
    w = c.workspace_alloc()
    result = c.evolve_with_receipt(c.TRUE, w)
    return result == c.TRUE

def test_validated_store_passes_with_true_predicate():
    """validated_store with predicate I (identity) on TRUE should store and return TRUE."""
    c = ChartWithMeta()
    w = c.workspace_alloc()
    result = c.validated_store(c.TRUE, w, c.I)
    if result != c.TRUE:
        return f"result={c.show(result)}, expected TRUE"
    entry = c._workspace[w]
    if entry is None or entry[0] != 'validated':
        return f"workspace[w] = {entry}, expected validated tuple"
    return True

def test_validated_store_fails_with_false_predicate():
    """validated_store with a predicate that returns FALSE should leave workspace empty."""
    c = ChartWithMeta()
    w = c.workspace_alloc()
    # (K FALSE) applied to anything → FALSE
    KFalse = c.cons(c.K, c.FALSE)
    result = c.validated_store(c.TRUE, w, KFalse)
    if result != c.FAILURE:
        return f"result={c.show(result)}, expected FAILURE"
    if c._workspace[w] is not None:
        return f"workspace[w] = {c._workspace[w]}, expected None"
    return True


# ============================================================
# Group 6: the meta-protocol's derived relations
# ============================================================

def test_inverse_signature_derivation():
    """For each registered op, invert_signature() should swap source and sink."""
    c = ChartWithMeta()
    for op in c.registry.all():
        inv = op.invert_signature()
        if inv != (op.sink, op.source, op.witness):
            return f"{op.name}: invert_signature wrong"
    return True

def test_v4_twin_signature_derivation():
    """For each registered op, V_4 swap should produce signatures in the same orbit."""
    c = ChartWithMeta()
    for op in c.registry.all():
        for swap_name in ('α', 'β', 'γ'):
            ns, nt, nw = op.v4_rotate_signature(swap_name)
            new_chir = chirality_of(ns, nt, nw)
            new_pair, new_pairing = opposite_pair(ns, nt)
            if new_chir != op.chirality or new_pairing != op.pairing:
                return f"{op.name}/{swap_name}: orbit not preserved"
    return True


# ============================================================
# Group 7: no regression — existing operations still work
# ============================================================

def test_baseline_apply_still_works():
    """apply (from base Chart) should still reduce correctly."""
    c = ChartWithMeta()
    term = c.cons(c.I, c.TRUE)
    return c.normalize(term) == c.TRUE

def test_baseline_store_still_works():
    """store (M32) should still write to workspace."""
    c = ChartWithMeta()
    w = c.workspace_alloc()
    c.store(w, c.TRUE)
    return c.load(w) == c.TRUE


# ============================================================
# Run all tests
# ============================================================

def main():
    print("=" * 78)
    print("  verify_meta_protocol.py — coherence and coverage verification")
    print("=" * 78)

    runner = TestRunner()

    print("\n[chirality computation]")
    runner.run('chirality_apply (α-even)', test_chirality_apply)
    runner.run('chirality_workspace_witness (α-odd)', test_chirality_workspace_witness)
    runner.run('chirality_interp (β-odd)', test_chirality_interp)
    runner.run('chirality_evolve_with_receipt (β-even)', test_chirality_evolve_with_receipt)
    runner.run('chirality_validated_store (γ-even)', test_chirality_validated_store)
    runner.run('chirality_store (γ-odd)', test_chirality_store)

    print("\n[inverse always flips chirality]")
    runner.run('inverse_flips_chirality_all_24', test_inverse_flips_chirality_all_24)

    print("\n[V_4 swaps preserve V_4-orbit]")
    runner.run('v4_preserves_pairing_and_chirality', test_v4_preserves_pairing_and_chirality)

    print("\n[registry behaviors]")
    runner.run('registry_size = 6', test_registry_size)
    runner.run('each_of_6_orbits_populated', test_each_orbit_populated)
    runner.run('chirality_consistent_with_orbit', test_chirality_consistent_with_orbit)

    print("\n[2 new patterns operational]")
    runner.run('evolve_with_receipt_advances_state', test_evolve_with_receipt_advances_state)
    runner.run('evolve_with_receipt_writes_workspace', test_evolve_with_receipt_writes_workspace)
    runner.run('evolve_with_receipt_returns_data', test_evolve_with_receipt_returns_data)
    runner.run('validated_store_passes_with_true_predicate', test_validated_store_passes_with_true_predicate)
    runner.run('validated_store_fails_with_false_predicate', test_validated_store_fails_with_false_predicate)

    print("\n[meta-protocol derived relations]")
    runner.run('inverse_signature_derivation', test_inverse_signature_derivation)
    runner.run('v4_twin_signature_derivation', test_v4_twin_signature_derivation)

    print("\n[no regression]")
    runner.run('baseline_apply_still_works', test_baseline_apply_still_works)
    runner.run('baseline_store_still_works', test_baseline_store_still_works)

    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print()
    runner.summary()
    print()


if __name__ == "__main__":
    main()
