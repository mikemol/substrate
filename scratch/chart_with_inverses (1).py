"""
chart_with_inverses.py — extends ChartWithMeta with the 6 inverse operations.

After M34, the 6 fundamental patterns are populated. M35 adds:
  - quote_via_state         (inverse of apply)
  - quote_via_workspace     (inverse of workspace_witness)
  - decode_via_compute      (inverse of interp)
  - restore_from_receipt    (inverse of evolve_with_receipt)
  - validated_load          (inverse of validated_store)
  - load_with_log           (inverse of store)

Each inverse:
  - has the same pair and witness as its partner
  - reverses source ↔ sink (which flips chirality)
  - lives in the OPPOSITE-chirality V_4-orbit relative to its partner

After M35, each V_4-orbit has 2 of 4 cells populated. The remaining 2 cells
per orbit (12 total) are V_4-rotations — implementable mechanically as M36.
"""

from chart_meta import ChartWithMeta
from meta_protocol import WitnessedOp


class ChartWithInverses(ChartWithMeta):
    """ChartWithMeta + the 6 inverse operations."""

    def __init__(self):
        super().__init__()
        self._install_inverses()
        self._register_inverses()

    # ========================================================
    # The 6 inverse operations
    # ========================================================

    def _install_inverses(self) -> None:

        # ----- inverse(apply): C→D w/ S, α-odd -----
        def quote_via_state(compute_id: int) -> int:
            """C→D w/ S: given a compute result, return latest term that reduced to it.

            Reverse-search the memo for a term whose normalized form equals compute_id.
            State witnesses the quotation by appending to history.
            """
            # Reverse memo lookup — find data terms that reduce to compute_id
            matches = [t for t, r in self._apply_memo.items() if r == compute_id]
            if not matches:
                self._history.append(('quote_via_state', (compute_id,), self.FAILURE))
                return self.FAILURE
            result = matches[-1]  # Most recent reduction
            self._history.append(('quote_via_state', (compute_id,), result))
            return result

        self.quote_via_state = quote_via_state

        # ----- inverse(workspace_witness): C→D w/ W, α-even -----
        def quote_via_workspace(compute_id: int, workspace_id: int) -> int:
            """C→D w/ W: given a compute and workspace witness, return data term.

            The workspace slot must contain a witness tuple ('witness', term, compute).
            Returns the term iff it matches the given compute_id.
            """
            entry = self._workspace[workspace_id]
            if entry is None:
                return self.FAILURE
            # Workspace can hold various tags; accept 'witness' or fallback to 'validated'
            if entry[0] == 'witness' and len(entry) >= 3 and entry[2] == compute_id:
                return entry[1]
            # If workspace holds a 'validated' tag, the data is the term
            if entry[0] == 'validated' and len(entry) >= 2:
                # Cross-check: does this data reduce to compute_id?
                if self.normalize(entry[1]) == compute_id:
                    return entry[1]
            return self.FAILURE

        self.quote_via_workspace = quote_via_workspace

        # ----- inverse(interp): S→D w/ C, β-even -----
        def decode_via_compute(history_index: int) -> int:
            """S→D w/ C: given a history index, return the data argument of that transition.

            Compute is the witness: the history entry's structural form (op_name, args, result)
            is a compute-tagged record that we decode to extract the data input.
            """
            if history_index < 0 or history_index >= len(self._history):
                return self.FAILURE
            entry = self._history[history_index]
            # Entry shape: (op_name, args_tuple, result)
            if len(entry) < 2:
                return self.FAILURE
            args = entry[1]
            if not args:
                return self.FAILURE
            return args[0]  # First argument is conventionally the data input

        self.decode_via_compute = decode_via_compute

        # ----- inverse(evolve_with_receipt): S→D w/ W, β-odd -----
        def restore_from_receipt(workspace_id: int) -> int:
            """S→D w/ W: given a workspace slot containing a receipt, return the data referenced.

            The workspace slot should hold ('receipt', data_id, transition_idx).
            We restore the data_id. State is the implicit source (the receipt points
            at a state transition), workspace witnesses.
            """
            entry = self._workspace[workspace_id]
            if entry is None or entry[0] != 'receipt':
                return self.FAILURE
            return entry[1]  # data_id from receipt

        self.restore_from_receipt = restore_from_receipt

        # ----- inverse(validated_store): W→D w/ C, γ-odd -----
        def validated_load(workspace_id: int, predicate_id: int) -> int:
            """W→D w/ C: read workspace; return data iff predicate validates it.

            Workspace is the source (W); data is the sink (D); compute (predicate)
            witnesses. Returns FAILURE if predicate doesn't reduce to TRUE.
            """
            entry = self._workspace[workspace_id]
            if entry is None:
                return self.FAILURE
            # Get the data part of the entry
            if entry[0] in ('validated', 'data'):
                data = entry[1]
            elif entry[0] == 'receipt':
                data = entry[1]
            else:
                return self.FAILURE
            # Validate via compute
            check = self.cons(predicate_id, data)
            if self.normalize(check) == self.TRUE:
                return data
            return self.FAILURE

        self.validated_load = validated_load

        # ----- inverse(store): W→D w/ S, γ-even -----
        def load_with_log(workspace_id: int) -> int:
            """W→D w/ S: read workspace and log the access to state.

            Workspace is source; data is sink; state witnesses (the load event is
            recorded in history).
            """
            entry = self._workspace[workspace_id]
            if entry is None:
                self._history.append(('load_with_log', (workspace_id,), self.FAILURE))
                return self.FAILURE
            # Extract data depending on entry shape
            if isinstance(entry, tuple) and len(entry) >= 2:
                if entry[0] in ('validated', 'data', 'witness', 'receipt'):
                    data = entry[1]
                else:
                    data = entry[0]  # Raw value (legacy store)
            else:
                data = entry
            self._history.append(('load_with_log', (workspace_id,), data))
            return data

        self.load_with_log = load_with_log

    # ========================================================
    # Register the inverses
    # ========================================================

    def _register_inverses(self) -> None:
        self.registry.register(WitnessedOp(
            name='quote_via_state',
            source='C', sink='D', witness='S',
            fn=self.quote_via_state,
            description='inverse of apply: compute → data via state log',
        ))
        self.registry.register(WitnessedOp(
            name='quote_via_workspace',
            source='C', sink='D', witness='W',
            fn=self.quote_via_workspace,
            description='inverse of workspace_witness: compute → data via workspace witness',
        ))
        self.registry.register(WitnessedOp(
            name='decode_via_compute',
            source='S', sink='D', witness='C',
            fn=self.decode_via_compute,
            description='inverse of interp: state → data, compute decodes the transition',
        ))
        self.registry.register(WitnessedOp(
            name='restore_from_receipt',
            source='S', sink='D', witness='W',
            fn=self.restore_from_receipt,
            description='inverse of evolve_with_receipt: state → data via workspace receipt',
        ))
        self.registry.register(WitnessedOp(
            name='validated_load',
            source='W', sink='D', witness='C',
            fn=self.validated_load,
            description='inverse of validated_store: workspace → data iff compute validates',
        ))
        self.registry.register(WitnessedOp(
            name='load_with_log',
            source='W', sink='D', witness='S',
            fn=self.load_with_log,
            description='inverse of store: workspace → data with state log',
        ))


def demo():
    print("=" * 78)
    print("  ChartWithInverses — M35: inverse-pair completion")
    print("=" * 78)
    print()

    c = ChartWithInverses()
    print(f"  Operations registered: {len(c.registry)} (was 6 in M34; +6 inverses)")
    print()
    print(f"  {'name':<24} {'sig':<11} {'orbit':<14}")
    print(f"  {'-'*24} {'-'*11} {'-'*14}")
    for op in c.registry.all():
        sig = f"{op.source}→{op.sink} w/ {op.witness}"
        orbit = f"{op.pairing}-{op.chirality}"
        print(f"  {op.name:<24} {sig:<11} {orbit:<14}")

    # =====================
    # Verify inverse pairs by signature
    # =====================
    print()
    print("=" * 78)
    print("  Verifying inverse pair structure")
    print("=" * 78)
    print()
    print(f"  {'fundamental':<22} {'inverse':<22} {'chirality flip?'}")
    print(f"  {'-'*22} {'-'*22} {'-'*15}")
    inverse_map = {
        'apply': 'quote_via_state',
        'workspace_witness': 'quote_via_workspace',
        'interp': 'decode_via_compute',
        'evolve_with_receipt': 'restore_from_receipt',
        'validated_store': 'validated_load',
        'store': 'load_with_log',
    }
    for fund_name, inv_name in inverse_map.items():
        fund = c.registry.get(fund_name)
        inv = c.registry.get(inv_name)
        # Check signature inverse: inv.source == fund.sink, inv.sink == fund.source, witness same
        sig_ok = (inv.source == fund.sink and
                  inv.sink == fund.source and
                  inv.witness == fund.witness)
        chir_flip = (fund.chirality != inv.chirality)
        marker = '✓' if sig_ok and chir_flip else '✗'
        fund_str = f"{fund.name} ({fund.pairing}-{fund.chirality})"
        inv_str = f"{inv.name} ({inv.pairing}-{inv.chirality})"
        print(f"  {fund_str:<22} {inv_str:<22} {marker}")

    # =====================
    # Each V_4-orbit now has 2 of 4 cells
    # =====================
    print()
    print("=" * 78)
    print("  V_4-orbit population — each orbit now has 2 of 4 cells")
    print("=" * 78)
    print()
    for pairing in ('α', 'β', 'γ'):
        for chirality in ('even', 'odd'):
            ops = c.registry.operations_in_orbit(pairing, chirality)
            names = ', '.join(op.name for op in ops)
            print(f"  {pairing}-{chirality}: {names}")

    # =====================
    # Run each inverse operationally
    # =====================
    print()
    print("=" * 78)
    print("  Running each inverse operation")
    print("=" * 78)

    # Setup: do some forward operations first
    print("\n  Setup: apply I to TRUE; store TRUE; receipt-evolve TRUE; validated-store TRUE")
    forward_result = c.normalize(c.cons(c.I, c.TRUE))   # apply via normalize
    w_store = c.workspace_alloc()
    c.store(w_store, c.TRUE)
    w_evolve = c.workspace_alloc()
    c.evolve_with_receipt(c.TRUE, w_evolve)
    w_validated = c.workspace_alloc()
    c.validated_store(c.TRUE, w_validated, c.I)
    interp_history_idx = len(c._history)
    # Inject a fake "interp" history entry for decode test
    c._history.append(('interp_demo', (c.TRUE,), c.TRUE))

    # 1. quote_via_state
    print(f"\n  1. quote_via_state(TRUE)  (reverse memo lookup for compute_id=TRUE)")
    result = c.quote_via_state(c.TRUE)
    print(f"     result: {c.show(result) if result != c.FAILURE else 'FAILURE'}")

    # 2. quote_via_workspace
    print(f"\n  2. quote_via_workspace(TRUE, w_validated)")
    result = c.quote_via_workspace(c.TRUE, w_validated)
    print(f"     result: {c.show(result) if result != c.FAILURE else 'FAILURE'}")

    # 3. decode_via_compute
    print(f"\n  3. decode_via_compute(interp_history_idx={interp_history_idx})")
    result = c.decode_via_compute(interp_history_idx)
    print(f"     result: {c.show(result)}")

    # 4. restore_from_receipt
    print(f"\n  4. restore_from_receipt(w_evolve)")
    result = c.restore_from_receipt(w_evolve)
    print(f"     result: {c.show(result)}")

    # 5. validated_load
    print(f"\n  5. validated_load(w_validated, I)  (load if I(data)→TRUE)")
    result = c.validated_load(w_validated, c.I)
    print(f"     result: {c.show(result) if result != c.FAILURE else 'FAILURE'}")

    # 6. load_with_log
    print(f"\n  6. load_with_log(w_store)")
    hbefore = len(c._history)
    result = c.load_with_log(w_store)
    print(f"     result: {c.show(result)}")
    print(f"     history grew by {len(c._history) - hbefore} (load logged to state)")


if __name__ == "__main__":
    demo()
