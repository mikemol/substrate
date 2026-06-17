#!/usr/bin/env python3
"""jea_m2_qcarrier.py — M2c: the real Q carrier + fused gcd-window, escalate-don't-truncate.

M2b evaluated an SPPF DAG over int64 with silent wrap. M2c swaps the carrier for the substrate's actual
arithmetic: Q = (num, den), den>0, kept REDUCED. Each (+)/(*) is computed in __int128 then canonicalized
by an on-device Euclid loop -- the FUSED GCD WINDOW (a bounded walk: finite-window-constructive, not an
unbounded decision). The window DEPTH (Euclid step count) varies per node = heterogeneous depths; the
data-driven sweep absorbs them (a deep-gcd node just iterates more inside its claim; other threads move
on). This is the "exactness/canonicality" arm of the value-window<->trace-window Pareto.

ESCALATE-DON'T-TRUNCATE (the substrate's no-silent-quotient law): after reduction, if |num| or den would
not fit the int64 lane, the node is FLAGGED (esc=1), never wrapped. Escalation POISON-PROPAGATES: a node
consuming an escalated child escalates too (its exact value is unrepresentable in this carrier -> the
honest move is "escalate the carrier," not emit a wrong number). The next carrier up (bignum/multi-limb)
is where esc nodes would be retried; M2c proves the boundary is detected exactly, never crossed silently.

Witnesses (each [W]):
1. EXACT: every NON-escalated node's (num,den) == the host Fraction reference (exact rationals). No wrap.
2. ESCALATE-CORRECT (no silent truncation): the device esc-set == exactly the unrepresentable set
   (poison-propagated). The lane boundary is detected precisely -- never a silently-wrong answer.
3. CANONICAL: every non-escalated result is fully reduced -- gcd(|num|,den)==1 and den>0.
4. HETEROGENEOUS FUSION: per-node gcd-window depths VARY (min/max/mean reported); one persistent launch
   absorbs the spread (the sweep load-balances deep vs shallow reductions).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
from fractions import Fraction
import numpy as np, cupy as cp

SRC = r"""
typedef long long i64;
extern "C" __global__ void qeval(const int* op, const i64* lnum, const i64* lden,
                                 const int* c0, const int* c1, i64* num, i64* den, int* esc, int* steps,
                                 volatile int* status, int* completed, volatile int* stop, int n) {
    const __int128 LIM = ((__int128)1) << 62;
    int stride = gridDim.x * blockDim.x, t0 = blockIdx.x * blockDim.x + threadIdx.x;
    long long sweeps = 0, cap = (long long)n + 16;
    while (*completed < n && sweeps++ < cap) {
        if (*stop) return;
        for (int i = t0; i < n; i += stride) {
            if (status[i] != 0) continue;
            int o = op[i]; bool ready = false; int e = 0, st = 0; __int128 N = 0, D = 1;
            if (o == 0) { N = lnum[i]; D = lden[i]; ready = true; }            // gen leaf (pre-reduced)
            else if (status[c0[i]] == 1 && status[c1[i]] == 1) {               // children DONE?
                ready = true;
                if (esc[c0[i]] || esc[c1[i]]) { e = 1; N = 0; D = 1; }         // poison-propagate
                else {
                    __int128 xn = num[c0[i]], xd = den[c0[i]], yn = num[c1[i]], yd = den[c1[i]];
                    if (o == 1) { N = xn * yd + yn * xd; D = xd * yd; }        // (+)
                    else        { N = xn * yn;            D = xd * yd; }        // (*)
                    __int128 a = N < 0 ? -N : N, b = D;                        // fused gcd window (Euclid)
                    while (b) { __int128 t = a % b; a = b; b = t; st++; }
                    __int128 g = a;                                            // g>0 since D>0
                    N /= g; D /= g;
                    __int128 an = N < 0 ? -N : N;
                    if (an >= LIM || D >= LIM) { e = 1; N = 0; D = 1; }        // ESCALATE, don't wrap
                }
            }
            if (ready && atomicCAS((int*)&status[i], 0, 2) == 0) {
                num[i] = (i64)N; den[i] = (i64)D; esc[i] = e; steps[i] = st;
                __threadfence(); status[i] = 1; __threadfence(); atomicAdd(completed, 1);
            }
        }
        __threadfence();
    }
}
"""

if __name__ == "__main__":
    ker = cp.RawKernel(SRC, "qeval", options=("--device-int128",))            # 128-bit intermediates (overflow detection)
    W, D = 1200, 45                                                            # layered DAG: depth forces some escalation
    n = W * D
    rng = np.random.default_rng(0)
    op = np.zeros(n, np.int32); lnum = np.zeros(n, np.int64); lden = np.ones(n, np.int64)
    c0 = np.zeros(n, np.int32); c1 = np.zeros(n, np.int32)
    dens = np.array([1, 2, 3, 5], np.int64)
    for i in range(W):                                                         # layer 0 = leaves (small reduced Q)
        f = Fraction(int(rng.integers(-2, 3)), int(rng.choice(dens)))
        lnum[i], lden[i] = f.numerator, f.denominator
    for k in range(1, D):                                                      # layers 1..D-1
        lo, hi = k * W, (k + 1) * W
        op[lo:hi] = rng.integers(1, 3, W)                                      # 1=+, 2=*
        c0[lo:hi] = rng.integers(0, k * W, W); c1[lo:hi] = rng.integers(0, k * W, W)  # children strictly earlier

    # append a distinct-prime multiplicative chain: den -> primorial defeats reduction, FORCES escalation
    # (around the 16th prime primorial exceeds 2^62) and exercises poison-propagation down the chain.
    primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
    ch_op, ch_ln, ch_ld, ch_c0, ch_c1 = [0], [1], [primes[0]], [0], [0]       # leaf 1/2
    prev, idx = n, n + 1
    for j in range(1, len(primes)):
        ch_op += [0, 2]; ch_ln += [1, 0]; ch_ld += [primes[j], 1]             # leaf 1/p_j ; mul(prev, leaf)
        ch_c0 += [0, prev]; ch_c1 += [0, idx]; prev = idx + 1; idx += 2
    op  = np.concatenate([op,  np.array(ch_op, np.int32)])
    lnum = np.concatenate([lnum, np.array(ch_ln, np.int64)]); lden = np.concatenate([lden, np.array(ch_ld, np.int64)])
    c0  = np.concatenate([c0,  np.array(ch_c0, np.int32)]); c1 = np.concatenate([c1, np.array(ch_c1, np.int32)])
    n = len(op)

    LIM = 1 << 62
    fits = lambda fr: abs(fr.numerator) < LIM and fr.denominator < LIM
    val = [None] * n; esc_ref = np.zeros(n, np.int32)                          # host reference + poison-propagation
    for i in range(n):
        if op[i] == 0:
            val[i] = Fraction(int(lnum[i]), int(lden[i])); esc_ref[i] = 0 if fits(val[i]) else 1
        else:
            a, b = int(c0[i]), int(c1[i])
            if esc_ref[a] or esc_ref[b]: esc_ref[i] = 1; val[i] = Fraction(0); continue
            val[i] = val[a] + val[b] if op[i] == 1 else val[a] * val[b]
            esc_ref[i] = 0 if fits(val[i]) else 1
    ref_num = np.array([0 if esc_ref[i] else val[i].numerator for i in range(n)], np.int64)
    ref_den = np.array([1 if esc_ref[i] else val[i].denominator for i in range(n)], np.int64)

    d = lambda x: cp.asarray(x)
    num = cp.zeros(n, cp.int64); den = cp.ones(n, cp.int64); esc = cp.zeros(n, cp.int32); steps = cp.zeros(n, cp.int32)
    status = cp.zeros(n, cp.int32); completed = cp.zeros(1, cp.int32); stop = cp.zeros(1, cp.int32)
    blocks, threads = 64, 128
    print(f"evaluating a Q-carrier SPPF DAG of {n} nodes (depth {D}) via persistent data-driven sweep ({blocks}x{threads})\n")
    ker((blocks,), (threads,), (d(op), d(lnum), d(lden), d(c0), d(c1), num, den, esc, steps,
                                status, completed, stop, np.int32(n)))
    cp.cuda.Stream.null.synchronize()
    gn, gd, ge, gs = num.get(), den.get(), esc.get(), steps.get(); comp = int(completed.get()[0])

    live = ge == 0                                                             # non-escalated mask
    w1 = bool((gn[live] == ref_num[live]).all() and (gd[live] == ref_den[live]).all())
    w2 = bool((ge == esc_ref).all())
    g = np.gcd(np.abs(gn[live]), gd[live])
    w3 = bool((g == 1).all() and (gd[live] > 0).all())
    internal = (op != 0) & live
    sd = gs[internal]; w4 = bool(sd.size > 0 and sd.min() != sd.max()) and comp == n
    nesc = int(ge.sum())
    print(f"1. EXACT: all {int(live.sum())} non-escalated nodes (num,den) == host Fraction reference {w1}")
    print(f"2. ESCALATE-CORRECT: device esc-set == unrepresentable set exactly ({nesc} escalated, no wrap) {w2}")
    print(f"3. CANONICAL: every non-escalated result fully reduced gcd==1, den>0 {w3}")
    print(f"4. HETEROGENEOUS FUSION: gcd-window depth min={int(sd.min())} max={int(sd.max())} "
          f"mean={sd.mean():.2f}; completed={comp}/{n}; one launch {w4}")

    ok = w1 and w2 and w3 and w4
    print(f"\nM2c Q-CARRIER: exact {w1}; escalate-correct {w2}; canonical {w3}; hetero-fusion {w4}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the JEA evaluator now carries EXACT rationals: Q=(num,den)")
    print(f"  reduced by an on-device fused gcd-window (heterogeneous depths absorbed by the sweep), with")
    print(f"  ESCALATE-DON'T-TRUNCATE -- {nesc} lane-overflowing nodes flagged exactly, never silently")
    print(f"  wrapped. Never-discard-residue at the carrier level. Folds into M2d (the nedge oracle steers")
    print(f"  the sweep + the value-window<->trace-window Pareto choice).")
