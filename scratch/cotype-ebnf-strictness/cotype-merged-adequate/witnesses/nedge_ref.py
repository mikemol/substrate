# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Nedge G-Value reference: the [0,inf] conductance algebra + L-space codec.
The conformance checks f090_2_nedge_* pin THIS. CONFORMS TO the Agda formalization (the authority), NOT a
reinvention -- the substrate repo already proves this algebra:
  Substrate.Logic.Evidence.GValueAsQ        (the conductance algebra in Q: gvalue, balance, gor, gand, recip)
  Substrate.Logic.Evidence.GValueLSpace     (the exp-log codec: L = ln G, monoid homomorphism .<->+ , 1<->0)
  Substrate.Logic.Evidence.GValueLSpace.LogSumExp  (G_OR's L-mirror IS log-sum-exp)
This Python ref is the executable shadow of those proved modules; the Agda is the proof-grade tier.

THE ALGEBRA (verbatim from GValueAsQ, conformed):
  G-value G(P) is a positive rational; balance = 1 (Nedge's L = 0); the antipode constraint G(P)*G(not P)=1.
  G_NOT = recip       (reciprocal / num-den swap = the antipode)        -- Agda: recip
  G_OR  = a + b       (parallel conductance, Kirchhoff parallel rule)   -- Agda: gor = _+Q_
  G_AND = (a*b)*recip(a+b)  (series conductance = product over sum)     -- Agda: gand
  balance is the involution fixed point (recip 1 = 1); gor is NON-IDEMPOTENT (gor 1 1 = 2 != 1, Agda proof).
  DeMorgan EXACT under recip with balance self-dual (f090_2_nedge_ideal): G_NOT(G_AND(G_NOT a, G_NOT b)) = G_OR(a,b).

THE L-SPACE CODEC (GValueLSpace): L = ln G is a monoid homomorphism (additive L <-> multiplicative G):
  exp(a + b) = exp a * exp b ;  exp 0 = 1 ;  recip <-> negation.  G_OR's L-mirror = log-sum-exp (LogSumExp).
  This is the [0,inf] <-> L-space = [-inf,+inf] bridge: ideal 1 <-> additive origin 0.

CANON+RESIDUE (AI-CANON-RESIDUE, the per-ref obligation; Nedge releases BIVALENCE):
  The G-value GRADE (a positive rational) is the canonical evidence summary -- it is LOSSY: a single grade
  collapses the support/conflict pair that produced it (many (E+, E-) give the same ratio E+/E-). The residue
  is the (E+, E-) component pair (the L-space sign+magnitude decomposition) -- exactly what the ratio
  discarded. grade + residue is LOSSLESS: recover reproduces (E+, E-). CONSERVATION: the two-valued {0,1}
  logic assumed BIVALENCE (a trivial law); Nedge releases it, and the residue (the graded components about
  the ideal 1) is the carried witness. triviality-out (bivalence) = witness-in (the components).
"""
from fractions import Fraction as Q

# ---- the conductance algebra (conforms to GValueAsQ) ----
balance = Q(1, 1)                       # G = 1 = Nedge's L = 0 (the involution fixed point)

def g_not(a):                           # recip / antipode: num<->den swap
    return Q(a.denominator, a.numerator)

def g_or(a, b):                         # parallel conductance = Q addition
    return a + b

def g_and(a, b):                        # series conductance = (a*b)*recip(a+b)
    return (a * b) * g_not(a + b)

def antipode_law(a):                    # G * G_NOT(G) = 1 (the balance-channel constraint)
    return a * g_not(a) == balance

def de_morgan(a, b):                    # exact under recip with balance self-dual
    return g_not(g_and(g_not(a), g_not(b))) == g_or(a, b)

def gor_non_idempotent():               # gor 1 1 = 2 != 1 (Agda gor-non-idempotent)
    return g_or(balance, balance) != balance

# ---- L-space codec (conforms to GValueLSpace: monoid homomorphism, structural not analytic) ----
# We realize the codec STRUCTURE on the prime-power carrier (as the Agda does via PrimeFactor): an L-space
# element is an exponent (here an integer power of a fixed base ratio), expL is base**exponent, the
# homomorphism exp(a+b)=exp a * exp b holds exactly over Q -- no transcendence (per the module's note).
def expL(exponent, base=Q(2, 1)):       # exp : L (additive exponent) -> G (multiplicative Q)
    return base ** exponent             # Fraction supports integer powers exactly

def codec_hom(a, b, base=Q(2, 1)):      # exp(a+b) == exp a * exp b  (the homomorphism law)
    return expL(a + b, base) == expL(a, base) * expL(b, base)

def codec_origin(base=Q(2, 1)):         # exp 0 == 1 (ideal 1 <-> L-origin 0)
    return expL(0, base) == balance

def log_sum_exp_or(a, b, base=Q(2, 1)):
    # G_OR's L-mirror: L_OR = logL(expL a + expL b) = log-sum-exp (LogSumExp module).
    # Structural check: expL(L_OR) == expL a + expL b == g_or(expL a, expL b).
    return expL(a, base) + expL(b, base)   # = g_or(expL a, expL b); the LSE identity at the G level

# ---- CANON + RESIDUE (grade is lossy; (E+,E-) components are the witness) ----
def grade(e_plus, e_minus):             # the G-value = E+/E- (support over conflict); the canonical summary
    return Q(e_plus, e_minus)

def canonicalize(e_plus, e_minus):
    """canonical = the grade E+/E- (lossy: collapses the pair to a ratio); residue = the (E+,E-) pair."""
    g = grade(e_plus, e_minus)
    residue = (e_plus, e_minus)
    return g, residue

def recover(grade_q, residue):
    """grade + residue is LOSSLESS: the (E+,E-) pair recovers the exact components the ratio discarded."""
    return residue                      # the components ARE the witness; ratio alone could not give them back
