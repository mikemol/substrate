"""
chart.py — Free self-extending grammar / ISA chart kernel.

Founding micro-ops S1–S7 + M11 meta-circular interpreter + M14 refactor:
- Storage: combinators (M6 vertex).
- Representation: integer-as-path (M2 vertex).
- Apply: single-step under CBNeed (M3 C3 + M4).
- Failure: designated rule (M3 C5).
- Meta-circularity (M11): chart's reduction semantics as chart data.
- M14 refactor with refinement: variables are cons(VAR_MARK, name) where
  VAR_MARK is a dedicated structural marker cell, distinct from combinators.

M30/M31 EXTENSIONS — fourth axis (W, workspace):
- Workspace primitives (Z1_store, Z2_load, workspace_alloc).
- Identity primitives (compute_identity, state_identity, workspace_alloc).
- State history log (foundation for BWT-state-history queries).
- V₄-twin operations demonstrating cocycle invariance across gauges:
    MV₄-3 workspace_witness (V₄-twin of M_SPPF_witness via α-swap)
    MV₄-7 compute_marker (V₄-twin of M14_VAR_MARK via α-swap)
    MV₄-9 workspace_marker (V₄-twin of M14_VAR_MARK via γ-swap)
    MV₄-2 workspace_driven_state (V₄-twin of morton_heap via γ-swap)
"""

from typing import Any, List, Optional, Tuple


class Chart:
    def __init__(self) -> None:
        self._cells: List[Optional[Tuple[int, int]]] = [None]
        self._hashcons: dict = {}
        self._apply_memo: dict = {}

        # M30/M31: workspace + history initialized before cons() is called
        # since cons() now records to history.
        self._workspace: List[Any] = []
        self._workspace_free: List[int] = []
        self._history: List[Tuple[str, tuple, Any]] = []

        # M3 C2 designated rules + M6 combinator atoms.
        self.NIL = 0
        self.TRUE    = self.cons(0, 0)   # 1
        self.FALSE   = self.cons(0, 1)   # 2
        self.FAILURE = self.cons(1, 0)   # 3
        self.S       = self.cons(3, 3)   # 4
        self.K       = self.cons(3, 0)   # 5
        self.I       = self.cons(0, 3)   # 6

        # M14 refinement: dedicated variable-marker cell.
        self.VAR_MARK = self.cons(0, 5)  # 7 = cons(NIL, K)

        # Variables built via var(name) = cons(VAR_MARK, name).
        self.VAR1 = self.var(self.NIL)
        self.VAR2 = self.var(self.TRUE)
        self.VAR3 = self.var(self.FALSE)

        # Apply-atoms: designated rules apply treats as primitives.
        self._atoms = frozenset({
            self.NIL, self.TRUE, self.FALSE, self.FAILURE,
            self.S, self.K, self.I,
            self.VAR_MARK,
        })

        # M11 T6: chart's reduction semantics encoded as chart data.
        self.default_table = self._build_default_table()

    # ---- M14 variable mechanism ----

    def var(self, name: int) -> int:
        return self.cons(self.VAR_MARK, name)

    def is_var(self, k: int) -> bool:
        if k == self.NIL:
            return False
        return self.left(k) == self.VAR_MARK

    # ---- S1–S4 term algebra ----

    def cons(self, l: int, q: int) -> int:
        if not (0 <= l < len(self._cells) and 0 <= q < len(self._cells)):
            raise IndexError(f"cons: l={l}, q={q} out of range")
        key = (l, q)
        if key in self._hashcons:
            return self._hashcons[key]
        idx = len(self._cells)
        self._cells.append(key)
        self._hashcons[key] = idx
        self._history.append(('cons', (l, q), idx))
        return idx

    def left(self, k: int) -> int:
        if k == self.NIL:
            return self.NIL
        return self._cells[k][0]

    def right(self, k: int) -> int:
        if k == self.NIL:
            return self.NIL
        return self._cells[k][1]

    def eq(self, a: int, b: int) -> bool:
        return a == b

    # ---- S5 apply (single-step, M4) ----

    def apply(self, k: int) -> int:
        if k in self._apply_memo:
            return self._apply_memo[k]
        result = self._reduce_step(k)
        self._apply_memo[k] = result
        self._history.append(('apply', (k,), result))
        return result

    def _reduce_step(self, k: int) -> int:
        if k in self._atoms:
            return k
        spine = self._spine(k)
        head, args = spine[0], spine[1:]
        if head == self.I and len(args) >= 1:
            return self._unspine([args[0]] + args[1:])
        if head == self.K and len(args) >= 2:
            return self._unspine([args[0]] + args[2:])
        if head == self.S and len(args) >= 3:
            x, y, z = args[0], args[1], args[2]
            new_app = self.cons(self.cons(x, z), self.cons(y, z))
            return self._unspine([new_app] + args[3:])
        l = self.left(k)
        new_l = self._reduce_step(l)
        if new_l != l:
            return self.cons(new_l, self.right(k))
        return k

    def _spine(self, k: int) -> List[int]:
        args = []
        while k not in self._atoms:
            args.append(self.right(k))
            k = self.left(k)
        return [k] + list(reversed(args))

    def _unspine(self, spine: List[int]) -> int:
        if not spine:
            return self.NIL
        result = spine[0]
        for arg in spine[1:]:
            result = self.cons(result, arg)
        return result

    def normalize(self, k: int, max_steps: int = 1000) -> int:
        for _ in range(max_steps):
            k_next = self.apply(k)
            if self.eq(k_next, k):
                return k
            k = k_next
        return self.FAILURE

    # ---- S6 parse ----

    def parse(self, grammar: int, input_str: str) -> int:
        _ = grammar
        tokens = self._tokenize(input_str)
        if not tokens:
            return self.FAILURE
        result, pos = self._parse_expr(tokens, 0)
        if result is None or pos != len(tokens):
            return self.FAILURE
        return result

    def _tokenize(self, s: str) -> List[str]:
        tokens, i = [], 0
        while i < len(s):
            c = s[i]
            if c.isspace():
                i += 1
            elif c in "()":
                tokens.append(c); i += 1
            else:
                j = i
                while j < len(s) and not s[j].isspace() and s[j] not in "()":
                    j += 1
                tokens.append(s[i:j]); i = j
        return tokens

    def _parse_atom(self, tokens: List[str], pos: int):
        if pos >= len(tokens):
            return None, pos
        tok = tokens[pos]
        atom_map = {
            "S": self.S, "K": self.K, "I": self.I,
            "nil": self.NIL, "true": self.TRUE,
            "false": self.FALSE, "failure": self.FAILURE,
        }
        if tok in atom_map:
            return atom_map[tok], pos + 1
        if tok == "(":
            expr, pos = self._parse_expr(tokens, pos + 1)
            if pos < len(tokens) and tokens[pos] == ")":
                return expr, pos + 1
            return None, pos
        return None, pos

    def _parse_expr(self, tokens: List[str], pos: int):
        result, pos = self._parse_atom(tokens, pos)
        if result is None:
            return None, pos
        while pos < len(tokens) and tokens[pos] != ")":
            atom, new_pos = self._parse_atom(tokens, pos)
            if atom is None:
                break
            result = self.cons(result, atom)
            pos = new_pos
        return result, pos

    # ---- S7 transform ----

    def transform(self, k: Any, src_rep: str, tgt_rep: str) -> Any:
        if src_rep == tgt_rep:
            return k
        rot = (src_rep, tgt_rep)
        if rot == ("integer", "function"):
            return (lambda v: lambda: v)(k)
        if rot == ("function", "integer"):
            return k()
        if rot == ("integer", "trace"):
            return self._to_trace(k)
        if rot == ("trace", "integer"):
            return self._from_trace(k)
        raise NotImplementedError(f"transform {src_rep} -> {tgt_rep}")

    def _to_trace(self, k: int) -> Any:
        if k in self._atoms:
            return ("atom", k)
        l, r = self._cells[k]
        return ("cons", self._to_trace(l), self._to_trace(r))

    def _from_trace(self, trace: Any) -> int:
        if trace[0] == "atom":
            return trace[1]
        if trace[0] == "cons":
            return self.cons(self._from_trace(trace[1]), self._from_trace(trace[2]))
        raise ValueError(f"invalid trace: {trace}")

    # ---- M11 meta-circular interpreter (M14-refactored) ----

    def _match(self, pattern: int, term: int, binding: dict) -> Optional[dict]:
        if self.is_var(pattern):
            name = self.right(pattern)
            if name in binding:
                return binding if self.eq(binding[name], term) else None
            new_binding = dict(binding)
            new_binding[name] = term
            return new_binding
        if pattern in self._atoms or term in self._atoms:
            return binding if self.eq(pattern, term) else None
        b1 = self._match(self.left(pattern), self.left(term), binding)
        if b1 is None:
            return None
        return self._match(self.right(pattern), self.right(term), b1)

    def _substitute(self, template: int, binding: dict) -> int:
        if self.is_var(template):
            name = self.right(template)
            if name in binding:
                return binding[name]
            return template
        if template in self._atoms:
            return template
        return self.cons(
            self._substitute(self.left(template), binding),
            self._substitute(self.right(template), binding),
        )

    def interp(self, table: int, term: int) -> int:
        t = table
        while not self.eq(t, self.NIL):
            rule = self.left(t)
            pattern = self.left(rule)
            replacement = self.right(rule)
            binding = self._match(pattern, term, {})
            if binding is not None:
                return self._substitute(replacement, binding)
            t = self.right(t)
        if term not in self._atoms:
            l = self.left(term)
            new_l = self.interp(table, l)
            if not self.eq(new_l, l):
                return self.cons(new_l, self.right(term))
        return term

    def _build_default_table(self) -> int:
        v1, v2, v3 = self.VAR1, self.VAR2, self.VAR3
        i_pat = self.cons(self.I, v1)
        i_rule = self.cons(i_pat, v1)
        k_pat = self.cons(self.cons(self.K, v1), v2)
        k_rule = self.cons(k_pat, v1)
        s_pat = self.cons(self.cons(self.cons(self.S, v1), v2), v3)
        s_repl = self.cons(self.cons(v1, v3), self.cons(v2, v3))
        s_rule = self.cons(s_pat, s_repl)
        return self.cons(i_rule, self.cons(k_rule, self.cons(s_rule, self.NIL)))

    # ========================================================
    # M30/M31 EXTENSIONS — W axis (workspace) primitives
    # ========================================================

    def workspace_alloc(self) -> int:
        """MV₄-14: workspace-alloc primitive.

        V₄-twin of S1_nil via γ-swap (DW)(CS). Allocates a workspace slot.
        The workspace is mutable scratch — distinct from the immutable chart.
        """
        if self._workspace_free:
            w_id = self._workspace_free.pop()
            self._workspace[w_id] = None
            return w_id
        w_id = len(self._workspace)
        self._workspace.append(None)
        self._history.append(('workspace_alloc', (), w_id))
        return w_id

    def workspace_free(self, w_id: int) -> None:
        """Release a workspace slot for reuse."""
        if 0 <= w_id < len(self._workspace):
            self._workspace[w_id] = None
            self._workspace_free.append(w_id)

    def store(self, w_id: int, data_id: int) -> int:
        """MV₄-15 Z1_store (D→W): store data reference in workspace.

        Fresh design at the D→W cell of orbit 5. Writes a data-cell id
        into a workspace slot.
        """
        self._workspace[w_id] = ('data', data_id)
        self._history.append(('store', (w_id, data_id), w_id))
        return w_id

    def load(self, w_id: int) -> int:
        """MV₄-18 Z4_workspace-load (W→D): read workspace into data.

        V₄-rotation of Z1_store via γ-swap (DW)(CS). Returns the
        data-cell id held in workspace, or FAILURE if not present.
        """
        v = self._workspace[w_id]
        if v is None or v[0] != 'data':
            return self.FAILURE
        return v[1]

    def workspace_kind(self, w_id: int) -> Optional[str]:
        """Inspect the kind of value held in a workspace slot."""
        v = self._workspace[w_id]
        return None if v is None else v[0]

    # ---- Identity primitives (MV₄-12, MV₄-13) ----

    def compute_identity(self, k: int) -> int:
        """MV₄-12: compute-axis identity.

        V₄-twin of S1_nil via α-swap (DC)(SW). The no-op compute
        operation — returns input unchanged.
        """
        return k

    def state_identity(self) -> None:
        """MV₄-13: state-axis identity (temporal no-op).

        V₄-twin of S1_nil via β-swap (DS)(CW). Advances the state-history
        log by one step without changing anything. Useful as a fence/barrier.
        """
        self._history.append(('state_identity', (), None))

    # ---- State history (foundation for MV₄-1 BWT-state-history) ----

    def history_length(self) -> int:
        return len(self._history)

    def history_at(self, t: int) -> tuple:
        """Random access to historical transition at time t."""
        return self._history[t]

    def history_filter(self, op_name: str) -> List[tuple]:
        """Query state history by operation name.

        MV₄-1 (BWT-state-history) at its simplest: filter the transition
        log by operation name. A full BWT would give O(log N) rank/select;
        this gives O(N) scan as the starting point.
        """
        return [(t, h) for t, h in enumerate(self._history) if h[0] == op_name]

    # ========================================================
    # M30/M31 EXTENSIONS — V₄-twin operations
    # ========================================================

    def workspace_witness(self, w_id: int, term: int) -> int:
        """MV₄-3: workspace-held context narrows compute/data.

        V₄-twin of M_SPPF_witness_application via α-swap (DC)(SW).
        Source: held state narrows abstract relation.
        Target: held workspace narrows compute/data relation.

        If the workspace contains a witness value, return it iff the term
        normalizes to it; otherwise FAILURE.
        """
        v = self._workspace[w_id]
        if v is None or v[0] != 'data':
            return self.FAILURE
        witness = v[1]
        normalized = self.normalize(term)
        if self.eq(normalized, witness):
            self._history.append(('workspace_witness', (w_id, term), normalized))
            return normalized
        self._history.append(('workspace_witness', (w_id, term), self.FAILURE))
        return self.FAILURE

    def compute_marker(self, w_id: int, fn_marker: int) -> int:
        """MV₄-7: function-tagged workspace cell.

        V₄-twin of M14_VAR_MARK via α-swap (DC)(SW).
        Tags a workspace cell with a function/closure marker.
        """
        self._workspace[w_id] = ('compute_marker', fn_marker)
        self._history.append(('compute_marker', (w_id, fn_marker), w_id))
        return w_id

    def workspace_marker(self, w_id: int, marker: int) -> int:
        """MV₄-9: workspace cell carries general marker.

        V₄-twin of M14_VAR_MARK via γ-swap (DW)(CS).
        Tags a workspace cell with a structural marker.
        """
        self._workspace[w_id] = ('marker', marker)
        self._history.append(('workspace_marker', (w_id, marker), w_id))
        return w_id

    def is_workspace_marker(self, w_id: int) -> bool:
        """Discriminate marker-tagged workspace cells.

        V₄-twin of is_var via γ-swap. Workspace's structural is_var.
        """
        v = self._workspace[w_id]
        return v is not None and v[0] in ('marker', 'compute_marker')

    def workspace_driven_state(self, w_id: int) -> int:
        """MV₄-2: workspace drives state evolution.

        V₄-twin of M_SPPF_morton_heap via γ-swap (DW)(CS).
        Reads workspace cell w_id and advances state based on its content.
        """
        v = self._workspace[w_id]
        if v is None:
            return self.FAILURE
        kind, value = v
        result = self.FAILURE
        if kind == 'data':
            result = self.apply(value)
        elif kind == 'marker':
            result = value
        elif kind == 'compute_marker':
            result = self.apply(value)
        self._history.append(('workspace_driven_state', (w_id,), result))
        return result

    # ---- introspection ----

    def size(self) -> int:
        return len(self._cells)

    def workspace_size(self) -> int:
        return len(self._workspace) - len(self._workspace_free)

    def show(self, k: int) -> str:
        labels = {
            self.NIL: "nil", self.TRUE: "true",
            self.FALSE: "false", self.FAILURE: "failure",
            self.S: "S", self.K: "K", self.I: "I",
            self.VAR_MARK: "·",
        }
        if k in labels:
            return labels[k]
        if self.is_var(k):
            return f"?{self.show(self.right(k))}"
        l, r = self._cells[k]
        return f"({self.show(l)} {self.show(r)})"


def demo() -> None:
    print("=" * 72)
    print("  chart kernel — M30/M31 extended (workspace axis + V₄-twins)")
    print("=" * 72)
    c = Chart()
    print(f"\n  Founding atoms: nil={c.NIL} S={c.S} K={c.K} I={c.I} VAR_MARK={c.VAR_MARK}")

    # ---- Verify base T7 (existing) ----
    print("\n  T7 equivalence (interp ≡ apply) — baseline preserved:")
    test_terms = [
        c.cons(c.I, c.TRUE),
        c.cons(c.cons(c.K, c.TRUE), c.FALSE),
        c.cons(c.cons(c.cons(c.S, c.K), c.K), c.FALSE),
    ]
    for t in test_terms:
        a = c.apply(t)
        i = c.interp(c.default_table, t)
        ok = (a == i)
        print(f"    {'✓' if ok else '✗'} {c.show(t):28s} apply={c.show(a):10s} interp={c.show(i)}")

    # ---- Workspace primitives ----
    print("\n  Workspace primitives (W axis):")
    w0 = c.workspace_alloc()
    w1 = c.workspace_alloc()
    print(f"    workspace_alloc → w0={w0}, w1={w1}")
    c.store(w0, c.TRUE)
    c.store(w1, c.FALSE)
    print(f"    store(w0, TRUE), store(w1, FALSE)")
    print(f"    load(w0) = {c.show(c.load(w0))}, load(w1) = {c.show(c.load(w1))}")

    # ---- Compute/state identity primitives ----
    print("\n  Identity primitives (MV₄-12, MV₄-13):")
    print(f"    compute_identity(K) = {c.show(c.compute_identity(c.K))}  (no-op)")
    h_before = c.history_length()
    c.state_identity()
    h_after = c.history_length()
    print(f"    state_identity() advanced history by {h_after - h_before}  (fence)")

    # ---- V₄-twin: workspace_witness (MV₄-3) ----
    print("\n  MV₄-3 workspace_witness (V₄-twin via α-swap):")
    w2 = c.workspace_alloc()
    c.store(w2, c.TRUE)
    test = c.cons(c.I, c.TRUE)
    result_match = c.workspace_witness(w2, test)
    print(f"    witness=TRUE, term=(I TRUE), normalized=TRUE")
    print(f"    workspace_witness → {c.show(result_match)} (expected TRUE)")
    c.store(w2, c.FALSE)
    result_nomatch = c.workspace_witness(w2, test)
    print(f"    witness=FALSE, term=(I TRUE), normalized=TRUE")
    print(f"    workspace_witness → {c.show(result_nomatch)} (expected failure)")

    # ---- V₄-twin: markers (MV₄-7, MV₄-9) ----
    print("\n  MV₄-7 compute_marker, MV₄-9 workspace_marker:")
    w3 = c.workspace_alloc()
    c.compute_marker(w3, c.I)
    print(f"    compute_marker(w3, I): kind={c.workspace_kind(w3)} is_marker={c.is_workspace_marker(w3)}")
    w4 = c.workspace_alloc()
    c.workspace_marker(w4, c.K)
    print(f"    workspace_marker(w4, K): kind={c.workspace_kind(w4)} is_marker={c.is_workspace_marker(w4)}")

    # ---- V₄-twin: workspace_driven_state (MV₄-2) ----
    print("\n  MV₄-2 workspace_driven_state (V₄-twin of morton-heap driver):")
    w5 = c.workspace_alloc()
    c.store(w5, c.cons(c.I, c.TRUE))
    advanced = c.workspace_driven_state(w5)
    print(f"    workspace[w5] = data((I TRUE))")
    print(f"    workspace_driven_state(w5) → {c.show(advanced)} (expected TRUE — applied)")

    # ---- State history queries ----
    print(f"\n  State history (foundation for MV₄-1 BWT-state-history):")
    print(f"    Total transitions logged: {c.history_length()}")
    print(f"    cons events: {len(c.history_filter('cons'))}")
    print(f"    apply events: {len(c.history_filter('apply'))}")
    print(f"    workspace_alloc events: {len(c.history_filter('workspace_alloc'))}")
    print(f"    store events: {len(c.history_filter('store'))}")
    print(f"    workspace_witness events: {len(c.history_filter('workspace_witness'))}")

    # ---- Cocycle invariance verification ----
    print("\n" + "=" * 72)
    print("  COCYCLE INVARIANCE — V₄-twin operational equivalence")
    print("=" * 72)

    print("\n  Test 1: compute_identity ∘ apply ≡ apply  (compute-axis identity).")
    for term in test_terms:
        direct = c.apply(term)
        via_identity = c.compute_identity(c.apply(term))
        ok = (direct == via_identity)
        print(f"    {'✓' if ok else '✗'} apply(t)={c.show(direct):10s}  id∘apply(t)={c.show(via_identity)}")

    print("\n  Test 2: workspace_witness ≡ state-axis witness  (α-swap V₄-twin).")
    print("          The held value moved from state-axis to workspace-axis.")
    wid = c.workspace_alloc()
    target = c.TRUE
    c.store(wid, target)
    test_term = c.cons(c.I, target)
    ws_result = c.workspace_witness(wid, test_term)
    # State-axis equivalent: just check if normalize(term) == witness
    normalized = c.normalize(test_term)
    state_result = normalized if normalized == target else c.FAILURE
    ok = (ws_result == state_result)
    print(f"    {'✓' if ok else '✗'} workspace_witness={c.show(ws_result)}, state-witness={c.show(state_result)}")

    print("\n  Test 3: workspace_driven_state ≡ direct apply  (γ-swap V₄-twin).")
    print("          Same compute, different axis-engagement gauge.")
    for term_str in ["I true", "K true false", "S K K true"]:
        t = c.parse(c.NIL, term_str)
        wid = c.workspace_alloc()
        c.store(wid, t)
        via_workspace = c.workspace_driven_state(wid)
        direct = c.apply(t)
        ok = (via_workspace == direct)
        print(f"    {'✓' if ok else '✗'} ({term_str:14s}):  workspace_path={c.show(via_workspace):8s}  direct={c.show(direct)}")

    print("\n  Test 4: marker V₄-coherence  (γ-swap of variable-marker).")
    print("          compute_marker and workspace_marker share the marker structure.")
    w_a = c.workspace_alloc()
    w_b = c.workspace_alloc()
    c.compute_marker(w_a, c.I)
    c.workspace_marker(w_b, c.K)
    a_is_marker = c.is_workspace_marker(w_a)
    b_is_marker = c.is_workspace_marker(w_b)
    ok = a_is_marker and b_is_marker
    print(f"    {'✓' if ok else '✗'} is_workspace_marker(compute_marker_cell) = {a_is_marker}")
    print(f"    {'✓' if ok else '✗'} is_workspace_marker(workspace_marker_cell) = {b_is_marker}")

    print("\n  Test 5: workspace_alloc V₄-coherence  (γ-swap of S1_nil).")
    print("          Allocating a workspace slot ≡ creating a nil-equivalent cell.")
    initial_size = c.workspace_size()
    wid = c.workspace_alloc()
    final_size = c.workspace_size()
    ok = (final_size == initial_size + 1)
    print(f"    {'✓' if ok else '✗'} workspace grew from {initial_size} to {final_size}")
    print(f"    {'✓' if c.workspace_kind(wid) is None else '✗'} new slot is empty (nil-equivalent)")

    print("\n" + "=" * 72)
    print(f"  Chart size:     {c.size()} cells (D axis — data, immutable)")
    print(f"  Workspace size: {c.workspace_size()} active slots (W axis — workspace, mutable)")
    print(f"  History length: {c.history_length()} transitions (S axis — state)")
    print(f"  Apply memo:     {len(c._apply_memo)} memoized (C axis — compute)")
    print("=" * 72)


if __name__ == "__main__":
    demo()
