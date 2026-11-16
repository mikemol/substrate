# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""ASPF cohomology bridge: prime = cocycle = SPPF-node label (USER), with the precise residue.
Grounded this turn from USER's claim, tested by construction (see register [AI-ASPF-COCYCLE]).

THE CLAIM (witnessed where it holds, residue recorded where it breaks):
  A prime p is "the cocycle of all the numbers in which it is a factor" -- p is the atomic generator of the
  divisor poset; its up-set (multiples) is the set of structures that SHARE it (its parents), exactly as an
  SPPF node is shared by all its parents. A prime can be the UNIQUE LABEL of an atomic shared node (by unique
  factorization), and a composite = the product = a packed (assembled) node.

THIS UNIFIES THE THREE ASPF REFERENCES as three projections of ONE shared-packed structure:
  aspf_ref.py (prime product)    = the label of ONE unambiguous derivation: a MONOMIAL in primes (cocycle
                                   product); order-blind, span-blind.
  aspf_rsbpf_ref.py ({L,R}*+GF2) = the ORDERED address + which-alternative-active (the derivation tree).
  packed SPPF node               = the INTERNED SET of alternative-derivation labels = a POWERSET element
                                   under idempotent union (A u A = A), NOT an additive sum. Aggressive
                                   re-interning (sequitur-style, no promotion threshold) collapses
                                   structurally-equal derivations to one ORBIT; the recursion is over the
                                   powerset P(P(...)).
The exp/log transition (g-calculus, cf. nedge_ref) bridges the two faces: WITHIN a derivation factors MULTIPLY
(exp / AND side), ACROSS alternatives labels UNION idempotently (log / OR side). The soft log-sum-exp (Nedge
G_OR L-mirror) COUNTS duplicates (non-idempotent); the T->0 HARD limit is max = union = idempotent, and
aggressive interning operates at that hard limit. (CORRECTION: an earlier draft modeled ambiguity as an
additive sum in N[primes] -- that is the SOFT, multiplicity-counting reading; interning makes it the HARD,
idempotent powerset. Same soft/hard exchange as nedge_lspace and APSP annealing.)

COHOMOLOGY (the precise sense of "cocycle"): the divisor poset is an incidence structure; the Mobius function
mu is the inverse of the zeta (divisibility) relation in its incidence algebra -- sum_{d|n} mu(d) = [n==1].
This is the coboundary identity: mu is d^{-1}. Primes are the degree-1 (atomic) generators under the grading
Omega(n) = number of prime factors with multiplicity (degree 0 = the unit 1 = the root/empty derivation).

RESIDUE (where prime <-> SPPF-node iso BREAKS -- held open, not welded; the subsystems stay distinct):
  (1) ORDER  -- prime multiset unordered; SPPF children ordered. (aspf_ref's order-residue; RSBPF keeps it.)
  (2) SPAN   -- SPPF node = (X,i,j) carries an input span; the prime carries identity, not position.
  (3) PACKING -- the prime PRODUCT labels one derivation (the exp/AND side); an ambiguous node is the
                 IDEMPOTENT UNION (powerset) of its derivation labels (the log/OR side), reached via the
                 exp/log transition, NOT an additive semiring sum. Interning makes the union idempotent.
"""
from sympy import factorint, divisors, mobius

# ─────────────────────────────────────────────────────────────────────────────
# grading: Omega(n) = #prime factors with multiplicity = the chain degree.
# degree 0 = {1} (unit/root); degree 1 = primes (atomic shared nodes); higher = packed/composite.
# ─────────────────────────────────────────────────────────────────────────────
def degree(n):
    return sum(factorint(n).values())

def is_atomic_node(n):
    """A prime: a degree-1 node -- an irreducible shared substructure (a terminal/leaf shared node)."""
    return degree(n) == 1

def shared_into(p, universe):
    """The up-set of p: the structures that SHARE p (its 'parents') = multiples of p in the universe.
    This is the SPPF 'one node, many parents' relation for the atomic node p."""
    return [n for n in universe if n % p == 0]

# ─────────────────────────────────────────────────────────────────────────────
# cohomology: the Mobius coboundary identity sum_{d|n} mu(d) = [n==1].
# mu is d^{-1} in the incidence algebra of the divisor poset; the primes are its atomic cocycle generators.
# ─────────────────────────────────────────────────────────────────────────────
def mobius_coboundary(n):
    """sum_{d|n} mu(d). Equals 1 iff n==1, else 0 (the delta/coboundary identity)."""
    return sum(mobius(d) for d in divisors(n))

def is_coboundary_identity(n):
    return mobius_coboundary(n) == (1 if n == 1 else 0)

# ─────────────────────────────────────────────────────────────────────────────
# the powerset reading (USER correction): a PACKED node is NOT an additive sum of monomials (that is the SOFT,
# multiplicity-COUNTING reading -- non-idempotent G_OR). With AGGRESSIVE RE-INTERNING (sequitur-style: intern
# on sight, no promotion threshold), structurally-equal derivations collapse to ONE ORBIT immediately, so
# ambiguity is IDEMPOTENT: a SET (powerset element) under union, A u A = A. The recursion is over the powerset
# (each alternative is itself a set of sub-alternatives, P(P(...))) -- "that's a powerset problem, which is how
# my SPPFs recurse." The g-calculus exp/log transition bridges the two faces: WITHIN a derivation factors
# MULTIPLY (prime product, the AND / exp / multiplicative side); ACROSS alternatives labels UNION idempotently
# (the OR / log / powerset side). The soft log-sum-exp (Nedge G_OR L-mirror) COUNTS dups; the T->0 hard limit
# is max = union = idempotent -- interning operates at that hard limit. Same soft/hard exchange as nedge_lspace.
# ─────────────────────────────────────────────────────────────────────────────
def derivation_label(prime_multiset):
    """Label one derivation by the PRODUCT of its atomic sub-node primes (a monomial). This is the WITHIN-
    derivation, multiplicative (AND / exp-side) combination of factors of ONE parse."""
    prod = 1
    for p in prime_multiset:
        assert is_atomic_node(p), f"{p} is not an atomic (prime) node"
        prod *= p
    return prod

def node_factor_multiset(n):
    """Recover the multiset of atomic sub-nodes (primes) of a derivation label -- the FTA inverse."""
    f = factorint(n)
    out = []
    for p, e in sorted(f.items()):
        out += [p] * e
    return out

def intern_orbit(packed_set, derivation):
    """AGGRESSIVE RE-INTERNING: add a derivation's label to the packed node as an ORBIT. Structurally-equal
    derivations (same label) collapse -- the set absorbs duplicates IDEMPOTENTLY (no multiplicity, no promotion
    threshold). Returns the updated frozenset (the powerset element)."""
    return frozenset(packed_set | {derivation_label(derivation)})

def packed_node(derivations):
    """A PACKED (ambiguous) node = the INTERNED SET of its alternative-derivation labels (a powerset element),
    NOT a multiset/sum. Idempotent: re-discovering a derivation does not change the node. |set| > 1 iff
    genuinely ambiguous (>=2 STRUCTURALLY DISTINCT derivations of the span = payload-alternation)."""
    s = frozenset()
    for d in derivations:
        s = intern_orbit(s, d)
    return s

def is_ambiguous(packed):
    """Ambiguous iff the interned set has >= 2 distinct derivation labels (payload-alternation)."""
    return len(packed) >= 2

def union_alternatives(packed_a, packed_b):
    """ACROSS-alternatives OR: idempotent set UNION (the powerset join). A u A = A -- the HARD (interned) limit
    of the soft log-sum-exp G_OR. This is how alternatives of the SAME span combine (not addition)."""
    return frozenset(packed_a | packed_b)

def concat_spans(packed_a, packed_b):
    """WITHIN-derivation composition across adjacent spans: the multiplicative product distributes over the
    set (each alternative of A pairs with each of B), and the result is again INTERNED (idempotent). This is
    the exp-side (product) lifted over the powerset: the set of all label-products, deduped."""
    return frozenset(ma * mb for ma in packed_a for mb in packed_b)

# the exp/log bridge (g-calculus): exp turns the additive (alternative, log/OR side) into the multiplicative
# (factor, exp/AND side). soft = log-sum-exp (counts); hard T->0 limit = max = idempotent union = interning.
def soft_or_value(labels, T):
    """The SOFT OR over alternative labels (Nedge G_OR L-mirror = log-sum-exp). COUNTS multiplicity (a dup
    label contributes twice) -- this is the NON-interned, additive reading. As T->0 it -> max (the hard,
    idempotent union limit that interning realizes)."""
    import math
    return T * math.log(sum(math.exp(math.log(x) / T) for x in labels))

def hard_or_value(labels):
    """The HARD (T->0) limit: max = the dominant alternative. IDEMPOTENT (max of a set ignores duplicates) --
    this is the interned/powerset reading. The exp/log transition's hard pole."""
    return max(labels)

