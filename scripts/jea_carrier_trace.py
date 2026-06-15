#!/usr/bin/env python3
"""jea_carrier_trace.py — U4: the TRACE-WINDOW lane on GPU = the value-window's discarded gcd residue.

jea_trace_window proved the trace-window carrier's properties host-side (canonical-by-construction,
compare-by-prefix, round-trip=reduce, the value<->trace Pareto). U4 realizes it as an ON-GPU lane and ties
it to the evaluator, closing the value<->trace DUAL:

  The eager value-window (M2c/strat) runs Euclid to get the gcd and EMITS the reduced (num/g, den/g) --
  but it THROWS AWAY the quotient sequence. That quotient sequence IS the continued fraction = the
  canonical CF/EEA shape. So the trace-window lane is precisely the residue the value-window discards
  ([[feedback_never_discard_residue]]) -- captured at ZERO extra Euclid cost (the SAME loop). The
  value-window keeps (num,den) and discards the CF; the trace-window keeps the CF and recovers (num,den)
  by the fold. Two dual projections of one rational; the round-trip between them is reduce (a retraction).

On-GPU: cf_window runs the Euclid window per lane and CAPTURES the quotients (the value-window's gcd
captures only the step COUNT and the final gcd). Canonicality is then FREE -- scale-free CF, compare by
prefix, no reduce, no cross-multiply -- which is the corner lazy value-window (fast but non-canonical)
cannot reach. Reuses jea_trace_window's from_cf / cf_less (the host fold + prefix order).

Witnesses (each [W]):
1. CANONICAL ON GPU: GPU-CF(p,q) == GPU-CF(s*p, s*q) (scale-free) -- equal value <=> equal CF, NO reduce.
2. RESIDUE-OF-GCD (free): the captured CF == host to_cf, and its length == the Euclid step count the
   value-window's gcd already runs -- so the trace lane is the discarded residue, at zero extra cost.
3. ROUND-TRIP = REDUCE: from_cf(GPU-CF) == reduce(p,q) (the value<->trace retraction; the dual closes).
4. COMPARE-BY-PREFIX: cf_less on GPU-CFs == true rational order -- canonicality+comparison with no
   value materialization and no cross-multiply (the trace-window's win over the value-window).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
from math import gcd
from jea_trace_window import to_cf, from_cf, cf_less

_SRC = r'''
extern "C" __global__
void cf_window(const long long* P, const long long* Q, long long* cf, int* clen, int n, int maxcf)
{
    int i = blockIdx.x*blockDim.x + threadIdx.x; if (i >= n) return;
    long long p = P[i], q = Q[i]; int k = 0;          // positive rationals: floor div = trunc
    while (q && k < maxcf) {                            // the SAME Euclid the gcd runs -- but KEEP the quotients
        long long a = p / q; cf[i*maxcf + k] = a;       // a = the CF coefficient = the discarded residue
        long long t = p - a*q; p = q; q = t; k++;
    }
    clen[i] = k;                                        // == the value-window gcd's step count
}
'''
_kern = cp.RawKernel(_SRC, "cf_window")


def gpu_cf(P, Q, maxcf=80):
    n = len(P)
    dP = cp.asarray(P, cp.int64); dQ = cp.asarray(Q, cp.int64)
    cf = cp.zeros(n * maxcf, cp.int64); clen = cp.zeros(n, cp.int32)
    _kern(((n + 255) // 256,), (256,), (dP, dQ, cf, clen, np.int32(n), np.int32(maxcf)))
    cf = cf.get().reshape(n, maxcf); clen = clen.get()
    return [list(cf[i, :clen[i]]) for i in range(n)], clen


if __name__ == "__main__":
    n = 50_000
    rng = np.random.default_rng(0)
    P = [int(x) for x in rng.integers(1, 1 << 28, n)]
    Q = [int(x) for x in rng.integers(1, 1 << 28, n)]
    S = [int(x) for x in rng.integers(2, 16, n)]
    maxcf = 80
    cfs, clen = gpu_cf(P, Q, maxcf)
    cfs_scaled, _ = gpu_cf([S[i] * P[i] for i in range(n)], [S[i] * Q[i] for i in range(n)], maxcf)
    assert clen.max() < maxcf, "CF truncated -- raise maxcf"

    # 1. canonical on GPU (scale-free)
    w1 = all(cfs[i] == cfs_scaled[i] for i in range(n))
    # 2. residue-of-gcd: captured CF == host to_cf, length == Euclid step count (the gcd work)
    w2 = all(cfs[i] == to_cf(P[i], Q[i]) and clen[i] == len(to_cf(P[i], Q[i])) for i in range(n))
    # 3. round-trip == reduce
    w3 = True
    for i in range(n):
        h, k = from_cf(cfs[i]); g = gcd(P[i], Q[i])
        if (h, k) != (P[i] // g, Q[i] // g): w3 = False; break
    # 4. compare-by-prefix == true order (no cross-multiply)
    w4 = True
    for _ in range(20000):
        i, j = int(rng.integers(0, n)), int(rng.integers(0, n))
        if cf_less(cfs[i], cfs[j]) != (Fraction(P[i], Q[i]) < Fraction(P[j], Q[j])): w4 = False; break
    # duality check: trace->value->trace identity too (both round-trips close)
    dual = all(to_cf(*from_cf(cfs[i])) == cfs[i] for i in range(0, n, 50))

    print(f"trace-window lane on GPU — {n} rationals, max CF length {int(clen.max())} (avg {clen.mean():.1f})\n")
    print(f"1. CANONICAL ON GPU (CF(p,q)==CF(sp,sq), scale-free, no reduce): {w1}")
    print(f"2. RESIDUE-OF-GCD (captured CF == to_cf; len == Euclid step count = the gcd work, kept free): {w2}")
    print(f"3. ROUND-TRIP = REDUCE (from_cf(GPU-CF) == reduce(p,q); the value<->trace retraction): {w3}")
    print(f"4. COMPARE-BY-PREFIX (cf_less == true order, no value materialization / cross-multiply): {w4}")
    print(f"   (duality: trace->value->trace identity also holds: {dual})")
    ok = w1 and w2 and w3 and w4 and dual
    print(f"\n  {'PASS' if ok else 'FAIL'} — U4: the value<->trace DUAL is realized. The trace-window lane is")
    print(f"  the value-window's DISCARDED gcd residue (same Euclid, quotients kept), computed on GPU:")
    print(f"  canonical by construction (no reduce), compare-by-prefix (no cross-multiply) -- the corner the")
    print(f"  lazy value-window (fast, non-canonical) cannot reach. The round-trip between the lanes IS")
    print(f"  reduce. NEXT: Gosper Mobius arithmetic on the CF lane (the trace-window's expensive arm = the")
    print(f"  other side of the value<->trace Pareto, jea_trace_window's bridge null).")
