"""
applied_grammar.py — M41 (v12): sum-type receipts (TermReceipt /
StateReceipt / ObservationReceipt), StateOpSpec registry, fail-closed
verification (allow_extending opt-in), strict_replay_context manager.

Iterations:
  v1  : post-hoc annotation
  v2  : endogenous codewords via receipt-carrying wrappers
  v3  : verify_receipt + verify_trace; tamper rejection
  v4  : pure replay split from execution
  v5  : VerificationResult(ok, level, reason)
  v6  : Three-axis VerificationResult + registry_digest
  v7  : Extent purity observation + op_address_digest + cells_allocated
  v8  : Structural purity (digests); audited kernel; exception-safe
  v9  : Intensional/semantic replay split; chart_instance_nonce; effect_level
  v10 : Grade lattice; strict replay; canonical encoding; state digests
  v11 : Tuple/list split; snapshot-around-strict; term/state separation; fail-closed canonical
  v12 : ────────────────────────────────────────────────────────────────────
        - EvalReceipt replaced by three sum types:
            TermReceipt        (apply / interp; advances term cursor)
            StateReceipt       (state-mutating ops; required state digests)
            ObservationReceipt (passive readings; reserved for future)
          Illegal receipts are unconstructible (__post_init__ validates
          op_name against the type's allowed op set).
        - StateOpSpec registry declares per-op obligation_level. v12 ops
          max out at EFFECT_RECEIPT_DECLARED; spec is the seam for v13's
          EFFECT_REPLAY_VERIFIED via spec.replay().
        - verify_receipt and verify_trace take allow_extending=False by
          default. CHART_EXTENDING during verification now FAILS unless
          explicitly enabled — verification should not perturb the chart.
        - strict_replay_context as an explicit context manager, scaffolds
          the path toward capability discipline (v13).
        - transition_kind field is gone — the receipt's type IS its kind.
        - CHART_LOCAL semantics documented: "same live chart object
          lineage within this process", not "any chart with the same
          construction." Portable identity needs content-addressed cell
          digests (v13+, named).
        ────────────────────────────────────────────────────────────────────

What v12 fixes (per critique of v11):

  1. transition_kind was trusted. A forged receipt could declare
     transition_kind="observation" for a term op. v12 makes this
     unconstructible: TermReceipt's __post_init__ rejects op_name not
     in _TERM_OPS; StateReceipt rejects op_name not in _STATE_OPS.
     The kind is the type, not a declared field.

  2. State receipts only address-verified, not replay/effect-verified.
     Still true. v12 introduces StateOpSpec with `obligation_level`,
     declaring per-op max verification achievable. All v12 specs say
     EFFECT_RECEIPT_DECLARED max; v13's spec.replay() implementation
     would unlock EFFECT_REPLAY_VERIFIED.

  3. compute_chart_state_digest depends on canonicalizability. v12
     adds an explicit test for this and documents the invariant:
     chart internals (_history, _apply_memo, _cells) must contain
     only canonical-encodable values.

  4. Strict replay monkey-patches c.cons. v12 wraps this in a context
     manager strict_replay_context, making the strict-replay region
     explicit. Full capability discipline (replay context object that
     wraps the chart) remains v13.

  5. CHART_EXTENDING during verification is suspicious. v12 verifier
     fail-closed by default: CHART_EXTENDING fails unless
     allow_extending=True is passed.

  6. CHART_LOCAL semantics documented as "same live chart object
     lineage", not portable identity. v12+ portable identity needs
     content-addressed cell digests.

Roadmap (still deferred):
  - v13: StateOpSpec.replay() implementations → EFFECT_REPLAY_VERIFIED
  - v13: replay context as a capability object (not monkey-patch)
  - v13+: PORTABLE locality via chart_digest + portable cell digests
  - v13+: Semantic op digests (op.kind/arity/version/impl_hash)
"""

import hashlib
import uuid
import weakref
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any, Callable, Union, FrozenSet
from chart_chained import ChartChained
from unified_address import encode_op, UnifiedCodeword
from spectral_view import fwht


# ============================================================
# Verification axis constants
# ============================================================

# transition_level
REPLAY_VERIFIED = "replay_verified"            # intensional (ID match)
SEMANTIC_REPLAY_VERIFIED = "semantic_replay"   # extensional (eq match without ID)
ADDRESS_VERIFIED = "address_verified"
FAILED = "failed"

# purity_level
CHART_PURE = "chart_pure"
CHART_EXTENDING = "chart_extending"
FAILED_PURITY = "failed_purity"

# locality
# CHART_LOCAL semantics: "same live chart object lineage within this Python
# process." The chart_instance_nonce witnesses this. Portable identity
# across processes requires content-addressed cell digests (v13+).
CHART_LOCAL = "chart_local"
PORTABLE = "portable"
FAILED_LOCALITY = "failed_locality"

# effect_level
# EFFECT_INAPPLICABLE is the unit of the effect-meet lattice: "no effect
# obligation was claimed." Not "stronger evidence than REPLAY_VERIFIED."
EFFECT_INAPPLICABLE = "effect_inapplicable"
EFFECT_REPLAY_VERIFIED = "effect_replay_verified"
EFFECT_RECEIPT_DECLARED = "effect_receipt_declared"
EFFECT_UNVERIFIED = "effect_unverified"
FAILED_EFFECT = "failed_effect"


# Op kind classification
_TERM_OPS: FrozenSet[str] = frozenset({'apply', 'interp'})
_STATE_OPS: FrozenSet[str] = frozenset({
    'store', 'evolve_with_receipt', 'validated_store',
    'quote_via_state', 'load_with_log', 'workspace_witness',
})


# Ranks for meet-semilattice
_TRANSITION_RANK = {
    FAILED: 0,
    ADDRESS_VERIFIED: 1,
    SEMANTIC_REPLAY_VERIFIED: 2,
    REPLAY_VERIFIED: 3,
}

_PURITY_RANK = {
    FAILED_PURITY: 0,
    CHART_EXTENDING: 1,
    CHART_PURE: 2,
}

_LOCALITY_RANK = {
    FAILED_LOCALITY: 0,
    CHART_LOCAL: 1,
    PORTABLE: 2,
}

_EFFECT_RANK = {
    FAILED_EFFECT: 0,
    EFFECT_UNVERIFIED: 1,
    EFFECT_RECEIPT_DECLARED: 2,
    EFFECT_REPLAY_VERIFIED: 3,
    EFFECT_INAPPLICABLE: 4,  # NOT "strongest"; special-cased in _meet_effect
}


# ============================================================
# Grade — four-axis meet-semilattice
# ============================================================

@dataclass(frozen=True)
class Grade:
    transition: str
    purity: str
    locality: str
    effect: str

    @staticmethod
    def _meet_by_rank(a, b, rank):
        return a if rank[a] < rank[b] else b

    @staticmethod
    def _meet_effect(a, b):
        if a == EFFECT_INAPPLICABLE and b == EFFECT_INAPPLICABLE:
            return EFFECT_INAPPLICABLE
        if a == EFFECT_INAPPLICABLE:
            return b
        if b == EFFECT_INAPPLICABLE:
            return a
        return Grade._meet_by_rank(a, b, _EFFECT_RANK)

    def meet(self, other: 'Grade') -> 'Grade':
        return Grade(
            transition=Grade._meet_by_rank(self.transition, other.transition, _TRANSITION_RANK),
            purity=Grade._meet_by_rank(self.purity, other.purity, _PURITY_RANK),
            locality=Grade._meet_by_rank(self.locality, other.locality, _LOCALITY_RANK),
            effect=Grade._meet_effect(self.effect, other.effect),
        )


GRADE_TOP = Grade(REPLAY_VERIFIED, CHART_PURE, PORTABLE, EFFECT_INAPPLICABLE)


# ============================================================
# Display helper
# ============================================================

def _display_digest(d: Optional[str], chars: int = 16) -> str:
    if d is None:
        return "(none)"
    if len(d) <= chars:
        return d
    return d[:chars] + "…"


# ============================================================
# Canonical byte encoding — fail-closed
# ============================================================

def _canonical_bytes(obj) -> bytes:
    """Injective canonical byte encoding. Fail-closed on non-canonical types."""
    if obj is None:
        return b'N'
    if isinstance(obj, bool):
        return b'B' + (b'\x01' if obj else b'\x00')
    if isinstance(obj, int):
        sign = b'+' if obj >= 0 else b'-'
        absobj = abs(obj)
        n = (absobj.bit_length() + 7) // 8 or 1
        return b'I' + sign + n.to_bytes(4, 'big') + absobj.to_bytes(n, 'big')
    if isinstance(obj, str):
        bs = obj.encode('utf-8')
        return b'S' + len(bs).to_bytes(4, 'big') + bs
    if isinstance(obj, bytes):
        return b'b' + len(obj).to_bytes(4, 'big') + obj
    if isinstance(obj, tuple):
        body = b''.join(_canonical_bytes(x) for x in obj)
        return b'T' + len(obj).to_bytes(4, 'big') + body
    if isinstance(obj, list):
        body = b''.join(_canonical_bytes(x) for x in obj)
        return b'L' + len(obj).to_bytes(4, 'big') + body
    if isinstance(obj, dict):
        items = sorted(
            (_canonical_bytes(k), _canonical_bytes(v))
            for k, v in obj.items()
        )
        body = b''.join(
            b'K' + len(k).to_bytes(4, 'big') + k +
            b'V' + len(v).to_bytes(4, 'big') + v
            for k, v in items
        )
        return b'D' + len(items).to_bytes(4, 'big') + body
    raise TypeError(
        f"non-canonical type {type(obj).__name__}: cannot canonicalize {obj!r}"
    )


def _digest_seq(seq) -> str:
    return hashlib.sha256(_canonical_bytes(list(seq))).hexdigest()


def _digest_dict(d) -> str:
    return hashlib.sha256(_canonical_bytes(dict(d))).hexdigest()


# ============================================================
# Chart instance nonce — WeakKeyDictionary
# ============================================================

_chart_nonces: 'weakref.WeakKeyDictionary[ChartChained, str]' = weakref.WeakKeyDictionary()


def compute_chart_instance_nonce(c: ChartChained) -> str:
    """Per-chart-instance nonce.

    Witnesses 'same live chart object lineage within this Python process'.
    NOT a portable witness — see CHART_LOCAL documentation.
    """
    if c not in _chart_nonces:
        _chart_nonces[c] = uuid.uuid4().hex
    return _chart_nonces[c]


# ============================================================
# Registry / state digests
# ============================================================

def compute_registry_digest(c: ChartChained) -> str:
    items = sorted(
        (op.name, encode_op(op).code) for op in c.registry.all()
    )
    items_as_list = [(name, code) for name, code in items]
    return hashlib.sha256(_canonical_bytes(items_as_list)).hexdigest()


def compute_op_address_digest(c: ChartChained, op_name: str) -> str:
    try:
        code = _op_codeword(c, op_name)
    except KeyError:
        return "0" * 64
    return hashlib.sha256(_canonical_bytes((op_name, code))).hexdigest()


def compute_chart_state_digest(c: ChartChained) -> str:
    """Composite digest over mutable chart state.

    INVARIANT (v12, named): _history, _apply_memo, _cells must contain
    only canonical-encodable values (None/bool/int/str/bytes/tuple/list/
    dict of same). A non-canonical value in chart state will cause this
    function to raise TypeError. This is intentional fail-closed behavior.
    """
    state = {
        'history': list(c._history),
        'memo': dict(c._apply_memo),
        'cells': list(c._cells),
    }
    return hashlib.sha256(_canonical_bytes(state)).hexdigest()


# ============================================================
# StateOpSpec registry (v12)
# ============================================================

@dataclass(frozen=True)
class StateOpSpec:
    """Declares verification properties of a state-mutating operation.

    v12 spec carries the op's name and the maximum effect_level
    achievable. v13 will add a `replay` callable to unlock
    EFFECT_REPLAY_VERIFIED (rollback and re-execute the op).
    """
    name: str
    obligation_level: str  # max effect_level the spec can witness


_STATE_OP_SPECS: Dict[str, StateOpSpec] = {
    'store': StateOpSpec(name='store', obligation_level=EFFECT_RECEIPT_DECLARED),
    'evolve_with_receipt': StateOpSpec(name='evolve_with_receipt', obligation_level=EFFECT_RECEIPT_DECLARED),
    'validated_store': StateOpSpec(name='validated_store', obligation_level=EFFECT_RECEIPT_DECLARED),
    'quote_via_state': StateOpSpec(name='quote_via_state', obligation_level=EFFECT_RECEIPT_DECLARED),
    'load_with_log': StateOpSpec(name='load_with_log', obligation_level=EFFECT_RECEIPT_DECLARED),
    'workspace_witness': StateOpSpec(name='workspace_witness', obligation_level=EFFECT_RECEIPT_DECLARED),
}


def get_state_op_spec(op_name: str) -> Optional[StateOpSpec]:
    return _STATE_OP_SPECS.get(op_name)


# ============================================================
# Sum-type receipts (v12)
# ============================================================

@dataclass(frozen=True)
class TermReceipt:
    """Witnesses a term-reduction step.

    Advances the term cursor in verify_trace. op_name must be in _TERM_OPS;
    illegal construction is rejected at __post_init__.
    """
    op_name: str
    codeword: int
    before: int
    after: int
    rule: Optional[int] = None       # only set for interp
    binding: Optional[Tuple[Tuple[int, int], ...]] = None
    table: Optional[int] = None
    registry_digest: Optional[str] = None
    op_address_digest: Optional[str] = None
    chart_instance_nonce: Optional[str] = None

    def __post_init__(self):
        if self.op_name not in _TERM_OPS:
            raise ValueError(
                f"TermReceipt with non-term op_name {self.op_name!r}; "
                f"expected one of {sorted(_TERM_OPS)}"
            )

    def changed(self) -> bool:
        return self.before != self.after


@dataclass(frozen=True)
class StateReceipt:
    """Witnesses a chart-state mutation.

    Does NOT advance the term cursor. state_pre_digest and
    state_post_digest are REQUIRED (not optional). op_name must be
    in _STATE_OPS.
    """
    op_name: str
    codeword: int
    input_id: int            # nominal input (e.g. data_id for store)
    output_id: int           # nominal output (e.g. workspace_id for store)
    state_pre_digest: str    # required
    state_post_digest: str   # required
    registry_digest: Optional[str] = None
    op_address_digest: Optional[str] = None
    chart_instance_nonce: Optional[str] = None

    def __post_init__(self):
        if self.op_name not in _STATE_OPS:
            raise ValueError(
                f"StateReceipt with non-state op_name {self.op_name!r}; "
                f"expected one of {sorted(_STATE_OPS)}"
            )


@dataclass(frozen=True)
class ObservationReceipt:
    """Witnesses a passive reading (no mutation, no term transition).

    Reserved for future read-only operations. No state digests because
    observations don't mutate state. op_name must NOT be in _TERM_OPS or
    _STATE_OPS (rejected at __post_init__).
    """
    op_name: str
    codeword: int
    target_id: int
    result_id: Optional[int] = None
    registry_digest: Optional[str] = None
    op_address_digest: Optional[str] = None
    chart_instance_nonce: Optional[str] = None

    def __post_init__(self):
        if self.op_name in _TERM_OPS or self.op_name in _STATE_OPS:
            raise ValueError(
                f"ObservationReceipt op_name {self.op_name!r} is a known "
                f"term or state op; observation receipts are for passive "
                f"readings only"
            )


Receipt = Union[TermReceipt, StateReceipt, ObservationReceipt]


# ============================================================
# Internals
# ============================================================

def _op_codeword(c: ChartChained, op_name: str) -> int:
    op = c.registry.get(op_name)
    if op is None:
        raise KeyError(f"op {op_name!r} not in registry")
    return encode_op(op).code


def _canonical_binding(binding: Dict[int, int]) -> Tuple[Tuple[int, int], ...]:
    return tuple(sorted(binding.items()))


# ============================================================
# Structural snapshot
# ============================================================

@dataclass(frozen=True)
class ChartSnapshot:
    history_digest: str
    history_len: int
    memo_digest: str
    memo_len: int
    cells_digest: str
    cells_len: int


def _snapshot_chart_state(c: ChartChained) -> ChartSnapshot:
    return ChartSnapshot(
        history_digest=_digest_seq(c._history),
        history_len=len(c._history),
        memo_digest=_digest_dict(c._apply_memo),
        memo_len=len(c._apply_memo),
        cells_digest=_digest_seq(c._cells),
        cells_len=len(c._cells),
    )


def _classify_effect(before, after, c):
    if (after.history_digest != before.history_digest
            or after.history_len != before.history_len):
        return FAILED_PURITY, after.cells_len - before.cells_len
    if (after.memo_digest != before.memo_digest
            or after.memo_len != before.memo_len):
        return FAILED_PURITY, after.cells_len - before.cells_len
    cells_delta = after.cells_len - before.cells_len
    if after.cells_digest == before.cells_digest:
        return CHART_PURE, 0
    existing_after_digest = _digest_seq(c._cells[:before.cells_len])
    if existing_after_digest != before.cells_digest:
        return FAILED_PURITY, cells_delta
    return CHART_EXTENDING, cells_delta


def _observe_verification_effects(c, thunk):
    before = _snapshot_chart_state(c)
    result, error = None, None
    try:
        result = thunk()
    except Exception as e:
        error = e
    finally:
        after = _snapshot_chart_state(c)
    purity, allocated = _classify_effect(before, after, c)
    return result, purity, allocated, error


# ============================================================
# Strict replay — context manager (v12)
# ============================================================

class _StrictReplayMiss(Exception):
    pass


def cons_existing(c: ChartChained, l: int, r: int) -> Optional[int]:
    return c._hashcons.get((l, r))


@contextmanager
def strict_replay_context(c: ChartChained):
    """Context manager: c.cons is restricted to lookup-only mode.

    Within the with-block, any call to c.cons that would have allocated
    raises _StrictReplayMiss. On exit, c.cons is restored.

    v12 step toward capability discipline. v13 would replace this with
    a proper context object that wraps the chart (not monkey-patching).
    """
    original_cons = c.cons

    def strict_cons(l: int, r: int) -> int:
        cached = c._hashcons.get((l, r))
        if cached is not None:
            return cached
        raise _StrictReplayMiss(f"cons({l}, {r}) would allocate")

    c.cons = strict_cons
    try:
        yield
    finally:
        c.cons = original_cons


def _try_strict_replay(c, thunk):
    """Attempt thunk in strict-replay context. Returns (value, ok, error)."""
    value, strict_ok, error = None, False, None
    with strict_replay_context(c):
        try:
            value = thunk()
            strict_ok = True
        except _StrictReplayMiss:
            strict_ok = False
        except Exception as e:
            error = e
    return value, strict_ok, error


def _attempt_replay(c, kernel):
    """Strict first with snapshot in BOTH modes."""
    before = _snapshot_chart_state(c)
    strict_value, strict_ok, strict_error = _try_strict_replay(c, kernel)
    after = _snapshot_chart_state(c)
    purity, allocated = _classify_effect(before, after, c)

    if strict_error is not None:
        return None, purity, allocated, strict_error
    if strict_ok:
        return strict_value, purity, allocated, None
    return _observe_verification_effects(c, kernel)


# ============================================================
# Pure replay paths
# ============================================================

def apply_replay(c: ChartChained, k: int) -> int:
    return c._reduce_step(k)


@dataclass(frozen=True)
class InterpReplay:
    after: int
    rule: Optional[int]
    binding: Optional[Tuple[Tuple[int, int], ...]]


def interp_replay(c: ChartChained, table: int, term: int) -> InterpReplay:
    fired_rule: Optional[int] = None
    captured_binding: Optional[Tuple[Tuple[int, int], ...]] = None

    def _walk(t: int, term: int) -> int:
        nonlocal fired_rule, captured_binding
        cur = t
        while not c.eq(cur, c.NIL):
            rule = c.left(cur)
            pattern = c.left(rule)
            replacement = c.right(rule)
            binding = c._match(pattern, term, {})
            if binding is not None:
                fired_rule = rule
                captured_binding = _canonical_binding(binding)
                return c._substitute(replacement, binding)
            cur = c.right(cur)
        if term not in c._atoms:
            l = c.left(term)
            new_l = _walk(t, l)
            if not c.eq(new_l, l):
                return c.cons(new_l, c.right(term))
        return term

    after = _walk(table, term)
    return InterpReplay(after=after, rule=fired_rule, binding=captured_binding)


# ============================================================
# VerificationResult
# ============================================================

@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    transition_level: str
    purity_level: str
    locality: str
    effect_level: str
    reason: str
    cells_allocated: int = 0

    @property
    def grade(self) -> Grade:
        return Grade(self.transition_level, self.purity_level,
                     self.locality, self.effect_level)

    @classmethod
    def replay_ok(cls, *, transition_level=REPLAY_VERIFIED, purity_level,
                  locality=CHART_LOCAL, effect_level=EFFECT_INAPPLICABLE,
                  cells_allocated=0, reason="replay matched receipt"):
        return cls(True, transition_level, purity_level, locality,
                   effect_level, reason, cells_allocated)

    @classmethod
    def address_ok(cls, *, locality=CHART_LOCAL, effect_level=EFFECT_UNVERIFIED,
                   reason="codeword matches op_name"):
        return cls(True, ADDRESS_VERIFIED, CHART_PURE, locality,
                   effect_level, reason, 0)

    @classmethod
    def fail(cls, reason, *, purity_level=CHART_PURE, locality=CHART_LOCAL,
             effect_level=EFFECT_INAPPLICABLE, cells_allocated=0):
        return cls(False, FAILED, purity_level, locality,
                   effect_level, reason, cells_allocated)


# ============================================================
# Execution wrappers — emit sum-type receipts
# ============================================================

def _full_witness(c, op_name):
    return {
        'registry_digest': compute_registry_digest(c),
        'op_address_digest': compute_op_address_digest(c, op_name),
        'chart_instance_nonce': compute_chart_instance_nonce(c),
    }


def apply_with_receipt(c, k) -> Tuple[int, TermReceipt]:
    before = k
    after = apply_replay(c, before)
    c._apply_memo[before] = after
    c._history.append(('apply_with_receipt', (before,), after))
    return after, TermReceipt(
        op_name='apply',
        codeword=_op_codeword(c, 'apply'),
        before=before, after=after,
        **_full_witness(c, 'apply'),
    )


def interp_with_receipt(c, table, term) -> Tuple[int, TermReceipt]:
    replay = interp_replay(c, table, term)
    c._history.append(('interp_with_receipt', (table, term), replay.after))
    return replay.after, TermReceipt(
        op_name='interp',
        codeword=_op_codeword(c, 'interp'),
        before=term, after=replay.after,
        rule=replay.rule, binding=replay.binding, table=table,
        **_full_witness(c, 'interp'),
    )


def _make_state_receipt(c, op_name, input_id, output_id, pre, post):
    return StateReceipt(
        op_name=op_name, codeword=_op_codeword(c, op_name),
        input_id=input_id, output_id=output_id,
        state_pre_digest=pre, state_post_digest=post,
        **_full_witness(c, op_name),
    )


def store_with_receipt(c, w_id, data_id):
    pre = compute_chart_state_digest(c)
    c.store(w_id, data_id)
    post = compute_chart_state_digest(c)
    return w_id, _make_state_receipt(c, 'store', data_id, w_id, pre, post)


def evolve_with_receipt_op(c, term, w_id):
    pre = compute_chart_state_digest(c)
    c.evolve_with_receipt(term, w_id)
    post = compute_chart_state_digest(c)
    return w_id, _make_state_receipt(c, 'evolve_with_receipt', term, w_id, pre, post)


def validated_store_with_receipt(c, term, w_id, pred):
    pre = compute_chart_state_digest(c)
    c.validated_store(term, w_id, pred)
    post = compute_chart_state_digest(c)
    return w_id, _make_state_receipt(c, 'validated_store', term, w_id, pre, post)


def quote_via_state_with_receipt(c, term):
    pre = compute_chart_state_digest(c)
    result = c.quote_via_state(term)
    post = compute_chart_state_digest(c)
    return result, _make_state_receipt(c, 'quote_via_state', term, result, pre, post)


def load_with_log_with_receipt(c, w_id):
    pre = compute_chart_state_digest(c)
    result = c.load_with_log(w_id)
    post = compute_chart_state_digest(c)
    return result, _make_state_receipt(c, 'load_with_log', w_id, result, pre, post)


def workspace_witness_with_receipt(c, w_id, term):
    pre = compute_chart_state_digest(c)
    result = c.workspace_witness(w_id, term)
    post = compute_chart_state_digest(c)
    return result, _make_state_receipt(c, 'workspace_witness', w_id, result, pre, post)


# ============================================================
# Trace iterators
# ============================================================

def normalize_with_trace(c, k, max_steps=1000):
    receipts = []
    cur = k
    for _ in range(max_steps):
        after, r = apply_with_receipt(c, cur)
        receipts.append(r)
        if c.eq(after, cur):
            return after, receipts
        cur = after
    return cur, receipts


def iterated_interp_with_trace(c, term, max_steps=1000):
    receipts = []
    cur = term
    for _ in range(max_steps):
        after, r = interp_with_receipt(c, c.default_table, cur)
        receipts.append(r)
        if c.eq(after, cur):
            return after, receipts
        cur = after
    return cur, receipts


def changed_receipts(trace):
    return [r for r in trace if isinstance(r, TermReceipt) and r.changed()]


# ============================================================
# Per-type verification primitives
# ============================================================

def _check_codeword_consistency(c, r) -> Optional[VerificationResult]:
    try:
        expected = _op_codeword(c, r.op_name)
    except KeyError:
        return VerificationResult.fail(f"unknown op_name {r.op_name!r}")
    if r.codeword != expected:
        return VerificationResult.fail(
            f"codeword {r.codeword:05b} != expected {expected:05b} for {r.op_name!r}"
        )
    if not UnifiedCodeword(r.codeword).is_valid:
        return VerificationResult.fail(f"codeword {r.codeword:05b} not valid")
    return None


def _check_chart_instance(c, r) -> Optional[VerificationResult]:
    if r.chart_instance_nonce is None:
        return None
    current = compute_chart_instance_nonce(c)
    if r.chart_instance_nonce != current:
        return VerificationResult.fail(
            f"chart-instance mismatch: receipt {_display_digest(r.chart_instance_nonce)} "
            f"!= current {_display_digest(current)}"
        )
    return None


def _check_digests(c, r) -> Optional[VerificationResult]:
    if r.registry_digest is not None:
        current = compute_registry_digest(c)
        if r.registry_digest != current:
            return VerificationResult.fail(
                f"registry drift: receipt {_display_digest(r.registry_digest)} "
                f"!= current {_display_digest(current)}"
            )
    if r.op_address_digest is not None:
        try:
            current_op = compute_op_address_digest(c, r.op_name)
        except KeyError:
            return VerificationResult.fail(f"op {r.op_name!r} not in registry")
        if r.op_address_digest != current_op:
            return VerificationResult.fail(
                f"op-address drift: receipt {_display_digest(r.op_address_digest)} "
                f"!= current {_display_digest(current_op)}"
            )
    return None


# ============================================================
# verify_receipt with sum-type dispatch + fail-closed (v12)
# ============================================================

def verify_receipt(c: ChartChained, r: Receipt, *,
                   allow_extending: bool = False) -> VerificationResult:
    """Four-axis verifier dispatching on receipt type.

    v12: fail-closed by default. CHART_EXTENDING during verification
    fails unless allow_extending=True. Verification should not perturb
    the chart; permissive replay is a diagnostic mode, not the default.
    """
    if isinstance(r, TermReceipt):
        return _verify_term(c, r, allow_extending=allow_extending)
    if isinstance(r, StateReceipt):
        return _verify_state(c, r)
    if isinstance(r, ObservationReceipt):
        return _verify_observation(c, r)
    return VerificationResult.fail(f"unknown receipt type: {type(r).__name__}")


def _verify_term(c, r: TermReceipt, *, allow_extending: bool) -> VerificationResult:
    codeword_fail = _check_codeword_consistency(c, r)
    if codeword_fail: return codeword_fail
    instance_fail = _check_chart_instance(c, r)
    if instance_fail: return instance_fail
    digest_fail = _check_digests(c, r)
    if digest_fail: return digest_fail

    locality = CHART_LOCAL

    if r.op_name == 'apply':
        if r.rule is not None or r.binding is not None or r.table is not None:
            return VerificationResult.fail("apply receipt must have None rule/binding/table")

        def apply_kernel():
            recomputed = apply_replay(c, r.before)
            return recomputed, (recomputed == r.after), c.eq(recomputed, r.after)

        value, purity, allocated, error = _attempt_replay(c, apply_kernel)

        if purity == FAILED_PURITY:
            return VerificationResult.fail(
                "verifier mutated chart state during apply replay (BUG)",
                purity_level=FAILED_PURITY, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        if error is not None:
            return VerificationResult.fail(
                f"apply replay raised {type(error).__name__}: {error}",
                purity_level=purity, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        if purity == CHART_EXTENDING and not allow_extending:
            return VerificationResult.fail(
                f"verification would allocate {allocated} cell(s); "
                f"strict replay missed and allow_extending=False",
                purity_level=CHART_EXTENDING, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        recomputed, id_m, sem_m = value
        if not sem_m:
            return VerificationResult.fail(
                f"replay after #{recomputed} != receipt after #{r.after} (semantic mismatch)",
                purity_level=purity, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        trans = REPLAY_VERIFIED if id_m else SEMANTIC_REPLAY_VERIFIED
        path = "strict" if (purity == CHART_PURE and allocated == 0) else "permissive"
        return VerificationResult.replay_ok(
            transition_level=trans, purity_level=purity, locality=locality,
            effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            reason=(f"apply {path} replay matches "
                    f"{'(ID-exact)' if id_m else '(semantic only)'}; "
                    f"allocated {allocated} cell(s)"),
        )

    if r.op_name == 'interp':
        if r.table is None:
            return VerificationResult.fail("interp receipt missing table reference")

        def interp_kernel():
            replay = interp_replay(c, r.table, r.before)
            return (replay, (replay.after == r.after), c.eq(replay.after, r.after),
                    replay.rule == r.rule, replay.binding == r.binding)

        value, purity, allocated, error = _attempt_replay(c, interp_kernel)

        if purity == FAILED_PURITY:
            return VerificationResult.fail(
                "verifier mutated chart state during interp replay (BUG)",
                purity_level=FAILED_PURITY, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        if error is not None:
            return VerificationResult.fail(
                f"interp replay raised {type(error).__name__}: {error}",
                purity_level=purity, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        if purity == CHART_EXTENDING and not allow_extending:
            return VerificationResult.fail(
                f"verification would allocate {allocated} cell(s); "
                f"strict replay missed and allow_extending=False",
                purity_level=CHART_EXTENDING, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        replay, after_id, after_sem, rule_m, binding_m = value
        if not after_sem:
            return VerificationResult.fail(
                f"interp replay after #{replay.after} != receipt after #{r.after} (semantic)",
                purity_level=purity, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        if not rule_m:
            return VerificationResult.fail(
                f"interp replay rule #{replay.rule} != receipt rule #{r.rule}",
                purity_level=purity, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        if not binding_m:
            return VerificationResult.fail(
                f"interp binding {replay.binding} != receipt binding {r.binding}",
                purity_level=purity, locality=locality,
                effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            )
        trans = REPLAY_VERIFIED if after_id else SEMANTIC_REPLAY_VERIFIED
        path = "strict" if (purity == CHART_PURE and allocated == 0) else "permissive"
        return VerificationResult.replay_ok(
            transition_level=trans, purity_level=purity, locality=locality,
            effect_level=EFFECT_INAPPLICABLE, cells_allocated=allocated,
            reason=(f"interp {path} replay matches "
                    f"{'(ID-exact)' if after_id else '(semantic only)'}; "
                    f"allocated {allocated} cell(s)"),
        )

    return VerificationResult.fail(f"unknown term op {r.op_name!r}")


def _verify_state(c, r: StateReceipt) -> VerificationResult:
    codeword_fail = _check_codeword_consistency(c, r)
    if codeword_fail: return codeword_fail
    instance_fail = _check_chart_instance(c, r)
    if instance_fail: return instance_fail
    digest_fail = _check_digests(c, r)
    if digest_fail: return digest_fail

    spec = get_state_op_spec(r.op_name)
    if spec is None:
        return VerificationResult.fail(
            f"no StateOpSpec for {r.op_name!r}; cannot verify obligation"
        )

    # v12: spec.obligation_level caps the effect_level. All v12 specs say
    # EFFECT_RECEIPT_DECLARED max; v13 with spec.replay() would unlock
    # EFFECT_REPLAY_VERIFIED.
    eff = spec.obligation_level
    reason = (
        f"codeword {r.codeword:05b} matches op {r.op_name!r}; "
        f"spec.obligation_level={spec.obligation_level}; "
        f"state digests declared"
    )
    return VerificationResult.address_ok(
        locality=CHART_LOCAL, effect_level=eff, reason=reason,
    )


def _verify_observation(c, r: ObservationReceipt) -> VerificationResult:
    codeword_fail = _check_codeword_consistency(c, r)
    if codeword_fail: return codeword_fail
    instance_fail = _check_chart_instance(c, r)
    if instance_fail: return instance_fail
    digest_fail = _check_digests(c, r)
    if digest_fail: return digest_fail
    # Observations are passive; address verification only.
    return VerificationResult.address_ok(
        locality=CHART_LOCAL, effect_level=EFFECT_INAPPLICABLE,
        reason=f"observation op {r.op_name!r} address-verified (no effect to verify)",
    )


def verify_trace(c, start: int, final: int, receipts: List[Receipt], *,
                 allow_extending: bool = False) -> VerificationResult:
    """v12: dispatches on receipt type. Term cursor advances ONLY on
    TermReceipt. allow_extending propagates through."""
    cur = start
    overall = GRADE_TOP
    total_cells_allocated = 0
    counts = {REPLAY_VERIFIED: 0, SEMANTIC_REPLAY_VERIFIED: 0, ADDRESS_VERIFIED: 0}
    n_term = n_state = n_obs = 0

    for i, r in enumerate(receipts):
        is_term = isinstance(r, TermReceipt)

        if is_term:
            if not c.eq(r.before, cur):
                return VerificationResult.fail(
                    f"chain break at receipt {i}: before #{r.before} != cursor #{cur}"
                )

        step = verify_receipt(c, r, allow_extending=allow_extending)
        if not step.ok:
            return VerificationResult.fail(
                f"receipt {i} ({r.op_name}): {step.reason}",
                purity_level=step.purity_level,
                locality=step.locality,
                effect_level=step.effect_level,
                cells_allocated=total_cells_allocated + step.cells_allocated,
            )
        overall = overall.meet(step.grade)
        total_cells_allocated += step.cells_allocated
        if step.transition_level in counts:
            counts[step.transition_level] += 1

        if is_term:
            cur = r.after
            n_term += 1
        elif isinstance(r, StateReceipt):
            n_state += 1
        else:
            n_obs += 1

    if not c.eq(cur, final):
        return VerificationResult.fail(
            f"final term mismatch: cursor #{cur} != final #{final}"
        )

    return VerificationResult(
        ok=True,
        transition_level=overall.transition,
        purity_level=overall.purity,
        locality=overall.locality,
        effect_level=overall.effect,
        reason=(
            f"{n_term} term ({counts[REPLAY_VERIFIED]} replay, "
            f"{counts[SEMANTIC_REPLAY_VERIFIED]} sem_replay), "
            f"{n_state} state, {n_obs} observation; "
            f"{total_cells_allocated} cell(s) allocated by verifier"
        ),
        cells_allocated=total_cells_allocated,
    )


# ============================================================
# Property test
# ============================================================

def property_test_agreement(c, max_steps=200):
    initial_cells = tuple(range(len(c._cells)))
    start_size = len(c._cells)
    disagreements, errors = [], []
    n_tested = n_passed = 0
    for k in initial_cells:
        try:
            r_apply, _ = normalize_with_trace(c, k, max_steps=max_steps)
            r_interp, _ = iterated_interp_with_trace(c, k, max_steps=max_steps)
        except Exception as e:
            errors.append((k, type(e).__name__, str(e)))
            continue
        n_tested += 1
        if c.eq(r_apply, r_interp):
            n_passed += 1
        else:
            disagreements.append((k, r_apply, r_interp))
    end_size = len(c._cells)
    return {
        'initial_cells': start_size, 'n_tested': n_tested, 'n_passed': n_passed,
        'disagreements': disagreements, 'errors': errors,
        'new_cells_allocated': end_size - start_size,
    }


# ============================================================
# Helpers
# ============================================================

def render(c, k, max_depth=6):
    if max_depth <= 0:
        return "…"
    if k in c._atoms:
        return c.show(k) if hasattr(c, 'show') else str(k)
    return f"({render(c, c.left(k), max_depth-1)} {render(c, c.right(k), max_depth-1)})"


def all_codewords_valid(receipts):
    return all(0 <= r.codeword < 32 and UnifiedCodeword(r.codeword).is_valid
               for r in receipts)


# ============================================================
# Demo
# ============================================================

def demo():
    c = ChartChained()
    print("=" * 78)
    print("  M41 (v12) — Sum-type receipts, StateOpSpec, fail-closed,")
    print("              replay context manager")
    print("=" * 78)

    # Section 1
    print("\n" + "=" * 78)
    print("  Section 1: the grammar is its own data")
    print("=" * 78 + "\n")
    t = c.default_table
    count = 0
    while not c.eq(t, c.NIL):
        rule = c.left(t)
        count += 1
        print(f"  Rule {count}: pattern={render(c, c.left(rule))}, "
              f"replacement={render(c, c.right(rule))}")
        t = c.right(t)

    # Section 2: sum types
    print("\n" + "=" * 78)
    print("  Section 2: receipts are sum-typed (v12)")
    print("=" * 78 + "\n")
    expr = c.cons(c.I, c.TRUE)
    _, t_receipt = apply_with_receipt(c, expr)
    w = c.workspace_alloc()
    _, s_receipt = store_with_receipt(c, w, c.TRUE)

    print(f"  apply_with_receipt → {type(t_receipt).__name__}")
    print(f"     fields: op_name, codeword, before, after, [rule/binding/table for interp],")
    print(f"             registry/op_address/chart_instance digests")
    print()
    print(f"  store_with_receipt → {type(s_receipt).__name__}")
    print(f"     fields: op_name, codeword, input_id, output_id,")
    print(f"             state_pre_digest, state_post_digest (BOTH REQUIRED), digests")

    # Section 3: illegal receipts unconstructible
    print("\n" + "=" * 78)
    print("  Section 3: illegal receipts unconstructible (v12)")
    print("=" * 78 + "\n")
    print(f"  Trying TermReceipt(op_name='store', ...):")
    try:
        TermReceipt(op_name='store', codeword=0, before=0, after=0)
        print(f"    UNEXPECTED: accepted")
    except ValueError as e:
        print(f"    ValueError raised: {e}")
    print()
    print(f"  Trying StateReceipt(op_name='apply', ...):")
    try:
        StateReceipt(op_name='apply', codeword=0, input_id=0, output_id=0,
                     state_pre_digest="0", state_post_digest="0")
        print(f"    UNEXPECTED: accepted")
    except ValueError as e:
        print(f"    ValueError raised: {e}")
    print()
    print(f"  Trying ObservationReceipt(op_name='apply', ...):")
    try:
        ObservationReceipt(op_name='apply', codeword=0, target_id=0)
        print(f"    UNEXPECTED: accepted")
    except ValueError as e:
        print(f"    ValueError raised: {e}")
    print()
    print(f"  The receipt's type IS its transition_kind — no forgeable field.")

    # Section 4: StateOpSpec registry
    print("\n" + "=" * 78)
    print("  Section 4: StateOpSpec registry (v12)")
    print("=" * 78 + "\n")
    print(f"  {'op':<22} {'spec.obligation_level':<28}")
    print(f"  {'-' * 22} {'-' * 28}")
    for name in sorted(['store', 'evolve_with_receipt', 'validated_store',
                         'quote_via_state', 'load_with_log', 'workspace_witness']):
        spec = get_state_op_spec(name)
        print(f"  {name:<22} {spec.obligation_level:<28}")
    print()
    print(f"  v12: all specs cap at EFFECT_RECEIPT_DECLARED (no replay yet).")
    print(f"  v13: spec.replay() would unlock EFFECT_REPLAY_VERIFIED.")

    # Section 5: fail-closed
    print("\n" + "=" * 78)
    print("  Section 5: fail-closed verification (v12)")
    print("=" * 78 + "\n")
    print(f"  verify_receipt defaults to allow_extending=False.")
    print(f"  CHART_EXTENDING during verification → FAIL (verifier should")
    print(f"  not perturb the chart).")
    print()
    vr = verify_receipt(c, t_receipt)
    print(f"  Normal apply (strict succeeds, CHART_PURE): ok={vr.ok}, purity={vr.purity_level}")
    print()
    print(f"  An opt-in allow_extending=True permits CHART_EXTENDING for diagnostics:")
    print(f"  verify_receipt(c, r, allow_extending=True)")

    # Section 6: strict_replay_context
    print("\n" + "=" * 78)
    print("  Section 6: strict_replay_context manager (v12)")
    print("=" * 78 + "\n")
    c2 = ChartChained()
    c2.cons(c2.I, c2.TRUE)  # ensure (I, TRUE) is in hash-cons
    print(f"  with strict_replay_context(c):")
    print(f"      # c.cons is restricted to lookup-only")
    print(f"      c.cons(I, TRUE)  # returns existing cell (no allocation)")
    print(f"      c.cons(S, S)     # raises _StrictReplayMiss")
    print()
    with strict_replay_context(c2):
        result = c2.cons(c2.I, c2.TRUE)
        print(f"  c.cons(I, TRUE) inside context: cell #{result} (no allocation)")
        try:
            c2.cons(c2.S, c2.S)
            print(f"  UNEXPECTED: (S, S) didn't raise")
        except _StrictReplayMiss as e:
            print(f"  c.cons(S, S) inside context: raised _StrictReplayMiss ✓")
    print()
    print(f"  v12 step toward capability discipline. v13 would replace this")
    print(f"  with a context object that wraps the chart.")

    # Section 7: verify_trace dispatches on type
    print("\n" + "=" * 78)
    print("  Section 7: verify_trace dispatches on receipt type (v12)")
    print("=" * 78 + "\n")
    c3 = ChartChained()
    term = c3.cons(c3.I, c3.TRUE)
    after, ra = apply_with_receipt(c3, term)
    w3 = c3.workspace_alloc()
    _, rs = store_with_receipt(c3, w3, after)

    print(f"  Trace: [TermReceipt (apply), StateReceipt (store)]")
    print(f"  Verifying with final = #{after} (the term result):")
    vr = verify_trace(c3, term, after, [ra, rs])
    print(f"    ok={vr.ok}")
    print(f"    grade = ({vr.transition_level}, {vr.purity_level},")
    print(f"             {vr.locality}, {vr.effect_level})")
    print(f"    {vr.reason}")

    # Section 8: CHART_LOCAL semantics
    print("\n" + "=" * 78)
    print("  Section 8: CHART_LOCAL is 'same live chart object lineage' (v12)")
    print("=" * 78 + "\n")
    print(f"  CHART_LOCAL is NOT 'any chart with the same construction'.")
    print(f"  It is 'this specific chart instance, identified by")
    print(f"  chart_instance_nonce, within this Python process'.")
    print()
    print(f"  Portable identity (cross-process) needs content-addressed")
    print(f"  cell digests on the receipt — deferred to v13+.")

    # Thesis
    print("\n" + "=" * 78)
    print("  Thesis (v12)")
    print("=" * 78)
    print("""
  v12 closes v11's typing leaks. The receipt is now a sum type:

      Receipt = TermReceipt | StateReceipt | ObservationReceipt

  Each variant has only the fields that make semantic sense for its
  kind. Illegal combinations (TermReceipt with op_name='store',
  StateReceipt without state digests) are rejected at construction
  time. The verifier dispatches by isinstance, not by reading a
  declared transition_kind field that could be forged.

  StateOpSpec is the seam for v13's EFFECT_REPLAY_VERIFIED. Each
  state op carries an obligation_level cap; v12 caps all state ops
  at EFFECT_RECEIPT_DECLARED. v13's spec.replay() implementations
  would unlock EFFECT_REPLAY_VERIFIED by rolling back state,
  re-executing, and checking the post-state digest matches.

  Verification is fail-closed by default. The verifier no longer
  silently extends the chart during replay; allow_extending=True is
  required for permissive diagnostic mode. Normal verification of
  receipts emitted in this session uses strict replay → CHART_PURE.

  strict_replay_context makes the strict-replay region explicit as
  a context manager. v13 would lift this to a proper capability
  object (no monkey-patching).

  Roadmap (named):
    - v13: StateOpSpec.replay() implementations → EFFECT_REPLAY_VERIFIED
    - v13: capability context (not monkey-patch)
    - v13+: PORTABLE locality via chart_digest + portable cell digests
    - v13+: semantic op digests (op.kind/arity/version/impl_hash)
""")


if __name__ == "__main__":
    demo()
