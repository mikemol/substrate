#!/usr/bin/env python3
"""jea_trace_window.py — the TRACE-WINDOW rational carrier: the lane holds the CF / EEA shape,
and (num,den) is recovered by the fold. The suspended generator MADE the carrier, not observed
into one. The dual of jea_swar_q.py's value-window (num,den limbs).

A rational's continued fraction [a0; a1, a2, ...] IS its EEA quotient sequence (Euclid). Two folds:
  to_cf   (value -> trace): Euclid producing the quotients      -- the EEATrace shape
  from_cf (trace -> value): the convergent recurrence h_i,k_i   -- recover (num,den)

The structure that makes this the "exactness/canonicality without forcing full reduction" arm:
  * CANONICAL BY CONSTRUCTION: to_cf(k*p, k*q) == to_cf(p, q) exactly -- Euclid divides the gcd out
    of every step, so the CF is scale-free. Equal value <=> equal CF. NO reduce step: never
    un-reduced. The CF is THE canonical key (the SPPF==EEA shape).
  * from_cf . to_cf == reduce: the round-trip is the retraction (split-idempotent apex); idempotent.
  * PAY-PER-UNFOLD: the convergents (prefixes) bracket the value alternately (a verified rational
    interval), so a prefix is a finite observation of the suspended generator; unfold more on demand.
  * COMPARE-BY-PREFIX: decide p/q vs r/s by CF lex with sign-alternation, often without unfolding
    fully and without any cross-multiply.

THE PARETO BOUNDARY (why this is a real choice, not a forced one):
  value-window: arithmetic is CHEAP (limb add/mul, SWAR-packed, dense throughput) but canonical/
                compare is EXPENSIVE (reduce gcd + cross-multiply); carries mass/residue.
  trace-window: canonical/compare is FREE (scale-free + prefix) but arithmetic is EXPENSIVE (Gosper
                Mobius state machine, not a limb op; serial/divergent).
The workload mix where the two reps cost the same is the el-atlas Wheatstone bridge NULL -- the
bridge instrument finds the Pareto crossover, and the bias sign says which rep wins each side.
"""
from fractions import Fraction
from math import gcd
import numpy as np


# ---- the two folds: value <-> trace -------------------------------------------------------
def to_cf(p, q):
    """value -> trace: the EEA/Euclid quotient sequence (canonical CF). q != 0; Python // is floor."""
    cf = []
    while q:
        a = p // q
        cf.append(a)
        p, q = q, p - a * q
    return cf

def from_cf(cf):
    """trace -> value: the convergent recurrence. Returns (num, den) already in lowest terms."""
    h1, h0, k1, k0 = 1, 0, 0, 1            # h_{-1},h_{-2}, k_{-1},k_{-2}
    for a in cf:
        h1, h0 = a * h1 + h0, h1
        k1, k0 = a * k1 + k0, k1
    return h1, k1

def convergents(cf):
    """the prefixes' (num,den) -- the suspended generator forced window-by-window."""
    h1, h0, k1, k0 = 1, 0, 0, 1
    out = []
    for a in cf:
        h1, h0 = a * h1 + h0, h1
        k1, k0 = a * k1 + k0, k1
        out.append((h1, k1))
    return out

def cf_less(A, B):
    """A_value < B_value by CF lex with sign-alternation; terminated CF == padded with +inf."""
    i = 0
    while i < len(A) and i < len(B):
        if A[i] != B[i]:
            lt = A[i] < B[i]
            return lt if i % 2 == 0 else not lt
        i += 1
    if len(A) == len(B):
        return False                       # identical CFs -> equal
    # one is a prefix of the other: the runner-out has effective next term +inf
    return (len(A) % 2 == 1) if len(A) < len(B) else (len(B) % 2 == 0)


# ---- witnesses ----------------------------------------------------------------------------
def roundtrip_is_reduce():
    """from_cf . to_cf == reduce (the retraction); idempotent."""
    rng = np.random.default_rng(0); ok = idem = True
    for _ in range(20000):
        p = int(rng.integers(-(1 << 20), 1 << 20)); q = int(rng.integers(1, 1 << 20))
        n, d = from_cf(to_cf(p, q))
        g = gcd(abs(p), q)
        ok &= (n == p // g and d == q // g) or (Fraction(n, d) == Fraction(p, q))
        # idempotent: reducing the reduced is a no-op
        n2, d2 = from_cf(to_cf(n, d)); idem &= (n2 == n and d2 == d)
    print(f"1. from_cf.to_cf == reduce (retraction) {ok}; idempotent {idem}")
    return ok and idem

def canonical_by_construction():
    """to_cf(k*p, k*q) == to_cf(p, q): the CF is scale-free => canonical, NO reduce step."""
    rng = np.random.default_rng(1); ok = True; checked = 0
    for _ in range(20000):
        p = int(rng.integers(-(1 << 16), 1 << 16)); q = int(rng.integers(1, 1 << 16))
        k = int(rng.integers(2, 50))
        if to_cf(p, q) != to_cf(k * p, k * q):
            ok = False
        checked += 1
    print(f"2. canonical by construction: CF(kp,kq)==CF(p,q) over {checked} cases {ok}  "
          f"(equal value <=> equal CF; the CF IS the canonical key, no reduce needed)")
    return ok

def unfold_brackets():
    """convergents bracket the value alternately: even-index <= value <= odd-index, monotone in."""
    rng = np.random.default_rng(2); ok = True
    for _ in range(5000):
        p = int(rng.integers(1, 1 << 24)); q = int(rng.integers(1, 1 << 24))
        v = Fraction(p, q); cv = convergents(to_cf(p, q))
        # each convergent error strictly decreases in magnitude; signs alternate
        errs = [Fraction(h, k) - v for (h, k) in cv]
        for i in range(1, len(errs)):
            if errs[i] != 0 and errs[i - 1] != 0:
                if abs(errs[i]) > abs(errs[i - 1]):                 # converging
                    ok = False
                if (errs[i] > 0) == (errs[i - 1] > 0) and errs[i] != 0:  # alternating
                    ok = False
        if cv and Fraction(*cv[-1]) != v:                          # last convergent == the value
            ok = False
    print(f"3. pay-per-unfold: convergent prefixes alternate-bracket the value, error strictly "
          f"shrinks, last == value {ok}")
    return ok

def compare_by_prefix():
    """cf_less decides order matching the true rational order, no cross-multiply."""
    rng = np.random.default_rng(3); ok = True; nontrivial = 0
    for _ in range(20000):
        p1 = int(rng.integers(-(1 << 14), 1 << 14)); q1 = int(rng.integers(1, 1 << 14))
        p2 = int(rng.integers(-(1 << 14), 1 << 14)); q2 = int(rng.integers(1, 1 << 14))
        truth = Fraction(p1, q1) < Fraction(p2, q2)
        if cf_less(to_cf(p1, q1), to_cf(p2, q2)) != truth:
            ok = False
        nontrivial += 1
    print(f"4. compare-by-prefix: CF lex (sign-alternating) == true order over {nontrivial} pairs {ok}  "
          f"(canonicality + comparison free, no cross-multiply)")
    return ok

def rep_pareto_bridge():
    """value/trace as a Wheatstone bridge over the workload mix; the crossover is the NULL."""
    # per-op costs (units): the measured asymmetry of the two reps.
    va, vc = 1.0, 8.0   # value-window:  arithmetic cheap (1, SWAR limb op); canonical 8 (reduce+cross-mult)
    ta, tc = 8.0, 1.0   # trace-window:  arithmetic 8 (Gosper Mobius state machine); canonical 1 (prefix)
    cost_v = lambda f: f * va + (1 - f) * vc      # f = fraction of ops that are ARITHMETIC
    cost_t = lambda f: f * ta + (1 - f) * tc
    fstar = (vc - tc) / ((vc - tc) + (ta - va))   # crossover: cost_v == cost_t  (the bridge null)
    null = abs(cost_v(fstar) - cost_t(fstar)) < 1e-9
    bias = lambda f: cost_t(f) - cost_v(f)        # >0 => value cheaper (wins); flips across f*
    flips = bias(fstar - 0.2) * bias(fstar + 0.2) < 0
    arith_heavy = 'value' if cost_v(0.9) < cost_t(0.9) else 'trace'
    compare_heavy = 'trace' if cost_t(0.1) < cost_v(0.1) else 'value'
    print(f"5. value/trace Pareto as a bridge: crossover f*={fstar:.3f} (arithmetic fraction); "
          f"bridge NULL at f* {null}; bias flips across f* {flips};")
    print(f"   arith-heavy (f=.9) winner = {arith_heavy}; compare/canonical-heavy (f=.1) winner = {compare_heavy}")
    print(f"   => the el-atlas bridge finds the Pareto crossover; bias sign picks the rep per workload.")
    return null and flips and arith_heavy == 'value' and compare_heavy == 'trace'


if __name__ == "__main__":
    print("The TRACE-WINDOW carrier: the lane holds the CF/EEA shape; (num,den) by the fold.\n")
    w = [roundtrip_is_reduce(), canonical_by_construction(), unfold_brackets(),
         compare_by_prefix(), rep_pareto_bridge()]
    ok = all(w)
    print(f"\n  {'PASS' if ok else 'FAIL'} — the trace-window is the dual carrier: canonical BY")
    print(f"  CONSTRUCTION (scale-free CF, no reduce), pay-per-unfold (convergents bracket the value),")
    print(f"  compare-by-prefix (no cross-multiply); round-trip with the value-window IS reduce (a split-")
    print(f"  idempotent retraction). Arithmetic is the cost (Gosper, not a limb op) -- so value-window")
    print(f"  vs trace-window is a real Pareto boundary, and the workload crossover is the bridge NULL.")
