"""
chart_full_v4.py — completes the V_4-extension to all 24 directed witnessed operations (M36).

After M35, each V_4-orbit has 2 of 4 cells populated. M36 adds the remaining 12
V_4-rotations — gauge-equivalent variants playing the same operational role with
axes rotated.

Each new op has a clear (source, sink, witness) signature derived from V_4-rotation
of an existing registered op. The structural form is preserved:
  - read from source axis
  - optionally verify witness invariant
  - write to sink axis
  - return result or FAILURE

After M36: 24 registered ops = full S_4 orbit.
                Each V_4-orbit has 4 of 4 cells populated.
"""

from chart_with_inverses import ChartWithInverses
from meta_protocol import WitnessedOp


class ChartFullV4(ChartWithInverses):
    """ChartWithInverses + the 12 V_4-rotation operations completing the 24-op set."""

    def __init__(self):
        super().__init__()
        self._install_v4_extensions()
        self._register_v4_extensions()

    # ========================================================
    # Helpers for axis-uniform access
    # ========================================================

    def _read_data_arg(self, history_entry):
        """Extract the data argument from a history entry (op_name, args, result)."""
        if not isinstance(history_entry, tuple) or len(history_entry) < 2:
            return None
        args = history_entry[1]
        return args[0] if args else None

    def _read_workspace_value(self, entry):
        """Extract the data value from a workspace entry of any tag."""
        if entry is None:
            return None
        if isinstance(entry, tuple) and len(entry) >= 2:
            if entry[0] in ('validated', 'data', 'witness', 'receipt',
                            'snapshot', 'verified_snapshot', 'compute_result',
                            'compute_verified', 'replay'):
                return entry[1]
            return entry[0]
        return entry

    # ========================================================
    # The 12 V_4-rotation operations
    # ========================================================

    def _install_v4_extensions(self) -> None:

        # ─────────────────────────────────────────────────────────────
        # α-even orbit completing: missing (S,W,D) and (W,S,C)
        # (registered: apply (D,C,S), quote_via_workspace (C,D,W))
        # ─────────────────────────────────────────────────────────────

        def state_to_workspace_via_data(history_index: int, workspace_id: int, data_id: int) -> int:
            """S→W w/ D (α-even): snapshot history entry to workspace, with data invariant.

            V_4-α twin of apply (DC↔CD, SW↔WS swap applied).
            """
            if not (0 <= history_index < len(self._history)):
                return self.FAILURE
            entry = self._history[history_index]
            # Witness: data invariant attached to snapshot
            self._workspace[workspace_id] = ('snapshot', history_index, data_id, entry)
            return data_id
        self.state_to_workspace_via_data = state_to_workspace_via_data

        def workspace_to_state_via_compute(workspace_id: int, predicate_id: int) -> int:
            """W→S w/ C (α-even): promote workspace contents to state, compute validates.

            V_4-γ twin of apply.
            """
            entry = self._workspace[workspace_id]
            if entry is None:
                return self.FAILURE
            data = self._read_workspace_value(entry)
            if data is None:
                return self.FAILURE
            check = self.cons(predicate_id, data)
            if self.normalize(check) == self.TRUE:
                self._history.append(('promote_via_compute', (workspace_id, predicate_id), data))
                return data
            return self.FAILURE
        self.workspace_to_state_via_compute = workspace_to_state_via_compute

        # ─────────────────────────────────────────────────────────────
        # α-odd orbit completing: missing (S,W,C) and (W,S,D)
        # (registered: workspace_witness (D,C,W), quote_via_state (C,D,S))
        # ─────────────────────────────────────────────────────────────

        def state_to_workspace_via_compute(history_index: int, workspace_id: int, predicate_id: int) -> int:
            """S→W w/ C (α-odd): snapshot history to workspace iff compute validates."""
            if not (0 <= history_index < len(self._history)):
                return self.FAILURE
            entry = self._history[history_index]
            data = self._read_data_arg(entry)
            if data is None:
                return self.FAILURE
            check = self.cons(predicate_id, data)
            if self.normalize(check) == self.TRUE:
                self._workspace[workspace_id] = ('verified_snapshot', history_index, data)
                return data
            return self.FAILURE
        self.state_to_workspace_via_compute = state_to_workspace_via_compute

        def workspace_to_state_via_data(workspace_id: int, data_id: int) -> int:
            """W→S w/ D (α-odd): promote workspace to state iff matches data invariant."""
            entry = self._workspace[workspace_id]
            if entry is None:
                return self.FAILURE
            data = self._read_workspace_value(entry)
            if data == data_id:
                self._history.append(('promote_via_invariant', (workspace_id, data_id), data))
                return data
            return self.FAILURE
        self.workspace_to_state_via_data = workspace_to_state_via_data

        # ─────────────────────────────────────────────────────────────
        # β-even orbit completing: missing (C,W,S) and (W,C,D)
        # (registered: evolve_with_receipt (D,S,W), decode_via_compute (S,D,C))
        # ─────────────────────────────────────────────────────────────

        def compute_to_workspace_via_state(compute_id: int, workspace_id: int) -> int:
            """C→W w/ S (β-even): deposit compute result into workspace, log to state."""
            self._workspace[workspace_id] = ('compute_result', compute_id)
            self._history.append(('deposit_compute', (compute_id, workspace_id), compute_id))
            return compute_id
        self.compute_to_workspace_via_state = compute_to_workspace_via_state

        def workspace_to_compute_via_data(workspace_id: int, data_id: int) -> int:
            """W→C w/ D (β-even): activate compute on workspace content, data invariant witnesses."""
            entry = self._workspace[workspace_id]
            if entry is None:
                return self.FAILURE
            content = self._read_workspace_value(entry)
            if content is None:
                return self.FAILURE
            # Apply data_id as a function to workspace content via compute
            result = self.normalize(self.cons(data_id, content))
            return result
        self.workspace_to_compute_via_data = workspace_to_compute_via_data

        # ─────────────────────────────────────────────────────────────
        # β-odd orbit completing: missing (C,W,D) and (W,C,S)
        # (registered: interp (D,S,C), restore_from_receipt (S,D,W))
        # ─────────────────────────────────────────────────────────────

        def compute_to_workspace_via_data(compute_id: int, workspace_id: int, data_id: int) -> int:
            """C→W w/ D (β-odd): deposit compute result iff data invariant holds."""
            check = self.cons(data_id, compute_id)
            if self.normalize(check) == self.TRUE:
                self._workspace[workspace_id] = ('compute_verified', compute_id, data_id)
                return compute_id
            return self.FAILURE
        self.compute_to_workspace_via_data = compute_to_workspace_via_data

        def workspace_to_compute_via_state(workspace_id: int) -> int:
            """W→C w/ S (β-odd): activate compute on workspace content; state logs the firing."""
            entry = self._workspace[workspace_id]
            if entry is None:
                return self.FAILURE
            content = self._read_workspace_value(entry)
            if content is None:
                return self.FAILURE
            result = self.normalize(content)
            self._history.append(('fire_compute', (workspace_id,), result))
            return result
        self.workspace_to_compute_via_state = workspace_to_compute_via_state

        # ─────────────────────────────────────────────────────────────
        # γ-even orbit completing: missing (C,S,D) and (S,C,W)
        # (registered: validated_store (D,W,C), load_with_log (W,D,S))
        # ─────────────────────────────────────────────────────────────

        def compute_to_state_via_data(compute_id: int, data_id: int) -> int:
            """C→S w/ D (γ-even): log compute result to state iff data invariant holds."""
            check = self.cons(data_id, compute_id)
            if self.normalize(check) == self.TRUE:
                self._history.append(('compute_state', (compute_id, data_id), compute_id))
                return compute_id
            return self.FAILURE
        self.compute_to_state_via_data = compute_to_state_via_data

        def state_to_compute_via_workspace(history_index: int, workspace_id: int) -> int:
            """S→C w/ W (γ-even): replay history entry through compute; workspace stages."""
            if not (0 <= history_index < len(self._history)):
                return self.FAILURE
            entry = self._history[history_index]
            data = self._read_data_arg(entry)
            if data is None:
                return self.FAILURE
            result = self.normalize(data)
            self._workspace[workspace_id] = ('replay', history_index, result)
            return result
        self.state_to_compute_via_workspace = state_to_compute_via_workspace

        # ─────────────────────────────────────────────────────────────
        # γ-odd orbit completing: missing (C,S,W) and (S,C,D)
        # (registered: store (D,W,S), validated_load (W,D,C))
        # ─────────────────────────────────────────────────────────────

        def compute_to_state_via_workspace(compute_id: int, workspace_id: int) -> int:
            """C→S w/ W (γ-odd): log compute result to state, workspace witnesses."""
            ws_tag = self._workspace[workspace_id]
            self._history.append(('compute_state_ws', (compute_id, workspace_id), compute_id))
            return compute_id
        self.compute_to_state_via_workspace = compute_to_state_via_workspace

        def state_to_compute_via_data(history_index: int, data_id: int) -> int:
            """S→C w/ D (γ-odd): replay history into compute; data invariant witnesses."""
            if not (0 <= history_index < len(self._history)):
                return self.FAILURE
            entry = self._history[history_index]
            result_in_entry = entry[2] if len(entry) >= 3 else None
            # Witness: data invariant either matches the entry result, or governs the replay
            if result_in_entry == data_id:
                return result_in_entry
            data_arg = self._read_data_arg(entry)
            if data_arg is None:
                return self.FAILURE
            return self.normalize(self.cons(data_id, data_arg))
        self.state_to_compute_via_data = state_to_compute_via_data

    # ========================================================
    # Register all 12 V_4-extensions
    # ========================================================

    def _register_v4_extensions(self) -> None:
        regs = [
            # α-even
            ('state_to_workspace_via_data', 'S', 'W', 'D',
             'α-even V_4-twin of apply: snapshot history to workspace'),
            ('workspace_to_state_via_compute', 'W', 'S', 'C',
             'α-even V_4-twin: promote workspace to state via compute'),
            # α-odd
            ('state_to_workspace_via_compute', 'S', 'W', 'C',
             'α-odd V_4-twin of workspace_witness: snapshot iff compute validates'),
            ('workspace_to_state_via_data', 'W', 'S', 'D',
             'α-odd V_4-twin: promote workspace to state iff data invariant'),
            # β-even
            ('compute_to_workspace_via_state', 'C', 'W', 'S',
             'β-even V_4-twin of evolve_with_receipt: deposit compute to workspace'),
            ('workspace_to_compute_via_data', 'W', 'C', 'D',
             'β-even V_4-twin: activate compute on workspace via data invariant'),
            # β-odd
            ('compute_to_workspace_via_data', 'C', 'W', 'D',
             'β-odd V_4-twin of interp: deposit compute iff data invariant'),
            ('workspace_to_compute_via_state', 'W', 'C', 'S',
             'β-odd V_4-twin: fire compute on workspace with state log'),
            # γ-even
            ('compute_to_state_via_data', 'C', 'S', 'D',
             'γ-even V_4-twin of validated_store: log compute via data invariant'),
            ('state_to_compute_via_workspace', 'S', 'C', 'W',
             'γ-even V_4-twin: replay history through compute with workspace staging'),
            # γ-odd
            ('compute_to_state_via_workspace', 'C', 'S', 'W',
             'γ-odd V_4-twin of store: log compute with workspace witness'),
            ('state_to_compute_via_data', 'S', 'C', 'D',
             'γ-odd V_4-twin of validated_load: replay history with data invariant'),
        ]
        for name, s, t, w, desc in regs:
            self.registry.register(WitnessedOp(
                name=name,
                source=s, sink=t, witness=w,
                fn=getattr(self, name),
                description=desc,
            ))


def demo():
    print("=" * 78)
    print("  ChartFullV4 — M36: V_4-extension to 24 ops (complete S_4 orbit)")
    print("=" * 78)
    print()

    c = ChartFullV4()
    print(f"  Operations registered: {len(c.registry)} (was 12 in M35; +12 V_4-rotations)")
    print(f"  Expected: 24 = |S_4|")
    print()

    # Show full orbit population
    print("=" * 78)
    print("  V_4-orbit population — each orbit now has 4 of 4 cells")
    print("=" * 78)
    print()
    print(f"  {'pairing':<8} {'chirality':<10} {'count':<6}  {'operations':<60}")
    print(f"  {'-'*8} {'-'*10} {'-'*6}  {'-'*60}")
    for pairing in ('α', 'β', 'γ'):
        for chir in ('even', 'odd'):
            ops = c.registry.operations_in_orbit(pairing, chir)
            count = len(ops)
            names = ', '.join(op.name for op in ops)
            marker = '✓' if count == 4 else '✗'
            print(f"  {pairing:<8} {chir:<10} [{marker}] {count}    {names[:60]}")

    # =====================
    # Verify V_4-twins are now structurally present
    # =====================
    print()
    print("=" * 78)
    print("  V_4-twin discovery — each op now has 3 registered V_4-twins")
    print("=" * 78)

    all_have_3_twins = True
    for op in c.registry.all():
        twins = c.registry.find_v4_twins(op)
        twin_count = sum(len(v) for v in twins.values())
        if twin_count != 3:
            all_have_3_twins = False
            print(f"  ✗ {op.name}: found {twin_count} V_4-twins (expected 3)")

    if all_have_3_twins:
        print(f"\n  ✓ All 24 ops have exactly 3 V_4-twins each (V_4-orbits fully closed).")

    # =====================
    # Run a sample of V_4-rotation ops
    # =====================
    print()
    print("=" * 78)
    print("  Running a sample of V_4-rotation operations")
    print("=" * 78)

    # Setup
    w_data = c.workspace_alloc()
    c.store(w_data, c.TRUE)

    # Sample tests
    samples = [
        ('compute_to_workspace_via_state', lambda: c.compute_to_workspace_via_state(c.TRUE, c.workspace_alloc())),
        ('workspace_to_state_via_data', lambda: c.workspace_to_state_via_data(w_data, c.TRUE)),
        ('compute_to_state_via_data', lambda: c.compute_to_state_via_data(c.TRUE, c.I)),
        ('state_to_compute_via_data', lambda: c.state_to_compute_via_data(0, c.I)),
    ]
    for name, fn in samples:
        result = fn()
        status = c.show(result) if result != c.FAILURE else 'FAILURE'
        print(f"  {name:<40} → {status}")


if __name__ == "__main__":
    demo()
