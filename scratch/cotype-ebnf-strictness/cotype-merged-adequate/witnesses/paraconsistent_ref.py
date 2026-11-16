# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""[AI-CORPUS-WIDER Nedge-paraconsistency] The paraconsistency of the Nedge G-value algebra, on the CORRECT
[0,inf] structure (CONFORMS TO nedge_ref / Agda GValueAsQ -- ideal 1, reciprocal negation, conductance ops).

CORRECTION (USER + koan): an earlier version of this ref modeled a bounded [0,1] (t,c) truth-degree logic with
negation (1-t) and min/max ops. THAT WAS WRONG -- it is a generic fuzzy/Belnap paraconsistent logic, NOT Nedge.
Nedge is [0,inf] with the ideal at balance 1, reciprocal (antipode) negation, and conductance operations; it is
explicitly NOT probabilistic (probability would idempotently cap; conductance ACCUMULATES). This ref is rebuilt
to conform.

THE REAL NEDGE PARACONSISTENCY (three sources, all on the [0,inf] algebra):
  1. NON-IDEMPOTENT G_OR (gor 1 1 = 2): accumulating the same evidence twice differs from once -- the algebra
     COUNTS evidence (resource/conductance), it does NOT collapse to a capped truth value. The anti-probabilistic
     core: P + P != P. (A probability/Boolean OR would be idempotent.)
  2. RECIPROCAL ANTIPODE G(P)*G(not P) = 1: P and its negation 1/P are both FINITE and POSITIVE -- neither 0
     (false) nor inf (true). They COEXIST as graded conductances; their series combination P AND (1/P) is a
     specific SUB-BALANCE value, never a trivializing collapse. No explosion.
  3. NO EXPLOSION via series boundedness: g_and(a,b) = (a*b)/(a+b) <= min(a,b) always, so a contradiction
     (a small conductance) combined with an arbitrary Q can never LIFT Q toward truth (inf). Ex contradictione
     quodlibet fails: from a contradiction you cannot derive an arbitrary proposition at full truth.

The genuine DUAL-COMPONENT carrier is the (E+, E-) two-accumulator residue (the EL-Atlas carrier, [0,inf]^2),
which is ALREADY nedge_ref's canon/residue: the scalar grade G = E+/E- is lossy (many (E+,E-) share a ratio);
the residue is the (E+, E-) pair. Paraconsistency is the refusal to collapse (E+,E-) to a single bivalent verdict.
"""
from fractions import Fraction as Q

balance = Q(1)

def g_not(a):
    """Reciprocal antipode (num<->den swap). G(P)*G(not P)=1. Conforms to nedge_ref.g_not."""
    return Q(a.denominator, a.numerator)

def g_or(a, b):
    """Parallel conductance = sum. NON-IDEMPOTENT (the anti-probabilistic core). Conforms to nedge_ref.g_or."""
    return a + b

def g_and(a, b):
    """Series conductance = (a*b)/(a+b). Bounded above by min(a,b). Conforms to nedge_ref.g_and."""
    return (a * b) / (a + b)

def antipode_law(a):
    """G(P) * G(not P) = 1: P and its negation are reciprocal (both finite, positive, coexisting)."""
    return a * g_not(a) == balance

def gor_non_idempotent(a):
    """The anti-probabilistic core: G_OR(a,a) = 2a != a (evidence ACCUMULATES, it does not idempotently cap)."""
    return g_or(a, a) != a and g_or(a, a) == 2 * a

def series_bounded_by_min(a, b):
    """g_and(a,b) <= min(a,b): series conductance only ever LOWERS -- a contradiction cannot lift Q to truth."""
    return g_and(a, b) <= min(a, b)

def no_explosion(P):
    """Paraconsistency on the real algebra: P and not-P (= 1/P) coexist (both finite, positive), their series
    combination is a specific sub-balance value (< 1), and combining that contradiction with ANY Q cannot lift
    Q toward truth (series is <= min). Returns True iff all three hold."""
    nP = g_not(P)
    coexist = P > 0 and nP > 0 and P != Q(0) and nP != Q(0)        # neither false(0) nor unreachable
    contra = g_and(P, nP)
    sub_balance = contra < balance                                  # the contradiction is below balance, not a collapse
    no_lift = all(g_and(contra, Q(q)) <= min(contra, Q(q)) for q in [1, 3, 7, 50])
    return coexist and sub_balance and no_lift

def grade_is_lossy(Ep1, Em1, Ep2, Em2):
    """The (E+, E-) two-accumulator residue (the EL-Atlas carrier) vs the scalar grade G = E+/E-. The grade is
    LOSSY: distinct (E+, E-) pairs can share a ratio. Paraconsistency = keeping (E+, E-), refusing to collapse to
    the bivalent grade. Returns True iff the two distinct pairs share a grade but differ as pairs (the residue is
    real -- non-vacuous)."""
    g1 = Q(Ep1, Em1); g2 = Q(Ep2, Em2)
    return g1 == g2 and (Ep1, Em1) != (Ep2, Em2)


# ─────────────────────────────────────────────────────────────────────────────
# [AI-CORPUS-WIDER rule-graph] The rule-graph kernel's vacuous-until-tipped projection (Drive 1jvhlmOX,
# rule-graph-kernel-design.md), a FOURTH decorrelated arm stating our realizability charter verbatim and
# re-deriving the paraconsistency quotient independently in a game-REPL framing. The doc's project() is a
# concrete realization of the (E+,E-) two-accumulator paraconsistency: per source, sum the +evidence and
# -evidence; if they BALANCE the variable is VACUOUS (absent from the world dict -- "open != refuted"); else the
# dominant sign fires with magnitude |plus - minus| (the grade, the signed distance from balance). This conforms
# in STRUCTURE (not in carrier type: the doc uses signed ints +-3, an OPEN parameter per its sec13.3 -- the same
# [0,inf]-vs-bounded slot left open) to the corrected Nedge/EL-Atlas paraconsistency.
# ─────────────────────────────────────────────────────────────────────────────
def rulegraph_project_edge(plus_ev, minus_ev):
    """The rule-graph kernel's per-source projection (doc sec 8): given the summed +evidence and -evidence for
    one source->target group, return None if balanced (VACUOUS -- the key is absent from the world, 'open !=
    refuted'), else (sign, magnitude) where magnitude = |plus - minus| (the grade)."""
    if plus_ev == minus_ev:
        return None                       # vacuous: no projection output (absence, not a value)
    sign = '+' if plus_ev > minus_ev else '-'
    return (sign, abs(plus_ev - minus_ev))

def rulegraph_is_paraconsistent_carrier(plus_ev, minus_ev):
    """The (plus, minus) per-source pair IS the (E+, E-) two-accumulator carrier. Verify the structural conformance
    to the paraconsistency: (a) balance => vacuous (the contradiction does not explode, it goes inert); (b) the
    grade = signed distance from balance = the magnitude; (c) the carrier is the dual accumulator (two independent
    sums), matching grade_is_lossy's (E+, E-)."""
    proj = rulegraph_project_edge(plus_ev, minus_ev)
    if plus_ev == minus_ev:
        return proj is None               # balanced contradiction is inert (no explosion)
    # asymmetric: fires with the dominant sign, magnitude = the grade
    sign, mag = proj
    return mag == abs(plus_ev - minus_ev) and sign == ('+' if plus_ev > minus_ev else '-')

def rulegraph_cut(sign_ab, sign_bc):
    """The CUT operator (doc sec 6.1): A->B, B->C => A->C with COMPOSED sign. Sign composition is the GF(2)/V4
    sign product (+*+=+, +*-=-, -*-=+). = span-DP (x) composition with sign tracking (our coherence Cell B)."""
    return '+' if sign_ab == sign_bc else '-'
