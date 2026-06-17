#!/usr/bin/env python3
"""jea_swar_q.py — what is IN the SWAR lanes: Q. And how Q + traces relate to them.

A lane carries a rational Q = the pair (num, den). That pair IS the el-atlas nedge (E+, E-)
carrier (the lift theorem): G_OR = fraction-add (n1d2+n2d1, d1d2); G_NOT = swap (n,d)->(d,n) =
reciprocal; G_AND = swap(add(swap,swap)) = n1n2/(n1d2+n2d1) = the series-conductance formula.
So the nedge pilot's E+/E- WAS num/den. A register packs N rationals as N (num,den) lane-pairs;
Q-multiply = num*num, den*den = two lane-wise bignum multiplies (jea_swar_bignum) in one pass.

The TRACE is the suspended EEA/CF generator the (num,den) lane is a forced WINDOW of. The
el-atlas crossbar on a Q-lane is mass = num+den, bias = num-den, and the closure is:

    reduce (gcd) LOWERS MASS at fixed value. The common factor g it strips is exactly the
    residue the trace retains.

Two facts that turn out identical:
  - el-atlas:  the quotient erases the mass the unquotiented pair keeps.
  - substrate: never discard residue -- reduce is a RETRACTION (split-idempotent apex),
               lossless because the trace keeps g to multiply back.

So: lane = value-window (num,den) = nedge carrier; trace = generator + the residue/mass reduce
would discard. Lane width = how much of the trace you've unfolded; reduce shrinks mass, not value.

Sections:
  1. SWAR: N rationals per register as adjacent (num,den) lanes; Q-multiply via one lane-wise
     bignum multiply; verified == the unreduced (n1n2, d1d2) reference (cupy).
  2. nedge identity on the (num,den) carrier: G_OR == Q-add; G_NOT == swap == reciprocal;
     G_AND == series-conductance -- the lift, on the lane pair (pure).
  3. crossbar + trace: mass=num+den / bias=num-den; reduce lowers mass strictly at fixed value;
     the gcd cofactor IS the residue; keeping it makes reduce an invertible retraction (pure).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
from math import gcd
import numpy as np, cupy as cp
import jea_swar_bignum as B


# ---- 1. Q rides the SWAR carrier: N rationals/register, Q-multiply in one bignum pass ----
def swar_q_multiply():
    """Each Q uses TWO adjacent lanes (even=num, odd=den). One SWAR bignum multiply does
    num*num and den*den simultaneously (lanes are independent) => N//2 Q-products per register."""
    L, K, W, Bsz = 2, 4, 8, 256            # 2-bit limbs, 4 limbs => values < 2^8; W per bignum rule
    Q = 4                                  # rationals per register (N*W<=64: 8 lanes * 8 bits = 64)
    N = 2 * Q                              # lanes: (num,den) per Q
    M = (1 << (L * K)) - 1
    rng = np.random.default_rng(0)
    # build Q rationals per word; lane 2q = num_q, lane 2q+1 = den_q (den >= 1)
    nums = [[int(rng.integers(0, M + 1)) for _ in range(Q)] for _ in range(Bsz)]
    dens = [[int(rng.integers(1, M + 1)) for _ in range(Q)] for _ in range(Bsz)]
    vA, vB = [], []
    for b in range(Bsz):
        rowA, rowB = [], []
        for q in range(Q):
            rowA += [nums[b][q], dens[b][q]]
            rowB += [nums[b][q], dens[b][q]]   # squaring here just to exercise; any pair works
        vA.append(rowA); vB.append(rowB)
    A = B.pack(vA, L, K, W); Bp = B.pack(vB, L, K, W)
    out = B.swar_bignum_mul(A, Bp, L, K, N, W, carryless=False)
    got = B.unpack(out, L, W, N)
    ok = True
    for b in range(Bsz):
        for q in range(Q):
            n1, d1 = vA[b][2 * q], vA[b][2 * q + 1]
            n2, d2 = vB[b][2 * q], vB[b][2 * q + 1]
            # lane product is the UNREDUCED Q-product (mass-carrying): (n1*n2, d1*d2)
            if got[b][2 * q] != n1 * n2 or got[b][2 * q + 1] != d1 * d2:
                ok = False
    print(f"1. SWAR Q-multiply: {Q} rationals/register x {Bsz} words = {Q * Bsz} Q-products, "
          f"one lane-wise bignum pass (num & den in adjacent lanes), == unreduced (n1n2,d1d2): {ok}")
    return ok


# ---- 2. the (num,den) lane IS the nedge carrier: the lift, verified -----------------------
def nedge_lift_on_pairs():
    add  = lambda p, q: (p[0] * q[1] + q[0] * p[1], p[1] * q[1])     # fraction-add  = G_OR
    swap = lambda p: (p[1], p[0])                                   # reciprocal    = G_NOT
    sand = lambda p, q: swap(add(swap(p), swap(q)))                 # G_AND via swap-conjugation
    cls  = lambda p: p[0] / p[1]                                    # the conductance G = num/den
    G_OR  = lambda a, b: a + b
    G_AND = lambda a, b: a * b / (a + b)
    G_NOT = lambda g: 1.0 / g
    rng = np.random.default_rng(1); ok_or = ok_not = ok_and = True
    for _ in range(2000):
        p = (int(rng.integers(1, 50)), int(rng.integers(1, 50)))
        q = (int(rng.integers(1, 50)), int(rng.integers(1, 50)))
        ok_or  &= abs(cls(add(p, q))  - G_OR(cls(p), cls(q)))  < 1e-9
        ok_not &= abs(cls(swap(p))    - G_NOT(cls(p)))         < 1e-9
        ok_and &= abs(cls(sand(p, q)) - G_AND(cls(p), cls(q))) < 1e-9
    print(f"2. nedge lift on (num,den) lane: G_OR==Q-add {ok_or}; G_NOT==swap==reciprocal {ok_not}; "
          f"G_AND==series-conductance {ok_and}  => the lane pair IS the nedge carrier")
    return ok_or and ok_not and ok_and


# ---- 3. crossbar + trace: reduce lowers mass at fixed value; cofactor = residue = trace ----
def reduce_is_mass_drop():
    """mass = num+den, bias = num-den (the el-atlas crossbar on the Q-lane). reduce by g=gcd
    lowers mass strictly (when g>1) at FIXED value; g is the residue the trace keeps; keeping
    it makes reduce an invertible retraction (multiply the cofactor back)."""
    rng = np.random.default_rng(2)
    ok_value = ok_mass = ok_retract = True
    saw_drop = False
    for _ in range(5000):
        n0 = int(rng.integers(1, 1 << 20)); d0 = int(rng.integers(1, 1 << 20))
        g = gcd(n0, d0); n, d = n0 // g, d0 // g
        ok_value &= Fraction(n0, d0) == Fraction(n, d)            # value invariant under reduce
        mass0, mass = n0 + d0, n + d
        ok_mass &= (mass <= mass0)                                # reduce never raises mass
        if g > 1:
            saw_drop |= (mass < mass0)                            # and strictly drops when g>1
        ok_retract &= (n * g == n0 and d * g == d0)               # cofactor g restores: lossless retraction
    print(f"3. crossbar+trace: value invariant under reduce {ok_value}; reduce lowers mass {ok_mass} "
          f"(strict drop seen {saw_drop}); cofactor g restores (retraction) {ok_retract}")
    print(f"   => trace = the retained mass/residue g; reduce = the quotient that would discard it;")
    print(f"      never-discard-residue keeps g, so reduce is a split-idempotent (lossless) retraction.")
    return ok_value and ok_mass and saw_drop and ok_retract


if __name__ == "__main__":
    print("Q in the SWAR lanes, and how Q + traces relate to them.\n")
    w1 = swar_q_multiply()
    w2 = nedge_lift_on_pairs()
    w3 = reduce_is_mass_drop()
    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the SWAR lane carries Q = (num,den) = the el-atlas nedge")
    print(f"  (E+,E-) carrier; Q-multiply rides one lane-wise bignum pass; the lift (G_OR/G_NOT/G_AND)")
    print(f"  holds on the lane pair; and reduce is a mass-lowering retraction whose discarded cofactor")
    print(f"  IS the trace's residue. 'The quotient erases the mass the pair keeps' (el-atlas) = 'never")
    print(f"  discard residue' (substrate): the SAME fact. The trace is the generator the lane windows.")
