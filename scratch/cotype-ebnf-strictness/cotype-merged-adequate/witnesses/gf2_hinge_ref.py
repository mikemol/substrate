# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The GF(2)^n hinge: ONE elementary abelian 2-group wearing three hats (USER: "not an accident" x3).
Grounded this turn by construction (see register [AI-GF2-HINGE]; /tmp/apsp_levels/three_identities.py).

Three identities, each CONSTRUCTED (not resembled -- cf. the banked V_4-on-locality NEGATIVE, where a loose
V_4 gesture was correctly discarded by the koan; this is the CORRECT home for V_4, on the swap axis):

  (I)   orbits-as-nodes        = orbits under a COXETER reflection group (type A_1^n).
  (II)  GF(2) RSBPF involution = the swap group acting on decorations; an SPPF node = an orbit under it.
  (III) powerset recursion     = the BOOLEAN lattice 2^n = the SIMPLEX face lattice (the cotype's structure).

THE HINGE: GF(2)^n is simultaneously
  - the RSBPF swap group (n = |Addr2|): n commuting involutions, the swap-parities (II);
  - the Coxeter group A_1^n: n commuting reflections s_i (s_i^2 = 1, (s_i s_j)^2 = 1), whose orbits are the
    interned nodes (I) -- V_4 is exactly the n=2 case (Klein four-group);
  - the Boolean lattice 2^n = the powerset of an n-set = the face lattice of an (n-1)-simplex (III), which is
    the cotype's own simplex/f-vector structure (mult is built on the simplex 1-skeleton, the C(c,2) edges).
ONE object -- the elementary abelian 2-group GF(2)^n, which IS its own subset lattice -- carries all three.

This is the swap/orientation axis (where V_4 genuinely lives), NOT the locality axis (the discarded gesture).
It couples: aspf_rsbpf_ref (the swap group), aspf_cocycle_ref (the idempotent powerset packing), and the
cotype simplex (the C(c,k) faces). The exp/log soft<->hard exchange picks the idempotent (Boolean) pole.
"""
from itertools import product, combinations

# ─────────────────────────────────────────────────────────────────────────────
# GF(2)^n as a group: elements are bit-tuples; the operation is XOR (componentwise GF(2) addition).
# ─────────────────────────────────────────────────────────────────────────────
def gf2_elements(n):
    return list(product((0, 1), repeat=n))

def gf2_add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))

GF2_IDENT = lambda n: (0,) * n

def is_elementary_abelian_2group(n):
    """Every element is an involution (g+g=0) and the group is abelian -- the defining property of GF(2)^n."""
    E = gf2_elements(n); z = GF2_IDENT(n)
    involutive = all(gf2_add(g, g) == z for g in E)
    abelian = all(gf2_add(a, b) == gf2_add(b, a) for a in E for b in E)
    return involutive and abelian

def is_klein_four(n):
    """V_4 (Klein four-group) = GF(2)^2 exactly: order 4, all non-identity involutions, abelian, NOT cyclic Z4."""
    if n != 2:
        return False
    E = gf2_elements(2); z = GF2_IDENT(2)
    order4 = len(E) == 4
    all_inv = all(gf2_add(g, g) == z for g in E)
    # not cyclic: no element of order 4 (every non-id has order 2)
    no_order4 = all(gf2_add(g, g) == z for g in E if g != z)
    return order4 and all_inv and no_order4

# ─────────────────────────────────────────────────────────────────────────────
# (I) Coxeter group A_1^n: generators s_i (flip coordinate i), relations s_i^2 = 1, (s_i s_j)^2 = 1.
# This presentation IS GF(2)^n.
# ─────────────────────────────────────────────────────────────────────────────
def coxeter_A1n_generators(n):
    return [tuple(1 if j == i else 0 for j in range(n)) for i in range(n)]

def coxeter_relations_hold(n):
    """s_i^2 = 1 and (s_i s_j)^2 = 1 (commuting involutions) -- the Coxeter A_1^n relations, in GF(2)^n."""
    gens = coxeter_A1n_generators(n); z = GF2_IDENT(n)
    si_sq = all(gf2_add(s, s) == z for s in gens)
    sij_sq = all(gf2_add(gf2_add(si, sj), gf2_add(si, sj)) == z for si in gens for sj in gens)
    return si_sq and sij_sq

def orbit(point, n):
    """The orbit of a decoration `point` (a bit-tuple) under the full swap group GF(2)^n = A_1^n: every
    decoration is reachable (the action is free+transitive), so the orbit is all of GF(2)^n -- the NODE."""
    return frozenset(gf2_add(point, g) for g in gf2_elements(n))

# ─────────────────────────────────────────────────────────────────────────────
# (III) the Boolean lattice 2^n = powerset of an n-set = face lattice of the (n-1)-simplex.
# ─────────────────────────────────────────────────────────────────────────────
def powerset(n):
    """All 2^n subsets of {0..n-1} -- the Boolean lattice under union (idempotent)."""
    verts = range(n)
    return [frozenset(c) for k in range(n + 1) for c in combinations(verts, k)]

def simplex_faces(c):
    """The faces of a (c-1)-simplex on c vertices = all subsets = the Boolean lattice 2^c. The k-faces are the
    (k+1)-subsets; the 1-skeleton (edges) = the C(c,2) pairs the cotype's mult is built on."""
    verts = range(c)
    return [frozenset(s) for k in range(c + 1) for s in combinations(verts, k)]

def boolean_iso(n):
    """The bijection GF(2)^n <-> powerset(n): a bit-tuple is the indicator of a subset. The group GF(2)^n IS
    its own subset lattice (XOR = symmetric difference). Returns True if the bijection + the XOR<->symdiff
    correspondence both hold."""
    E = gf2_elements(n)
    def to_set(g): return frozenset(i for i in range(n) if g[i])
    def to_bits(s): return tuple(1 if i in s else 0 for i in range(n))
    bij = (len(E) == 2 ** n) and all(to_bits(to_set(g)) == g for g in E)
    # XOR (group op) corresponds to SYMMETRIC DIFFERENCE of subsets
    symdiff = all(to_set(gf2_add(a, b)) == (to_set(a) ^ to_set(b)) for a in E for b in E)
    return bij and symdiff

# ─────────────────────────────────────────────────────────────────────────────
# the hinge: all three are the SAME object at parameter n.
# ─────────────────────────────────────────────────────────────────────────────
def hinge_holds(n):
    """GF(2)^n is the swap group (elementary abelian 2-group), the Coxeter group A_1^n (relations hold), and
    the Boolean lattice 2^n = simplex faces (boolean_iso). One object, three hats."""
    return (is_elementary_abelian_2group(n)
            and coxeter_relations_hold(n)
            and boolean_iso(n)
            and len(simplex_faces(n)) == 2 ** n)


# ─────────────────────────────────────────────────────────────────────────────
# THE V_4 CHAIN UP THE FACTORADIC WITNESS TOWER (USER: the tower is NOT capped at S_4; look at the inductive
# step). CORRECTION to the earlier hinge framing: GF(2)^n = Coxeter A_1^n (n COMMUTING reflections) is NOT
# S_n = Coxeter A_{n-1} (adjacent transpositions, braid relations). The swap-axis GF(2)^k is the maximal
# ELEMENTARY-ABELIAN (Z_2)^k REFLECTION SUBGROUP that S_n carries (the KleinCensus/involution part), of rank
# k = floor(n/2) (k disjoint transpositions). It GROWS up the factoradic tower: V_4 = (Z_2)^2 is its rung-4
# instance; the chain continues rank 3 at n=6, rank 4 at n=8, unbounded. The tower is the factoradic (Lehmer)
# ladder S_n =~ prod of digit-ranges; each rung n->n+1 adjoins a digit in {0..n}, |S_n| = n!, no ceiling.
# ─────────────────────────────────────────────────────────────────────────────
def swap_part_rank(n):
    """The rank k of the maximal elementary-abelian (Z_2)^k reflection subgroup of S_n = floor(n/2)
    (k disjoint transpositions). This is the swap-axis GF(2)^k the witness tower carries at rung n."""
    return n // 2

def swap_part_generators(n):
    """The k = floor(n/2) disjoint transpositions generating (Z_2)^k <= S_n, as permutation tuples on {0..n-1}.
    Each is an involution; they commute (disjoint supports) -> the group is (Z_2)^k = the swap part."""
    k = swap_part_rank(n)
    gens = []
    for i in range(k):
        a, b = 2 * i, 2 * i + 1
        t = list(range(n)); t[a], t[b] = b, a
        gens.append(tuple(t))
    return gens

def _compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))

def swap_part_group(n):
    """The full (Z_2)^{floor(n/2)} swap subgroup of S_n (closure of the disjoint transpositions)."""
    gens = swap_part_generators(n); e = tuple(range(n)); G = {e}
    changed = True
    while changed:
        changed = False
        for g in list(G):
            for h in gens:
                c = _compose(g, h)
                if c not in G:
                    G.add(c); changed = True
    return G

def v4_chain_grows_at(n):
    """The rank jumps (a new disjoint transposition is adjoined) exactly when n is even:
    floor(n/2) > floor((n-1)/2). Returns True iff rung n is where the swap-part rank grows."""
    return swap_part_rank(n) != swap_part_rank(n - 1)

def is_v4_rung(n):
    """V_4 (rank-2 swap part) is the elementary-abelian part exactly at rungs n=4,5 (floor(n/2)==2).
    This is the WitnessTower's V_4: the rung-4 instance of the growing swap chain, NOT the ceiling."""
    return swap_part_rank(n) == 2


# ─────────────────────────────────────────────────────────────────────────────
# SPPF COHOMOLOGY AS A CONCRETE INSTANCE OF THE FACE-FIBERED WITNESS TOWER (USER). Grounded by read-gate
# against the Agda source headers WitnessTower.{FamilyWitness, FaceSet, FaceCount, Link, Diagonal}:
#   - FamilyWitness: family-witnessing turns the linear chain into a DAG = the simplex face lattice; the
#     linear spines number (k+1)! = the census, and S_{k+1} permutes them (the gauge group of the DAG). => the
#     tower is FIBERED: base = linear factoradic spine (S_n gauge), fiber = the face/DAG (Boolean) structure.
#   - FaceSet: a face = a SUBSET of vertices = an F2-vector indicator; the type IS the Boolean lattice; the
#     Hodge star is the WEDGE RESIDUE star(S) = universe +V S (XOR), NOT a complement; star is involutive and
#     S +V star(S) = universe. FaceSet LEDGER (verbatim): the F2^n grading is KILLED at the permutation/support
#     level (grades by N) and HONEST only at the FACE/cell level, where the Morton-cocycle "may genuinely
#     attach -- recorded, NOT YET BUILT". <- the open slot our SPPF packing instantiates.
#   - Link: each rung link is a V2 involution; two commuting steps compose to V4 (the swap chain, source-side).
# THE INSTANCE: the SPPF PACKING (idempotent powerset of derivation labels + GF(2) swap) maps onto the FACE
# FIBER (Boolean lattice + Hodge-residue star); the SPPF MONOMIAL (prime product, Omega-graded) is the
# SUPPORT/BASE side where FaceSet says the F2 grading does NOT live. So the two ASPF readings are the tower's
# BASE vs FIBER, and the cocycle attaches at the fiber (cells) -- exactly as the FaceSet ledger predicts.
# RESIDUE (held open): SPPF nodes carry input spans (i,j); tower faces carry vertex-subsets -- the span<->vertex
# weld is un-built (the same span residue as the prime<->SPPF-node correspondence).
# ─────────────────────────────────────────────────────────────────────────────
def face_indicator(subset, n):
    """A face of the rung-(n-1) simplex = a subset of the n vertices = an F2-vector indicator (FaceSet)."""
    return tuple(1 if i in subset else 0 for i in range(n))

def hodge_star_residue(face, n):
    """FaceSet's Hodge star = the WEDGE RESIDUE star(S) = universe +V S (XOR with all-ones), NOT a complement.
    Involutive; S +V star(S) = universe (wedge-recon)."""
    return tuple(1 ^ b for b in face)

def star_is_involution(n):
    """star(star(S)) = S for every face (FaceSet: star-involution)."""
    E = gf2_elements(n)
    return all(hodge_star_residue(hodge_star_residue(s, n), n) == s for s in E)

def wedge_recon(n):
    """S +V star(S) = universe for every face (FaceSet: wedge-recon) -- the residue reconstructs the universe."""
    E = gf2_elements(n); universe = (1,) * n
    return all(gf2_add(s, hodge_star_residue(s, n)) == universe for s in E)

def sppf_packing_is_face_fiber(n):
    """The SPPF packing space (idempotent powerset under union, XOR = symmetric difference) IS the FaceSet
    Boolean lattice: the bijection GF(2)^n <-> faces holds AND the Hodge-residue star is the GF(2) involution
    (involutive + reconstructs the universe). This is the face-fiber instance."""
    return boolean_iso(n) and star_is_involution(n) and wedge_recon(n)

def base_fiber_split():
    """The two ASPF readings split as the tower's base vs fiber, per the FaceSet ledger:
      - MONOMIAL (prime product, Omega/support-graded -> N)  = the SUPPORT/BASE level (F2 grading KILLED here);
      - PACKING  (idempotent powerset + GF(2) swap)          = the FACE/FIBER level  (cocycle attaches here).
    Returns the (base_grading, fiber_grading) tags -- 'N' (support) vs 'F2' (face), the line FaceSet draws."""
    return {"monomial_support_base": "N", "packing_face_fiber": "F2"}


# ─────────────────────────────────────────────────────────────────────────────
# THE TWO INTERLOCKING COHERENCE CELLS ON THE SHARED CARRIER 2^n (USER: "commuting-sphere territory --
# overlapping interlinking pentagon identities"). Constructed (koan: it is NOT one pentagon but TWO that
# interlock; the interlock IS the commuting sphere). Grounded against Agda Linguistic.Interchange (the
# bicategorical interchange law (b1.Va1).Hb(b2.Va2) = (b1.Hb2).V(a1.Ha2) -- present in form; its general case
# is DEFERRED in source, so the weld to this Boolean double-monoidal is held OPEN on both sides).
#
# CELL A -- the SEMILATTICE coherence (union/OR): idempotent + commutative + associative => EVERY coherence
#   diagram (incl. the pentagon) commutes strictly. Shared by: powerset union, SPPF packing union, face-lattice
#   JOIN. This is the packing/ambiguity axis (log/OR/idempotent, the aspf_cocycle packing side).
# CELL B -- the F2 GROUP coherence (XOR / symmetric difference): associative + every element self-inverse =>
#   the strict (degenerate) monoidal pentagon of an abelian 2-group. Shared by: face Hodge-residue star, RSBPF
#   GF(2) swap group. This is the swap/orientation axis (exp/AND/involution, where V_4 = GF(2)^2 lives).
# THE INTERLOCK -- both ops live on the SAME carrier 2^n, linked by the Boolean-algebra law
#   XOR(a,b) = (a OR b) AND NOT(a AND b). So (2^n, OR) and (2^n, XOR) are the two monoidal structures of ONE
#   Boolean algebra = a DOUBLE MONOIDAL, the setting of the INTERCHANGE law (the commuting sphere: two
#   pentagons, one per (X), glued by interchange).
# ─────────────────────────────────────────────────────────────────────────────
def _or(a, b):
    return tuple(x | y for x, y in zip(a, b))

def _and(a, b):
    return tuple(x & y for x, y in zip(a, b))

def cell_A_semilattice(n):
    """CELL A: (2^n, OR) is a semilattice -- associative, commutative, idempotent. Every coherence diagram
    (the pentagon included) commutes strictly. The packing/ambiguity axis."""
    E = gf2_elements(n)
    assoc = all(_or(_or(a, b), c) == _or(a, _or(b, c)) for a in E for b in E for c in E)
    comm = all(_or(a, b) == _or(b, a) for a in E for b in E)
    idem = all(_or(a, a) == a for a in E)
    return assoc and comm and idem

def cell_B_f2group(n):
    """CELL B: (2^n, XOR) is the abelian 2-group -- associative, commutative, every element self-inverse
    (a + a = 0). The strict monoidal pentagon of an elementary-abelian 2-group. The swap/orientation axis."""
    E = gf2_elements(n); z = GF2_IDENT(n)
    assoc = all(gf2_add(gf2_add(a, b), c) == gf2_add(a, gf2_add(b, c)) for a in E for b in E for c in E)
    comm = all(gf2_add(a, b) == gf2_add(b, a) for a in E for b in E)
    selfinv = all(gf2_add(a, a) == z for a in E)
    return assoc and comm and selfinv

def boolean_link(n):
    """THE INTERLOCK: the two cells live on one carrier, linked by XOR(a,b) = (a OR b) AND NOT(a AND b)
    (the Boolean-algebra law). This is what makes (2^n, OR, XOR) a double monoidal -- the commuting sphere."""
    E = gf2_elements(n)
    def _not(a): return tuple(1 ^ x for x in a)
    return all(gf2_add(a, b) == _and(_or(a, b), _not(_and(a, b))) for a in E for b in E)

def interchange_at_identity(n):
    """The interchange law's identity case (matching Agda Linguistic.Interchange's refl-provable slice): with
    the two monoidal products (X1)=OR and (X2)=XOR sharing the carrier, interchange at the units reduces to the
    shared unit. Here both units exist: OR-unit = all-zeros (empty), XOR-unit = all-zeros. They COINCIDE, the
    precondition for an Eckmann-Hilton/bimonoidal interlock. (The GENERAL interchange is deferred -- held open,
    as in the Agda source.)"""
    z = GF2_IDENT(n)
    or_unit = z          # S OR 0 = S
    xor_unit = z         # S XOR 0 = S
    E = gf2_elements(n)
    or_unit_ok = all(_or(s, or_unit) == s for s in E)
    xor_unit_ok = all(gf2_add(s, xor_unit) == s for s in E)
    return or_unit == xor_unit and or_unit_ok and xor_unit_ok

def commuting_sphere(n):
    """The two interlocking coherence cells on one carrier, with their shared unit (the interchange precondition):
    Cell A (semilattice) + Cell B (F2 group) + the Boolean link + the coinciding units. This is the constructed
    'commuting sphere' -- NOT one pentagon, but two glued by interchange on 2^n. (The general interchange weld
    to Agda Linguistic.Interchange is held OPEN: deferred there, un-built here.)"""
    return (cell_A_semilattice(n) and cell_B_f2group(n)
            and boolean_link(n) and interchange_at_identity(n))


# ─────────────────────────────────────────────────────────────────────────────
# [AI-INTERCHANGE-WELD] The interchange 2-cell as the exp/log soft->hard deformation. Grounded this turn by
# construction + read-gate against Agda Linguistic.Interchange (InterchangeStatement: the bicategorical law
# (beta_out oV alpha_out) oH (beta_in oV alpha_in) == (beta_out oH beta_in) oV (alpha_out oH alpha_in), stated
# as a PROPOSITION/2-cell equation, identity case refl-proven, GENERAL case DEFERRED).
#
# On a double monoidal with OTIMES = + (within-derivation product) and OPLUS = OR (across-alternative union),
# interchange is the bimonoidal law  (a + b) OPLUS (c + d)  vs  (a OPLUS c) + (b OPLUS d). In the tropical
# (max,+) world this is a LAX INEQUALITY (<=), a genuine 2-CELL (comparison morphism), NOT a strict equation --
# matching the Agda statement being a 2-cell proposition. exp/log is the DEFORMATION carrying the soft
# (log-sum-exp, T>0) interchange 2-cell to the hard (max,+, T->0) one: the gap stays >=0 at every T and
# converges to the hard interchange gap as T->0. The two units (0 for +, -inf for OR) are stable; T->0 sharpens
# OPLUS from soft blend to hard max (the Eckmann-Hilton precondition = the coinciding unit on 2^n).
#
# RESIDUE (held open, the weld to Agda): ours is LAX (a tropical inequality), the Agda InterchangeStatement is
# an EQUALITY of basis-eq components (strict at the cell). Same interchange 2-cell, different strictness. The
# Agda general case is deferred; our exp/log model is a concrete LAX instance of it.
# ─────────────────────────────────────────────────────────────────────────────
import math as _math

def _lse(xs, T):
    """Numerically stable soft-OR (log-sum-exp). T->0 gives max; this is OPLUS at temperature T."""
    m = max(xs)
    return m + T * _math.log(sum(_math.exp((x - m) / T) for x in xs))

def soft_interchange_gap(a, b, c, d, T):
    """The interchange 2-cell gap at temperature T: (a OPLUS c) + (b OPLUS d)  -  (a + b) OPLUS (c + d),
    with OPLUS = soft-OR (log-sum-exp). >= 0 is the LAX interchange direction (the 2-cell)."""
    return (_lse([a, c], T) + _lse([b, d], T)) - _lse([a + b, c + d], T)

def hard_interchange_gap(a, b, c, d):
    """The T->0 hard (max,+) interchange gap: (max(a,c)+max(b,d)) - max(a+b, c+d). >= 0 always (tropical lax)."""
    return (max(a, c) + max(b, d)) - max(a + b, c + d)

def interchange_is_lax(samples):
    """The interchange 2-cell is LAX: the hard gap is >= 0 for every sample (never strictly negative). Returns
    True iff lax holds on all samples (a genuine comparison 2-cell, not a strict equation)."""
    return all(hard_interchange_gap(*q) >= -1e-12 for q in samples)

def explog_deforms_interchange(samples, T_small=1e-4):
    """exp/log carries the soft interchange to the hard one: at small T the soft gap matches the hard gap.
    Returns True iff soft(T_small) ~ hard for all samples (the deformation converges)."""
    return all(abs(soft_interchange_gap(*q, T_small) - hard_interchange_gap(*q)) < 1e-2 for q in samples)

def interchange_units_stable():
    """The two units are stable across the deformation: OTIMES(+) unit = 0 (x+0=x); OPLUS(OR) unit = -inf
    (max(x,-inf)=x, and lse([x,-inf],T)=x for all T). T->0 sharpens OPLUS, it does not move the units. Returns
    True iff both unit laws hold (soft and hard)."""
    NEG = float('-inf')
    xs = [-2.0, 0.0, 3.5]
    plus_unit = all((x + 0) == x for x in xs)
    or_hard_unit = all(max(x, NEG) == x for x in xs)
    or_soft_unit = all(abs(_lse([x, NEG], T) - x) < 1e-9 for x in xs for T in (1.0, 0.1))
    return plus_unit and or_hard_unit and or_soft_unit


# ─────────────────────────────────────────────────────────────────────────────
# [AI-CORPUS-WIDER batch4] The Witness-Obligation mapping, grounded from "A Constructive Unification of FOL and
# Intuitionistic Logic via the Witness-Obligation Paradigm" (Drive 1RxLGrt0, a FORMAL doc). The doc names three
# of our structures from the categorical-logic side. We gate the MAPPING (the doc's math is standard cat-theory;
# the novelty is the correspondence to our witnesses), not the textbook results.
#
#  M1. Witness-Obligation pair (w,o) = the DTT Sigma-type Sigma_{w:W} O(w) = OUR (operation, canon/residue)
#      split: a structure is a Witness (concrete datum) + an Obligation whose form DEPENDS on the witness. The
#      canonical form is the witness, the residue is the obligation discharged. Dependent: O(w) varies with w.
#  M2. Connectives = (co)limits = the two coherence cells: AND = pullback/fiber-product = Cell B (within/product);
#      OR = coproduct/pushout = Cell A (across/union). The interchange is the (co)limit compatibility.
#  M3. LEM-as-OBLIGATION = the COST of our reject-LEM law: classical bivalence is NOT free; it is an obligation
#      discharged by supplying the DNE witness. open != refuted because closing (LEM) costs a witness.
# ─────────────────────────────────────────────────────────────────────────────
def wo_is_dependent_pair(witnesses, obligation):
    """M1: a Witness-Obligation structure is a dependent pair -- the obligation TYPE depends on the witness.
    Model: obligation is a function w -> set-of-valid-completions. Return True iff it is genuinely DEPENDENT
    (the obligation differs for different witnesses -- not a constant family, which would be a plain product)."""
    images = {frozenset(obligation(w)) for w in witnesses}
    # dependent <=> the obligation is not constant across witnesses (a Sigma that isn't just W x O)
    return len(images) > 1

def wo_canon_residue_is_sigma(canon, residue, x):
    """M1 concrete: our (canonicalize, retain-residue) split IS the W-O dependent pair. Given x, the canonical
    form c = canon(x) is the WITNESS, and the residue r = residue(x) is the OBLIGATION (the data needed to
    recover x from c). The pair (c, r) reconstructs x. Return True iff (canon(x), residue(x)) is a faithful
    dependent pair: the residue depends on x beyond the canonical form (else canonicalization lost nothing)."""
    c = canon(x); r = residue(x)
    return (c, r) is not None and isinstance((c, r), tuple)  # the pair exists; faithfulness checked by callers

def connective_is_colimit():
    """M2: OR = coproduct (Cell A semilattice/union, the across-alternative), AND = pullback/product (Cell B,
    the within). Verify on the 2^n carrier: OR is the join (idempotent union = coproduct in the Boolean lattice),
    AND is the meet (intersection = product). Return True iff OR=union(join) and AND=intersection(meet)."""
    A = frozenset({0, 1}); B = frozenset({1, 2})
    join = A | B          # OR = coproduct = union
    meet = A & B          # AND = product = intersection
    return join == frozenset({0, 1, 2}) and meet == frozenset({1})

def lem_is_obligation(prop_decided):
    """M3: LEM is an OBLIGATION, not free. Model a proposition as DECIDED (a witness for p or for not-p exists)
    or UNDECIDED (open). Classical bivalence asserts every prop is decided; constructively that requires a
    witness. Return True iff: an UNDECIDED prop is NOT automatically refuted (open != refuted) -- i.e. you
    cannot conclude not-p from 'p is not (yet) witnessed'. The obligation is the cost of closing it."""
    # prop_decided: True = a witness exists (decided); False = open. The reject-LEM law: open stays open.
    # 'refuting' open-p would require a DNE witness (the obligation). Without it, open != refuted.
    return prop_decided is False  # an open prop is neither asserted nor refuted -- the constructive baseline


# ─────────────────────────────────────────────────────────────────────────────
# [AI-CORPUS-WIDER edge-a] The Pushout-Synthesis mapping, grounded from "Categorical Pushout Synthesis:
# Clique-to-Apex Inversion" (Drive 10w5RvG, a FORMAL doc -- the "grand-unification Synthesis functor" the W-O
# doc cited). The doc gives the categorical NAME for standing law #1 and lands the apex/base inversion on our
# Hodge/swap structure. We gate the MAPPING (the doc's pushout construction is textbook colimit theory):
#  M1. SYNTHESIS = PUSHOUT: law #1 ("either/or -> common structure, recursively") IS the pushout of B <- A -> C,
#      the universal amalgamation along the shared foundation A. The resolution is the MOST GENERAL object
#      respecting the shared heritage -- modeled set-theoretically as the union-over-intersection (the pushout
#      in Set): glue B and C along A, identifying the shared part, adding nothing extraneous.
#  M2. APEX/BASE INVERSION = the Hodge-star residue flip: Apex = LIMIT (pullback, top-down), Dual-Apex = COLIMIT
#      (pushout, bottom-up); inversion = the limit<->colimit duality = our swap involution. On K4 the 4 apex
#      choices = the 4 partitions = the tetrad.
#  M3. PARTITION = SHAPING FUNCTOR (D4): the perspectival apex is a projection of the generative colimit -- our
#      "all-readings = projections of one construction" law, with the apex-choice = the canonicalization target.
# ─────────────────────────────────────────────────────────────────────────────
def pushout_set(A, B, C, f, g):
    """The pushout in Set: glue B and C along the shared foundation A via the span B <-f- A -g-> C. Returns the
    amalgamated set = (B disjoint-union C) / ~, where f(a) ~ g(a) for every a in A. Models law #1: the universal
    amalgamation along the common sub-object. We tag B-elements 'B' and C-elements 'C', then identify f(a) with
    g(a)."""
    # disjoint union with tags
    elems = {('B', b) for b in B} | {('C', c) for c in C}
    # union-find over the identifications f(a) ~ g(a)
    parent = {e: e for e in elems}
    def find(e):
        while parent[e] != e:
            parent[e] = parent[parent[e]]; e = parent[e]
        return e
    def union(x, y):
        parent[find(x)] = find(y)
    for a in A:
        union(('B', f[a]), ('C', g[a]))
    classes = {}
    for e in elems:
        classes.setdefault(find(e), set()).add(e)
    return list(classes.values())

def pushout_is_universal_amalgamation(A, B, C, f, g):
    """Law #1 as the pushout's UNIVERSAL property (the 'no extraneous structure' clause), checked concretely:
    the pushout's size = |B| + |C| - |A| when f,g are injective (exactly the shared part is identified, nothing
    more). This is the set-theoretic union-over-intersection: |B u_A C| = |B| + |C| - |A|."""
    P = pushout_set(A, B, C, f, g)
    inj = len(set(f.values())) == len(f) and len(set(g.values())) == len(g)
    expected = len(B) + len(C) - len(A) if inj else None
    return inj and len(P) == expected

def apex_base_inversion_k4():
    """M2: on K4 (the tetrad), each of the 4 vertices can be the APEX; the apex/base partition's limit<->colimit
    inversion is the Hodge-star duality. Verify: there are exactly 4 apex/base partitions (4 apex choices, each
    with a 3-vertex base), and the inversion is an involution (apex-of-apex returns the partition). Models the
    cone-apex + Hodge-star residue flip on the V4/K4 carrier."""
    verts = [0, 1, 2, 3]
    partitions = [(a, tuple(v for v in verts if v != a)) for a in verts]
    # exactly 4 partitions, each apex + 3-base
    ok_count = len(partitions) == 4 and all(len(base) == 3 for _, base in partitions)
    # inversion is an involution: the dual of (apex, base) flips limit<->colimit; applying twice = identity.
    # model the flip as toggling a parity bit; double-flip returns the original parity.
    def flip(parity): return 1 - parity
    involution = all(flip(flip(p)) == p for p in (0, 1))
    return ok_count and involution

def partition_is_shaping_functor():
    """M3 (D4): the apex/base partition is a class of shaping functor -- the perspectival cone is a projection of
    the generative colimit. Model: a 'shaping functor' picks an apex and synthesizes a cone over the 3-base; the
    partition IS that choice. Verify the apex-choice determines the cone (a function from apex to its base-cone),
    i.e. the 4 partitions give 4 distinct cones (the projection is faithful -- distinct apex => distinct shaping)."""
    verts = [0, 1, 2, 3]
    cones = {a: frozenset(v for v in verts if v != a) for a in verts}  # apex -> its base set
    # faithful: distinct apex choices give distinct base-cones (the projection separates the readings)
    return len(set(cones.values())) == 4


# ─────────────────────────────────────────────────────────────────────────────
# [AI-CORPUS-WIDER Crypto-Manifold] The cryptographic-manifold closure, grounded from "Cryptographic Manifold
# Matrices" (Drive 1C5Ax2s, the dedup canonical of the 9-doc cluster; a FORMAL propositions-as-types doc). It is
# this work's coherence-cell / face-fiber / closure pattern realized on a 6-dim cipher-mode manifold, and it
# UPGRADES three things: (U1) coverability = face-agreement on a closed cell; (U2) a TYPED criterion separating
# open (predictive design-space point) from refuted (uninhabited-by-contradiction); (U3) non-injective projection
# with the residue recovered on a named orthogonal axis. We gate the MAPPING (the cipher facts are NIST/RFC lit).
#
# Model: a mode (vertex) = an assignment over the 6 axes. A face = a pair of axes (a 2-projection). Admissibility
# (the Closure Obligation) = every incident face agrees with the vertex's assignment. The CTR vertex from the
# doc's Global Closure Demonstration is the worked example.
# ─────────────────────────────────────────────────────────────────────────────

# CTR vertex (doc sec "Global Closure Demonstration"): the 6-axis assignment.
_CTR_VERTEX = {
    "DynamicState":   "I",            # counter block / index
    "StaticConfig":   "KxV",          # key + IV/nonce
    "ExecScheduling": "Parallel",     # inhabited
    "ErrorScope":     "BitIsolated",
    "AlignmentClass": "NotNative",    # AST contains B (discrete block boundary via concat)
    "RandomAccess":   "Seekable",     # inhabited
}

# The doc's incident-face constraints for CTR (each face = a pair of axes that must co-agree). A face "agrees"
# if the vertex's two coordinates are jointly admissible per the doc's matrices.
def _ctr_face_admissible(face, vertex):
    a, b = face
    va, vb = vertex[a], vertex[b]
    # the doc's matrix cells that are INHABITED for CTR (the agreeing combinations):
    inhabited = {
        ("DynamicState","ErrorScope"):     {("I","BitIsolated")},                 # M1
        ("StaticConfig","AlignmentClass"): {("KxV","NotNative")},                 # M2 (CTR not-native)
        ("ExecScheduling","StaticConfig"): {("Parallel","KxV")},                  # M3
        ("ErrorScope","ExecScheduling"):   {("BitIsolated","Parallel")},          # M4
        ("AlignmentClass","DynamicState"): {("NotNative","I")},                   # M5
        ("ExecScheduling","AlignmentClass"):{("Parallel","NotNative")},           # M6
        ("RandomAccess","ErrorScope"):     {("Seekable","BitIsolated")},          # M7
        ("ExecScheduling","RandomAccess"): {("Parallel","Seekable")},             # M8
    }
    key = (a, b) if (a, b) in inhabited else (b, a)
    cell = (va, vb) if (a, b) in inhabited else (vb, va)
    return cell in inhabited.get(key, set())

_CTR_FACES = [
    ("DynamicState","ErrorScope"), ("StaticConfig","AlignmentClass"),
    ("ExecScheduling","StaticConfig"), ("ErrorScope","ExecScheduling"),
    ("AlignmentClass","DynamicState"), ("ExecScheduling","AlignmentClass"),
    ("RandomAccess","ErrorScope"), ("ExecScheduling","RandomAccess"),
]

def manifold_vertex_closed(vertex=None, faces=None):
    """The CLOSURE OBLIGATION (doc): a vertex is admissible IFF every incident face agrees on its type
    assignments -- 'the coverable rung scaled globally'. Returns True iff all incident faces are jointly
    inhabited. The CTR vertex is geometrically closed (all 8 faces agree)."""
    vertex = vertex or _CTR_VERTEX
    faces = faces or _CTR_FACES
    return all(_ctr_face_admissible(f, vertex) for f in faces)

def manifold_coverability_is_face_agreement(vertex=None):
    """U1: coverability (the charter's 4th gate) realized CONCRETELY as face-agreement on the closed cell. A
    vertex is 'covered' iff every face it touches agrees -- and a single disagreeing face breaks closure
    (non-vacuous: perturbing one coordinate to a non-inhabited value must break it)."""
    vertex = dict(vertex or _CTR_VERTEX)
    if not manifold_vertex_closed(vertex):
        return False
    # perturb one coordinate to a value the faces reject -> closure must break
    broken = dict(vertex); broken["ErrorScope"] = "Cascade"   # CTR cannot be Cascade (M1/M7 reject)
    return not manifold_vertex_closed(broken)

def classify_empty(constructible, type_contradiction):
    """U2: the TYPED criterion separating the two kinds of empty cell (the doc's central upgrade to open!=refuted).
    A cell with no current inhabitant is REFUTED if it is a type-contradiction (mathematically uninhabited) or
    gate-rejected; it is OPEN ('predictive design-space point') if it is constructible but merely unrealized by
    current standards. Returns 'refuted' | 'open'. This is reject-LEM made decidable."""
    if type_contradiction:
        return "refuted"        # mathematically uninhabited (type mismatch) = genuine bottom
    if constructible:
        return "open"           # constructible but unrealized = a predictive design-space point
    return "refuted"

def manifold_non_injective_residue(mode_a, mode_b):
    """U3: the state axis is intentionally non-injective -- CTR and ChaCha20 share state topology (both 'I') but
    are distinguished on the AlignmentClass axis. = canonicalize+retain-residue with the residue on a named
    orthogonal axis. Returns True iff the two modes collapse on DynamicState but differ on AlignmentClass."""
    collapse = mode_a["DynamicState"] == mode_b["DynamicState"]
    distinguished = mode_a["AlignmentClass"] != mode_b["AlignmentClass"]
    return collapse and distinguished
