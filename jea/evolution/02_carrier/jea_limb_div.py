#!/usr/bin/env python3
"""jea_limb_div.py — U5: byte-limb DIVISION -> Q reduce (gcd + canonical) at arbitrary precision.

jea_limb_gpu gave the byte-limb carrier multiply (dp4a) + add + parallel carry, so U3 could DELIVER
arbitrary-precision ARITHMETIC on escalation. But Q reduce / canonicalization needs gcd, and gcd needs
DIVISION (the Euclid remainder) -- which the carrier lacked. U5 adds it, completing APEX-2: the full Q
carrier (arithmetic AND reduce) at arbitrary precision, so escalate-don't-truncate delivers the CANONICAL
value too, not just the arithmetic.

Division here is RESTORING DIVISION BY DOUBLING (radix-2 long division): build b, 2b, 4b, ... (each a
gpu_add doubling) up to a, then subtract greedily from the top -- a correct, exact division algorithm
reusing the existing byte-limb add/sub. Grown for CORRECTNESS first (charter ethos); the sub-quadratic /
parallel division (Knuth-D, Newton-Raphson reciprocal) is the named perf follow-on, exactly as the carry
went serial -> parallel-prefix. The Euclid quotients this produces are also the continued fraction, so
this extends U4's trace-window (reduce = to_cf then from_cf) to arbitrary precision.

Witnesses (each [W]):
1. DIVMOD EXACT: limb_divmod(a,b) == (a//b, a%b) vs Python, including >128-bit operands.
2. GCD EXACT: limb_gcd(a,b) == math.gcd, big operands.
3. Q REDUCE AT ARBITRARY PRECISION: limb_qreduce(k*p, k*q) == reduced (p,q), with k*p,k*q >> 2^128
   (the reduce-delivery escalate-don't-truncate was missing -- U3 delivered arithmetic, U5 delivers reduce).
4. CF AT ARBITRARY PRECISION: the Euclid quotients == host to_cf -- the U4 trace-window now past 128 bits.
"""
# --- jea-evolution rung bootstrap: jea/ foundation + sibling rungs on the path (see 00_SYLLABUS.md) ---
import os as _os, sys as _sys, glob as _glob
_EVO = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))   # .../jea/evolution
_sys.path[:0] = [_os.path.dirname(_EVO), *sorted(_glob.glob(_os.path.join(_EVO, "*", "")))]
# --- end bootstrap ---
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from math import gcd
from fractions import Fraction
from jea_limb_gpu import gpu_add, to_limbs, from_limbs
from jea_trace_window import to_cf


def _trim(x):
    nz = cp.nonzero(x)[0]
    return x[:int(nz[-1]) + 1] if nz.size else cp.zeros(1, cp.uint8)
def _is_zero(x): return not bool((x != 0).any())
def lcmp(a, b):                                              # -1/0/1 on byte-limb magnitudes
    a, b = _trim(a), _trim(b)
    if a.size != b.size: return -1 if a.size < b.size else 1
    d = a.astype(cp.int64) - b.astype(cp.int64); nz = cp.nonzero(d)[0]
    return 0 if nz.size == 0 else (-1 if int(d[int(nz[-1])]) < 0 else 1)
def lsub(a, b):                                              # a - b (require a >= b), parallel borrow
    r = cp.zeros(int(a.size), cp.int64); r[:] = a.astype(cp.int64); r[:b.size] -= b.astype(cp.int64)
    while True:
        neg = r < 0
        if not bool(neg.any()): break
        r = r + neg.astype(cp.int64) * 256                   # +256 where borrowed
        r[1:] = r[1:] - neg[:-1].astype(cp.int64)            # borrow 1 from the next limb
    return _trim(r.astype(cp.uint8))
def ldouble(x): return gpu_add(x, x)                         # 2x via the byte-limb adder


def limb_divmod(a, b):
    """byte-limb (q, r) with a = q*b + r, 0 <= r < b. q returned as a Python int (a CF coefficient),
    r as byte-limbs. Restoring division by doubling: subtract the largest fitting 2^k * b."""
    a = cp.asarray(a); b = cp.asarray(b)
    if _is_zero(b): raise ZeroDivisionError
    if lcmp(a, b) < 0: return 0, _trim(a)
    doubles = [_trim(b)]
    while lcmp(ldouble(doubles[-1]), a) <= 0: doubles.append(ldouble(doubles[-1]))
    q = 0; r = _trim(a)
    for k in range(len(doubles) - 1, -1, -1):
        if lcmp(doubles[k], r) <= 0:
            r = lsub(r, doubles[k]); q += (1 << k)
    return q, r


def limb_gcd(a, b):
    a, b = _trim(cp.asarray(a)), _trim(cp.asarray(b))
    while not _is_zero(b):
        _, r = limb_divmod(a, b); a, b = b, r
    return a


def limb_qreduce(num, den):
    """(num/g, den/g) as byte-limbs, g = gcd -- canonical, at arbitrary precision."""
    g = limb_gcd(num, den)
    qn, rn = limb_divmod(num, g); qd, rd = limb_divmod(den, g)
    assert _is_zero(rn) and _is_zero(rd), "gcd must divide exactly"
    return to_limbs(qn), to_limbs(qd)


def limb_to_cf(p, q):                                        # CF via repeated byte-limb divmod = U4 at any size
    P, Q = cp.asarray(to_limbs(p)), cp.asarray(to_limbs(q)); cf = []
    while not _is_zero(Q):
        a, r = limb_divmod(P, Q); cf.append(a); P, Q = Q, r
    return cf


if __name__ == "__main__":
    L = lambda v: cp.asarray(to_limbs(v))
    rng = np.random.default_rng(0)
    big = lambda b: int.from_bytes(bytes(rng.integers(0, 256, b // 8, dtype=np.uint8).tolist()), "little") | (1 << (b - 1))

    # 1. divmod exact (incl. >128 bit)
    w1 = True; mx1 = 0
    for _ in range(20):
        a = big(int(rng.integers(40, 400))); b = big(int(rng.integers(20, 200)))
        if a < b: a, b = b, a
        q, r = limb_divmod(L(a), L(b)); mx1 = max(mx1, a.bit_length())
        if q != a // b or from_limbs(r) != a % b: w1 = False; break
    # 2. gcd exact
    w2 = True
    for _ in range(20):
        a = big(int(rng.integers(40, 300))); b = big(int(rng.integers(40, 300)))
        if from_limbs(limb_gcd(L(a), L(b))) != gcd(a, b): w2 = False; break
    # 3. Q reduce at arbitrary precision: (k*p)/(k*q) -> (p/g', q/g') reduced, k*p >> 2^128
    w3 = True; mx3 = 0
    for _ in range(12):
        p = big(int(rng.integers(60, 250))); q = big(int(rng.integers(60, 250))); k = big(int(rng.integers(80, 200)))
        rn, rd = limb_qreduce(L(k * p), L(k * q)); mx3 = max(mx3, (k * p).bit_length())
        f = Fraction(k * p, k * q)
        if from_limbs(rn) != f.numerator or from_limbs(rd) != f.denominator: w3 = False; break
    # 4. CF at arbitrary precision == host to_cf
    w4 = True
    for _ in range(8):
        p = big(int(rng.integers(60, 220))); q = big(int(rng.integers(60, 220)))
        if limb_to_cf(p, q) != to_cf(p, q): w4 = False; break

    print(f"byte-limb division -> Q reduce at arbitrary precision\n")
    print(f"1. DIVMOD EXACT vs Python (operands to {mx1} bits): {w1}")
    print(f"2. GCD EXACT vs math.gcd (big operands): {w2}")
    print(f"3. Q REDUCE AT ARBITRARY PRECISION (k*p/k*q -> reduced, to {mx3} bits >> 2^128): {w3}")
    print(f"4. CF AT ARBITRARY PRECISION (Euclid quotients == host to_cf; U4 past 128b): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — U5: byte-limb DIVISION via restoring-doubling (reusing the byte-limb")
    print(f"  adder), exact, completes APEX-2's carrier ops. Q REDUCE / canonicalization now DELIVERS at")
    print(f"  arbitrary precision (escalate-don't-truncate's canonical arm, was missing), and U4's trace-")
    print(f"  window extends past 128 bits. NEXT (perf): sub-quadratic division (Knuth-D / Newton reciprocal)")
    print(f"  + parallelize across limbs -- as the carry went serial -> parallel-prefix.")
