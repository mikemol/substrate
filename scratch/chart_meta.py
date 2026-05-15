"""
chart_meta.py — Chart extended with the meta-protocol and the 2 missing
fundamental patterns (β-even and γ-even).

After M34, the architecture has 6 fundamental V_4-orbit patterns. The
current chart populates 4 of them. This file:
  1. Registers each existing relevant operation under the meta-protocol.
  2. Implements the 2 missing patterns:
       β-even: workspace-receipted state change (D→S w/ W)
       γ-even: compute-validated store (D→W w/ C)
  3. Demonstrates that the 6-pattern coverage closes.

After this, every fundamental architectural pattern has at least one
running instance.
"""

from chart import Chart
from meta_protocol import (
    WitnessedOp, OperationRegistry, PATTERN_NAMES, pattern_name,
    chirality_of, opposite_pair,
)


class ChartWithMeta(Chart):
    """Chart with witnessed-pair meta-protocol registration."""

    def __init__(self):
        super().__init__()
        self.registry = OperationRegistry()

        # Implement the 2 missing fundamental patterns first so they're
        # available as methods before registration.
        self._install_missing_patterns()

        # Register all relevant operations under the meta-protocol.
        self._register_operations()

    # ========================================================
    # The 2 missing fundamental patterns
    # ========================================================

    def _install_missing_patterns(self) -> None:
        # β-even — workspace-receipted state change (D→S w/ W)
        # The state advances, with workspace logging a receipt (timestamp + ref).
        # This is the workspace-witnessed analogue of M11 interp.
        def evolve_with_receipt(data_id: int, workspace_id: int) -> int:
            """β-even: D→S w/ W. Evolve state with data; workspace receipts the transition.

            Operationally:
              - data_id drives a state transition (history advances with the transition)
              - workspace[workspace_id] receives a receipt linking back to that transition
              - returns data_id (the data is unchanged; what changed is the state log)

            This is the architectural pattern for event-sourced state changes
            with workspace audit trail.
            """
            # The state transition
            transition_idx = len(self._history)
            self._history.append((
                'evolve_with_receipt',
                (data_id, workspace_id),
                data_id,
            ))
            # Workspace receipt: tag + data ref + history index
            self._workspace[workspace_id] = (
                'receipt',
                data_id,
                transition_idx,
            )
            return data_id

        self.evolve_with_receipt = evolve_with_receipt

        # γ-even — compute-validated store (D→W w/ C)
        # Data goes to workspace iff a compute predicate validates it.
        # Compute is the witness: it confirms (or denies) the store.
        def validated_store(data_id: int, workspace_id: int, predicate_id: int) -> int:
            """γ-even: D→W w/ C. Store data in workspace iff predicate computes to TRUE.

            Operationally:
              - apply predicate to data_id (compute is the witness)
              - if the normalized result is TRUE: store data_id in workspace[workspace_id]
              - if not: return FAILURE without storing

            This is the architectural pattern for precondition-checked storage.
            The compute axis acts as the gatekeeper.
            """
            # Compute validates: predicate(data_id) reduce to TRUE?
            check_expr = self.cons(predicate_id, data_id)
            result = self.normalize(check_expr)
            if result == self.TRUE:
                self._workspace[workspace_id] = ('validated', data_id)
                self._history.append((
                    'validated_store',
                    (data_id, workspace_id, predicate_id),
                    data_id,
                ))
                return data_id
            self._history.append((
                'validated_store_rejected',
                (data_id, workspace_id, predicate_id),
                self.FAILURE,
            ))
            return self.FAILURE

        self.validated_store = validated_store

    # ========================================================
    # Register operations under the meta-protocol
    # ========================================================

    def _register_operations(self) -> None:
        # α-even: apply / reduce (D→C w/ S)
        self.registry.register(WitnessedOp(
            name='apply',
            source='D', sink='C', witness='S',
            fn=self.apply,
            description='single-step reduction; state witnesses the transformation',
        ))

        # α-odd: memoized apply / workspace-witnessed reduction (D→C w/ W)
        self.registry.register(WitnessedOp(
            name='workspace_witness',
            source='D', sink='C', witness='W',
            fn=self.workspace_witness,
            description='reduction validated by workspace-held witness value',
        ))

        # β-odd: compute-validated state change (D→S w/ C) — M11 interp
        # interp takes (table, term); wrap for meta-protocol uniformity
        self.registry.register(WitnessedOp(
            name='interp',
            source='D', sink='S', witness='C',
            fn=lambda term: self.interp(self.default_table, term),
            description='M11: data drives state change; compute validates each rule',
        ))

        # β-even: workspace-receipted state change (D→S w/ W) — NEW
        self.registry.register(WitnessedOp(
            name='evolve_with_receipt',
            source='D', sink='S', witness='W',
            fn=self.evolve_with_receipt,
            description='state change witnessed by workspace receipt',
        ))

        # γ-even: compute-validated store (D→W w/ C) — NEW
        self.registry.register(WitnessedOp(
            name='validated_store',
            source='D', sink='W', witness='C',
            fn=self.validated_store,
            description='store iff compute predicate holds',
        ))

        # γ-odd: logged store (D→W w/ S)
        self.registry.register(WitnessedOp(
            name='store',
            source='D', sink='W', witness='S',
            fn=self.store,
            description='write data to workspace; state log witnesses',
        ))

    # ========================================================
    # Introspection helpers for the meta-protocol
    # ========================================================

    def coverage_report(self) -> dict:
        """Report which of 6 V_4-orbits are populated."""
        return self.registry.coverage_report()

    def show_pattern_coverage(self) -> None:
        """Print a coverage table for the 6 fundamental patterns."""
        report = self.coverage_report()
        print(f"  {'pairing':<8} {'chirality':<10} {'pattern':<40} {'count':<6}")
        print(f"  {'-'*8} {'-'*10} {'-'*40} {'-'*6}")
        for pairing in ('α', 'β', 'γ'):
            for chirality in ('even', 'odd'):
                count = report[(pairing, chirality)]
                name = PATTERN_NAMES[(pairing, chirality)]
                marker = '✓' if count > 0 else '·'
                print(f"  {pairing:<8} {chirality:<10} {name:<40} [{marker}] {count}")


def demo():
    print("=" * 78)
    print("  chart_meta — meta-protocol + 2 missing fundamental patterns")
    print("=" * 78)
    print()

    c = ChartWithMeta()

    print(f"  Operations registered: {len(c.registry)}")
    print()
    print("  Each operation's derived structure:")
    print(f"  {'name':<22} {'sig (s,t,w)':<15} {'pairing':<8} {'chirality':<10}")
    print(f"  {'-'*22} {'-'*15} {'-'*8} {'-'*10}")
    for op in c.registry.all():
        sig_str = f"{op.source},{op.sink},{op.witness}"
        print(f"  {op.name:<22} {sig_str:<15} {op.pairing:<8} {op.chirality:<10}")

    # =====================
    # Test that the 2 new patterns actually run
    # =====================
    print()
    print("=" * 78)
    print("  Running the 2 new fundamental patterns")
    print("=" * 78)

    # β-even: workspace-receipted state change
    print(f"\n  β-even: evolve_with_receipt (D→S w/ W)")
    w0 = c.workspace_alloc()
    result = c.evolve_with_receipt(c.TRUE, w0)
    print(f"    evolve_with_receipt(TRUE, w0) → {c.show(result)}")
    print(f"    workspace[w0] = {c._workspace[w0]}")
    print(f"    history grew (last entry): {c._history[-1]}")

    # γ-even: compute-validated store
    print(f"\n  γ-even: validated_store (D→W w/ C)")
    w1 = c.workspace_alloc()
    # I is identity: I(TRUE) = TRUE, so the validation passes
    result = c.validated_store(c.TRUE, w1, c.I)
    print(f"    validated_store(TRUE, w1, I)")
    print(f"    [predicate I(TRUE) reduces to TRUE — validation passes]")
    print(f"    result: {c.show(result)}")
    print(f"    workspace[w1] = {c._workspace[w1]}")

    # And a failing case
    w2 = c.workspace_alloc()
    # K is constant function: K(TRUE)(_) = TRUE, but K(FALSE) doesn't fully reduce as predicate
    # Let's use a predicate that yields FALSE
    # (K FALSE) applied to anything → FALSE. So predicate K FALSE applied to TRUE → FALSE.
    KFalse = c.cons(c.K, c.FALSE)
    result2 = c.validated_store(c.TRUE, w2, KFalse)
    print(f"\n    validated_store(TRUE, w2, K FALSE)")
    print(f"    [predicate (K FALSE)(TRUE) reduces to FALSE — validation fails]")
    print(f"    result: {c.show(result2)}")
    print(f"    workspace[w2] = {c._workspace[w2]} (should be None — not stored)")

    # =====================
    # Coverage of 6 fundamental patterns
    # =====================
    print()
    print("=" * 78)
    print("  6-pattern coverage")
    print("=" * 78)
    print()
    c.show_pattern_coverage()

    report = c.coverage_report()
    populated = sum(1 for v in report.values() if v > 0)
    print()
    print(f"  Populated patterns: {populated} / 6")
    if populated == 6:
        print(f"  ✓✓✓ ALL 6 FUNDAMENTAL PATTERNS POPULATED")

    # =====================
    # Demonstrate the meta-protocol's automatic relations
    # =====================
    print()
    print("=" * 78)
    print("  Automatic relations derived by the meta-protocol")
    print("=" * 78)

    for op in c.registry.all():
        inv_sig = op.invert_signature()
        inv_found = c.registry.at_signature(*inv_sig)
        print(f"\n  {op.name} ({op.source}→{op.sink} w/ {op.witness}, {op.pairing}-{op.chirality})")
        print(f"    inverse signature: {inv_sig[0]}→{inv_sig[1]} w/ {inv_sig[2]}")
        if inv_found:
            inv_names = ', '.join(o.name for o in inv_found)
            print(f"    inverse registered: {inv_names}")
        else:
            print(f"    inverse: not registered (chirality would be opposite)")
        # V_4-twins
        twins = c.registry.find_v4_twins(op)
        for swap_name, twin_list in twins.items():
            twin_names = ', '.join(o.name for o in twin_list)
            print(f"    V_4-twin under {swap_name}: {twin_names}")


if __name__ == "__main__":
    demo()
