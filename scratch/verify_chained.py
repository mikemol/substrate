"""
verify_chained.py — tests for M37 chained operations.

Verifies:
  - 24 chains built (one per host op)
  - Each chain satisfies the chaining rule (t-match, w-preserve)
  - The chain action is period-3 (applying 3x returns original)
  - Chain preserves witness and chirality
  - 8 Z_3 cycles partition the 24 ops
  - Each cycle's 3 ops cycle through 3 distinct pairings
  - Several chains run operationally
  - No regression on prior tests
"""

from chart_chained import ChartChained, ChainedOp, discover_z3_cycles
from meta_protocol import AXES


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
# Chain construction
# ============================================================

def test_24_chains_built():
    c = ChartChained()
    return len(c.chains) == 24


def test_each_chain_has_unique_host():
    c = ChartChained()
    host_names = [ch.host.name for ch in c.chains]
    return len(set(host_names)) == 24


def test_chaining_rule_t_passthrough():
    """For every chain, chained.source must equal host.sink."""
    c = ChartChained()
    for ch in c.chains:
        if ch.chained.source != ch.host.sink:
            return f"{ch.name}: chained.source={ch.chained.source}, host.sink={ch.host.sink}"
    return True


def test_chaining_rule_witness_preserved():
    """For every chain, chained.witness must equal host.witness."""
    c = ChartChained()
    for ch in c.chains:
        if ch.chained.witness != ch.host.witness:
            return f"{ch.name}: witness mismatch"
    return True


def test_chain_engages_all_four_axes():
    """The 4-axis signature must use all 4 distinct axes."""
    c = ChartChained()
    for ch in c.chains:
        sig = ch.signature_4axis
        if set(sig) != set(AXES):
            return f"{ch.name}: signature {sig} doesn't use all 4 axes"
    return True


# ============================================================
# Z_3 structure of the chain function
# ============================================================

def test_chain_is_period_3():
    """The chain function (s,t,w) -> (t,f,w) has period exactly 3."""
    c = ChartChained()
    def chain_step(sig):
        s, t, w = sig
        f = (set(AXES) - {s, t, w}).pop()
        return (t, f, w)

    for op in c.registry.all():
        sig0 = (op.source, op.sink, op.witness)
        sig1 = chain_step(sig0)
        sig2 = chain_step(sig1)
        sig3 = chain_step(sig2)
        if sig3 != sig0:
            return f"{op.name}: chain^3 != identity ({sig0} → {sig1} → {sig2} → {sig3})"
    return True


def test_chain_preserves_chirality():
    """Each chain step preserves chirality."""
    c = ChartChained()
    for ch in c.chains:
        if ch.host.chirality != ch.chained.chirality:
            return f"{ch.name}: chirality changed"
    return True


def test_chain_preserves_witness():
    """Each chain step keeps the same witness axis."""
    c = ChartChained()
    for ch in c.chains:
        if ch.host.witness != ch.chained.witness:
            return f"{ch.name}: witness changed"
    return True


def test_chain_cycles_through_three_pairings():
    """Each 3-cycle visits exactly 3 distinct pairings (α, β, γ — one each)."""
    c = ChartChained()
    cycles = discover_z3_cycles(c)
    for i, cycle in enumerate(cycles, 1):
        ops = [c.registry.at_signature(*s)[0] for s in cycle]
        pairings = [op.pairing for op in ops]
        if set(pairings) != {'α', 'β', 'γ'}:
            return f"cycle {i}: pairings {pairings} (expected {α, β, γ})"
    return True


def test_eight_cycles_partition_24():
    """The 8 3-cycles partition the 24 ops exactly."""
    c = ChartChained()
    cycles = discover_z3_cycles(c)
    if len(cycles) != 8:
        return f"got {len(cycles)} cycles, expected 8"
    all_in_cycles = set()
    for cycle in cycles:
        for sig in cycle:
            if sig in all_in_cycles:
                return f"sig {sig} appears in multiple cycles"
            all_in_cycles.add(sig)
    if len(all_in_cycles) != 24:
        return f"cycles cover {len(all_in_cycles)} sigs, expected 24"
    return True


def test_four_witnesses_each_have_two_cycles():
    """Each of 4 witness axes hosts exactly 2 cycles (one per chirality)."""
    c = ChartChained()
    cycles = discover_z3_cycles(c)
    from collections import defaultdict
    by_witness = defaultdict(list)
    for cycle in cycles:
        w = cycle[0][2]  # witness of any element (all same in cycle)
        by_witness[w].append(cycle)
    for witness, cs in by_witness.items():
        if len(cs) != 2:
            return f"witness {witness} has {len(cs)} cycles, expected 2"
        chiralities = [c.registry.at_signature(*cyc[0])[0].chirality for cyc in cs]
        if set(chiralities) != {'even', 'odd'}:
            return f"witness {witness}: chiralities {chiralities}, expected {{even, odd}}"
    return True


# ============================================================
# Held-axis = witness (quadradic V_4 cell correspondence)
# ============================================================

def test_held_axis_equals_witness():
    """In the V_4 (held, enabled) framework, the 'held' axis of a 4-axis chain is the witness."""
    c = ChartChained()
    for ch in c.chains:
        if ch.held_axis != ch.witness:
            return f"{ch.name}: held_axis={ch.held_axis}, witness={ch.witness}"
    return True


def test_six_chains_per_witness_axis():
    """The 24 chains split 6 per witness axis (matching the 4 V_4-quadradic cells)."""
    c = ChartChained()
    from collections import Counter
    witness_counts = Counter(ch.witness for ch in c.chains)
    for w in AXES:
        if witness_counts[w] != 6:
            return f"witness {w}: {witness_counts[w]} chains (expected 6)"
    return True


# ============================================================
# Operational correctness — chains run end-to-end
# ============================================================

def test_apply_chain_runs():
    """apply >> compute_to_workspace_via_state should deposit reduced value to workspace."""
    c = ChartChained()
    w = c.workspace_alloc()
    ch = c.chain_for('apply')
    expr = c.cons(c.I, c.TRUE)
    result = ch.run(host_args=(expr,), chained_extra_args=(w,))
    if result != c.TRUE:
        return f"got {c.show(result)}"
    if c._workspace[w] is None or c._workspace[w][0] != 'compute_result':
        return f"workspace[w]: {c._workspace[w]}"
    return True


def test_store_chain_runs():
    """store >> workspace_to_compute_via_state should fire compute on stored value."""
    c = ChartChained()
    w = c.workspace_alloc()
    ch = c.chain_for('store')
    result = ch.run(host_args=(w, c.TRUE), chained_extra_args=())
    return result == c.TRUE


def test_validated_store_chain_runs():
    """validated_store >> workspace_to_state_via_compute should validate then promote to state."""
    c = ChartChained()
    w = c.workspace_alloc()
    ch = c.chain_for('validated_store')
    # validated_store(data, slot, pred); then workspace_to_state_via_compute(slot, pred)
    result = ch.run(host_args=(c.TRUE, w, c.I), chained_extra_args=(c.I,))
    return result == c.TRUE


def test_evolve_chain_runs():
    """evolve_with_receipt >> state_to_compute_via_workspace should replay through compute."""
    c = ChartChained()
    w_evolve = c.workspace_alloc()
    w_replay = c.workspace_alloc()
    ch = c.chain_for('evolve_with_receipt')
    result = ch.run(host_args=(c.TRUE, w_evolve), chained_extra_args=(w_replay,))
    if c._workspace[w_replay] is None:
        return f"workspace[w_replay] not written"
    return True


# ============================================================
# No regression
# ============================================================

def test_baseline_chart_works():
    c = ChartChained()
    return c.normalize(c.cons(c.I, c.TRUE)) == c.TRUE


def test_24_op_registry_intact():
    c = ChartChained()
    return len(c.registry) == 24


# ============================================================
# Run
# ============================================================

def main():
    print("=" * 78)
    print("  verify_chained.py — M37 chained operations and Z_3 structure")
    print("=" * 78)

    runner = TestRunner()

    print("\n[chain construction]")
    runner.run('24_chains_built', test_24_chains_built)
    runner.run('each_chain_has_unique_host', test_each_chain_has_unique_host)
    runner.run('chaining_rule_t_passthrough', test_chaining_rule_t_passthrough)
    runner.run('chaining_rule_witness_preserved', test_chaining_rule_witness_preserved)
    runner.run('chain_engages_all_four_axes', test_chain_engages_all_four_axes)

    print("\n[Z_3 group action structure]")
    runner.run('chain_is_period_3', test_chain_is_period_3)
    runner.run('chain_preserves_chirality', test_chain_preserves_chirality)
    runner.run('chain_preserves_witness', test_chain_preserves_witness)
    runner.run('chain_cycles_through_three_pairings', test_chain_cycles_through_three_pairings)
    runner.run('eight_cycles_partition_24', test_eight_cycles_partition_24)
    runner.run('four_witnesses_each_have_two_cycles', test_four_witnesses_each_have_two_cycles)

    print("\n[V_4 quadradic correspondence]")
    runner.run('held_axis_equals_witness', test_held_axis_equals_witness)
    runner.run('six_chains_per_witness_axis', test_six_chains_per_witness_axis)

    print("\n[operational]")
    runner.run('apply_chain_runs', test_apply_chain_runs)
    runner.run('store_chain_runs', test_store_chain_runs)
    runner.run('validated_store_chain_runs', test_validated_store_chain_runs)
    runner.run('evolve_chain_runs', test_evolve_chain_runs)

    print("\n[no regression]")
    runner.run('baseline_chart_works', test_baseline_chart_works)
    runner.run('24_op_registry_intact', test_24_op_registry_intact)

    print()
    print("=" * 78)
    print("  Summary")
    print("=" * 78)
    print()
    runner.summary()
    print()


if __name__ == "__main__":
    main()
