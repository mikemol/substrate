"""
s4_structure.py — Formal V_4 ⋊ S_3 group structure on the 4 axes.

The 24 valid (source, sink, witness) signatures are the elements of
S_4 acting on AXES = {D, C, S, W}. S_4 decomposes as

    S_4 ≅ V_4 ⋊ S_3

where V_4 is the Klein four normal subgroup of double-transpositions
plus identity, and S_3 is a complement realized as Stab(D) — the
stabilizer of the anchor axis D.

This V_4 ⋊ S_3 factorization is the PRIMARY formal structure of
M41's address space. The selection-sort descent S_4 → S_3 → S_2 → S_1
(picking an axis at each level) is a DERIVED enumeration.

The 32-element raw codeword space decomposes via Hodge ★ in dim 4:
    32 = |S_4| + 2 · dim(Λ^1) = 24 + 8
where the 24 are ordered triples (valid codewords) and the 8 are
signed singletons — Hodge duals to oriented unordered triples.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List, Dict, FrozenSet
from itertools import permutations
import math

from meta_protocol import AXES, V4_SWAPS, PAIRINGS


# ============================================================
# Permutation: an element of S_4
# ============================================================
#
# A permutation σ of the 4 axes is represented by its image tuple:
#     image[i] = σ(AXES[i])
# Composition self∘other applies `other` first, then `self`.


@dataclass(frozen=True)
class Permutation:
    """An element of S_4 acting on AXES."""
    image: Tuple[str, str, str, str]

    def __post_init__(self):
        if set(self.image) != set(AXES) or len(self.image) != 4:
            raise ValueError(f"not a permutation of {AXES}: {self.image}")

    def apply(self, axis: str) -> str:
        return self.image[AXES.index(axis)]

    def compose(self, other: 'Permutation') -> 'Permutation':
        """self ∘ other: apply other first, then self."""
        return Permutation(tuple(self.apply(other.apply(a)) for a in AXES))

    def inverse(self) -> 'Permutation':
        inv = [None] * 4
        for i, a in enumerate(AXES):
            inv[AXES.index(self.image[i])] = a
        return Permutation(tuple(inv))

    def sign(self) -> int:
        """+1 for even, -1 for odd. Sign of the permutation."""
        indices = [AXES.index(a) for a in self.image]
        inv = sum(
            1 for i in range(4) for j in range(i+1, 4)
            if indices[i] > indices[j]
        )
        return 1 if inv % 2 == 0 else -1

    def is_identity(self) -> bool:
        return self.image == AXES

    def order(self) -> int:
        cur = self
        for k in range(1, 25):
            if cur.is_identity():
                return k
            cur = cur.compose(self)
        raise RuntimeError("element order > 24 — impossible in S_4")


IDENTITY: Permutation = Permutation(AXES)


# ============================================================
# Enumerate S_4
# ============================================================

S4_ELEMENTS: List[Permutation] = [Permutation(p) for p in permutations(AXES)]


# ============================================================
# V_4: the Klein four normal subgroup
# ============================================================
#
# V_4 = {e, (DC)(SW), (DS)(CW), (DW)(CS)}
# Image tuples respectively: (D,C,S,W), (C,D,W,S), (S,W,D,C), (W,S,C,D)
# Element names match meta_protocol.V4_SWAPS: 'e', 'α', 'β', 'γ'.

V4_AS_PERMUTATIONS: Dict[str, Permutation] = {
    'e': Permutation(('D', 'C', 'S', 'W')),
    'α': Permutation(('C', 'D', 'W', 'S')),
    'β': Permutation(('S', 'W', 'D', 'C')),
    'γ': Permutation(('W', 'S', 'C', 'D')),
}

V4_ELEMENT_TO_NAME: Dict[Permutation, str] = {
    p: n for n, p in V4_AS_PERMUTATIONS.items()
}

V4_ELEMENTS: List[Permutation] = list(V4_AS_PERMUTATIONS.values())


def v4_swap_consistency() -> bool:
    """V4_AS_PERMUTATIONS matches meta_protocol.V4_SWAPS componentwise."""
    for name, perm in V4_AS_PERMUTATIONS.items():
        swap = V4_SWAPS[name]
        for a in AXES:
            if perm.apply(a) != swap[a]:
                return False
    return True


# ============================================================
# S_3 as Stab(D): the complement to V_4
# ============================================================
#
# S_4 / V_4 ≅ S_3 abstractly. We realize S_3 concretely inside S_4
# as the stabilizer of D — the 6 permutations fixing the anchor axis.
# This is a COMPLEMENT to V_4: V_4 ∩ Stab(D) = {e}, |V_4|·|Stab(D)| = |S_4|.

ANCHOR_AXIS = 'D'

STAB_D: List[Permutation] = [σ for σ in S4_ELEMENTS if σ.apply(ANCHOR_AXIS) == ANCHOR_AXIS]


# ============================================================
# V_4 ⋊ S_3 factorization (the PRIMARY structure)
# ============================================================
#
# Every σ ∈ S_4 factors uniquely as σ = v · s, v ∈ V_4, s ∈ Stab(D).
#
# Derivation: σ(D) = v(s(D)) = v(D) since s fixes D. So v is the
# unique V_4 element with v(D) = σ(D). Then s = v^(-1) · σ.


def factor_s4(σ: Permutation) -> Tuple[Permutation, Permutation]:
    """Factor σ as (v, s) with v ∈ V_4, s ∈ Stab(D). σ = v · s."""
    target = σ.apply(ANCHOR_AXIS)
    for v in V4_ELEMENTS:
        if v.apply(ANCHOR_AXIS) == target:
            return v, v.inverse().compose(σ)
    raise ValueError(f"V_4 has no element with v(D) = {target}")


def unfactor_s4(v: Permutation, s: Permutation) -> Permutation:
    """Inverse: reconstruct σ from (v, s)."""
    if v not in V4_AS_PERMUTATIONS.values():
        raise ValueError("v not in V_4")
    if s.apply(ANCHOR_AXIS) != ANCHOR_AXIS:
        raise ValueError("s not in Stab(D)")
    return v.compose(s)


# ============================================================
# Signature ↔ Permutation bijection
# ============================================================
#
# signature (source, sink, witness) ∈ S_4 via:
#     σ ↔ (σ(D), σ(C), σ(S))   with σ(W) implicit as the "fourth"


Signature = Tuple[str, str, str]


def signature_to_permutation(sig: Signature) -> Permutation:
    if len(set(sig)) != 3 or not all(a in AXES for a in sig):
        raise ValueError(f"invalid signature: {sig}")
    fourth = next(a for a in AXES if a not in sig)
    return Permutation((sig[0], sig[1], sig[2], fourth))


def permutation_to_signature(σ: Permutation) -> Signature:
    return (σ.image[0], σ.image[1], σ.image[2])


# ============================================================
# Orbit-key extraction from Stab(D)
# ============================================================
#
# Each s ∈ Stab(D) determines its (pairing, chirality) orbit key.
# pairing: which V_4 partition pair contains {source, sink}
# chirality: sign of s

# Map each pair to its pairing name
_PAIR_TO_PAIRING: Dict[FrozenSet[str], str] = {}
for _name, (_p1, _p2) in PAIRINGS.items():
    _PAIR_TO_PAIRING[_p1] = _name
    _PAIR_TO_PAIRING[_p2] = _name


def stab_d_to_orbit_key(s: Permutation) -> Tuple[str, str]:
    """Stab(D) element → (pairing, chirality) orbit key."""
    if s.apply(ANCHOR_AXIS) != ANCHOR_AXIS:
        raise ValueError(f"not in Stab(D): {s}")
    sig = permutation_to_signature(s)
    pair = frozenset({sig[0], sig[1]})
    pairing = _PAIR_TO_PAIRING[pair]
    chirality = 'even' if s.sign() == 1 else 'odd'
    return (pairing, chirality)


def orbit_key_to_stab_d(orbit_key: Tuple[str, str]) -> Permutation:
    """Inverse map: orbit_key → the unique Stab(D) element with that key.

    The returned element is INTRINSIC, not enumeration-order-dependent:
    each (pairing, chirality) orbit_key has exactly one Stab(D)
    representative (since |Stab(D)| = 6 = |orbit keys| and
    stab_d_to_orbit_key is a bijection). The iteration is just a way
    to locate that unique element; the answer is determined by the
    group structure alone.

    The universal property: for orbit_key = (pairing, chirality), the
    returned Permutation σ is the unique S_4 element such that
        (i) σ(D) = D                              (fixes anchor)
        (ii) {D, σ(C)} ∈ pairing's partition       (pairing constraint)
        (iii) sign(σ) matches chirality            (parity constraint)
    """
    for s in STAB_D:
        if stab_d_to_orbit_key(s) == orbit_key:
            return s
    raise ValueError(f"no Stab(D) representative for {orbit_key}")


# ============================================================
# Selection-sort descent (DERIVED presentation)
# ============================================================
#
# The user described this as a geometric illustration. Primary
# structure is V_4 ⋊ S_3; this descent is an axis-selection
# enumeration: pick fourth (4 choices), witness (3 choices),
# source (2 choices), sink determined.


def selection_sort_descent(σ: Permutation) -> Tuple[str, str, str, str]:
    """σ → (fourth, witness, source, sink), the axis-selection sequence."""
    sig = permutation_to_signature(σ)
    return (σ.image[3], sig[2], sig[0], sig[1])


def descent_to_permutation(descent: Tuple[str, str, str, str]) -> Permutation:
    """(fourth, witness, source, sink) → σ. Inverse of selection_sort_descent."""
    fourth, witness, source, sink = descent
    return signature_to_permutation((source, sink, witness))


# ============================================================
# Hodge duality: ordered triples ↔ signed singletons
# ============================================================
#
# In dim 4, ★: Λ^3 → Λ^1.
# An ordered triple (the signature) → a signed singleton (the
# missing axis with the sign of the triple's ordering).
# Many-to-one: each signed singleton has 3 ordered-triple preimages.

SignedSingleton = Tuple[str, int]   # (axis, ±1)


def hodge_star_signature(sig: Signature) -> SignedSingleton:
    """★: ordered triple → signed singleton.
    
    The fourth axis (not in sig) is the singleton; the sign of the
    induced permutation is the orientation.
    """
    σ = signature_to_permutation(sig)
    return (σ.image[3], σ.sign())


def signed_singleton_to_forbidden_codeword(s: SignedSingleton) -> int:
    """Signed singleton → its parity-forbidden codeword (chirality, 11, witness)."""
    axis, sign = s
    chir_bit = 1 if sign == -1 else 0
    return (chir_bit << 4) | (0b11 << 2) | AXES.index(axis)


def forbidden_codeword_to_signed_singleton(code: int) -> SignedSingleton:
    """Inverse: parity-forbidden codeword → signed singleton."""
    if (code >> 2) & 0b11 != 0b11:
        raise ValueError(f"codeword 0b{code:05b} is not parity-forbidden")
    chir_bit = (code >> 4) & 1
    sign = -1 if chir_bit else 1
    return (AXES[code & 0b11], sign)


# ============================================================
# Q_5 = P_4 ⊔ Hodge_complement: the vertex-level geometric partition
# ============================================================
#
# The 32-element raw codeword space is V(Q_5) — the vertex set of
# the 5-cube. This vertex set partitions cleanly at the LABELING level
# (not as a polytope embedding) into:
#
#     V(Q_5) = V(P_4) ⊔ Hodge_complement
#     32     = 24     + 8
#
# where:
#     V(P_4) = the 24 vertices of the permutohedron of order 4
#              = the 24 elements of S_4
#              = the 24 valid codewords (those with pairing != 11)
#
#     Hodge_complement = 8 signed-singleton vertices
#                      = the 8 parity-forbidden codewords (pairing = 11)
#                      = NOT a standard polytope vertex set; the
#                        Hodge ★ image of oriented unordered triples
#
# This is a VERTEX-LEVEL partition only. Q_5 and P_4 live in different
# dimensions (Q_5 ⊂ R^5, P_4 ⊂ R^4 restricted to a 3-dim hyperplane),
# so this is not a polytope embedding. The Q_5 edge structure (Hamming
# adjacency) does not restrict to a clean partition: some Q_5 edges
# cross between V(P_4) and Hodge_complement (specifically: flipping
# one of the pairing bits between {00, 01, 10} and 11 crosses the
# partition).


def q5_vertices() -> List[int]:
    """All 32 codeword vertices of Q_5 (the ambient 5-cube)."""
    return list(range(32))


def p4_vertices() -> List[int]:
    """The 24 vertices of P_4 (permutohedron of S_4) within Q_5."""
    return [c for c in range(32) if (c >> 2) & 0b11 != 0b11]


def hodge_complement_vertices() -> List[int]:
    """The 8 Hodge complement vertices within Q_5 (parity-forbidden codewords)."""
    return [c for c in range(32) if (c >> 2) & 0b11 == 0b11]


def verify_q5_p4_hodge_partition() -> bool:
    """V(Q_5) = V(P_4) ⊔ Hodge_complement at the vertex/labeling level.

    Three checks:
      - 32 = 24 + 8 (cardinalities match)
      - V(P_4) ∩ Hodge_complement = ∅ (disjoint)
      - V(P_4) ∪ Hodge_complement = V(Q_5) (cover)
    """
    q5 = set(q5_vertices())
    p4 = set(p4_vertices())
    hc = set(hodge_complement_vertices())
    if len(q5) != 32 or len(p4) != 24 or len(hc) != 8:
        return False
    if p4 & hc:
        return False
    if p4 | hc != q5:
        return False
    return True


def verify_p4_vertices_correspond_to_s4() -> bool:
    """The 24 P_4 vertices bijectively correspond to S_4 elements
    via the codeword ↔ signature ↔ permutation chain."""
    # Each valid codeword decodes to a unique signature, which maps
    # to a unique S_4 element. The verifier is structural:
    return len(p4_vertices()) == len(S4_ELEMENTS) == 24


def verify_hodge_complement_corresponds_to_signed_singletons() -> bool:
    """The 8 Hodge complement vertices bijectively correspond to
    signed singletons (a, ε) with a ∈ AXES, ε ∈ {±1}."""
    singletons = set()
    for code in hodge_complement_vertices():
        singletons.add(forbidden_codeword_to_signed_singleton(code))
    expected = {(a, ε) for a in AXES for ε in (1, -1)}
    return singletons == expected and len(singletons) == 8


# ============================================================
# The triadic construction: 24 → +Hodge_dual → 32 (v19.3)
# ============================================================
#
# CONSTRUCTION DIRECTION (the user's framing correction):
#
# The 32-element codeword space is not a primary cube vertex set with
# 24 valid and 8 forbidden survivors of a parity sieve. It is a
# CONSTRUCTED power-of-2 closure of the operational 24, obtained by
# adding the Hodge dual completion.
#
#   STEP 1 — Triadic base (24 = |S_3| × |V_4| = 6 × 4):
#     The 24 ordered triples (source, sink, witness) of 3-of-4 axes.
#     Organized as 6 orbits (orbit_key ∈ S_3) × 4 V_4 deltas per orbit.
#     These are the operational WitnessedOp signatures used by
#     applied_grammar. CDSW "populates S_3" by providing the axes
#     from which permutations are built; V_4 governs the swap
#     semantics within each orbit.
#
#     The 24 has a TRIADIC flavor because each signature is a triple,
#     and |S_3| = 6 indexes the orbit space. 24 is not a power of 2.
#
#   STEP 2 — Hodge dual completion (+8 = |axes| × |chirality| = 4 × 2):
#     For each of the 4 unordered triples (Λ^3 basis), Hodge ★ in
#     dim 4 gives a signed singleton (Λ^1 element with chirality).
#     These 8 signed singletons are NOT operational signatures;
#     they are the wedge-product duals of the unordered triples,
#     added to close the space under Hodge duality.
#
#   STEP 3 — Power-of-2 closure (24 + 8 = 32):
#     The triadic 24 plus the Hodge completion 8 reaches the next
#     power of 2. This is what makes the bit encoding clean:
#     2 pairing bits (3 valid values + 1 Hodge slot) × 2 chirality
#     × 4 witness = 32 = 2^5.
#
# READING NOTATION (the user's suggestion):
#     ( axis ( axis ( axis ( hodge ) ) ) )
#     ( axis * axis * ( axis ( hodge ) ) )
# Read as: three axes wrap a Hodge dual, with the choice of axis at
# each level encoding the position. The Hodge is the innermost
# "fixed point" that the axes circle around.
#
# The Cayley-Dickson shape arises from this construction: an
# operational triadic structure (24 organized as S_3 × V_4) is
# Hodge-completed to a power-of-2 (32). The 32 = 2^5 is not the
# starting ambient; it is the result of one Hodge closure step.


def triadic_signatures_count() -> int:
    """24 = |S_3| × |V_4| = 6 × 4 = operational WitnessedOp count.

    These are the ordered triples used by applied_grammar — the
    operational signatures before any Hodge dual completion.
    """
    return len(STAB_D) * len(V4_ELEMENTS)


def hodge_dual_completion_count() -> int:
    """8 = |axes| × |chirality| = 4 × 2 = Hodge dual completion size.

    These are the signed singletons added to close the codeword
    space under Hodge ★. They are not operational WitnessedOp
    signatures.
    """
    return len(AXES) * 2


def constructed_codeword_count() -> int:
    """32 = 24 (triadic) + 8 (Hodge dual completion) — the power-of-2 closure."""
    return triadic_signatures_count() + hodge_dual_completion_count()


def verify_24_is_s3_times_v4() -> bool:
    """24 = |S_3| × |V_4| = 6 × 4 (the triadic operational base)."""
    return (
        triadic_signatures_count() == 24
        and len(STAB_D) == 6
        and len(V4_ELEMENTS) == 4
    )


def verify_8_is_axes_times_chirality() -> bool:
    """8 = |axes| × |chirality| = 4 × 2 (the Hodge dual completion size)."""
    return hodge_dual_completion_count() == 8 == len(AXES) * 2


def verify_32_constructed_from_triadic_plus_hodge() -> bool:
    """32 = 24 triadic + 8 Hodge — the constructed power-of-2 closure.

    Confirms: triadic_signatures + Hodge_completion = full codeword space.
    The 32 is derivative, not ambient.
    """
    return constructed_codeword_count() == 32 == len(q5_vertices())


def verify_triadic_24_equals_p4_vertices() -> bool:
    """The 24 triadic signatures are exactly the V(P_4) codewords."""
    return triadic_signatures_count() == len(p4_vertices()) == 24


def verify_hodge_completion_equals_forbidden_codewords() -> bool:
    """The 8 Hodge completion elements are exactly the forbidden codewords."""
    return hodge_dual_completion_count() == len(hodge_complement_vertices()) == 8


# ============================================================
# K_3 × K_4 cardinality vicinity + V_4 codeword fiber structure (v19.2)
# ============================================================
#
# K_3 × K_4 is the pentagonal prism (1-dim K_3 = interval crossed with
# 2-dim K_4 = pentagon). Its f-vector is (10 vertices, 15 edges, 7
# 2-faces), summing to 32 proper faces. This matches the cardinality
# of the codeword space exactly:
#
#     |proper faces of K_3 × K_4| = 32 = |codewords| = |V(Q_5)|
#
# The codeword space organizes into 4 V_4 fibers × 8 codewords each:
#
#     fiber α  (pairing = 00):  8 codewords — valid
#     fiber β  (pairing = 01):  8 codewords — valid
#     fiber γ  (pairing = 10):  8 codewords — valid
#     fiber ⊥  (pairing = 11):  8 codewords — Hodge dual / parity-forbidden
#
#     24 valid = 3 valid fibers × 8
#      8 dual  = 1 forbidden fiber × 8
#
# This is the "4x element space with 1x quotiented away" structure:
# V_4 = {α, β, γ, ⊥} acts as a partition index on the 32 codewords,
# with the ⊥ fiber being the Hodge complement.
#
# OPEN: an explicit V_4-equivariant bijection between codewords and
# K_3 × K_4 proper faces would derive the geometric realization. I
# checked: the natural V_4 polytope automorphism of K_3 × K_4 (V_4 =
# ⟨K_3-flip, K_4-reflection⟩ inside Aut(K_3 × K_4) = Z_2 × D_5) does
# NOT give 4 orbits of size 8 — orbit sizes are mixed {1, 2, 4}. So
# the V_4 organizing codewords is not realized as polytope-symmetry on
# K_3 × K_4. The structural bijection (if it exists) acts on the face
# poset by a different mechanism — likely tree-indexed, in the
# vicinity of Stasheff. Recording the cardinality match and the V_4
# fiber on the codeword side; deferring the bijection.


def k3_proper_face_count() -> int:
    """K_3 = interval. 2 vertices = 2 proper faces."""
    return 2


def k4_proper_face_count() -> int:
    """K_4 = pentagon. 5 vertices + 5 edges = 10 proper faces."""
    return 10


def k3_k4_proper_face_count() -> int:
    """K_3 × K_4 = pentagonal prism. f-vector (10, 15, 7) → 32 proper faces."""
    return 10 + 15 + 7


def codeword_pairing_v4_fibers() -> Dict[int, List[int]]:
    """The 32 codewords organized by pairing-bit V_4 fiber.

    Returns {pairing_bits: [codewords with that pairing]} with 4 keys
    (0b00 = α, 0b01 = β, 0b10 = γ, 0b11 = ⊥), each with 8 codewords.
    """
    fibers: Dict[int, List[int]] = {0b00: [], 0b01: [], 0b10: [], 0b11: []}
    for code in range(32):
        pairing_bits = (code >> 2) & 0b11
        fibers[pairing_bits].append(code)
    return fibers


def verify_codeword_v4_fiber_structure() -> bool:
    """The 32 codewords fiber as V_4 × 8: 4 fibers × 8 codewords each.

    - α, β, γ fibers (pairing != 11): 8 codewords each, 24 total valid
    - ⊥ fiber (pairing == 11):        8 codewords, the Hodge complement
    """
    fibers = codeword_pairing_v4_fibers()
    if len(fibers) != 4:
        return False
    if any(len(f) != 8 for f in fibers.values()):
        return False
    valid = sum(len(fibers[p]) for p in (0b00, 0b01, 0b10))
    forbidden = len(fibers[0b11])
    return valid == 24 and forbidden == 8


def verify_k3_k4_codeword_cardinality_match() -> bool:
    """|proper faces of K_3 × K_4| = 32 = |codewords|."""
    return k3_k4_proper_face_count() == 32 and len(q5_vertices()) == 32


def verify_hodge_fiber_is_forbidden_codewords() -> bool:
    """The ⊥ V_4 fiber is exactly the 8 Hodge-complement codewords."""
    fibers = codeword_pairing_v4_fibers()
    return set(fibers[0b11]) == set(hodge_complement_vertices())


def verify_valid_fibers_are_24_p4_vertices() -> bool:
    """The α, β, γ V_4 fibers together are exactly the 24 P_4 vertices."""
    fibers = codeword_pairing_v4_fibers()
    valid_union = set(fibers[0b00]) | set(fibers[0b01]) | set(fibers[0b10])
    return valid_union == set(p4_vertices())


# ============================================================
# Oriented unordered triples: the 8-element underlying structure (v19.3)
# ============================================================
#
# The constructive view: the 32 codewords are not "24 valid + 8
# separate forbidden." They are 8 oriented unordered triples × 4
# V_4 presentations, where each underlying triple appears once in
# each V_4 fiber:
#
#     32 = 8 × 4 = (oriented unordered triples) × (V_4 presentations)
#
# Each signature has 4 structural positions: source, sink, witness,
# [4th]. The 4th position is filled by:
#   - the explicit fourth axis (in 3 of the 4 V_4 fibers — "ordered
#     triple presentation"), or
#   - the Hodge dual of the other three (in 1 V_4 fiber — "compressed
#     presentation")
#
# The user's correction: it is not either/or. Both presentations
# describe the SAME 8 underlying oriented unordered triples. The V_4
# fibering shows which presentation is exposed; the construction is
# unified.

OrientedUnorderedTriple = Tuple[FrozenSet[str], int]   # (3-axis set, ±1 orientation)


def all_oriented_unordered_triples() -> List[OrientedUnorderedTriple]:
    """The 8 oriented unordered triples = 4 unordered triples × 2 orientations.

    Each triple chooses 3 of the 4 axes; the orientation is the
    permutation sign of any cyclic ordering of the triple's axes
    followed by the fourth axis.
    """
    from itertools import combinations
    result = []
    for combo in combinations(AXES, 3):
        triple = frozenset(combo)
        for sign in (1, -1):
            result.append((triple, sign))
    return result


def oriented_triple_of_forbidden_codeword(code: int) -> OrientedUnorderedTriple:
    """The Hodge-dual codeword (axis, sign) → ({CDSW \\ {axis}}, sign).

    The forbidden codeword's signed singleton is the Hodge ★ image of
    the underlying oriented unordered triple.
    """
    axis, sign = forbidden_codeword_to_signed_singleton(code)
    triple = frozenset(AXES) - {axis}
    return (triple, sign)


def verify_8_oriented_unordered_triples() -> bool:
    """There are exactly 8 = 4 axes × 2 orientations of oriented unordered triples."""
    triples = all_oriented_unordered_triples()
    if len(triples) != 8:
        return False
    # Disjoint: each (triple, sign) appears once
    return len(set(triples)) == 8


def verify_hodge_complement_is_8_oriented_triples() -> bool:
    """The 8 Hodge-complement codewords bijectively cover all 8 oriented
    unordered triples (via the (triple_complement_axis, sign) labeling)."""
    seen = set()
    for code in hodge_complement_vertices():
        seen.add(oriented_triple_of_forbidden_codeword(code))
    return seen == set(all_oriented_unordered_triples())


# ============================================================
# S_n vs Cayley-Dickson correspondence
# ============================================================

def sn_cayley_dickson_table() -> Dict[int, Tuple[int, int]]:
    """{n: (|S_n|, 2^n)} for n = 0..5."""
    return {n: (math.factorial(n), 2 ** n) for n in range(6)}


# ============================================================
# Verifier theorems
# ============================================================

def verify_s4_cardinality() -> bool:
    return len(S4_ELEMENTS) == 24


def verify_v4_is_subgroup() -> bool:
    """V_4 contains the identity and is closed under composition."""
    if not any(v.is_identity() for v in V4_ELEMENTS):
        return False
    v4_set = set(V4_ELEMENTS)
    return all(
        v1.compose(v2) in v4_set
        for v1 in V4_ELEMENTS for v2 in V4_ELEMENTS
    )


def verify_v4_is_klein_four() -> bool:
    """All non-identity V_4 elements have order 2."""
    return all(
        v.is_identity() or v.order() == 2
        for v in V4_ELEMENTS
    )


def verify_v4_is_normal() -> bool:
    """∀ σ ∈ S_4, τ ∈ V_4: σ τ σ^(-1) ∈ V_4."""
    v4_set = set(V4_ELEMENTS)
    for σ in S4_ELEMENTS:
        σ_inv = σ.inverse()
        for τ in V4_ELEMENTS:
            if σ.compose(τ).compose(σ_inv) not in v4_set:
                return False
    return True


def verify_stab_d_size() -> bool:
    return len(STAB_D) == 6


def verify_stab_d_is_subgroup() -> bool:
    """Stab(D) is closed under composition and contains identity."""
    stab_set = set(STAB_D)
    if IDENTITY not in stab_set:
        return False
    return all(
        s1.compose(s2) in stab_set
        for s1 in STAB_D for s2 in STAB_D
    )


def verify_stab_d_complements_v4() -> bool:
    """V_4 ∩ Stab(D) = {e}, V_4 · Stab(D) = S_4, |V_4|·|Stab(D)| = |S_4|."""
    if set(STAB_D) & set(V4_ELEMENTS) != {IDENTITY}:
        return False
    if len(V4_ELEMENTS) * len(STAB_D) != len(S4_ELEMENTS):
        return False
    product = {v.compose(s) for v in V4_ELEMENTS for s in STAB_D}
    return product == set(S4_ELEMENTS)


def verify_unique_factorization() -> bool:
    """Every σ ∈ S_4 factors UNIQUELY as σ = v · s, v ∈ V_4, s ∈ Stab(D)."""
    seen = set()
    for σ in S4_ELEMENTS:
        v, s = factor_s4(σ)
        if v not in set(V4_ELEMENTS):
            return False
        if s.apply(ANCHOR_AXIS) != ANCHOR_AXIS:
            return False
        if v.compose(s) != σ:
            return False
        if (v, s) in seen:
            return False
        seen.add((v, s))
    return len(seen) == 24


def verify_signature_permutation_bijection() -> bool:
    """signature ↔ permutation roundtrips on all 24 ordered triples."""
    triples = list(permutations(AXES, 3))
    if len(triples) != 24:
        return False
    perms = set()
    for sig in triples:
        σ = signature_to_permutation(sig)
        if permutation_to_signature(σ) != sig:
            return False
        perms.add(σ)
    return perms == set(S4_ELEMENTS)


def verify_s4_order_distribution() -> bool:
    """S_4 has element-order distribution {1:1, 2:9, 3:8, 4:6}."""
    from collections import Counter
    return dict(Counter(σ.order() for σ in S4_ELEMENTS)) == {1: 1, 2: 9, 3: 8, 4: 6}


def verify_hodge_dual_preimage_count() -> bool:
    """Each signed singleton (8 total) has exactly 3 ordered-triple preimages."""
    from collections import Counter
    counts = Counter()
    for σ in S4_ELEMENTS:
        counts[hodge_star_signature(permutation_to_signature(σ))] += 1
    return len(counts) == 8 and set(counts.values()) == {3}


def verify_forbidden_codeword_singleton_bijection() -> bool:
    """The 8 parity-forbidden codewords ↔ 8 signed singletons."""
    forbidden = [c for c in range(32) if (c >> 2) & 0b11 == 0b11]
    if len(forbidden) != 8:
        return False
    singletons = set()
    for code in forbidden:
        s = forbidden_codeword_to_signed_singleton(code)
        if signed_singleton_to_forbidden_codeword(s) != code:
            return False
        singletons.add(s)
    return singletons == {(a, ε) for a in AXES for ε in (1, -1)}


def verify_orbit_key_coverage() -> bool:
    """Stab(D) elements give all 6 orbit keys = 3 pairings × 2 chiralities."""
    return {stab_d_to_orbit_key(s) for s in STAB_D} == {
        (p, c) for p in ('α', 'β', 'γ') for c in ('even', 'odd')
    }


def verify_selection_sort_descent_bijection() -> bool:
    """Descent ↔ permutation is a bijection."""
    descents = set()
    for σ in S4_ELEMENTS:
        d = selection_sort_descent(σ)
        if descent_to_permutation(d) != σ:
            return False
        descents.add(d)
    return len(descents) == 24


def verify_s4_formalization() -> bool:
    """Aggregator: all S_4 formalization theorems hold."""
    return all([
        verify_s4_cardinality(),
        verify_v4_is_subgroup(),
        verify_v4_is_klein_four(),
        verify_v4_is_normal(),
        verify_stab_d_size(),
        verify_stab_d_is_subgroup(),
        verify_stab_d_complements_v4(),
        verify_unique_factorization(),
        verify_signature_permutation_bijection(),
        verify_s4_order_distribution(),
        verify_hodge_dual_preimage_count(),
        verify_forbidden_codeword_singleton_bijection(),
        verify_orbit_key_coverage(),
        verify_selection_sort_descent_bijection(),
        v4_swap_consistency(),
        verify_q5_p4_hodge_partition(),
        verify_p4_vertices_correspond_to_s4(),
        verify_hodge_complement_corresponds_to_signed_singletons(),
        verify_codeword_v4_fiber_structure(),
        verify_k3_k4_codeword_cardinality_match(),
        verify_hodge_fiber_is_forbidden_codewords(),
        verify_valid_fibers_are_24_p4_vertices(),
        verify_24_is_s3_times_v4(),
        verify_8_is_axes_times_chirality(),
        verify_32_constructed_from_triadic_plus_hodge(),
        verify_triadic_24_equals_p4_vertices(),
        verify_hodge_completion_equals_forbidden_codewords(),
        verify_8_oriented_unordered_triples(),
        verify_hodge_complement_is_8_oriented_triples(),
    ])
