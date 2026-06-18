"""
applied_grammar.py — M41 (v22.0): AddressedOp, registry-domain digest,
audit-tightened scope claims.

Six audit items from v21.1 closed: (1) "full mutable surface" rescoped
to "known chart mutable surface" with explicit inclusion/exclusion
list; (2) compute_structural_address_digest exposed as the load-bearing
address-primary digest function with caller-supplied registry_domain;
(3) AddressedOp class introduced as the canonical (op_name, address)
bundle, accepted by all three receipt constructors; (4) bridge verifier
docstring sharpened to distinguish construction-time invariants from
verification-time re-derivation; (5) REGISTRY_DOMAIN separator added
to structural-address digests; (6) self-import in demo removed.

Iterations:
  v1  – v12 : annotation → endogenous codewords → verify_trace →
              pure replay → VerificationResult → three axes → cells_
              allocated → audited kernel → semantic replay → Grade
              lattice → tuple/list split → sum-type receipts
  v13 : Stream merge with M40; codeword↔address bijection
  v14 : Theorem rescoped; GRADE_TOP → GRADE_IDENTITY; spec.replay seam
  v15 : Grade as meet-monoid; GRADE_STRONGEST_EVIDENCE; state cursor seam
  v16 : Orbit-canonical signature decomposition (Cayley-Dickson seam)
  v17 : Purity-wrap replay; obligation cap; cached tables; parity
        predicate; codeword↔signature bridge
  v18 : Transactional verification; full mutable-surface snapshot;
        bridge enforcement in verifier; ContentAddressedReceiptFields
  v19 : ────────────────────────────────────────────────────────────────────
        Formal V_4 ⋊ S_3 group foundation in s4_structure.py.

        PRIMARY STRUCTURE (the user's formalization confirmation):
            S_4 ≅ V_4 ⋊ S_3
        where V_4 is the Klein four normal subgroup of double-
        transpositions plus identity, and S_3 is realized as
        Stab(D) (the stabilizer of the anchor axis D). Every
        σ ∈ S_4 factors UNIQUELY as σ = v · s with v ∈ V_4,
        s ∈ Stab(D).

        The 24 valid (source, sink, witness) signatures are
        precisely the elements of S_4 via
            σ ∈ S_4 ↔ (σ(D), σ(C), σ(S))
        with σ(W) implicit as the "fourth" axis.

        DERIVED PRESENTATIONS:
          - Selection-sort descent S_4 → S_3 → S_2 → S_1 (axis-
            selection at each level — "geometric illustration").
          - v17 (orbit_key, v4_delta) decomposition (used lex-min
            canonical instead of Stab(D) canonical). The two
            decompositions agree on the orbit_key and differ on
            the v4_delta by a fixed orbit-specific V_4 element δ.

        HODGE DUAL OF THE 8 FORBIDDEN CODEWORDS:
        In dim 4, ★: Λ^3 → Λ^1. The 24 valid codewords are ordered
        triples (3-vectors with ordering); the 8 parity-forbidden
        codewords are signed singletons (1-vectors with chirality).
        Each signed singleton has 3 ordered-triple preimages (the
        cyclic orderings of the other 3 axes with matching sign),
        giving 24 = 8 × 3 from the dual side.

        CAYLEY-DICKSON CORRESPONDENCE:
        |S_n| vs 2^n grows as (1, 1, 2, 6, 24, 120) vs (1, 2, 4, 8, 16, 32).
        At level 4, S_4 sits inside 2^5 = 32 (the level-5 CD ambient).
        24 = 32 × 3/4 is the parity-sieve ratio; the 8 missing are
        the Hodge complement.

        AGREEMENT THEOREM (v17 ↔ v19):
        verify_v17_v19_decomposition_agreement: for every signature,
        the V_4 ⋊ S_3 factorization yields the same orbit_key as v17,
        and there is a consistent per-orbit V_4 element δ such that
        v17_v4_delta = v · δ (in V_4 multiplication). The δ values
        encode the choice-of-canonical difference (lex-min vs Stab(D)
        representative). The two decompositions are inter-derivable.
        ────────────────────────────────────────────────────────────────────
  v19.1-3 : Q_5 = P_4 ⊔ Hodge_complement; K_3 × K_4 cardinality match;
            32 = 8 × 4 unified V_4-presentation theorem
  v20 : StructuralAddress dataclass; three-constructor commutativity;
        codeword demoted to one chart on the address manifold
  v21 : Receipt obligation — every receipt carries address consistent
        with its codeword (auto-derived if not supplied)
  v21.1 : ───────────────────────────────────────────────────────────────────
        StructuralAddress is now UNSKIPPABLE in every receipt path:

        (1) compute_op_address_digest hashes the structural address
            content (op_name, codeword, signature, orbit_key, v4_delta),
            not just (op_name, codeword). The digest commits to the
            address; v22's PORTABLE locality will use this.

        (2) _check_codeword_bridge collapsed from re-derivation to
            address-equality. The verifier now checks that the address
            on the receipt equals the canonical one derived from the
            codeword — a single equality check instead of four
            consistency derivations.

        (3) verify_every_receipt_carries_structural_address aggregates
            the v21 obligations into one umbrella verifier:
              - receipt has non-None address consistent with codeword
              - construction rejects inconsistent address
              - derived properties (signature, orbit_key, v4_delta)
                delegate to the address
              - op_address_digest uses structural payload

        With this umbrella passing, no receipt path bypasses
        StructuralAddress. The bridge layer remains as a verifier
        but is no longer load-bearing; it now confirms what
        construction already ensures.
        ────────────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════════════════════
  M40 ↔ M41 RELATIONSHIP (v13/v14 — load-bearing distinction)
═══════════════════════════════════════════════════════════════════════════════

The M38 codeword space (M41's address layer) has 24 valid elements. The
M40 spectral closure (spectral_view v6) also has 24 elements. These
cardinalities match, but their GROUP STRUCTURES differ:

  M38 codeword space under {v4_swap, invert, chain}:
      V_4 × S_3       (chain is chirality-dependent — see unified_address:
                       Z3_NEXT_PAIRING_ODD reverses Z3_NEXT_PAIRING_EVEN.
                       This makes (chirality, pairing) into S_3 = Z_3 ⋊ Z_2.)

  M40 spectral closure under {V_4 translations, Z_3 cycle, chirality}:
      A_4 × Z_2 = (V_4 ⋊ Z_3) × Z_2   (the Z_3 cycle conjugates V_4 — see
                                       spectral_view.a4z2_compose. Chirality
                                       is a separate central Z_2 factor.)

Both groups have order 24. They are NOT isomorphic, as witnessed by their
element-order distributions:

      V_4 × S_3     {1:1, 2:15, 3:2, 6:6}     no order-4 elements
      A_4 × Z_2     {1:1, 2:7,  3:8, 6:8}     no order-4 elements
      S_4           {1:1, 2:9,  3:8, 4:6}     six order-4 elements

The bridge between M38 codewords and M40 algebraic elements is a SET
BIJECTION at the level of LABELS:

      bit 4 (chirality)   ↔   sign      (even=+1, odd=-1)
      bits 2-3 (pairing)  ↔   j ∈ Z_3   (α=0, β=1, γ=2; pairing=11 invalid)
      bits 0-1 (witness)  ↔   m ∈ V_4   (D=0, C=1, S=2, W=3)

This bijection is a LABELING correspondence between two 24-element sets —
same coordinate carrier cardinality, NOT the same algebraic object. The
multiplication laws differ: M38's group operations and M40's group
operations produce different element-order distributions. The applied
grammar uses codewords as ADDRESSES (labels for operations), not as group
elements composed under any law. Verification cares about set membership
(every codeword is in the valid 24) and label correctness (each receipt's
codeword matches its op_name), not about which group structure the
addresses carry.

What v13/v14 do:
  - Decode M38 codewords into (sign, m, j) algebraic coordinates
  - Encode (sign, m, j) back into M38 codewords
  - Verify the set bijection exhaustively (all 24 round-trip)
  - Aggregate the M41 receipt-kernel admissibility into one verifier
  - Name the M38/M40 structural distinction openly

What v13/v14 do NOT do (named):
  - Prove the grammar is globally well-typed (v14's renamed theorem is
    explicit about scoping to the receipt/address verification kernel)
  - Identify M38's group structure with M40's (they are different groups)
  - Derive the architectural exclusion of odd permutations from the
    M30-M37 operation registry (still an axiom — see M40 v6 note)
  - PORTABLE locality; populated EFFECT_REPLAY_VERIFIED implementations
    (the SEAM is added in v14; actual spec.replay implementations require
    chart rollback semantics — v15+)
  - Capability-style replay context (monkey-patch from v12 retained)
"""

import hashlib
import uuid
import weakref
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any, Callable, Union, FrozenSet
from chart_chained import ChartChained
from unified_address import encode_op, UnifiedCodeword
import sys as _sv_sys, os as _sv_os  # spectral_view promoted scratch → jea/metalanguage/ (Ξ7)
_sv_sys.path.insert(0, _sv_os.path.join(_sv_os.path.dirname(_sv_os.path.abspath(__file__)), "jea", "metalanguage"))
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

# effect_level (v15: sharpened semantics)
#
# EFFECT_INAPPLICABLE
#     The unit of the effect-meet monoid: "no effect obligation was
#     claimed." NOT "stronger evidence than REPLAY_VERIFIED." On the
#     evidence-strength order, this is the WEAKEST (no claim); on the
#     meet-induced order, it is the strongest (unit absorbs nothing).
#     The two orders disagree on this axis — see GRADE_IDENTITY vs.
#     GRADE_STRONGEST_EVIDENCE below.
#
# EFFECT_REPLAY_VERIFIED
#     The strongest evidence-strength claim: a spec.replay implementation
#     re-executed the effect and confirmed it. Only reachable when
#     StateOpSpec.replay is populated and returns True.
#
# EFFECT_RECEIPT_DECLARED (v15: sharpened)
#     "Digest fields are PRESENT in the receipt; relation to current
#     chart state is NOT verified." The receipt declares pre/post
#     digests, but no machinery has confirmed these describe real
#     chart states. The state cursor (v15) chains these structurally
#     across receipts but does not verify the relation to the chart.
#     Replay (v15+ per spec) would verify the relation.
#
# EFFECT_UNVERIFIED
#     Claim could not be classified above; reserved.
#
# FAILED_EFFECT
#     Replay was attempted and returned False, or raised.
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

# v22: registry-domain separator for structural-address digests.
# Two unrelated grammars with the same op_name and same codeword/address
# would otherwise produce identical digests. The domain separator
# distinguishes registries so that "PORTABLE across instances" means
# "across instances of THIS grammar," not "across any grammar that
# happens to share namespace."
REGISTRY_DOMAIN: str = "m41.applied_grammar/v22"


# Ranks for evidence-strength order (used inside Grade.meet)
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
# Grade — four-axis meet-monoid (v15: not meet-semilattice)
# ============================================================
#
# Grade is a MEET-MONOID: an associative meet operation with an
# identity element. It is NOT presented as a meet-semilattice because
# the meet-induced order disagrees with the epistemic evidence-strength
# order on the effect axis.
#
# TWO ORDERS ON Grade:
#
#   (1) MEET-INDUCED ORDER
#       a ≤_meet b   iff   a.meet(b) == a
#       Under this order, GRADE_IDENTITY is the maximum element (top)
#       because meeting it with anything yields that thing (identity
#       law), so for all g, g ≤_meet GRADE_IDENTITY.
#
#   (2) EVIDENCE-STRENGTH ORDER
#       Per-axis monotone rank, where higher rank = stronger evidence:
#         transition: FAILED < ADDRESS < SEM_REPLAY < REPLAY_VERIFIED
#         purity:     FAILED < EXTENDING < PURE
#         locality:   FAILED < LOCAL < PORTABLE
#         effect:     FAILED < UNVERIFIED < DECLARED < REPLAY_VERIFIED
#       Note: EFFECT_INAPPLICABLE is WEAKEST under this order (no
#       claim made), but the MEET-MONOID identity (because the meet
#       special-cases it as unit-like rather than monotone).
#
# These orders AGREE on transition, purity, locality (the ranks are
# straightforwardly monotone). They DISAGREE only on the effect axis,
# at the EFFECT_INAPPLICABLE special case.
#
# Practical consequences:
#   - For accumulation across a trace: use Grade.meet (meet-monoid).
#   - For "is this the strongest possible evidence?": compare against
#     GRADE_STRONGEST_EVIDENCE (defined below), NOT GRADE_IDENTITY.

@dataclass(frozen=True)
class Grade:
    """Four-axis meet-monoid for verification grades.

    Composition under meet is associative with identity GRADE_IDENTITY.
    The meet-induced order makes GRADE_IDENTITY top of the meet order,
    but this is NOT the same as evidence-strength maximum on the effect
    axis. See module-level commentary above for the two-order story.
    """
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


GRADE_IDENTITY = Grade(REPLAY_VERIFIED, CHART_PURE, PORTABLE, EFFECT_INAPPLICABLE)
# GRADE_IDENTITY (v14 rename of GRADE_TOP; v15 clarified):
# The IDENTITY element of the meet-monoid. Under the meet-induced order,
# this is also the top (since a.meet(GRADE_IDENTITY) == a means
# a ≤_meet GRADE_IDENTITY for all a). However:
#   - The effect component is EFFECT_INAPPLICABLE, which under the
#     EVIDENCE-STRENGTH order is the WEAKEST claim (no claim made).
#   - The transition/purity/locality components ARE the strongest
#     under both orders.
# So GRADE_IDENTITY is "top of meet-order", NOT "strongest evidence".
# For the latter, use GRADE_STRONGEST_EVIDENCE below.
#
# Algebraic identities (all tested):
#   For all g: GRADE_IDENTITY.meet(g) == g
#   For all g: g.meet(GRADE_IDENTITY) == g
#   GRADE_IDENTITY.meet(GRADE_IDENTITY) == GRADE_IDENTITY


GRADE_STRONGEST_EVIDENCE = Grade(REPLAY_VERIFIED, CHART_PURE, PORTABLE, EFFECT_REPLAY_VERIFIED)
# GRADE_STRONGEST_EVIDENCE (v15 added):
# The strongest evidence claim achievable on every axis simultaneously:
#   - REPLAY_VERIFIED        : ID-exact term replay matched
#   - CHART_PURE             : verification did not perturb chart state
#   - PORTABLE               : cross-process identity (currently NOT
#                              achievable in v15 — requires content-
#                              addressed cell digests)
#   - EFFECT_REPLAY_VERIFIED : effect re-executed and confirmed (requires
#                              spec.replay populated and returning True;
#                              v14 added the seam, v15+ populates specs)
#
# This is what we mean by "strongest evidence." It is DIFFERENT from
# GRADE_IDENTITY (whose effect component is EFFECT_INAPPLICABLE).
#
# Under the meet operation:
#   GRADE_STRONGEST_EVIDENCE.meet(GRADE_IDENTITY)
#     == Grade(REPLAY_VERIFIED, CHART_PURE, PORTABLE,
#              _meet_effect(EFFECT_REPLAY_VERIFIED, EFFECT_INAPPLICABLE))
#     == GRADE_STRONGEST_EVIDENCE
# i.e., meeting with the identity preserves the stronger effect claim.


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


def compute_structural_address_digest(
    op_name: str,
    address: 'StructuralAddress',
    *,
    registry_domain: str = REGISTRY_DOMAIN,
) -> str:
    """v22: address-primary digest. Hashes the structural address content
    together with the op_name and a registry-domain separator.

    The `registry_domain` parameter prevents accidental cross-registry
    collisions: two unrelated grammars that happen to encode different
    semantic ops to the same codeword can be distinguished by their
    registry domain. Default is the module-level REGISTRY_DOMAIN constant;
    callers with isolated registries can pass a different domain string.

    Two receipts share this digest iff they have the same op_name AND
    the same StructuralAddress AND were constructed under the same
    registry domain. This is the prerequisite for v22's PORTABLE
    locality grade: a digest match across instances signals structural
    equivalence, not just codeword equality.

    The digest payload commits to:
        (registry_domain, op_name, address.codeword, address.signature,
         address.orbit_key, address.v4_delta)

    This is the load-bearing address-first digest. compute_op_address_digest
    is now a thin caller-level convenience that resolves op_name through
    a chart's registry, then delegates here.
    """
    payload = (
        registry_domain,
        op_name,
        address.codeword,
        address.signature,
        address.orbit_key,
        address.v4_delta,
    )
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def compute_op_address_digest(c: ChartChained, op_name: str) -> str:
    """Caller-level convenience: resolve op_name through chart's registry,
    then delegate to compute_structural_address_digest.

    For unknown op_names, returns the zero-digest (legacy behavior
    preserved for resilience under registry drift).

    v22 note: the load-bearing digest function is now
    compute_structural_address_digest(op_name, address). This wrapper
    exists so existing callsites that have a chart in hand don't need
    to look up the codeword themselves.
    """
    try:
        code = _op_codeword(c, op_name)
    except KeyError:
        return "0" * 64
    addr = structural_address_from_codeword(code)
    return compute_structural_address_digest(op_name, addr)


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

    v14: adds the `replay` seam — an optional callable that, given the
    chart and a StateReceipt, returns True iff the state mutation can
    be re-executed and produce the receipt's post-state digest.

    The seam splits effect verification into three observable outcomes:
        spec.replay is None         → EFFECT_RECEIPT_DECLARED  (typed only)
        spec.replay returns True    → EFFECT_REPLAY_VERIFIED   (effect re-checked)
        spec.replay returns False   → FAILED_EFFECT            (mismatch)
        spec.replay raises          → FAILED_EFFECT            (replay broken)

    All v14 specs ship with replay=None. Populating individual specs
    with real replay implementations is v15+ work — each requires the
    ability to roll back the chart and re-execute the op deterministically.

    obligation_level is the MAXIMUM effect_level the spec can witness.
    A spec with replay=None caps at EFFECT_RECEIPT_DECLARED. A spec
    with replay populated and obligation_level=EFFECT_REPLAY_VERIFIED
    promises that, when replay returns True, the effect is genuinely
    re-verified, not merely declared.
    """
    name: str
    obligation_level: str  # max effect_level the spec can witness
    replay: Optional[Callable[[ChartChained, 'StateReceipt'], bool]] = None


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
# v13: Codeword ↔ algebraic address bijection
# ============================================================
#
# Bridge between the M38 codeword space (this module's address layer) and
# the M40 algebraic parameter space (spectral_view's A_4 × Z_2 element form).
#
# This is a SET bijection between 24 labels, not a group homomorphism.
# See "M40 ↔ M41 RELATIONSHIP" in the module docstring.
#
# Bit layout (M38 codeword, 5 bits):
#     bit 4    : chirality   (0=even, 1=odd)
#     bits 2-3 : pairing     (00=α, 01=β, 10=γ; 11=invalid)
#     bits 0-1 : witness     (00=D, 01=C, 10=S, 11=W)
#
# Algebraic decomposition (M40 coordinates):
#     sign   ∈ {+1, -1}   ←   chirality bit (even=+1, odd=-1)
#     j      ∈ {0, 1, 2}  ←   pairing bits
#     m      ∈ {0, 1, 2, 3} ← witness bits

def codeword_to_address(code: int) -> Tuple[int, int, int]:
    """Decode M38 codeword into (sign, m, j) algebraic coordinates.

    Returns:
        (sign, m, j) where sign ∈ {±1}, m ∈ {0..3}, j ∈ {0..2}

    Raises:
        ValueError: if code is out of range or has invalid pairing bits (11).
    """
    if not (0 <= code < 32):
        raise ValueError(f"codeword {code} out of range [0, 32)")
    chirality_bit = (code >> 4) & 1
    pairing_bits = (code >> 2) & 0b11
    witness_bits = code & 0b11

    if pairing_bits == 0b11:
        raise ValueError(
            f"codeword {code:05b} has invalid pairing bits 11 "
            f"(not in the 24 valid codewords)"
        )

    sign = 1 if chirality_bit == 0 else -1
    m = witness_bits
    j = pairing_bits
    return (sign, m, j)


def address_to_codeword(sign: int, m: int, j: int) -> int:
    """Encode (sign, m, j) algebraic coordinates into M38 codeword.

    Raises:
        ValueError: if any coordinate is out of range.
    """
    if sign not in (1, -1):
        raise ValueError(f"sign must be ±1, got {sign}")
    if not (0 <= m < 4):
        raise ValueError(f"m must be in [0, 4), got {m}")
    if not (0 <= j < 3):
        raise ValueError(f"j must be in [0, 3), got {j}")
    chirality_bit = 0 if sign == 1 else 1
    return (chirality_bit << 4) | (j << 2) | m


def receipt_address(r) -> Tuple[int, int, int]:
    """Decode a receipt's codeword into algebraic coordinates.

    Works on any Receipt subtype (TermReceipt / StateReceipt /
    ObservationReceipt) — only the codeword field is read.
    """
    return codeword_to_address(r.codeword)


def all_valid_codewords() -> List[int]:
    """All 24 valid M38 codewords (those with pairing bits != 11)."""
    return [code for code in range(32) if ((code >> 2) & 0b11) != 0b11]


def all_algebraic_addresses() -> List[Tuple[int, int, int]]:
    """All 24 (sign, m, j) algebraic addresses."""
    return [(s, m, j) for s in (1, -1) for j in range(3) for m in range(4)]


def verify_codeword_address_bijection() -> bool:
    """The 24 valid M38 codewords ↔ 24 (sign, m, j) addresses bijectively.

    Exhaustive over all 24 codewords and all 24 algebraic addresses:
      - len(valid codewords) == 24
      - codeword_to_address is injective on the 24 valid codewords
      - address_to_codeword(*codeword_to_address(c)) == c for all 24 valid c
      - codeword_to_address(address_to_codeword(s, m, j)) == (s, m, j) for all 24
      - The image is exactly the 24 (sign, m, j) addresses
      - Invalid codewords (pairing=11) raise ValueError
    """
    valid = all_valid_codewords()
    if len(valid) != 24:
        return False

    # Forward: codewords → addresses, injective
    addresses_from_codes = set()
    for code in valid:
        addr = codeword_to_address(code)
        addresses_from_codes.add(addr)
        # Round-trip codeword → address → codeword
        if address_to_codeword(*addr) != code:
            return False
    if len(addresses_from_codes) != 24:
        return False

    # Backward: addresses → codewords → addresses
    expected_addresses = set(all_algebraic_addresses())
    if addresses_from_codes != expected_addresses:
        return False
    for addr in expected_addresses:
        code = address_to_codeword(*addr)
        if codeword_to_address(code) != addr:
            return False

    # Invalid codewords (pairing=11) raise
    for code in range(32):
        if ((code >> 2) & 0b11) == 0b11:
            try:
                codeword_to_address(code)
                return False  # should have raised
            except ValueError:
                pass

    return True


def verify_all_registry_ops_have_valid_codewords(c: ChartChained) -> bool:
    """Every operation in the chart's registry has a codeword in the
    valid 24-element set. This is the architectural admissibility witness
    at the level of operation addresses."""
    for op in c.registry.all():
        code = encode_op(op).code
        if not UnifiedCodeword(code).is_valid:
            return False
        # Should successfully decode
        try:
            codeword_to_address(code)
        except ValueError:
            return False
    return True


# ============================================================
# v16: Orbit-canonical signature decomposition
# ============================================================
#
# The 24 valid (source, sink, witness) signatures live in the
# Cayley-Dickson ladder at level 2:
#
#     "real"      = witness label  (V_4,    2 bits)
#     "imaginary" = pairing       (V_4,    2 bits, parity-sieved)
#     chirality   = sign           (Z_2,    1 bit)
#
# Naive product: 2^5 = 32. Parity sieve forbids pairing=11 (the fourth
# pairing — the case where "no V_4 quotient is consumed by the triple").
# 32 × 3/4 = 24 valid signatures. NOT 8 × 3 with awkward Z_3; it is
# the parity quotient of a full V_4 × V_4 × Z_2.
#
# Under V_4 axis-swap action, the 24 signatures partition into 6 orbits
# of 4 signatures each:
#     6 V_4 orbits  =  3 pairings × 2 chiralities
#     4 V_4-deltas  =  the witness offset from canonical
#
# Each signature decomposes uniquely:
#     signature  ↔  ((pairing, chirality), v4_delta)
#
# where:
#     (pairing, chirality)  is the V_4-INVARIANT content of the op
#     v4_delta              is the V_4 swap mapping canonical → actual
#
# Canonical signature within an orbit = lex-min over the 4 V_4-translates
# (the "left-choice" of the Cayley-Dickson framing — alphabetically
# earliest signature). Together with the orbit-key, this gives an
# orbit-canonical content address.
#
# This is the seam from raw addresses (cell IDs, codewords) toward
# PORTABLE-locality content-addressed identifiers. Two receipts with
# V_4-equivalent signatures share the same orbit-key; their differing
# v4_delta records the witness offset.

from meta_protocol import (
    AXES, V4_SWAPS, PAIRINGS,
    validate_signature, chirality_of, opposite_pair,
)
from unified_address import (
    AXIS_TO_LABEL, LABEL_TO_AXIS,
    PAIRING_TO_BITS, BITS_TO_PAIRING,
)


OrbitKey = Tuple[str, str]        # (pairing, chirality)
Signature = Tuple[str, str, str]  # (source, sink, witness)


# ----- raw enumeration (used once at module load to build cached tables) -----

def _enumerate_valid_signatures() -> List[Signature]:
    """Enumerate all valid (source, sink, witness) triples.

    Used once at module load to build cached tables. Direct callers
    should use all_valid_signatures() which reads from the cache.
    """
    sigs = []
    for s in AXES:
        for t in AXES:
            if s == t:
                continue
            for w in AXES:
                if w in (s, t):
                    continue
                try:
                    validate_signature(s, t, w)
                    sigs.append((s, t, w))
                except Exception:
                    pass
    return sigs


def _v4_swap_signature(sig: Signature, swap_name: str) -> Signature:
    """Apply a V_4 axis-swap to a signature componentwise."""
    swap = V4_SWAPS[swap_name]
    s, t, w = sig
    return (swap[s], swap[t], swap[w])


@dataclass(frozen=True)
class CanonicalDecomposition:
    """Orbit-canonical decomposition of a signature.

    The signature is uniquely determined by:
      - orbit_key: (pairing, chirality) — V_4-invariant content
      - v4_delta:  V_4 swap name (witness offset from canonical)

    Combined: signature = _v4_swap_signature(canonical, v4_delta)
    where canonical = lex-min over the V_4 orbit.
    """
    orbit_key: OrbitKey
    v4_delta: str

    def to_signature(self) -> Signature:
        canonical = _ORBIT_TABLE[self.orbit_key]['e']
        return _v4_swap_signature(canonical, self.v4_delta)


# ----- cached tables (built once at module load, v17) -----

def _build_orbit_tables() -> Tuple[
    Dict[OrbitKey, Dict[str, Signature]],
    Dict[Signature, CanonicalDecomposition],
]:
    """Build the canonical orbit tables once at module load.

    Returns:
      orbit_table:  orbit_key → {v4_delta_name → signature}
      decomp_table: signature → CanonicalDecomposition

    The canonical signature in each orbit (delta='e') is the lex-min
    of the orbit's V_4-translates. Other deltas record the V_4 swap
    that maps canonical → actual.
    """
    sigs = _enumerate_valid_signatures()

    # Group by orbit_key = (pairing, chirality)
    orbits_by_key: Dict[OrbitKey, List[Signature]] = {}
    for sig in sigs:
        s, t, w = sig
        _, pairing = opposite_pair(s, t)
        chir = chirality_of(s, t, w)
        orbits_by_key.setdefault((pairing, chir), []).append(sig)

    orbit_table: Dict[OrbitKey, Dict[str, Signature]] = {}
    decomp_table: Dict[Signature, CanonicalDecomposition] = {}
    for key, members in orbits_by_key.items():
        canonical = min(members)
        delta_to_sig: Dict[str, Signature] = {}
        for swap_name in V4_SWAPS:
            transformed = _v4_swap_signature(canonical, swap_name)
            delta_to_sig[swap_name] = transformed
            decomp_table[transformed] = CanonicalDecomposition(
                orbit_key=key, v4_delta=swap_name
            )
        orbit_table[key] = delta_to_sig

    return orbit_table, decomp_table


_ORBIT_TABLE, _SIGNATURE_DECOMP_TABLE = _build_orbit_tables()


# ----- accessors (read from cached tables) -----

def all_valid_signatures() -> List[Signature]:
    """All 24 valid (source, sink, witness) triples.

    v17: reads from cached _SIGNATURE_DECOMP_TABLE rather than
    re-enumerating on each call.
    """
    return sorted(_SIGNATURE_DECOMP_TABLE.keys())


def orbit_key_of(sig: Signature) -> OrbitKey:
    """The V_4-invariant content of a signature: (pairing, chirality).

    v17: O(1) lookup via cached table.
    """
    return _SIGNATURE_DECOMP_TABLE[sig].orbit_key


def canonical_signature_in_orbit(orbit_key: OrbitKey) -> Signature:
    """Return the canonical (lex-min) signature in the V_4 orbit.

    v17: O(1) lookup via cached table. Canonical = the orbit's
    member with delta='e'.
    """
    return _ORBIT_TABLE[orbit_key]['e']


def v4_delta_to_canonical(sig: Signature) -> str:
    """Return the V_4 swap name mapping canonical → sig.

    v17: O(1) lookup via cached table.
    """
    return _SIGNATURE_DECOMP_TABLE[sig].v4_delta


def decompose_signature(sig: Signature) -> CanonicalDecomposition:
    """Decompose a signature into (orbit_key, v4_delta).

    v17: O(1) lookup via cached table.
    """
    return _SIGNATURE_DECOMP_TABLE[sig]


def recompose_signature(orbit_key: OrbitKey, v4_delta: str) -> Signature:
    """Inverse of decompose_signature.

    v17: O(1) lookup via cached table.
    """
    return _ORBIT_TABLE[orbit_key][v4_delta]


def signatures_in_orbit(orbit_key: OrbitKey) -> List[Signature]:
    """The 4 signatures in the V_4 orbit identified by orbit_key.

    v17: returned in delta order ('e', 'α', 'β', 'γ').
    """
    return [_ORBIT_TABLE[orbit_key][d] for d in ('e', 'α', 'β', 'γ')]


def all_orbit_keys() -> List[OrbitKey]:
    """The 6 V_4 orbit-keys: 3 pairings × 2 chiralities."""
    return sorted(_ORBIT_TABLE.keys())


def verify_signature_decomposition_bijection() -> bool:
    """The 24 valid signatures bijectively correspond to
    {6 orbit-keys} × {4 V_4-deltas}.

    Exhaustive: decompose ∘ recompose = id on signatures,
    recompose ∘ decompose = id on (orbit_key, v4_delta) pairs,
    table sizes correct, all keys/deltas exercised.
    """
    sigs = all_valid_signatures()
    if len(sigs) != 24:
        return False
    for sig in sigs:
        decomp = decompose_signature(sig)
        if recompose_signature(decomp.orbit_key, decomp.v4_delta) != sig:
            return False
    decomps = {decompose_signature(sig) for sig in sigs}
    if len(decomps) != 24:
        return False
    if len({d.orbit_key for d in decomps}) != 6:
        return False
    if {d.v4_delta for d in decomps} != set(V4_SWAPS.keys()):
        return False
    from collections import Counter
    orbit_sizes = Counter(orbit_key_of(sig) for sig in sigs)
    return set(orbit_sizes.values()) == {4}


# ============================================================
# v17: Parity-sieve predicate (item 5 from audit)
# ============================================================
#
# The 24 = 32 × 3/4 split is now a named predicate, not commentary.
# A codeword is parity-forbidden iff its pairing bits are 11 — the
# case where no V_4 quotient is consumed by the triple. The fourth
# "pairing" (the one not in PAIRINGS) has no consistent (source,
# sink, witness) realization because all four axes would have to be
# simultaneously in use, leaving no axis as the "quotiented remainder."

def is_parity_forbidden(code: int) -> bool:
    """A codeword is parity-forbidden iff its pairing bits == 11.

    The triple (source, sink, witness) consumes three of the four
    V_4 axes; the fourth is the "quotiented remainder" used to
    compute chirality. The pairing bits encode which V_4 pair is
    NOT containing the witness — i.e., which pair contains (source,
    sink). The fourth pattern (pairing bits = 11) corresponds to
    "no V_4 quotient is consumed," which is structurally impossible
    for a valid triple. The parity sieve excludes these 8 codewords.
    """
    return (code >> 2) & 0b11 == 0b11


def verify_parity_sieve_characterization() -> bool:
    """The 8 invalid codewords are EXACTLY those with pairing bits = 11.

    This is the structural characterization of the parity sieve:
      32 total codewords   = 5 bits
       8 parity-forbidden  = (2 chirality) × (1 pairing pattern) × (4 witness)
      24 valid             = 32 × 3/4
    """
    valid_codewords = set(all_valid_codewords())
    forbidden_via_predicate = {c for c in range(32) if is_parity_forbidden(c)}
    valid_via_predicate = {c for c in range(32) if not is_parity_forbidden(c)}

    if len(forbidden_via_predicate) != 8:
        return False
    if valid_via_predicate != valid_codewords:
        return False
    # No valid codeword is parity-forbidden; no invalid one is parity-allowed
    for code in valid_codewords:
        if is_parity_forbidden(code):
            return False
    return True


# ============================================================
# v17: Codeword ↔ signature bridge (item 1 from audit)
# ============================================================
#
# Before v17: codeword ↔ (sign, m, j)  via codeword_to_address
#            signature ↔ (orbit_key, v4_delta)  via decompose_signature
# After v17:  codeword ↔ signature ↔ (orbit_key, v4_delta)
#
# The bridge is determined entirely by the bit-encoding:
#   chirality bit  : determines source/sink ordering within the (source, sink) pair
#   pairing bits   : determine which V_4 pair contains (source, sink)
#                    (the witness is in the OTHER pair)
#   witness bits   : the V_4 axis serving as witness
#
# Receipts still carry raw codewords (the v18+ refactor is to add
# orbit_key/v4_delta as first-class fields); v17 lets us decompose
# any receipt's codeword on the fly. The bridge composes cleanly:
#   codeword → signature → CanonicalDecomposition

def codeword_to_signature(code: int) -> Signature:
    """Map a valid M38 codeword to its (source, sink, witness) signature.

    Decoding (v18: prose tightened):
      • chirality bit (bit 4): the sign of the permutation
        [source, sink, witness, fourth]. Picks ONE of the two
        orderings (s, t) vs (t, s) of the (source, sink) pair.
      • pairing bits (bits 2-3): identify the PARTITION of {D, C, S, W}
        into two pairs. PAIRINGS[pairing] = (pair1, pair2). One of
        these pairs contains the witness; the OTHER contains (source,
        sink). The pairing bits do NOT directly identify which pair
        is (source, sink); they identify the partition, and the
        witness tells us which side of the partition is the witness
        pair (so the other side is the source/sink pair).
      • witness bits (bits 0-1): the V_4 axis serving as witness.
    """
    if is_parity_forbidden(code):
        raise ValueError(
            f"codeword 0b{code:05b} is parity-forbidden (pairing bits = 11)"
        )

    chir_bit = (code >> 4) & 1
    chir = 'odd' if chir_bit else 'even'
    pairing_bits = (code >> 2) & 0b11
    pairing = BITS_TO_PAIRING[pairing_bits]
    witness_bits = code & 0b11
    witness = LABEL_TO_AXIS[witness_bits]

    # The pairing identifies the PARTITION (pair1, pair2). The witness
    # is in one of the two pairs; the (source, sink) pair is the OTHER
    # one. Chirality picks which ordering of (source, sink) is meant.
    pair1, pair2 = PAIRINGS[pairing]
    source_sink_pair = pair2 if witness in pair1 else pair1
    candidates = sorted(source_sink_pair)

    # Two candidate orderings; chirality picks one.
    for (s, t) in [(candidates[0], candidates[1]), (candidates[1], candidates[0])]:
        try:
            validate_signature(s, t, witness)
        except Exception:
            continue
        if chirality_of(s, t, witness) == chir:
            return (s, t, witness)

    raise ValueError(
        f"no valid signature for codeword 0b{code:05b}: "
        f"chirality={chir}, pairing={pairing}, witness={witness}"
    )


def signature_to_codeword(sig: Signature) -> int:
    """Map a signature to its M38 codeword (inverse of codeword_to_signature)."""
    s, t, w = sig
    _, pairing = opposite_pair(s, t)
    chir = chirality_of(s, t, w)
    chir_bit = 1 if chir == 'odd' else 0
    pairing_bits = PAIRING_TO_BITS[pairing]
    witness_bits = AXIS_TO_LABEL[w]
    return (chir_bit << 4) | (pairing_bits << 2) | witness_bits


def codeword_to_orbit_decomposition(code: int) -> CanonicalDecomposition:
    """Compose the bridge: codeword → signature → orbit decomposition.

    This is the v17 architectural step: every receipt's codeword now
    decomposes orbit-canonically. Receipts still carry raw codewords;
    v17 lets us derive (orbit_key, v4_delta) on demand from any receipt.
    v18+ will refactor receipts to carry these as first-class fields.
    """
    sig = codeword_to_signature(code)
    return decompose_signature(sig)


def verify_codeword_signature_bijection() -> bool:
    """Roundtrip: codeword → signature → codeword = identity (24 cases).
    Roundtrip: signature → codeword → signature = identity (24 cases).
    """
    for code in all_valid_codewords():
        sig = codeword_to_signature(code)
        if signature_to_codeword(sig) != code:
            return False
    for sig in all_valid_signatures():
        code = signature_to_codeword(sig)
        if codeword_to_signature(code) != sig:
            return False
    return True


def verify_codeword_orbit_bridge_consistent() -> bool:
    """The bridge composes coherently with bit-level structure:

      For every valid codeword c, codeword_to_orbit_decomposition(c)
      returns a CanonicalDecomposition d such that:
        d.orbit_key.chirality matches the chirality bit of c
        d.orbit_key.pairing   matches the pairing bits of c

    This is the bridge invariant the user named:
      receipt.orbit_key == orbit_key_of(receipt.signature)
    """
    for code in all_valid_codewords():
        decomp = codeword_to_orbit_decomposition(code)
        chir_bit = (code >> 4) & 1
        expected_chir = 'odd' if chir_bit else 'even'
        if decomp.orbit_key[1] != expected_chir:
            return False
        pairing_bits = (code >> 2) & 0b11
        expected_pairing = BITS_TO_PAIRING[pairing_bits]
        if decomp.orbit_key[0] != expected_pairing:
            return False
    return True


# ============================================================
# v18: ContentAddressedReceiptFields + orbit_canonical_digest
# ============================================================

def orbit_canonical_digest(orbit_key: OrbitKey) -> str:
    """Stable, content-addressed digest of an orbit_key.

    Two receipts whose codewords decompose to the same orbit_key
    produce the same orbit_canonical_digest. Process- and chart-
    independent (V_4-equivalent operations are identified).

    v19.1: uses _canonical_bytes for codec uniformity with all other
    digests in the module. The earlier f-string formatting was stable
    locally but would have become an accidental second codec.
    """
    return hashlib.sha256(_canonical_bytes(("orbit", orbit_key))).hexdigest()


@dataclass(frozen=True)
class ContentAddressedReceiptFields:
    """v18: derivable content-addressed fields for a receipt.

    All four fields are determined by a receipt's codeword. Producing
    them at receipt-construction time would make a receipt's identity
    portable across charts and processes. v18 makes the fields
    derivable and optionally attachable; v19+ refactors receipt
    constructors to populate them by default.

    Fields:
      signature              : (source, sink, witness) — codeword-derived
      orbit_key              : (pairing, chirality) — V_4-invariant content
      v4_delta               : V_4 swap name (witness offset from canonical)
      orbit_canonical_digest : hash of orbit_key — equal across V_4-twins
    """
    signature: Signature
    orbit_key: OrbitKey
    v4_delta: str
    orbit_canonical_digest: str


def derive_content_addressed_fields(codeword: int) -> ContentAddressedReceiptFields:
    """Build the ContentAddressedReceiptFields for a codeword.

    Composes the v17 bridge with v18's orbit_canonical_digest:
      codeword → signature → (orbit_key, v4_delta) → orbit_canonical_digest

    Receipt construction (v19+) should call this and attach the result
    as a content_addressed field. The verifier already checks the
    attached fields for consistency (see _check_codeword_bridge).
    """
    sig = codeword_to_signature(codeword)
    decomp = decompose_signature(sig)
    return ContentAddressedReceiptFields(
        signature=sig,
        orbit_key=decomp.orbit_key,
        v4_delta=decomp.v4_delta,
        orbit_canonical_digest=orbit_canonical_digest(decomp.orbit_key),
    )


def verify_content_addressed_fields_for_all_codewords() -> bool:
    """For every valid codeword, derive_content_addressed_fields produces
    a self-consistent ContentAddressedReceiptFields where:
        signature → codeword roundtrip is identity
        orbit_key == orbit_key_of(signature)
        v4_delta  == v4_delta_to_canonical(signature)
        orbit_canonical_digest == orbit_canonical_digest(orbit_key)
    """
    for code in all_valid_codewords():
        f = derive_content_addressed_fields(code)
        if signature_to_codeword(f.signature) != code:
            return False
        if orbit_key_of(f.signature) != f.orbit_key:
            return False
        if v4_delta_to_canonical(f.signature) != f.v4_delta:
            return False
        if orbit_canonical_digest(f.orbit_key) != f.orbit_canonical_digest:
            return False
    return True


# ============================================================
# v19: agreement between V_4 ⋊ S_3 factorization and v17 decomposition
# ============================================================
#
# The formal V_4 ⋊ S_3 factorization (in s4_structure) and the v17
# (orbit_key, v4_delta) decomposition use different canonical-within-
# orbit conventions:
#   v17 canonical = lex-min signature in orbit
#   V_4 ⋊ S_3 canonical = Stab(D) representative
#
# Their orbit_keys agree exactly. Their v4_delta values differ by a
# fixed per-orbit δ ∈ V_4 that captures the canonical-choice offset.
#
# The agreement theorem proves these conventions are inter-derivable:
# for every signature, v17_v4_delta = v · δ_for_this_orbit in V_4
# multiplication, where v is the V_4 component from the V_4 ⋊ S_3
# factorization.

from s4_structure import (
    factor_s4 as _s4_factor,
    signature_to_permutation as _sig_to_perm,
    permutation_to_signature as _perm_to_sig,
    stab_d_to_orbit_key as _stab_d_to_key,
    Permutation as _Permutation,
    V4_AS_PERMUTATIONS as _V4_PERMS,
    V4_ELEMENT_TO_NAME as _V4_NAME,
    OrientedUnorderedTriple as _OUT,
    all_oriented_unordered_triples as _all_oriented,
    oriented_triple_of_forbidden_codeword as _oriented_of_forbidden,
    AXES as _AXES,
)


def v17_to_v4_s3(sig: Signature) -> Tuple[OrbitKey, str]:
    """Reproduce v17's decompose_signature output via V_4 ⋊ S_3.

    Steps:
      1. σ = signature_to_permutation(sig)
      2. (v, s) = factor_s4(σ)            — V_4 ⋊ S_3 factorization
      3. orbit_key = stab_d_to_orbit_key(s)
      4. v17's canonical in this orbit is lex-min (not Stab(D) rep).
         Express σ as δ · canonical_lex_min_perm where δ ∈ V_4. Then
         v17_v4_delta = name of δ.

    Returns (orbit_key, v17_v4_delta).
    """
    σ = _sig_to_perm(sig)
    v, s = _s4_factor(σ)
    orbit_key = _stab_d_to_key(s)
    # v17's canonical signature for this orbit (the lex-min)
    canonical_sig = canonical_signature_in_orbit(orbit_key)
    canonical_perm = _sig_to_perm(canonical_sig)
    # σ = δ_v17 · canonical_perm ⟹ δ_v17 = σ · canonical_perm⁻¹
    δ = σ.compose(canonical_perm.inverse())
    return orbit_key, _V4_NAME[δ]


def verify_v17_v19_decomposition_agreement() -> bool:
    """For every valid signature, v17's decompose_signature output
    equals what we derive from the V_4 ⋊ S_3 factorization via v17_to_v4_s3.

    Confirms the formal V_4 ⋊ S_3 structure underlies v17's presentation.
    """
    for sig in all_valid_signatures():
        v17_decomp = decompose_signature(sig)
        v19_orbit_key, v19_v4_delta = v17_to_v4_s3(sig)
        if v17_decomp.orbit_key != v19_orbit_key:
            return False
        if v17_decomp.v4_delta != v19_v4_delta:
            return False
    return True


def verify_canonical_offset_consistent_per_orbit() -> bool:
    """The δ that takes Stab(D) canonical → v17 lex-min canonical is
    consistent within each orbit.

    For each orbit, all 4 signatures share the same (v · stab_d_offset)
    structure, so the v17_delta = v · δ_orbit relation has a single
    δ_orbit ∈ V_4 per orbit.
    """
    per_orbit: Dict[OrbitKey, str] = {}
    for sig in all_valid_signatures():
        σ = _sig_to_perm(sig)
        v, s = _s4_factor(σ)
        orbit_key = _stab_d_to_key(s)
        v17_decomp = decompose_signature(sig)
        v17_v4_perm = _V4_PERMS[v17_decomp.v4_delta]
        # v17_v4_perm = v · δ_orbit ⟹ δ_orbit = v⁻¹ · v17_v4_perm
        δ_orbit_perm = v.inverse().compose(v17_v4_perm)
        δ_orbit_name = _V4_NAME[δ_orbit_perm]
        if orbit_key in per_orbit:
            if per_orbit[orbit_key] != δ_orbit_name:
                return False
        else:
            per_orbit[orbit_key] = δ_orbit_name
    return len(per_orbit) == 6


def canonical_offset_for_orbit(orbit_key: OrbitKey) -> str:
    """The V_4 element δ_orbit such that v17_canonical_perm = δ_orbit · stab_d_rep_perm.

    Computed on demand for any orbit_key. Used in the agreement proof.
    """
    from s4_structure import STAB_D
    canonical_sig = canonical_signature_in_orbit(orbit_key)
    canonical_perm = _sig_to_perm(canonical_sig)
    for s in STAB_D:
        if _stab_d_to_key(s) == orbit_key:
            δ = canonical_perm.compose(s.inverse())
            return _V4_NAME[δ]
    raise ValueError(f"no Stab(D) representative for {orbit_key}")


# ============================================================
# v19.3: unified V_4-presentation view of the 32-element codeword space
# ============================================================
#
# The user's correction: the 32 codewords are not "24 valid + 8 separate
# forbidden." They are 8 oriented unordered triples × 4 V_4 presentations:
#
#     32 = |oriented unordered triples| × |V_4| = 8 × 4
#
# Each oriented unordered triple has exactly 4 codeword presentations:
#   - 3 ordered-triple presentations (V_4 fibers α, β, γ — each with a
#     specific partition-pair {source, sink})
#   - 1 Hodge dual presentation (V_4 fiber ⊥, the compressed singleton)
#
# Equivalently: each V_4 fiber bijectively realizes all 8 oriented
# unordered triples. The construction view (24 + 8 = 32, "triadic plus
# Hodge completion") and the presentation view (8 × 4 = 32, "underlying
# triples with V_4-indexed views") describe the same structure.
# "It's not either/or. It's both."


def codeword_to_oriented_triple(code: int) -> _OUT:
    """Return the underlying oriented unordered triple of any codeword.

    For valid codewords: extract the unordered triple of the signature
    and the sign of its permutation.
    For forbidden codewords: extract the triple {CDSW \\ {axis}} and
    the singleton's sign.
    """
    if 0 <= code < 32:
        fiber = (code >> 2) & 0b11
        if fiber != 0b11:
            sig = codeword_to_signature(code)
            return (frozenset(sig), _sig_to_perm(sig).sign())
        return _oriented_of_forbidden(code)
    raise ValueError(f"codeword out of range: {code}")


def verify_v4_presentations_per_oriented_triple() -> bool:
    """Each oriented unordered triple has exactly 4 codeword presentations,
    one per V_4 fiber. THE LOAD-BEARING UNIFIED THEOREM.

    32 = |oriented unordered triples| × |V_4| = 8 × 4
    """
    from collections import defaultdict
    presentations: Dict[_OUT, set] = defaultdict(set)
    for code in range(32):
        oriented = codeword_to_oriented_triple(code)
        fiber = (code >> 2) & 0b11
        presentations[oriented].add(fiber)
    if len(presentations) != 8:
        return False
    return all(fibers == {0b00, 0b01, 0b10, 0b11} for fibers in presentations.values())


def verify_each_v4_fiber_covers_all_8_oriented_triples() -> bool:
    """Each V_4 fiber (8 codewords) bijectively covers all 8 oriented
    unordered triples. Dual statement of the unified theorem.
    """
    from collections import defaultdict
    fiber_to_triples: Dict[int, set] = defaultdict(set)
    for code in range(32):
        fiber = (code >> 2) & 0b11
        oriented = codeword_to_oriented_triple(code)
        fiber_to_triples[fiber].add(oriented)
    expected = set(_all_oriented())
    return (
        len(fiber_to_triples) == 4
        and all(triples == expected for triples in fiber_to_triples.values())
    )


def verify_codeword_count_factors_as_8_times_4() -> bool:
    """32 = 8 × 4 (oriented unordered triples × V_4 presentations).

    Confirms the unified structural decomposition: the codeword space
    is the product of underlying oriented triples and V_4-indexed
    presentations.
    """
    return len(_all_oriented()) * 4 == 32


# ============================================================
# v20: StructuralAddress — the receipt-ready structural object
# ============================================================
#
# The user's correction (post-v19.3): codewords are not primitive
# objects. They are coordinates on presentation choices. The PRIMARY
# object is the S_4 permutation; everything else is a projection or
# serialization:
#
#     permutation       — the underlying S_4 element (the OBJECT)
#     v4_component, s   — V_4 ⋊ S_3 factorization (intrinsic structure)
#     orbit_key         — quotient coordinate (S_4 / V_4 ≅ S_3)
#     v4_delta          — fiber coordinate (v17 lex-min convention)
#     signature         — projection (source, sink, witness)
#     codeword          — serialization (5-bit address)
#
# StructuralAddress carries all of these together as a single frozen
# object. Construction from any of (permutation, signature, codeword)
# produces the same result, witnessed by
# verify_structural_address_projections_commute.
#
# This is the seam for v21+: replace `codeword: int` in receipts with
# `address: StructuralAddress`. The codeword↔signature↔orbit bridge
# layer then disappears because the address carries all coordinates
# together; there is no longer a distinction between semantic object
# and address encoding, only between object and presentation/projection.


@dataclass(frozen=True)
class StructuralAddress:
    """The receipt-ready structural object.

    Carries the underlying S_4 permutation together with all its
    derived projections. All fields are mutually determined; the
    verifier `verify_structural_address_projections_commute` proves
    the commutative diagram closes for every valid signature.

    Fields:
      permutation:       the S_4 element (the underlying object)
      v4_component:      v ∈ V_4 in σ = v · s factorization
      stab_d_component:  s ∈ Stab(D) in σ = v · s factorization
      orbit_key:         (pairing, chirality) — S_3 quotient coordinate
      v4_delta:          V_4 fiber coordinate (v17 lex-min convention)
      signature:         (source, sink, witness) — projection
      codeword:          int — bit serialization
    """
    permutation: _Permutation
    v4_component: _Permutation
    stab_d_component: _Permutation
    orbit_key: OrbitKey
    v4_delta: str
    signature: Signature
    codeword: int


def structural_address_from_permutation(σ: _Permutation) -> StructuralAddress:
    """Build a StructuralAddress from an S_4 permutation (the primary form)."""
    v, s = _s4_factor(σ)
    sig = _perm_to_sig(σ)
    code = signature_to_codeword(sig)
    orbit_key, v4_delta = v17_to_v4_s3(sig)
    return StructuralAddress(
        permutation=σ,
        v4_component=v,
        stab_d_component=s,
        orbit_key=orbit_key,
        v4_delta=v4_delta,
        signature=sig,
        codeword=code,
    )


def structural_address_from_signature(sig: Signature) -> StructuralAddress:
    """Build a StructuralAddress from a signature (projection-level input)."""
    σ = _sig_to_perm(sig)
    return structural_address_from_permutation(σ)


def structural_address_from_codeword(code: int) -> StructuralAddress:
    """Build a StructuralAddress from a codeword (serialization-level input).

    Only defined for the 24 valid codewords. Parity-forbidden codewords
    (pairing bits = 11) are Hodge-dual presentations of underlying
    oriented unordered triples, not S_4 permutations themselves — they
    represent the same 8 underlying objects compressed, not 8 separate
    objects. For Hodge-dual codewords use codeword_to_oriented_triple.
    """
    if (code >> 2) & 0b11 == 0b11:
        raise ValueError(
            f"codeword 0b{code:05b} is parity-forbidden — "
            "Hodge-dual codewords are not S_4 permutations. "
            "Use codeword_to_oriented_triple for the underlying triple."
        )
    sig = codeword_to_signature(code)
    return structural_address_from_signature(sig)


def verify_structural_address_projections_commute() -> bool:
    """All paths through the projection diagram give the same StructuralAddress.

    For every valid signature, three construction paths must agree:
      from_permutation(σ), from_signature(sig), from_codeword(code)
    must produce the same StructuralAddress.

    Additional internal consistency checks:
      permutation = signature_to_permutation(signature)
      signature = permutation_to_signature(permutation)
      codeword = signature_to_codeword(signature)
      permutation = v4_component · stab_d_component
      stab_d_component fixes ANCHOR_AXIS
      v4_component ∈ V_4
      orbit_key derived from stab_d_component matches the field
      v4_delta agrees with v17's decompose_signature
    """
    from s4_structure import V4_ELEMENTS, ANCHOR_AXIS
    for sig in all_valid_signatures():
        # Three construction paths
        addr_sig = structural_address_from_signature(sig)
        σ = _sig_to_perm(sig)
        addr_perm = structural_address_from_permutation(σ)
        code = signature_to_codeword(sig)
        addr_code = structural_address_from_codeword(code)
        if not (addr_sig == addr_perm == addr_code):
            return False

        a = addr_sig

        # Internal projections must commute
        if _sig_to_perm(a.signature) != a.permutation:
            return False
        if _perm_to_sig(a.permutation) != a.signature:
            return False
        if signature_to_codeword(a.signature) != a.codeword:
            return False
        if codeword_to_signature(a.codeword) != a.signature:
            return False

        # Factorization: σ = v · s
        if a.v4_component.compose(a.stab_d_component) != a.permutation:
            return False

        # v ∈ V_4
        if a.v4_component not in set(V4_ELEMENTS):
            return False

        # s ∈ Stab(D)
        if a.stab_d_component.apply(ANCHOR_AXIS) != ANCHOR_AXIS:
            return False

        # orbit_key derived from s matches the field
        if _stab_d_to_key(a.stab_d_component) != a.orbit_key:
            return False

        # v17 decompose_signature agreement
        v17_decomp = decompose_signature(a.signature)
        if (v17_decomp.orbit_key, v17_decomp.v4_delta) != (a.orbit_key, a.v4_delta):
            return False

    return True


def verify_structural_address_codeword_roundtrip() -> bool:
    """For every valid codeword, address.codeword equals the input."""
    for code in all_valid_codewords():
        addr = structural_address_from_codeword(code)
        if addr.codeword != code:
            return False
    return True


def verify_structural_address_unique_per_signature() -> bool:
    """24 distinct signatures produce 24 distinct StructuralAddresses."""
    addresses = set()
    for sig in all_valid_signatures():
        addresses.add(structural_address_from_signature(sig))
    return len(addresses) == 24


def all_structural_addresses() -> List[StructuralAddress]:
    """The 24 StructuralAddresses corresponding to the 24 valid signatures."""
    return [structural_address_from_signature(sig) for sig in all_valid_signatures()]


# ============================================================
# v22: AddressedOp — the (op_name, address) bundle
# ============================================================
#
# The audit's v22.0 step (audit ~v21.1):
#
#   Then receipts take `addressed_op: AddressedOp`, not (op_name,
#   codeword). That collapses the remaining dual-entry bookkeeping
#   and makes "codeword is only a projection" behaviorally unavoidable.
#
# AddressedOp pairs an op_name with a StructuralAddress. It is the
# canonical operation identity: a registered op has exactly one
# StructuralAddress (under a given registry), so (op_name, address)
# fully identifies the op's semantic + structural content.
#
# v22.0 introduces AddressedOp and accepts it as an alternative
# constructor input on every receipt. The legacy (op_name, codeword)
# form is preserved with deprecation notice for v22.1+. When fully
# adopted, op_name and codeword move off the receipt dataclass and
# become @property delegations to addressed_op.


@dataclass(frozen=True)
class AddressedOp:
    """Canonical operation identity: an op_name paired with its address.

    AddressedOp is the v22 primary form for identifying operations on
    receipts. The op_name is the semantic identity; the StructuralAddress
    is the structural identity. Together they form an entity that can
    be passed around as the "what was done" of an operation, with the
    codeword derivable as a projection.

    Construction patterns:
        # From op_name + codeword (registry-resolved by caller)
        AddressedOp.from_op_and_codeword('apply', 0b00010)

        # From op_name + chart (registry lookup)
        AddressedOp.from_chart_op(chart, 'apply')

        # Direct construction (when address already in hand)
        AddressedOp(op_name='apply', address=structural_addr)
    """
    op_name: str
    address: StructuralAddress

    def __post_init__(self):
        if not isinstance(self.address, StructuralAddress):
            raise TypeError(
                f"AddressedOp.address must be StructuralAddress, "
                f"got {type(self.address).__name__}"
            )

    @property
    def codeword(self) -> int:
        """Projection: the codeword serialization of this op's address."""
        return self.address.codeword

    @property
    def signature(self) -> Signature:
        """Projection: the (source, sink, witness) signature."""
        return self.address.signature

    @property
    def orbit_key(self) -> OrbitKey:
        """Projection: the (pairing, chirality) orbit identifier."""
        return self.address.orbit_key

    @property
    def v4_delta(self) -> str:
        """Projection: the V_4 fiber coordinate."""
        return self.address.v4_delta

    @classmethod
    def from_op_and_codeword(cls, op_name: str, codeword: int) -> 'AddressedOp':
        """Build from op_name and codeword. The codeword is resolved into
        a StructuralAddress via structural_address_from_codeword."""
        return cls(
            op_name=op_name,
            address=structural_address_from_codeword(codeword),
        )

    @classmethod
    def from_chart_op(cls, c: 'ChartChained', op_name: str) -> 'AddressedOp':
        """Build from a chart's registry lookup of op_name."""
        code = _op_codeword(c, op_name)
        return cls.from_op_and_codeword(op_name, code)

    def structural_digest(self, registry_domain: str = REGISTRY_DOMAIN) -> str:
        """The structural-address digest for this AddressedOp.

        Two AddressedOps with the same op_name and same address (under
        the same registry_domain) share this digest. This is the
        portable identity used for cross-instance receipt matching.
        """
        return compute_structural_address_digest(
            self.op_name, self.address, registry_domain=registry_domain
        )


def verify_addressed_op_codeword_projection() -> bool:
    """AddressedOp.codeword projects from address.codeword (no dual storage)."""
    for code in all_valid_codewords():
        ao = AddressedOp.from_op_and_codeword('test_op', code)
        if ao.codeword != code:
            return False
        if ao.codeword != ao.address.codeword:
            return False
    return True


def verify_addressed_op_construction_paths_agree() -> bool:
    """from_op_and_codeword and direct construction give equivalent AddressedOps."""
    for code in all_valid_codewords():
        addr = structural_address_from_codeword(code)
        ao_direct = AddressedOp(op_name='test_op', address=addr)
        ao_indirect = AddressedOp.from_op_and_codeword('test_op', code)
        if ao_direct != ao_indirect:
            return False
    return True


def verify_addressed_op_rejects_non_structural_address() -> bool:
    """AddressedOp(op_name='x', address=42) must raise TypeError."""
    try:
        AddressedOp(op_name='test_op', address=42)
        return False
    except TypeError:
        return True


def verify_addressed_op_structural_digest_matches_function() -> bool:
    """ao.structural_digest() equals compute_structural_address_digest(name, addr)."""
    for code in all_valid_codewords():
        addr = structural_address_from_codeword(code)
        ao = AddressedOp(op_name='test_op', address=addr)
        if ao.structural_digest() != compute_structural_address_digest('test_op', addr):
            return False
    return True


# ============================================================
# Sum-type receipts (v12)
# ============================================================

@dataclass(frozen=True)
class TermReceipt:
    """Witnesses a term-reduction step.

    Advances the term cursor in verify_trace. op_name must be in _TERM_OPS;
    illegal construction is rejected at __post_init__.

    v21: address field carries the StructuralAddress derived from the
    codeword. If not supplied explicitly, it is constructed automatically.

    v22.0: addressed_op field bundles (op_name, address) into the canonical
    operation identity. If addressed_op is supplied, op_name and codeword
    are derived from it (and any explicit op_name/codeword must agree).
    The (op_name, codeword) constructor form remains supported for
    backward compatibility; v22.1+ may deprecate it.

    Primary form (v22+):
        TermReceipt(addressed_op=ao, before=0, after=0)
    Legacy form (pre-v22, still works):
        TermReceipt(op_name='apply', codeword=c, before=0, after=0)
    """
    op_name: str = None
    codeword: int = None
    before: int = 0
    after: int = 0
    rule: Optional[int] = None       # only set for interp
    binding: Optional[Tuple[Tuple[int, int], ...]] = None
    table: Optional[int] = None
    registry_digest: Optional[str] = None
    op_address_digest: Optional[str] = None
    chart_instance_nonce: Optional[str] = None
    address: Optional['StructuralAddress'] = None
    addressed_op: Optional['AddressedOp'] = None

    def __post_init__(self):
        # v22.0: reconcile addressed_op with (op_name, codeword, address)
        if self.addressed_op is not None:
            ao = self.addressed_op
            # Backfill op_name and codeword if not supplied
            if self.op_name is None:
                object.__setattr__(self, 'op_name', ao.op_name)
            elif self.op_name != ao.op_name:
                raise ValueError(
                    f"TermReceipt.op_name={self.op_name!r} disagrees with "
                    f"addressed_op.op_name={ao.op_name!r}"
                )
            if self.codeword is None:
                object.__setattr__(self, 'codeword', ao.codeword)
            elif self.codeword != ao.codeword:
                raise ValueError(
                    f"TermReceipt.codeword={self.codeword} disagrees with "
                    f"addressed_op.codeword={ao.codeword}"
                )
            if self.address is None:
                object.__setattr__(self, 'address', ao.address)
            elif self.address != ao.address:
                raise ValueError(
                    f"TermReceipt.address disagrees with addressed_op.address"
                )
        if self.op_name is None or self.codeword is None:
            raise ValueError(
                "TermReceipt requires either addressed_op or "
                "(op_name, codeword)"
            )
        if self.op_name not in _TERM_OPS:
            raise ValueError(
                f"TermReceipt with non-term op_name {self.op_name!r}; "
                f"expected one of {sorted(_TERM_OPS)}"
            )
        # Derive address from codeword if not supplied; if supplied, verify
        # consistency with the codeword.
        if self.address is None:
            derived = structural_address_from_codeword(self.codeword)
            object.__setattr__(self, 'address', derived)
        else:
            if self.address.codeword != self.codeword:
                raise ValueError(
                    f"TermReceipt.address.codeword={self.address.codeword} "
                    f"does not match codeword={self.codeword}"
                )
        # Backfill addressed_op if it was missing (legacy form)
        if self.addressed_op is None:
            object.__setattr__(
                self, 'addressed_op',
                AddressedOp(op_name=self.op_name, address=self.address),
            )

    @property
    def signature(self) -> 'Signature':
        """Derived projection: the (source, sink, witness) of the operation."""
        return self.address.signature

    @property
    def orbit_key(self) -> 'OrbitKey':
        """Derived projection: the (pairing, chirality) orbit identifier."""
        return self.address.orbit_key

    @property
    def v4_delta(self) -> str:
        """Derived projection: the V_4 fiber coordinate (lex-min convention)."""
        return self.address.v4_delta

    def changed(self) -> bool:
        return self.before != self.after


@dataclass(frozen=True)
class StateReceipt:
    """Witnesses a chart-state mutation.

    Does NOT advance the term cursor. state_pre_digest and
    state_post_digest are REQUIRED (not optional). op_name must be
    in _STATE_OPS.

    v21: carries StructuralAddress (see TermReceipt docstring).
    """
    op_name: str = None
    codeword: int = None
    input_id: int = 0
    output_id: int = 0
    state_pre_digest: str = ""
    state_post_digest: str = ""
    registry_digest: Optional[str] = None
    op_address_digest: Optional[str] = None
    chart_instance_nonce: Optional[str] = None
    address: Optional['StructuralAddress'] = None
    addressed_op: Optional['AddressedOp'] = None

    def __post_init__(self):
        # v22.0: reconcile addressed_op with (op_name, codeword, address)
        if self.addressed_op is not None:
            ao = self.addressed_op
            if self.op_name is None:
                object.__setattr__(self, 'op_name', ao.op_name)
            elif self.op_name != ao.op_name:
                raise ValueError(
                    f"StateReceipt.op_name={self.op_name!r} disagrees with "
                    f"addressed_op.op_name={ao.op_name!r}"
                )
            if self.codeword is None:
                object.__setattr__(self, 'codeword', ao.codeword)
            elif self.codeword != ao.codeword:
                raise ValueError(
                    f"StateReceipt.codeword={self.codeword} disagrees with "
                    f"addressed_op.codeword={ao.codeword}"
                )
            if self.address is None:
                object.__setattr__(self, 'address', ao.address)
            elif self.address != ao.address:
                raise ValueError(
                    f"StateReceipt.address disagrees with addressed_op.address"
                )
        if self.op_name is None or self.codeword is None:
            raise ValueError(
                "StateReceipt requires either addressed_op or "
                "(op_name, codeword)"
            )
        if self.op_name not in _STATE_OPS:
            raise ValueError(
                f"StateReceipt with non-state op_name {self.op_name!r}; "
                f"expected one of {sorted(_STATE_OPS)}"
            )
        if self.address is None:
            derived = structural_address_from_codeword(self.codeword)
            object.__setattr__(self, 'address', derived)
        else:
            if self.address.codeword != self.codeword:
                raise ValueError(
                    f"StateReceipt.address.codeword={self.address.codeword} "
                    f"does not match codeword={self.codeword}"
                )
        if self.addressed_op is None:
            object.__setattr__(
                self, 'addressed_op',
                AddressedOp(op_name=self.op_name, address=self.address),
            )

    @property
    def signature(self) -> 'Signature':
        return self.address.signature

    @property
    def orbit_key(self) -> 'OrbitKey':
        return self.address.orbit_key

    @property
    def v4_delta(self) -> str:
        return self.address.v4_delta


@dataclass(frozen=True)
class ObservationReceipt:
    """Witnesses a passive reading (no mutation, no term transition).

    Reserved for future read-only operations. No state digests because
    observations don't mutate state. op_name must NOT be in _TERM_OPS or
    _STATE_OPS (rejected at __post_init__).

    v21: carries StructuralAddress (see TermReceipt docstring).
    """
    op_name: str = None
    codeword: int = None
    target_id: int = 0
    result_id: Optional[int] = None
    registry_digest: Optional[str] = None
    op_address_digest: Optional[str] = None
    chart_instance_nonce: Optional[str] = None
    address: Optional['StructuralAddress'] = None
    addressed_op: Optional['AddressedOp'] = None

    def __post_init__(self):
        # v22.0: reconcile addressed_op with (op_name, codeword, address)
        if self.addressed_op is not None:
            ao = self.addressed_op
            if self.op_name is None:
                object.__setattr__(self, 'op_name', ao.op_name)
            elif self.op_name != ao.op_name:
                raise ValueError(
                    f"ObservationReceipt.op_name={self.op_name!r} disagrees with "
                    f"addressed_op.op_name={ao.op_name!r}"
                )
            if self.codeword is None:
                object.__setattr__(self, 'codeword', ao.codeword)
            elif self.codeword != ao.codeword:
                raise ValueError(
                    f"ObservationReceipt.codeword={self.codeword} disagrees with "
                    f"addressed_op.codeword={ao.codeword}"
                )
            if self.address is None:
                object.__setattr__(self, 'address', ao.address)
            elif self.address != ao.address:
                raise ValueError(
                    f"ObservationReceipt.address disagrees with addressed_op.address"
                )
        if self.op_name is None or self.codeword is None:
            raise ValueError(
                "ObservationReceipt requires either addressed_op or "
                "(op_name, codeword)"
            )
        if self.op_name in _TERM_OPS or self.op_name in _STATE_OPS:
            raise ValueError(
                f"ObservationReceipt op_name {self.op_name!r} is a known "
                f"term or state op; observation receipts are for passive "
                f"readings only"
            )
        if self.address is None:
            derived = structural_address_from_codeword(self.codeword)
            object.__setattr__(self, 'address', derived)
        else:
            if self.address.codeword != self.codeword:
                raise ValueError(
                    f"ObservationReceipt.address.codeword={self.address.codeword} "
                    f"does not match codeword={self.codeword}"
                )
        if self.addressed_op is None:
            object.__setattr__(
                self, 'addressed_op',
                AddressedOp(op_name=self.op_name, address=self.address),
            )

    @property
    def signature(self) -> 'Signature':
        return self.address.signature

    @property
    def orbit_key(self) -> 'OrbitKey':
        return self.address.orbit_key

    @property
    def v4_delta(self) -> str:
        return self.address.v4_delta


Receipt = Union[TermReceipt, StateReceipt, ObservationReceipt]


# ============================================================
# v21: receipts obligated to carry StructuralAddress
# ============================================================
#
# v20 made StructuralAddress available; v21 makes it unskippable.
# Every receipt now carries an `address: StructuralAddress` field,
# either supplied by the constructor or auto-derived from the
# codeword. The derived properties `signature`, `orbit_key`, and
# `v4_delta` expose the address coordinates without requiring
# callers to reach into `receipt.address.*`.
#
# The verifier `verify_every_receipt_carries_structural_address`
# (applied to a sample of constructed receipts) and
# `verify_receipt_address_codeword_agreement` (applied to every
# constructible receipt over all 24 valid codewords) prove the
# obligation: a receipt with `codeword=c` MUST carry
# `address.codeword == c`, and reconstructing the address from the
# codeword MUST yield the same StructuralAddress.


def receipt_addresses_codeword(r: Receipt) -> bool:
    """A single receipt carries a StructuralAddress consistent with its codeword."""
    if r.address is None:
        return False
    if r.address.codeword != r.codeword:
        return False
    return r.address == structural_address_from_codeword(r.codeword)


def verify_receipt_address_codeword_agreement() -> bool:
    """For every valid codeword, a constructed TermReceipt, StateReceipt,
    and ObservationReceipt all have receipt.address derivable from
    receipt.codeword.

    This is the v21 LOAD-BEARING obligation: the StructuralAddress is
    not optional; it is intrinsic to every receipt.
    """
    # We construct one receipt of each kind per valid codeword.
    # TermReceipt requires an op_name in _TERM_OPS; StateReceipt
    # requires _STATE_OPS; ObservationReceipt requires anything else.
    term_op = next(iter(_TERM_OPS))
    state_op = next(iter(_STATE_OPS))
    observation_op = '__v21_observation_test_op__'
    assert observation_op not in _TERM_OPS and observation_op not in _STATE_OPS

    for code in all_valid_codewords():
        t = TermReceipt(op_name=term_op, codeword=code, before=0, after=0)
        if not receipt_addresses_codeword(t):
            return False
        s = StateReceipt(
            op_name=state_op, codeword=code,
            input_id=0, output_id=0,
            state_pre_digest='x', state_post_digest='y',
        )
        if not receipt_addresses_codeword(s):
            return False
        o = ObservationReceipt(op_name=observation_op, codeword=code, target_id=0)
        if not receipt_addresses_codeword(o):
            return False
    return True


def verify_receipt_address_rejects_inconsistent() -> bool:
    """Constructing a receipt with codeword=c and address.codeword=c' (c≠c')
    must raise ValueError."""
    codes = list(all_valid_codewords())
    code_a, code_b = codes[0], codes[1]
    addr_a = structural_address_from_codeword(code_a)

    term_op = next(iter(_TERM_OPS))
    state_op = next(iter(_STATE_OPS))

    try:
        TermReceipt(op_name=term_op, codeword=code_b, before=0, after=0,
                    address=addr_a)
        return False
    except ValueError:
        pass

    try:
        StateReceipt(op_name=state_op, codeword=code_b,
                     input_id=0, output_id=0,
                     state_pre_digest='x', state_post_digest='y',
                     address=addr_a)
        return False
    except ValueError:
        pass

    try:
        ObservationReceipt(op_name='__v21_obs__', codeword=code_b, target_id=0,
                           address=addr_a)
        return False
    except ValueError:
        pass

    return True


def verify_receipt_derived_properties_match_address() -> bool:
    """For every constructible receipt, the derived properties (signature,
    orbit_key, v4_delta) match what's in the StructuralAddress."""
    term_op = next(iter(_TERM_OPS))
    state_op = next(iter(_STATE_OPS))

    for code in all_valid_codewords():
        t = TermReceipt(op_name=term_op, codeword=code, before=0, after=0)
        if (t.signature, t.orbit_key, t.v4_delta) != \
           (t.address.signature, t.address.orbit_key, t.address.v4_delta):
            return False
        s = StateReceipt(
            op_name=state_op, codeword=code,
            input_id=0, output_id=0,
            state_pre_digest='x', state_post_digest='y',
        )
        if (s.signature, s.orbit_key, s.v4_delta) != \
           (s.address.signature, s.address.orbit_key, s.address.v4_delta):
            return False
        o = ObservationReceipt(op_name='__v21_obs__', codeword=code, target_id=0)
        if (o.signature, o.orbit_key, o.v4_delta) != \
           (o.address.signature, o.address.orbit_key, o.address.v4_delta):
            return False
    return True


def verify_op_address_digest_uses_structural_address() -> bool:
    """v21.1/v22: compute_op_address_digest delegates to
    compute_structural_address_digest, which hashes the full structural
    address (registry_domain + op_name + codeword + signature +
    orbit_key + v4_delta), not just (op_name, codeword).

    This verifier confirms by reconstructing the hash with the
    structural payload and checking equality. Any code that bypasses
    structural_address_from_codeword in the hash path will fail.
    """
    from chart_chained import ChartChained
    c = ChartChained()
    for op_name in ('apply', 'interp', 'allocate', 'store', 'release'):
        try:
            code = _op_codeword(c, op_name)
        except KeyError:
            continue
        addr = structural_address_from_codeword(code)
        # Expected: delegate to the load-bearing address-primary digest
        expected = compute_structural_address_digest(op_name, addr)
        actual = compute_op_address_digest(c, op_name)
        if actual != expected:
            return False
        # And confirm it's NOT the legacy (op_name, code) hash:
        legacy = hashlib.sha256(_canonical_bytes((op_name, code))).hexdigest()
        if actual == legacy:
            return False
    return True


def verify_every_receipt_carries_structural_address() -> bool:
    """v21.1 LOAD-BEARING umbrella verifier.

    Aggregates the v21 receipt obligations into a single behavioral
    theorem:

      1. Every constructed receipt (Term/State/Observation, all 24
         valid codewords) has a non-None StructuralAddress consistent
         with its codeword. [verify_receipt_address_codeword_agreement]

      2. Constructing a receipt with codeword=c and address.codeword=c'
         (c≠c') raises ValueError. [verify_receipt_address_rejects_inconsistent]

      3. Derived properties (signature, orbit_key, v4_delta) match
         the carried address. [verify_receipt_derived_properties_match_address]

      4. compute_op_address_digest hashes the structural address, not
         the raw codeword. [verify_op_address_digest_uses_structural_address]

    When this verifier passes, StructuralAddress is UNSKIPPABLE in
    every receipt path: construction, derivation, digest computation.
    """
    return all([
        verify_receipt_address_codeword_agreement(),
        verify_receipt_address_rejects_inconsistent(),
        verify_receipt_derived_properties_match_address(),
        verify_op_address_digest_uses_structural_address(),
    ])


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
# v18: transactional verification boundary
# ============================================================
#
# v17 detected mutation but did not undo it. v18 makes the
# verification boundary observationally pure: snapshot the FULL
# mutable chart surface (not just the digest fields), run, classify
# what happened, and ALWAYS restore.
#
# The mutable surface of a ChartChained instance includes:
#     _cells              list of cons tuples
#     _hashcons           dict mapping cons tuple → cell id
#     _apply_memo         dict mapping (head, args) → result
#     _history            append-only event log
#     _workspace          mutable workspace cells
#     _workspace_free     free-index list for workspace
#
# v17 purity classification covered (_history, _apply_memo, _cells).
# v18 widens to also detect _hashcons / _workspace perturbations,
# because a replay mutating _hashcons without touching _cells could
# previously pass purity. Even when purity is reported as PURE, the
# restoration is unconditional — the verifier never commits state.

@dataclass(frozen=True)
class ChartFullSnapshot:
    """Captures all mutable chart state for transactional restoration.

    Distinct from ChartSnapshot (which stores digests for purity
    classification). This snapshot stores actual contents so the
    chart can be restored byte-for-byte after a thunk that may have
    mutated state.
    """
    cells: tuple
    hashcons_items: tuple
    apply_memo_items: tuple
    history: tuple
    workspace: tuple
    workspace_free: tuple


def _deep_snapshot_mutable_chart(c) -> ChartFullSnapshot:
    """Snapshot the KNOWN mutable surface of a chart.

    SCOPE (v22 audit): "known mutable surface" refers to the chart-level
    container fields enumerated below, NOT the truly-everything-mutable
    closure of the chart's reachable state. Specifically:

    INCLUDED (snapshotted and restored):
      - _cells: the term-storage list
      - _hashcons: the hash-cons dict
      - _apply_memo: the application memoization dict
      - _history: the operation log
      - _workspace: the active workspace list
      - _workspace_free: the free-workspace list

    NOT INCLUDED (intentionally — these are treated as INVARIANT for the
    transactional observation, not mutable state):
      - c.registry: the operation registry (taken as fixed during replay)
      - c.atoms: atom table
      - c.methods: bound method table
      - c.default_table: the default rule table
      - any spec objects, sub-tables, or nested mutable values held
        inside _cells (a cell containing a mutable list would have its
        list captured at sequence level but not deep-copied)

    A replay that mutates a NOT-INCLUDED field will not be detected
    by purity classification and will not be restored. Verifiers that
    depend on observational purity beyond the included surface should
    extend this snapshot or be explicitly scoped.

    For purity-classification digests (used in EFFECT classification),
    see _snapshot_chart_state. This function is for full restoration
    (actual contents); _snapshot_chart_state is for digests.
    """
    return ChartFullSnapshot(
        cells=tuple(c._cells),
        hashcons_items=tuple(c._hashcons.items()),
        apply_memo_items=tuple(c._apply_memo.items()),
        history=tuple(c._history),
        workspace=tuple(c._workspace),
        workspace_free=tuple(c._workspace_free),
    )


def _restore_mutable_chart(c, snap: ChartFullSnapshot) -> None:
    """Restore chart state from a full snapshot.

    Replaces in-place: lists are truncated/repopulated, dicts cleared
    and updated. Does NOT replace attribute references — important so
    that other holders of c's attributes still see the same objects.
    """
    c._cells[:] = list(snap.cells)
    c._hashcons.clear()
    c._hashcons.update(dict(snap.hashcons_items))
    c._apply_memo.clear()
    c._apply_memo.update(dict(snap.apply_memo_items))
    c._history[:] = list(snap.history)
    c._workspace[:] = list(snap.workspace)
    c._workspace_free[:] = list(snap.workspace_free)


def _hashcons_perturbed(c, snap: ChartFullSnapshot) -> bool:
    """v18: detect _hashcons mutation that doesn't show up in _cells digest.

    A replay could (incorrectly) mutate _hashcons without appending to
    _cells, e.g. by overwriting an entry. v17 purity classification
    missed this. We check the full hashcons against the snapshot.
    """
    current = tuple(sorted(c._hashcons.items()))
    expected = tuple(sorted(snap.hashcons_items))
    return current != expected


def _workspace_perturbed(c, snap: ChartFullSnapshot) -> bool:
    """v18: detect _workspace / _workspace_free perturbation."""
    return (tuple(c._workspace) != snap.workspace
            or tuple(c._workspace_free) != snap.workspace_free)


def _transactional_observe(c, thunk):
    """v18/v22: transactional verification boundary over the KNOWN
    chart mutable surface.

    snapshot known mutable state → run thunk → classify → RESTORE → return.

    Verification is observationally pure with respect to the KNOWN mutable
    surface (see _deep_snapshot_mutable_chart for the explicit scope):
    even if the thunk mutates the chart's _cells/_hashcons/_apply_memo/
    _history/_workspace/_workspace_free, the chart is restored to
    pre-thunk state before this function returns.

    The purity classification (computed BEFORE restoration) tells the
    caller what the thunk did to the included surface; restoration
    ensures the caller never sees those consequences.

    SCOPE LIMITATION: a thunk that mutates the registry, atoms table,
    methods table, default_table, or a mutable value reachable through
    a _cells entry will NOT be detected or restored. The transactional
    observation is scoped to the enumerated container fields.
    """
    full_snap = _deep_snapshot_mutable_chart(c)
    before = _snapshot_chart_state(c)
    result, error = None, None
    try:
        result = thunk()
    except Exception as e:
        error = e
    # Classify BEFORE restoration — _classify_effect inspects the
    # post-thunk state to distinguish CHART_PURE / CHART_EXTENDING /
    # FAILED_PURITY.
    after = _snapshot_chart_state(c)
    purity, allocated = _classify_effect(before, after, c)
    # v18: also check the additional mutable surface.
    if purity == CHART_PURE:
        if _hashcons_perturbed(c, full_snap) or _workspace_perturbed(c, full_snap):
            purity = FAILED_PURITY
    elif purity == CHART_EXTENDING:
        # extending should match an actual cell allocation; if hashcons
        # or workspace changed beyond what _cells would account for,
        # demote to FAILED_PURITY.
        if _workspace_perturbed(c, full_snap):
            purity = FAILED_PURITY
    # Always restore — verification never commits.
    _restore_mutable_chart(c, full_snap)
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
    # v18: use transactional observer — permissive replay must not
    # leave cell allocations on the chart even when the strict path
    # misses. The caller (verify_term) decides whether the result is
    # acceptable based on allow_extending; we never let the kernel's
    # mutations leak past the verification boundary.
    return _transactional_observe(c, kernel)


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
    # v18: bridge enforcement — every receipt's codeword must decompose
    # orbit-canonically. This makes the v17 bridge a receipt obligation,
    # not just a library invariant.
    bridge_fail = _check_codeword_bridge(c, r)
    if bridge_fail:
        return bridge_fail
    return None


def _check_codeword_bridge(c, r) -> Optional[VerificationResult]:
    """v21.1/v22: bridge verifier — confirms construction-time invariants
    held through to verification time.

    THEOREM PHRASING (audit-sharpened, v22):
      Construction makes StructuralAddress unavoidable on every receipt
      via __post_init__ (auto-derivation + consistency check). VERIFICATION
      then independently re-derives the canonical address from the
      receipt's codeword and compares for equality.

      Two different defenses against drift:
        (a) Construction: every receipt has an address, and that address
            is consistent with its codeword at construction time.
        (b) Verification: at the moment of replay, the receipt's address
            still equals the canonical projection of its codeword.

      A receipt that was constructed correctly but then tampered with
      (e.g., its address mutated post-construction — only possible if
      the frozen-dataclass guarantee is bypassed) would fail (b).

    The check is now a single equality:
       receipt.address == structural_address_from_codeword(receipt.codeword)

    Earlier (v18) re-derivation logic — codeword → signature →
    orbit_key → recompose with consistency check at each step — is
    preserved in comments below. Equivalent to what the constructor
    and StructuralAddress now enforce, but no longer load-bearing
    because the address itself is the canonical decomposition.

    The optional ContentAddressedReceiptFields check is preserved
    because some receipts may still carry CARF from external sources;
    when present, it must agree with the address.
    """
    addr = getattr(r, 'address', None)
    if addr is None:
        return VerificationResult.fail(
            f"receipt has no StructuralAddress (v21 obligation violated)"
        )
    if addr.codeword != r.codeword:
        return VerificationResult.fail(
            f"receipt.address.codeword={addr.codeword} != "
            f"receipt.codeword={r.codeword}"
        )
    expected_addr = structural_address_from_codeword(r.codeword)
    if addr != expected_addr:
        return VerificationResult.fail(
            f"receipt.address does not equal the canonical address "
            f"derived from codeword {r.codeword:05b}"
        )
    # Optional CARF consistency check (preserved from v18)
    carried = getattr(r, 'content_addressed', None)
    if carried is not None:
        if carried.signature != addr.signature:
            return VerificationResult.fail(
                f"receipt-carried signature {carried.signature} != "
                f"address.signature {addr.signature}"
            )
        if carried.orbit_key != addr.orbit_key:
            return VerificationResult.fail(
                f"receipt-carried orbit_key {carried.orbit_key} != "
                f"address.orbit_key {addr.orbit_key}"
            )
        if carried.v4_delta != addr.v4_delta:
            return VerificationResult.fail(
                f"receipt-carried v4_delta {carried.v4_delta!r} != "
                f"address.v4_delta {addr.v4_delta!r}"
            )
        expected_digest = orbit_canonical_digest(addr.orbit_key)
        if carried.orbit_canonical_digest != expected_digest:
            return VerificationResult.fail(
                f"receipt-carried orbit_canonical_digest mismatch"
            )
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


def _effect_cap(achieved: str, declared_max: str) -> str:
    """Cap achieved effect_level by the spec's declared maximum.

    Uses the evidence-strength rank order. If achieved is weaker than
    (or equal to) declared_max, return achieved; else return declared_max.

    Special case: EFFECT_INAPPLICABLE as declared_max means the spec
    declares no effect obligation, so the result is INAPPLICABLE
    regardless of what was achieved.

    v17: introduced to make StateOpSpec.obligation_level enforceable.
    Previously, a spec with replay populated could emit effect levels
    stronger than its declared maximum. Now the spec's claim is an
    honest upper bound on what verify_state will report.
    """
    if declared_max == EFFECT_INAPPLICABLE:
        return EFFECT_INAPPLICABLE
    achieved_rank = _EFFECT_RANK.get(achieved, -1)
    declared_rank = _EFFECT_RANK.get(declared_max, -1)
    if achieved_rank < 0 or declared_rank < 0:
        return achieved
    if achieved_rank <= declared_rank:
        return achieved
    return declared_max


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

    # v14: spec.replay seam.
    # v17: purity-wrapped + obligation_level capped.
    #   spec.replay is None         → EFFECT_RECEIPT_DECLARED (capped by obligation_level)
    #   spec.replay returns True    → EFFECT_REPLAY_VERIFIED  (capped by obligation_level)
    #   spec.replay returns False   → FAILED_EFFECT
    #   spec.replay raises          → FAILED_EFFECT
    #   spec.replay mutates chart   → FAILED_PURITY + FAILED_EFFECT (BUG in replay impl)
    if spec.replay is None:
        capped = _effect_cap(EFFECT_RECEIPT_DECLARED, spec.obligation_level)
        reason = (
            f"codeword {r.codeword:05b} matches op {r.op_name!r}; "
            f"spec.replay=None → declared only; "
            f"obligation_level={spec.obligation_level} → capped at {capped}"
        )
        return VerificationResult.address_ok(
            locality=CHART_LOCAL,
            effect_level=capped,
            reason=reason,
        )

    # v17/v18: Replay is registered. SNAPSHOT around the call to check
    # purity and TRANSACTIONALLY restore if the replay mutated state.
    # Even a buggy replay that mutates the chart cannot perturb it
    # past the verification boundary (v18 fix).
    def replay_thunk():
        return spec.replay(c, r)

    replay_value, purity, allocated, error = _transactional_observe(c, replay_thunk)

    if error is not None:
        # Even if exception occurred, purity may still have changed.
        return VerificationResult.fail(
            f"replay raised {type(error).__name__}: {error}",
            purity_level=(FAILED_PURITY if purity != CHART_PURE else CHART_PURE),
            locality=CHART_LOCAL,
            effect_level=FAILED_EFFECT,
            cells_allocated=allocated,
        )

    if purity != CHART_PURE:
        # v17: replay mutated state — implementation bug.
        return VerificationResult.fail(
            f"replay for {r.op_name!r} produced non-pure effects "
            f"(purity={purity}, allocated={allocated} cell(s)); "
            f"spec.replay must be pure (no chart mutation)",
            purity_level=FAILED_PURITY,
            locality=CHART_LOCAL,
            effect_level=FAILED_EFFECT,
            cells_allocated=allocated,
        )

    if replay_value is True:
        # v17: Cap by spec.obligation_level. Spec's declared maximum
        # is an honest upper bound — a spec with obligation_level
        # = EFFECT_RECEIPT_DECLARED but a "True" replay still caps
        # at DECLARED, because the spec only claims to witness that much.
        capped = _effect_cap(EFFECT_REPLAY_VERIFIED, spec.obligation_level)
        reason = (
            f"codeword {r.codeword:05b} matches op {r.op_name!r}; "
            f"spec.replay returned True; purity preserved; "
            f"obligation_level={spec.obligation_level} → capped at {capped}"
        )
        return VerificationResult(
            ok=True,
            transition_level=ADDRESS_VERIFIED,
            purity_level=CHART_PURE,
            locality=CHART_LOCAL,
            effect_level=capped,
            reason=reason,
            cells_allocated=0,
        )

    return VerificationResult.fail(
        f"spec.replay for {r.op_name!r} returned {replay_value!r} (expected True)",
        purity_level=CHART_PURE, locality=CHART_LOCAL,
        effect_level=FAILED_EFFECT,
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
                 allow_extending: bool = False,
                 initial_state_digest: Optional[str] = None,
                 final_state_digest: Optional[str] = None) -> VerificationResult:
    """Verify a trace of receipts. Dispatches on receipt type.

    TERM CURSOR (always enforced):
        start → final via TermReceipts. Each TermReceipt's `before`
        must match the current term cursor; `after` advances it.
        Final term cursor must equal `final`.

    STATE CURSOR (v15, optional — enforced iff initial_state_digest is
    not None):
        initial_state_digest → final_state_digest via StateReceipts.
        Each StateReceipt's `state_pre_digest` must match the current
        state cursor; `state_post_digest` advances it. If
        final_state_digest is provided, final state cursor must match.

        This is a STRUCTURAL property of the receipt chain (do the
        receipts internally chain coherently), separate from whether
        the digests describe real chart states. The latter requires
        StateOpSpec.replay (v14 seam, v15+ implementations).

    allow_extending: passed through to verify_receipt. Default False.
    initial_state_digest: optional v15 state cursor start. Default None
        (no state cursor discipline; backward compat with v14 callers).
    final_state_digest: optional v15 state cursor end check. Only
        meaningful if initial_state_digest is also provided.
    """
    cur = start
    state_cur = initial_state_digest    # None ⇒ state cursor inactive
    state_active = initial_state_digest is not None
    overall = GRADE_IDENTITY
    total_cells_allocated = 0
    counts = {REPLAY_VERIFIED: 0, SEMANTIC_REPLAY_VERIFIED: 0, ADDRESS_VERIFIED: 0}
    n_term = n_state = n_obs = 0

    for i, r in enumerate(receipts):
        is_term = isinstance(r, TermReceipt)
        is_state = isinstance(r, StateReceipt)

        if is_term:
            if not c.eq(r.before, cur):
                return VerificationResult.fail(
                    f"chain break at receipt {i}: before #{r.before} != cursor #{cur}"
                )

        if is_state and state_active:
            if r.state_pre_digest != state_cur:
                return VerificationResult.fail(
                    f"state-cursor break at receipt {i} ({r.op_name}): "
                    f"pre_digest {_display_digest(r.state_pre_digest)} "
                    f"!= state cursor {_display_digest(state_cur)}"
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
        elif is_state:
            if state_active:
                state_cur = r.state_post_digest
            n_state += 1
        else:
            n_obs += 1

    if not c.eq(cur, final):
        return VerificationResult.fail(
            f"final term mismatch: cursor #{cur} != final #{final}"
        )

    if state_active and final_state_digest is not None:
        if state_cur != final_state_digest:
            return VerificationResult.fail(
                f"final state-cursor mismatch: "
                f"cursor {_display_digest(state_cur)} != "
                f"expected {_display_digest(final_state_digest)}"
            )

    state_cursor_status = (
        "state cursor enforced" if state_active else "state cursor inactive"
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
            f"{total_cells_allocated} cell(s) allocated by verifier; "
            f"{state_cursor_status}"
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
# v13/v14: receipt-kernel admissibility aggregator
# ============================================================

def verify_m41_receipt_kernel_admissibility(c: ChartChained) -> bool:
    """M41 receipt/address verification kernel admissibility (v13/v14).

    SCOPE (v14, sharpened from v13):
    This aggregator proves the receipt/address verification kernel is
    coherent and fail-closed. It does NOT prove the grammar is globally
    well-typed or that traces are admissible end-to-end — those are
    weaker properties that hold per-trace, not as a global theorem.

    What this DOES prove (conjunction of seven sub-claims):

        Sum-type receipts: TermReceipt | StateReceipt | ObservationReceipt
          ↓ __post_init__ validation
        Illegal op-name/type combinations unconstructible
          ↓ codeword address decomposition
        24 valid M38 codewords ↔ 24 (sign, m, j) addresses (SET bijection)
          ↓ registry coverage
        Every op in the chart's registry has a valid codeword
          ↓ StateOpSpec registry
        Every state op has a spec; obligation_level is in the
        admissible set; spec.replay seam is in place (None or callable)
          ↓ Grade meet-monoid (four-axis)
        GRADE_IDENTITY is identity for the meet operation
          ↓ live verification
        A canonical apply receipt verifies as REPLAY_VERIFIED + CHART_PURE

    What this does NOT prove (named explicitly):
        - Global grammar well-typedness (would require an audit of every
          reachable program, not a kernel-level check)
        - That state effects are replay-verified (v14 specs ship with
          replay=None; the seam is in place, no impl populates it yet)
        - That M38's group structure matches M40's (they differ; v13's
          merge documented this honestly as a set bijection only)

    Each sub-claim is independently verifiable; this aggregator asserts
    the conjunction. Returns True iff every sub-claim holds. Takes a
    chart `c` parameter because some sub-claims need a live registry.
    """
    # 1. Type-level: illegal receipts unconstructible
    try:
        TermReceipt(op_name='store', codeword=0, before=0, after=0)
        return False  # should have raised
    except ValueError:
        pass

    try:
        StateReceipt(op_name='apply', codeword=0, input_id=0, output_id=0,
                     state_pre_digest="0", state_post_digest="0")
        return False
    except ValueError:
        pass

    try:
        ObservationReceipt(op_name='apply', codeword=0, target_id=0)
        return False
    except ValueError:
        pass

    # 2. Codeword address bijection (24 ↔ 24, exhaustive round-trip)
    if not verify_codeword_address_bijection():
        return False

    # 3. Every operation in the registry has a valid codeword
    if not verify_all_registry_ops_have_valid_codewords(c):
        return False

    # 4. Every state op has a StateOpSpec
    for op_name in _STATE_OPS:
        spec = get_state_op_spec(op_name)
        if spec is None:
            return False
        if spec.obligation_level not in {
            EFFECT_RECEIPT_DECLARED, EFFECT_REPLAY_VERIFIED, EFFECT_INAPPLICABLE
        }:
            return False

    # 5. Grade lattice: GRADE_IDENTITY is identity for meet
    test_grade = Grade(REPLAY_VERIFIED, CHART_PURE, CHART_LOCAL,
                       EFFECT_INAPPLICABLE)
    if test_grade.meet(GRADE_IDENTITY) != test_grade:
        return False
    if GRADE_IDENTITY.meet(test_grade) != test_grade:
        return False
    # Idempotence
    if GRADE_IDENTITY.meet(GRADE_IDENTITY) != GRADE_IDENTITY:
        return False

    # 6. Live verification: a canonical apply receipt verifies as
    #    REPLAY_VERIFIED + CHART_PURE (the strongest available transition
    #    and purity grades for a fresh apply receipt).
    term = c.cons(c.I, c.TRUE)
    _, r = apply_with_receipt(c, term)
    vr = verify_receipt(c, r)
    if not vr.ok:
        return False
    if vr.transition_level != REPLAY_VERIFIED:
        return False
    if vr.purity_level != CHART_PURE:
        return False

    # 7. Receipt's codeword decodes to a valid algebraic address
    try:
        addr = receipt_address(r)
        if addr not in set(all_algebraic_addresses()):
            return False
    except ValueError:
        return False

    return True


# ============================================================
# Demo
# ============================================================

def demo():
    c = ChartChained()

    print("=" * 78)
    print("  M41 (v22.0) — AddressedOp + registry-domain digest + scope tightening")
    print("              snapshot, bridge enforcement, ContentAddressedReceiptFields")
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

    # ============================================================
    # v13 sections
    # ============================================================
    print("\n" + "=" * 78)
    print("  Section 9: Codeword ↔ algebraic address bijection (v13)")
    print("=" * 78 + "\n")
    print(f"  Bit layout (5-bit M38 codeword):")
    print(f"      bit 4    : chirality (0=even, 1=odd)")
    print(f"      bits 2-3 : pairing   (00=α, 01=β, 10=γ; 11=invalid)")
    print(f"      bits 0-1 : witness   (00=D, 01=C, 10=S, 11=W)")
    print()
    print(f"  Algebraic address (sign, m, j):")
    print(f"      sign ∈ {{+1, -1}}  ↔  chirality bit (even=+1, odd=-1)")
    print(f"      j    ∈ {{0, 1, 2}} ↔  pairing bits")
    print(f"      m    ∈ {{0, 1, 2, 3}} ↔ witness bits")
    print()
    # Show decoding of t_receipt and s_receipt
    addr_t = receipt_address(t_receipt)
    addr_s = receipt_address(s_receipt)
    print(f"  Example decompositions of receipts from this session:")
    print(f"    {type(t_receipt).__name__:<18} codeword {t_receipt.codeword:05b} "
          f"→ address {addr_t}")
    print(f"    {type(s_receipt).__name__:<18} codeword {s_receipt.codeword:05b} "
          f"→ address {addr_s}")
    print()
    bij_ok = verify_codeword_address_bijection()
    n_valid = len(all_valid_codewords())
    n_addr = len(all_algebraic_addresses())
    print(f"  Bijection: 24 valid codewords ↔ 24 (sign, m, j) addresses")
    print(f"    verify_codeword_address_bijection(): {bij_ok}")
    print(f"    |valid codewords|     = {n_valid}")
    print(f"    |algebraic addresses| = {n_addr}")
    print()
    print(f"  Note (load-bearing): the bijection is a SET correspondence at")
    print(f"  the label level. The GROUP structures of the two 24-element")
    print(f"  spaces differ:")
    print(f"    M38 codeword ops {{v4_swap, invert, chain}}: V_4 × S_3")
    print(f"    M40 spectral closure                      : A_4 × Z_2")
    print(f"  Both order 24, non-isomorphic. The applied grammar uses")
    print(f"  codewords as addresses, not as group elements composed by")
    print(f"  any architectural law. See module docstring for details.")


    print("\n" + "=" * 78)
    print("  Section 10: M41 receipt-kernel admissibility")
    print("              (v13 aggregator, v14 rescoped name)")
    print("=" * 78 + "\n")
    print(f"  THEOREM (receipt-kernel admissibility — NOT global grammar):")
    print()
    print(f"    The receipt/address verification kernel is coherent and")
    print(f"    fail-closed. Receipts are sum-typed; illegal op-name/type")
    print(f"    combinations are unconstructible. The 24 valid M38 codewords")
    print(f"    bijectively correspond to (sign, m, j) algebraic addresses.")
    print(f"    Every op in the registry has a valid codeword. State ops")
    print(f"    have specs with declared obligation_levels and a replay seam")
    print(f"    (populated or None). The Grade lattice has GRADE_IDENTITY as")
    print(f"    meet identity. A live apply receipt verifies as REPLAY_VERIFIED")
    print(f"    + CHART_PURE.")
    print()
    print(f"    v14 NOTE: this does NOT prove global grammar well-typedness.")
    print(f"    The theorem's scope is the receipt/address verification kernel,")
    print(f"    not the entire applied-grammar program space.")
    print()
    c_theorem = ChartChained()
    result = verify_m41_receipt_kernel_admissibility(c_theorem)
    print(f"  verify_m41_receipt_kernel_admissibility(c): {result}")
    print()
    print(f"  Seven sub-claims chained, each independently verifiable.")
    print(f"  Methodologically parallel to M40's verify_m40_group_is_a4z2_not_s4.")

    # ============================================================
    # v14 sections
    # ============================================================
    print("\n" + "=" * 78)
    print("  Section 11: GRADE_IDENTITY (v14 rename of GRADE_TOP)")
    print("=" * 78 + "\n")
    print(f"  GRADE_IDENTITY = Grade(REPLAY_VERIFIED, CHART_PURE,")
    print(f"                          PORTABLE, EFFECT_INAPPLICABLE)")
    print()
    print(f"  This is the IDENTITY element for meet, not the strongest")
    print(f"  element of the product order. Because EFFECT_INAPPLICABLE is")
    print(f"  unit-like (special-cased rather than ranked above")
    print(f"  EFFECT_REPLAY_VERIFIED), meeting GRADE_IDENTITY with any g")
    print(f"  yields g. The old name GRADE_TOP implied lattice-maximum,")
    print(f"  which is misleading.")
    print()
    test_g = Grade(REPLAY_VERIFIED, CHART_PURE, CHART_LOCAL, EFFECT_RECEIPT_DECLARED)
    print(f"  Example: g = ({test_g.transition}, {test_g.purity},")
    print(f"               {test_g.locality}, {test_g.effect})")
    print(f"           g.meet(GRADE_IDENTITY) preserves g: "
          f"{test_g.meet(GRADE_IDENTITY) == test_g}")

    print("\n" + "=" * 78)
    print("  Section 12: StateOpSpec.replay seam (v14)")
    print("=" * 78 + "\n")
    print(f"  v14 adds a `replay` field to StateOpSpec:")
    print()
    print(f"      @dataclass(frozen=True)")
    print(f"      class StateOpSpec:")
    print(f"          name: str")
    print(f"          obligation_level: str")
    print(f"          replay: Optional[Callable[[ChartChained, StateReceipt], bool]]")
    print()
    print(f"  The seam splits effect verification into four observable outcomes:")
    print(f"      spec.replay is None         → EFFECT_RECEIPT_DECLARED")
    print(f"      spec.replay returns True    → EFFECT_REPLAY_VERIFIED")
    print(f"      spec.replay returns False   → FAILED_EFFECT")
    print(f"      spec.replay raises          → FAILED_EFFECT")
    print()
    print(f"  All v14 specs ship with replay=None — the SEAM is type-level.")
    print(f"  Populating individual specs with real replay implementations")
    print(f"  is v15+ work (each requires chart rollback semantics).")
    print()
    print(f"  Demonstration of all four branches (with temporarily patched specs):")
    print()
    # Demo the seam by temporarily replacing the 'store' spec
    original_spec = _STATE_OP_SPECS['store']
    try:
        # Case A: replay=None (the default)
        c_demo = ChartChained()
        w_demo = c_demo.workspace_alloc()
        _, r_demo = store_with_receipt(c_demo, w_demo, c_demo.TRUE)
        vr_A = verify_receipt(c_demo, r_demo)
        print(f"    replay=None:           effect_level = {vr_A.effect_level}")

        # Case B: replay returns True
        _STATE_OP_SPECS['store'] = StateOpSpec(
            name='store', obligation_level=EFFECT_REPLAY_VERIFIED,
            replay=lambda c, r: True,
        )
        c_demo = ChartChained()
        w_demo = c_demo.workspace_alloc()
        _, r_demo = store_with_receipt(c_demo, w_demo, c_demo.TRUE)
        vr_B = verify_receipt(c_demo, r_demo)
        print(f"    replay returns True:   effect_level = {vr_B.effect_level}")

        # Case C: replay returns False
        _STATE_OP_SPECS['store'] = StateOpSpec(
            name='store', obligation_level=EFFECT_REPLAY_VERIFIED,
            replay=lambda c, r: False,
        )
        c_demo = ChartChained()
        w_demo = c_demo.workspace_alloc()
        _, r_demo = store_with_receipt(c_demo, w_demo, c_demo.TRUE)
        vr_C = verify_receipt(c_demo, r_demo)
        print(f"    replay returns False:  effect_level = {vr_C.effect_level}  (ok={vr_C.ok})")

        # Case D: replay raises
        def _replay_boom(c, r):
            raise RuntimeError("replay implementation broken")
        _STATE_OP_SPECS['store'] = StateOpSpec(
            name='store', obligation_level=EFFECT_REPLAY_VERIFIED,
            replay=_replay_boom,
        )
        c_demo = ChartChained()
        w_demo = c_demo.workspace_alloc()
        _, r_demo = store_with_receipt(c_demo, w_demo, c_demo.TRUE)
        vr_D = verify_receipt(c_demo, r_demo)
        print(f"    replay raises:         effect_level = {vr_D.effect_level}  (ok={vr_D.ok})")
    finally:
        _STATE_OP_SPECS['store'] = original_spec
    print()
    print(f"  The effect axis is now SUBSTANTIVE: declared-only vs. genuinely")
    print(f"  re-verified are observably different runtime distinctions.")

    # ============================================================
    # v15 sections
    # ============================================================
    print("\n" + "=" * 78)
    print("  Section 13: GRADE_STRONGEST_EVIDENCE (v15)")
    print("=" * 78 + "\n")
    print(f"  v15 distinguishes TWO grade constants:")
    print()
    print(f"    GRADE_IDENTITY            = Grade(REPLAY_VERIFIED, CHART_PURE,")
    print(f"                                       PORTABLE, EFFECT_INAPPLICABLE)")
    print(f"    GRADE_STRONGEST_EVIDENCE  = Grade(REPLAY_VERIFIED, CHART_PURE,")
    print(f"                                       PORTABLE, EFFECT_REPLAY_VERIFIED)")
    print()
    print(f"  They differ on the effect axis:")
    print(f"    IDENTITY.effect   = {GRADE_IDENTITY.effect}")
    print(f"    STRONGEST.effect  = {GRADE_STRONGEST_EVIDENCE.effect}")
    print()
    print(f"  GRADE_IDENTITY is the meet identity (and top of the meet-induced")
    print(f"  order, since a.meet(IDENTITY) == a). But EFFECT_INAPPLICABLE is")
    print(f"  the WEAKEST claim on the evidence-strength axis (no claim made).")
    print(f"  GRADE_STRONGEST_EVIDENCE is what you compare against to ask 'is")
    print(f"  this the strongest possible evidence?'")
    print()
    meet_result = GRADE_IDENTITY.meet(GRADE_STRONGEST_EVIDENCE)
    print(f"  IDENTITY.meet(STRONGEST) preserves the stronger effect:")
    print(f"    result.effect = {meet_result.effect}")

    print("\n" + "=" * 78)
    print("  Section 14: State cursor seam (v15)")
    print("=" * 78 + "\n")
    print(f"  verify_trace gains two optional parameters:")
    print()
    print(f"    initial_state_digest: Optional[str] = None")
    print(f"    final_state_digest:   Optional[str] = None")
    print()
    print(f"  When initial_state_digest is provided, verify_trace checks the")
    print(f"  StateReceipt chain coherently advances:")
    print(f"      first.state_pre_digest  == initial_state_digest")
    print(f"      prev.state_post_digest  == next.state_pre_digest")
    print(f"      last.state_post_digest  == final_state_digest (if given)")
    print()
    print(f"  This is the STRUCTURAL dual of the term cursor. Term receipts")
    print(f"  advance start → final on term ids; state receipts advance")
    print(f"  initial_state → final_state on digests.")
    print()
    print(f"  Demonstration:")
    print()
    c_sc = ChartChained()
    w_sc = c_sc.workspace_alloc()    # pre-trace setup
    initial_sc = compute_chart_state_digest(c_sc)
    _, r1_sc = store_with_receipt(c_sc, w_sc, c_sc.TRUE)
    _, r2_sc = quote_via_state_with_receipt(c_sc, c_sc.TRUE)
    final_sc = compute_chart_state_digest(c_sc)

    # Case A: state cursor inactive (default v14 behavior)
    vr_A = verify_trace(c_sc, 0, 0, [r1_sc, r2_sc])
    print(f"    Default (cursor inactive):  ok={vr_A.ok}")

    # Case B: coherent chain with active cursor
    vr_B = verify_trace(c_sc, 0, 0, [r1_sc, r2_sc],
                        initial_state_digest=initial_sc,
                        final_state_digest=final_sc)
    print(f"    Coherent chain enforced:    ok={vr_B.ok}")

    # Case C: forge a chain-break to demonstrate detection
    from dataclasses import replace
    r2_forged = replace(r2_sc, state_pre_digest="0" * 64)
    vr_C = verify_trace(c_sc, 0, 0, [r1_sc, r2_forged],
                        initial_state_digest=initial_sc)
    print(f"    Forged middle pre_digest:   ok={vr_C.ok}")
    print(f"      reason: {vr_C.reason[:60]}...")
    print()
    print(f"  The state cursor catches receipt-chain corruption STRUCTURALLY,")
    print(f"  without needing replay to validate that any single digest")
    print(f"  describes a real chart state.")

    # ============================================================
    # v16: orbit-canonical decomposition
    # ============================================================
    print("\n" + "=" * 78)
    print("  Section 15: Orbit-canonical signature decomposition (v16)")
    print("=" * 78 + "\n")
    print(f"  The 24 valid (source, sink, witness) signatures form a Cayley-")
    print(f"  Dickson ladder at level 2:")
    print()
    print(f"      'real'      = witness (V_4, 2 bits)")
    print(f"      'imaginary' = pairing (V_4, 2 bits, parity-sieved)")
    print(f"      chirality   = sign    (Z_2, 1 bit)")
    print()
    print(f"  Naive: 2^5 = 32. Parity sieve forbids pairing=11 (the fourth")
    print(f"  pairing). 32 × 3/4 = 24 valid signatures. Not 8 × 3 — the")
    print(f"  'awkward' Z_3 is actually 'V_4 with 1/4 forbidden by parity'.")
    print()
    print(f"  Under V_4 axis-swap action, the 24 signatures partition into")
    print(f"  6 orbits of 4 each:")
    print()
    print(f"    {len(all_orbit_keys())} orbit-keys × {len(V4_SWAPS)} V_4-deltas = {len(all_valid_signatures())} signatures")
    print()
    print(f"  Orbit structure (each row is a V_4 orbit):")
    print()
    print(f"  {'orbit-key':<18} {'canonical':<18} {'delta:α':<18} "
          f"{'delta:β':<18} {'delta:γ':<18}")
    print(f"  {'-'*18} {'-'*18} {'-'*18} {'-'*18} {'-'*18}")
    for key in all_orbit_keys():
        canonical = canonical_signature_in_orbit(key)
        sigs = sorted(signatures_in_orbit(key),
                      key=lambda s: decompose_signature(s).v4_delta)
        # Build a dict {delta: sig} for clean printing
        by_delta = {decompose_signature(s).v4_delta: s for s in sigs}
        key_str = f"({key[0]}, {key[1]})"
        e_sig = str(by_delta.get('e', ''))
        a_sig = str(by_delta.get('α', ''))
        b_sig = str(by_delta.get('β', ''))
        g_sig = str(by_delta.get('γ', ''))
        print(f"  {key_str:<18} {e_sig:<18} {a_sig:<18} "
              f"{b_sig:<18} {g_sig:<18}")
    print()
    print(f"  Example decomposition:")
    sig_demo = ('D', 'C', 'S')
    decomp = decompose_signature(sig_demo)
    print(f"    signature       = {sig_demo}")
    print(f"    orbit_key       = {decomp.orbit_key}   (V_4-invariant content)")
    print(f"    v4_delta        = {decomp.v4_delta!r}            "
          f"(witness offset from canonical)")
    print(f"    recomposed      = {recompose_signature(decomp.orbit_key, decomp.v4_delta)}")
    print(f"    bijection holds: {verify_signature_decomposition_bijection()}")
    print()
    print(f"  This is the structural seam toward PORTABLE locality. Receipts")
    print(f"  carrying orbit-canonical fields would be content-addressed:")
    print(f"  V_4-equivalent operations share orbit_key, with v4_delta")
    print(f"  recording the witness offset. Wiring this into receipt")
    print(f"  construction is v17+ work; v16 establishes the decomposition.")

    # ============================================================
    # v17 sections
    # ============================================================
    print("\n" + "=" * 78)
    print("  Section 16: Codeword ↔ signature bridge (v17)")
    print("=" * 78 + "\n")
    print(f"  Before v17: codeword ↔ (sign, m, j)     via codeword_to_address")
    print(f"              signature ↔ (orbit_key, delta)  via decompose_signature")
    print(f"  After v17:  codeword ↔ signature ↔ (orbit_key, v4_delta)")
    print()
    print(f"  Every valid codeword decomposes orbit-canonically:")
    print()
    print(f"  {'code':<7} {'signature':<20} {'orbit_key':<20} {'v4_delta'}")
    print(f"  {'-'*7} {'-'*20} {'-'*20} {'-'*8}")
    for code in sorted(all_valid_codewords())[:6]:
        sig = codeword_to_signature(code)
        decomp = codeword_to_orbit_decomposition(code)
        print(f"  0b{code:05b} {str(sig):<20} {str(decomp.orbit_key):<20} {decomp.v4_delta!r}")
    print(f"  ... (24 valid codewords total)")
    print()
    print(f"  Bridge invariants verified:")
    print(f"    codeword↔signature bijection:    {verify_codeword_signature_bijection()}")
    print(f"    codeword→orbit bridge consistent: {verify_codeword_orbit_bridge_consistent()}")
    print(f"    parity-sieve characterization:    {verify_parity_sieve_characterization()}")

    print("\n" + "=" * 78)
    print("  Section 17: Purity-wrap + obligation_level cap (v17)")
    print("=" * 78 + "\n")
    print(f"  Before v17: _verify_state called spec.replay(c, r) directly.")
    print(f"  If replay mutated the chart, the verifier still emitted")
    print(f"  CHART_PURE. v17 snapshots state around the replay call.")
    print()
    print(f"  Demonstration:")
    print()

    # Case 1: pure replay returning True with obligation=DECLARED → capped
    c_demo = ChartChained()
    w_demo = c_demo.workspace_alloc()
    _, r_demo = store_with_receipt(c_demo, w_demo, c_demo.TRUE)

    original_spec = _STATE_OP_SPECS['store']
    try:
        # Spec claims DECLARED-level evidence even though replay returns True
        _STATE_OP_SPECS['store'] = StateOpSpec(
            name='store',
            obligation_level=EFFECT_RECEIPT_DECLARED,
            replay=lambda c, r: True,
        )
        vr_capped = verify_receipt(c_demo, r_demo)
        print(f"    obligation=DECLARED, replay=True:")
        print(f"      effect_level = {vr_capped.effect_level}")
        print(f"      (capped from REPLAY_VERIFIED — spec's claim is honored)")
        print()

        # Case 2: mutating replay → FAILED_PURITY + FAILED_EFFECT
        def mutating_replay(c, r):
            c.workspace_alloc()
            return True

        _STATE_OP_SPECS['store'] = StateOpSpec(
            name='store',
            obligation_level=EFFECT_REPLAY_VERIFIED,
            replay=mutating_replay,
        )
        vr_bad = verify_receipt(c_demo, r_demo)
        print(f"    obligation=REPLAY_VERIFIED, replay mutates chart:")
        print(f"      ok           = {vr_bad.ok}")
        print(f"      purity_level = {vr_bad.purity_level}")
        print(f"      effect_level = {vr_bad.effect_level}")
        print(f"      (the verifier no longer lies about purity)")
    finally:
        _STATE_OP_SPECS['store'] = original_spec

    print("\n" + "=" * 78)
    print("  Section 18: Cached orbit tables + parity-sieve predicate (v17)")
    print("=" * 78 + "\n")
    print(f"  Tables built once at module load:")
    print(f"    _ORBIT_TABLE             : {len(_ORBIT_TABLE)} orbit keys × "
          f"{len(next(iter(_ORBIT_TABLE.values())))} deltas each")
    print(f"    _SIGNATURE_DECOMP_TABLE  : {len(_SIGNATURE_DECOMP_TABLE)} signature entries")
    print()
    print(f"  Accessors (all_valid_signatures, orbit_key_of, decompose_signature,")
    print(f"  canonical_signature_in_orbit, v4_delta_to_canonical) read from the")
    print(f"  cache instead of re-enumerating. O(1) lookup.")
    print()
    print(f"  Parity-sieve as named predicate:")
    print()
    forbidden = [c for c in range(32) if is_parity_forbidden(c)]
    print(f"    is_parity_forbidden returns True for exactly 8 codewords:")
    print(f"    {[f'0b{c:05b}' for c in forbidden]}")
    print(f"    All 8 have pairing bits = 11 (the 'unconsumed quotient' case).")
    print(f"    32 (total) - 8 (forbidden) = 24 (valid) = 32 × 3/4")

    # ============================================================
    # v18 sections
    # ============================================================
    print("\n" + "=" * 78)
    print("  Section 19: Transactional verification boundary (v18)")
    print("=" * 78 + "\n")
    print(f"  v17 detected mutation but did not undo it. v18 makes verification")
    print(f"  OBSERVATIONALLY PURE: even a mutating replay leaves no trace.")
    print()
    print(f"  Demonstration: a deliberately buggy mutating replay")
    print()
    c_t = ChartChained()
    w_t = c_t.workspace_alloc()
    _, r_t = store_with_receipt(c_t, w_t, c_t.TRUE)
    snap_pre = _deep_snapshot_mutable_chart(c_t)

    def buggy_replay(c, r):
        c.workspace_alloc()                  # allocates workspace cell
        c.cons(c.TRUE, c.FALSE)              # allocates a chart cell
        return True                          # claims success

    original_spec = _STATE_OP_SPECS['store']
    try:
        _STATE_OP_SPECS['store'] = StateOpSpec(
            name='store',
            obligation_level=EFFECT_REPLAY_VERIFIED,
            replay=buggy_replay,
        )
        vr = verify_receipt(c_t, r_t)
        snap_post = _deep_snapshot_mutable_chart(c_t)
        print(f"    verify_receipt result:")
        print(f"      ok           = {vr.ok}")
        print(f"      purity_level = {vr.purity_level}")
        print(f"      effect_level = {vr.effect_level}")
        print()
        print(f"    Chart state after verification:")
        print(f"      mutable surface identical to before: {snap_pre == snap_post}")
        print()
        print(f"  v17 would have reported the failure but left the chart")
        print(f"  mutated. v18 restores: verification cannot perturb.")
    finally:
        _STATE_OP_SPECS['store'] = original_spec

    print("\n" + "=" * 78)
    print("  Section 20: Bridge enforcement + ContentAddressedReceiptFields (v18)")
    print("=" * 78 + "\n")
    print(f"  Every receipt now goes through _check_codeword_bridge:")
    print(f"    codeword → signature → orbit decomposition")
    print(f"    + codeword roundtrip identity")
    print(f"    + (if receipt carries them) consistency of:")
    print(f"        receipt.content_addressed.signature")
    print(f"        receipt.content_addressed.orbit_key")
    print(f"        receipt.content_addressed.v4_delta")
    print(f"        receipt.content_addressed.orbit_canonical_digest")
    print()
    print(f"  ContentAddressedReceiptFields (derivable from codeword):")
    print()
    sample_code = sorted(all_valid_codewords())[2]
    fields = derive_content_addressed_fields(sample_code)
    print(f"    For codeword 0b{sample_code:05b}:")
    print(f"      signature              = {fields.signature}")
    print(f"      orbit_key              = {fields.orbit_key}")
    print(f"      v4_delta               = {fields.v4_delta!r}")
    print(f"      orbit_canonical_digest = {fields.orbit_canonical_digest[:24]}...")
    print()
    print(f"  V_4 twins (same orbit_key) share orbit_canonical_digest:")
    print()
    orbit = signatures_in_orbit(fields.orbit_key)
    for sig in orbit:
        code = signature_to_codeword(sig)
        f = derive_content_addressed_fields(code)
        print(f"    sig {sig} → digest {f.orbit_canonical_digest[:16]}...")
    print()
    print(f"  All 4 V_4-translates produce identical orbit_canonical_digest.")
    print(f"  This is the content-addressed identity. Distinct orbit_keys")
    print(f"  produce distinct digests (6 orbits → 6 distinct digests).")

    # Thesis
    print("\n" + "=" * 78)
    print("  Thesis (v18)")
    print("=" * 78)
    print("""
  v18 closes the three audit issues from v17 and adds the
  forward-looking ContentAddressedReceiptFields type.

  TRANSACTIONAL VERIFICATION:
    _transactional_observe wraps any thunk in:
      snapshot full mutable state → run → classify → RESTORE
    Verification can never perturb the chart. Both replay paths
    (state replay and permissive term replay) now use this. The
    purity classification still tells you what the thunk did;
    restoration ensures the caller never sees consequences.

  FULL MUTABLE-SURFACE SNAPSHOT:
    v17 classified purity over (_history, _apply_memo, _cells).
    v18 adds _hashcons and _workspace / _workspace_free. A replay
    mutating _hashcons without touching _cells used to slip past
    v17's CHART_PURE check; v18 catches it.

  BRIDGE ENFORCEMENT IN VERIFIER:
    _check_codeword_bridge runs on every receipt. The v17 bridge
    (codeword ↔ signature ↔ orbit decomposition) is now an
    enforced receipt obligation, not just a library invariant.

  CONTENT-ADDRESSED RECEIPT FIELDS:
    ContentAddressedReceiptFields dataclass + derive_content_addressed_
    fields helper available. When a receipt carries these fields, the
    verifier checks consistency with derived values. Receipt-level
    adoption (constructors populating the field by default) is v19+.

  PROSE TIGHTENED:
    codeword_to_signature documentation distinguishes:
      pairing bits identify the PARTITION  (pair1, pair2)
      witness selects which side of the partition is NOT (source, sink)
    Previously the comment elided this distinction; v18 makes it
    explicit at the documentation level (the implementation was
    already correct).

  STILL DEFERRED (named):
    - Receipt constructors populating content_addressed by default (v19+)
    - PORTABLE locality grade emitted by verifiers (requires v19's
      first-class adoption to be load-bearing)
    - Populated EFFECT_REPLAY_VERIFIED implementations (v14 seam;
      v18 ensures any populated replay is now transactional)
    - Structural hash for chart cells (cell-level companion to
      operation-level orbit-canonical)
""")

    # ────────────────────────────────────────────────────────────────────
    # v19 sections
    # ────────────────────────────────────────────────────────────────────
    print()
    print("  Section 21: V_4 ⋊ S_3 as primary structure (v19)")
    print("  " + "-" * 70)
    print(f"  v17 introduced (orbit_key, v4_delta) decomposition; v19 grounds it")
    print(f"  in the formal V_4 ⋊ S_3 group structure on S_4.")
    print()
    from s4_structure import (
        S4_ELEMENTS, V4_AS_PERMUTATIONS, STAB_D,
        factor_s4, signature_to_permutation, stab_d_to_orbit_key,
        sn_cayley_dickson_table, verify_s4_formalization,
    )
    print(f"  |S_4| = {len(S4_ELEMENTS)}  =  |V_4| × |Stab(D)| = {len(V4_AS_PERMUTATIONS)} × {len(STAB_D)}")
    print(f"  verify_s4_formalization() → {verify_s4_formalization()}")
    print()
    print(f"  Sample factorization σ = v · s for signature ('S', 'D', 'C'):")
    σ = signature_to_permutation(('S', 'D', 'C'))
    v, s = factor_s4(σ)
    print(f"    σ          = {σ.image}    sign={σ.sign():+d}")
    print(f"    v ∈ V_4    = {v.image}    (name: {next(n for n, p in V4_AS_PERMUTATIONS.items() if p == v)!r})")
    print(f"    s ∈ Stab(D)= {s.image}    orbit_key = {stab_d_to_orbit_key(s)}")
    print(f"    v ∘ s      = {v.compose(s).image}   (= σ ✓)")
    print()

    print("  Section 22: S_n vs Cayley-Dickson correspondence (v19)")
    print("  " + "-" * 70)
    print(f"  Each S_n corresponds to a Cayley-Dickson level n, but the S_n grows")
    print(f"  by 'thick' steps (n!) while CD grows by 'thin' steps (2^n).")
    print()
    print(f"  {'n':<3} {'|S_n|':<8} {'2^n':<6} {'ratio':<10}")
    for n, (sn, cd) in sn_cayley_dickson_table().items():
        ratio_str = f"{sn}/{cd}"
        print(f"  {n:<3} {sn:<8} {cd:<6} {ratio_str:<10}")
    print()
    print(f"  At level 4: |S_4| = 24, 2^4 = 16. The user's correction was")
    print(f"  'compare 24 to 32, not 16' — that is, compare to the level-5 CD")
    print(f"  ambient (with chirality bit at the top). 32 = 24 + 8 splits as")
    print(f"  |S_4| + 2 · dim(Λ^1) = primal + Hodge dual.")
    print()
    print(f"  The 8 'missing' parity-forbidden codewords are signed singletons,")
    print(f"  Hodge-dual to oriented unordered triples (24/3 = 8 unordered orbits).")
    print()

    print("  Section 23: Agreement between v17 and V_4 ⋊ S_3 (v19)")
    print("  " + "-" * 70)
    print(f"  v17's (orbit_key, v4_delta) decomposition uses lex-min canonical;")
    print(f"  V_4 ⋊ S_3 uses Stab(D) canonical. They differ by a per-orbit V_4")
    print(f"  element δ.")
    print()
    print(f"  verify_v17_v19_decomposition_agreement() → {verify_v17_v19_decomposition_agreement()}")
    print(f"  verify_canonical_offset_consistent_per_orbit() → {verify_canonical_offset_consistent_per_orbit()}")
    print()
    print(f"  Canonical offset δ per orbit:")
    for key in all_orbit_keys():
        δ = canonical_offset_for_orbit(key)
        print(f"    orbit {key!r:>20} → δ = {δ!r}")
    print()
    print(f"  Uniform result: δ = 'α' across all 6 orbits. This reflects")
    print(f"  that Stab(D) canonical fixes D while v17 lex-min starts with C,")
    print(f"  and V_4 element 'α' = (DC)(SW) accounts for that swap uniformly.")
    print()

    print("  Thesis (v19)")
    print("  " + "-" * 70)
    print("""
  v19 establishes the V_4 ⋊ S_3 group structure of S_4 as the PRIMARY
  formal foundation of M41's address space, with v17's (orbit_key,
  v4_delta) decomposition as a DERIVED presentation.

  THE FORMALIZATION (s4_structure.py):
    1. S_4 as a concrete group: Permutation class, composition,
       inverse, sign, order. All 24 elements enumerated.
    2. V_4 ⊂ S_4 as the Klein four normal subgroup, with
       V_4 ≅ {'e', 'α', 'β', 'γ'} matching meta_protocol.V4_SWAPS.
    3. S_3 realized as Stab(D), the complement to V_4.
    4. Unique factorization σ = v · s, v ∈ V_4, s ∈ Stab(D).
    5. Signature ↔ Permutation bijection via (σ(D), σ(C), σ(S)).
    6. Selection-sort descent (S_4 → S_3 → S_2 → S_1) as the
       DERIVED axis-selection enumeration (the user's geometric
       illustration; not the primary structure).
    7. Hodge ★ structure: 24 ordered triples (valid codewords)
       Hodge-dual to 8 signed singletons (forbidden codewords)
       via the 4D wedge product.
    8. Cayley-Dickson correspondence table |S_n| vs 2^n for n=0..5.

  THE AGREEMENT (applied_grammar.py):
    v17_to_v4_s3(sig) reproduces decompose_signature(sig) via the
    V_4 ⋊ S_3 factorization. The two decompositions agree on
    orbit_key exactly; their v4_delta values differ by a fixed
    per-orbit δ ∈ V_4 (uniformly δ = 'α', reflecting the lex-min
    vs Stab(D) canonical choice).

    verify_v17_v19_decomposition_agreement and
    verify_canonical_offset_consistent_per_orbit are now
    load-bearing — they prove v17's combinatorial structure is
    grounded in the V_4 ⋊ S_3 group structure.

  WHAT v19 DOES NOT DO (named):
    - Receipt constructor adoption of ContentAddressedReceiptFields
      (still v20+; CARF is available but not populated by default).
    - PORTABLE locality emission by verifiers.
    - Cell-level structural hashing (operation-level orbit-canonical
      is in place; cell-level companion is deferred).
    - Generalization of the S_n / Cayley-Dickson table to operational
      use beyond the level-4 / level-5 axis count.

  CHARTER ALIGNMENT:
    - constructible: factor_s4 is concrete, deterministic, total on S_4
    - reachable: all 24 valid codewords map to S_4 elements; bridge ran
    - observable: verify_v17_v19_decomposition_agreement passes for all
    - coverable: 35 tests in verify_s4_structure + 5 new in verify_applied_grammar
    - distinction valid: V_4 ⋊ S_3 ≠ A_4 × Z_2 (M40); the M38/M40 SET
      bijection at label level remains as documented in v13
""")

    # ────────────────────────────────────────────────────────────────────
    # v20 sections
    # ────────────────────────────────────────────────────────────────────
    print()
    print("  Section 24: StructuralAddress as receipt-ready object (v20)")
    print("  " + "-" * 70)
    print(f"  v19 made S_4 the primary structure; v20 carries it into a")
    print(f"  receipt-ready StructuralAddress that bundles the permutation,")
    print(f"  the V_4 ⋊ S_3 factorization, the v17 (orbit_key, v4_delta)")
    print(f"  coordinates, the signature, and the codeword as a single")
    print(f"  frozen object. All projections commute.")
    print()
    print(f"  verify_structural_address_projections_commute() → "
          f"{verify_structural_address_projections_commute()}")
    print(f"  verify_structural_address_unique_per_signature() → "
          f"{verify_structural_address_unique_per_signature()}")
    print(f"  verify_structural_address_codeword_roundtrip() → "
          f"{verify_structural_address_codeword_roundtrip()}")
    print()
    sample = structural_address_from_signature(('S', 'D', 'C'))
    print(f"  Sample address for signature ('S', 'D', 'C'):")
    print(f"    permutation       = {sample.permutation.image}")
    print(f"    v4_component      = {sample.v4_component.image}")
    print(f"    stab_d_component  = {sample.stab_d_component.image}")
    print(f"    orbit_key         = {sample.orbit_key}")
    print(f"    v4_delta          = {sample.v4_delta!r}")
    print(f"    signature         = {sample.signature}")
    print(f"    codeword          = 0b{sample.codeword:05b} ({sample.codeword})")
    print()
    print(f"  Three construction paths agree:")
    addr_a = structural_address_from_signature(('S', 'D', 'C'))
    addr_b = structural_address_from_permutation(addr_a.permutation)
    addr_c = structural_address_from_codeword(addr_a.codeword)
    print(f"    from_signature == from_permutation: {addr_a == addr_b}")
    print(f"    from_signature == from_codeword:    {addr_a == addr_c}")
    print()

    print("  Thesis (v20)")
    print("  " + "-" * 70)
    print("""
  v20 elevates the address space's structural object to first-class
  status. The PRIMARY object is the S_4 permutation; everything else
  — V_4 ⋊ S_3 factorization, (orbit_key, v4_delta), signature,
  codeword — is a projection or serialization. StructuralAddress
  carries all coordinates together as a frozen object.

  THE INVERSION (from v17 to v20):
    Before:
        codeword algebra → inferred symmetry structure
    After:
        S_4 action geometry → codeword serialization/projection

    The codeword is no longer the primary witness; it is one chart
    on the address manifold. StructuralAddress is the chart-free
    object that carries the manifold's coordinates simultaneously.

  THE COMMUTATIVE DIAGRAM:
    For every valid signature, three construction paths agree:
        from_permutation(σ) == from_signature(sig) == from_codeword(code)
    And internally:
        permutation = signature_to_permutation(signature)
        signature   = permutation_to_signature(permutation)
        codeword    = signature_to_codeword(signature)
        permutation = v4_component · stab_d_component
        orbit_key   = stab_d_to_orbit_key(stab_d_component)
        v4_delta    = v17 decompose_signature output

    verify_structural_address_projections_commute proves all of these
    for every valid signature in a single load-bearing call.

  WHAT v20 DOES NOT DO (named, deferred to v21+):
    - Receipt dataclasses still carry `codeword: int`, not `address:
      StructuralAddress`. The address is available; receipts have not
      yet been refactored to carry it as their primary field.
    - PORTABLE locality grade emission via address-digesting verifiers
      (still depends on the receipt refactor; v22+ candidate).
    - Cell-level structural addressing (operation-level addressing is
      in place; cell-level analogue still uses structural hashes).
    - A categorical functor F: CD ambient → S_n signature sieve.
      The K_3 × K_4 cardinality match remains a heuristic geometric
      shadow, not a derived theorem. The natural V_4 polytope
      automorphism does NOT realize the codeword V_4-presentation
      structure (orbit sizes {1,2,4} mixed); any structural bijection,
      if it exists, must use a different mechanism.

  CHARTER ALIGNMENT:
    - constructible: StructuralAddress assembled from any of three
      input forms; all three give the same result
    - reachable: all 24 valid signatures yield a unique address
    - observable: verify_structural_address_projections_commute is
      exhaustive over all 24 signatures
    - coverable: 8 v20 tests in verify_applied_grammar covering the
      three constructors, the commutative diagram, factorization
      reconstruction, codeword roundtrip, forbidden-codeword refusal,
      and uniqueness
""")

    # ────────────────────────────────────────────────────────────────────
    # v21 sections
    # ────────────────────────────────────────────────────────────────────
    print()
    print("  Section 25: Receipts obligated to carry StructuralAddress (v21)")
    print("  " + "-" * 70)
    print(f"  v20 made StructuralAddress available; v21 makes it unskippable.")
    print(f"  Every TermReceipt, StateReceipt, and ObservationReceipt now")
    print(f"  carries an `address: StructuralAddress` field (auto-derived")
    print(f"  from codeword if not supplied; explicit addresses must match).")
    print(f"  Derived properties (signature, orbit_key, v4_delta) expose")
    print(f"  the address coordinates directly.")
    print()
    code = next(iter(all_valid_codewords()))
    r = TermReceipt(op_name=next(iter(_TERM_OPS)), codeword=code, before=0, after=0)
    print(f"  Sample receipt for codeword 0b{code:05b}:")
    print(f"    receipt.codeword     = 0b{r.codeword:05b}")
    print(f"    receipt.address.codeword  = 0b{r.address.codeword:05b}  (= codeword ✓)")
    print(f"    receipt.signature    = {r.signature}")
    print(f"    receipt.orbit_key    = {r.orbit_key}")
    print(f"    receipt.v4_delta     = {r.v4_delta!r}")
    print()
    print(f"  verify_receipt_address_codeword_agreement() → "
          f"{verify_receipt_address_codeword_agreement()}")
    print(f"  verify_receipt_address_rejects_inconsistent() → "
          f"{verify_receipt_address_rejects_inconsistent()}")
    print(f"  verify_receipt_derived_properties_match_address() → "
          f"{verify_receipt_derived_properties_match_address()}")
    print()

    print("  Thesis (v21)")
    print("  " + "-" * 70)
    print("""
  v21 makes StructuralAddress unskippable at the receipt level. Every
  TermReceipt, StateReceipt, and ObservationReceipt carries an
  `address: StructuralAddress` field. The codeword remains for
  backward compatibility and serialization, but the structural
  WITNESS is now the address — the codeword is one chart on it.

  THE OBLIGATION:
    Before v21:                          After v21:
      receipt.codeword → bridge →           receipt.address is intrinsic;
      derived (signature, orbit_key)        receipt.signature, .orbit_key,
      (verifier-enforced per receipt)       .v4_delta are properties on
                                            the address, never re-derived

  CONSTRUCTOR BEHAVIOR:
    Receipt(op_name=..., codeword=c)         # auto-derives address
    Receipt(op_name=..., codeword=c,
            address=structural_address_      # accepts explicit address
                from_codeword(c))
    Receipt(op_name=..., codeword=c,
            address=address_for_other_code)  # raises ValueError

    The constructor invariant `address.codeword == self.codeword` is
    proven by verify_receipt_address_codeword_agreement over all 24
    valid codewords × 3 receipt types = 72 constructions.

  WHAT v18's BRIDGE BECAME:
    v18's _check_codeword_bridge was a per-receipt verifier obligation.
    For any receipt constructed via the v21 path, that check is now
    redundant: the bridge holds by construction in __post_init__.
    The bridge verifier is preserved for backward compatibility but is
    no longer load-bearing for v21+ receipts.

  WHAT v21 DOES NOT DO (named, deferred to v22+):
    - op_address_digest still uses the older content-addressed-fields
      derivation; v22+ should digest the StructuralAddress directly.
    - PORTABLE locality is still chart-nonce-coupled; v22 makes
      PORTABLE reachable by digesting the StructuralAddress.
    - Cell-level structural addresses (the cell analogue of
      StructuralAddress); operations are now address-first, cells
      are not yet.
    - Hodge-dual codewords still cannot construct receipts; they are
      not S_4 permutations. (This is correct behavior, but the v19.3
      8 × 4 view suggests an "OrientedTripleReceipt" type that could
      carry the underlying triple without committing to a presentation.
      Whether this is worth building depends on whether any operation
      ever needs to act on the underlying triple presentation-free.)

  CHARTER ALIGNMENT:
    - constructible: every receipt obtains an address (auto or explicit)
    - reachable: all 24 valid codewords × 3 receipt types tested
    - observable: receipt.address inspectable; derived properties available
    - coverable: 8 v21 tests covering auto-derivation, explicit
      acceptance, inconsistency rejection, property agreement, and
      per-receipt-type construction across all 24 codewords
""")

    # ────────────────────────────────────────────────────────────────────
    # v21.1 sections — close the remaining structural-address obligations
    # ────────────────────────────────────────────────────────────────────
    print()
    print("  Section 26: Structural-address obligation closed (v21.1)")
    print("  " + "-" * 70)
    print(f"  v21 made every receipt carry a StructuralAddress. v21.1")
    print(f"  closes the remaining loose threads named in the audit:")
    print()
    print(f"    A. compute_op_address_digest now hashes the structural")
    print(f"       address content (op_name + codeword + signature +")
    print(f"       orbit_key + v4_delta), not just (op_name, codeword).")
    print()
    print(f"    B. _check_codeword_bridge collapsed from re-derivation")
    print(f"       to address-equality: three lines instead of four")
    print(f"       consistency checks.")
    print()
    print(f"    C. verify_every_receipt_carries_structural_address is")
    print(f"       the umbrella verifier — aggregating the v21 obligations")
    print(f"       into one load-bearing theorem.")
    print()
    print(f"  Verifiers:")
    print(f"    verify_op_address_digest_uses_structural_address() → "
          f"{verify_op_address_digest_uses_structural_address()}")
    print(f"    verify_every_receipt_carries_structural_address() → "
          f"{verify_every_receipt_carries_structural_address()}")
    print()
    print(f"  Digest sample (note: structural payload, not raw int):")
    sample_chart = ChartChained()
    for op in ('apply', 'allocate'):
        try:
            digest = compute_op_address_digest(sample_chart, op)
            print(f"    compute_op_address_digest({op!r:11}) = {digest[:16]}...")
        except Exception as e:
            print(f"    {op!r}: {e}")
    print()

    print("  Thesis (v21.1)")
    print("  " + "-" * 70)
    print("""
  v21.1 closes the structural-address obligation loop. The audit named
  the exact remaining seam:

      Right now, StructuralAddress is proven, but not yet obligated.
      v21 should make it unskippable.

  Three concrete moves landed:

    (A) The op_address_digest hashes the structural address. Two
        receipts for the same op with the same address share a digest
        even across chart instances (provided registries map op_names
        to the same codewords). This is the seam for v22's PORTABLE.

    (B) The bridge collapsed. _check_codeword_bridge was a four-step
        re-derivation (codeword → signature → orbit_key → recompose
        with consistency check at each step). It is now a single
        equality: address == structural_address_from_codeword(codeword).
        The earlier derivation logic is preserved in comments; what
        was load-bearing has migrated to construction.

    (C) The umbrella verifier ties off the obligation. When
        verify_every_receipt_carries_structural_address() returns True,
        no receipt path bypasses StructuralAddress — not construction,
        not derivation, not digest, not verification.

  WHAT THIS UNLOCKS:
    The structural-address digest commits to (op_name, codeword,
    signature, orbit_key, v4_delta). Two ChartChained instances with
    the same registry will produce the SAME op_address_digest for
    the SAME op, regardless of nonces or instance identity. This is
    the prerequisite for v22's PORTABLE locality grade: a receipt
    that can be replayed against a different chart instance with the
    same registry, because its address content commits to structural
    invariants rather than instance-specific state.

  WHAT v21.1 DOES NOT DO (named, still v22+):
    - Receipt construction still requires a codeword first; the
      preferred address-first API would be Receipt(op_name=...,
      address=...) with codeword derived. This is a cosmetic API
      improvement, not a structural one.
    - Cell-level structural addressing (operations now address-first;
      cells still use structural hashes).
    - PORTABLE locality grade emission by verifiers. The digest is
      now structural; the verifier should classify receipts as
      PORTABLE when their address digest matches across instances.

  CHARTER ALIGNMENT:
    - constructible: digest construction is total, deterministic, uses
      _canonical_bytes uniformly
    - reachable: umbrella verifier covers Term/State/Observation × 24
      codewords; digest tested on all registered ops
    - observable: digest content is inspectable via structural_address_
      from_codeword(receipt.codeword)
    - coverable: 3 v21.1 tests (digest-uses-structural, digest-differs-
      from-legacy, umbrella) covering the three named gaps
""")



if __name__ == "__main__":
    demo()
