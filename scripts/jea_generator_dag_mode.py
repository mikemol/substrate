#!/usr/bin/env python3
"""jea_generator_dag_mode.py — INTEGRATION: M2d's eager/lazy reduction-mode knob, added to the
production cooperative-generator evaluator (jea_generator_dag).

jea_generator_dag's controller steers only K (the gcd-window size); reduction is always EAGER (every
combine runs the gcd window to b==0 and emits fully reduced). This variant adds the value-window<->
trace-window PARETO as a second control knob, MODE, alongside K -- the genuinely-new piece from M2d
(scripts/jea_m2_dispatch.py), now living in the production architecture instead of a synthetic-DAG
reference build:
  * MODE=1 EAGER : windowed gcd to b==0, emit reduced (canonical, gcd==1) -- the original behavior.
  * MODE=0 LAZY  : skip the gcd, emit UNREDUCED -- high throughput, non-canonical (reduce-on-demand).
Both EXACT (an unreduced fraction is the right rational; reduce at readout recovers canonical).

Made MATURE (not a silent-overflow stub): overflow is PREDICTED from operand bit-widths before the
multiply (the SWAR W>=2L lane-spacing rule applied dynamically -- a k-bit times an m-bit value is
< 2^(k+m), so it fits the u64 lane iff the widths sum within it). Provably-safe -> native u64, overflow
impossible, no __int128. Otherwise -> the wide path computes in __int128 and DETECTS exactly: a product
that won't fit u64 is REDUCED WHEN THE LANE FORCES it ("reduce only when forced"); if even the reduced
value won't fit, the node ESCALATES (flag, never wrapped) and poison-propagates -- escalate-don't-
truncate, in the cooperative readiness gate. Predict (cheap __clzll) beats detect (compute-wide-then-
check): know before you spend. Same branchless monotonic body as jea_generator_dag otherwise.

The controller still relaxes K (for eager); MODE is read live from its own control slot (the oracle sets
it, the M2d way, from the workload's canonicality-demand C). run() demonstrates the Pareto on a real
tree; jea_agda_dispatch drives an Agda-emitted term through this under oracle control.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from math import gcd
from fractions import Fraction
import jea_core
from jea_generator_dag import build_dag                       # reuse the random-tree builder

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
__device__ __forceinline__ int bl(u64 x){ return x ? 64 - __clzll(x) : 0; }   // bit-width (0 for 0)
extern "C" __global__
void generator_dag_mode(
    volatile int* Kbuf, volatile int* obsmax, volatile int* pending, volatile int* mode,
    u64* vN, u64* vD, const int* lch, const int* rch, const int* op,
    volatile int* ready, int* initf, u64* a, u64* b, u64* naN, u64* naD, int* steps, int* esc,
    const int* own, const int* own_count,
    long long* cycles_by, volatile int* err,
    int nblocks, int maxown, long long maxcyc)
{
    if (threadIdx.x != 0) return;
    const u128 TWO64 = ((u128)1) << 64;                       // a value fits the u64 lane iff < 2^64
    int w = blockIdx.x; int oc = own_count[w]; long long c = 0;
    while (*pending > 0) {
        int est = 0;
        if (oc > 0) {
            int slot = own[w*maxown + (int)(c % oc)];
            int Lc = lch[slot], Rc = rch[slot];
            int active = ready[Lc] & ready[Rc] & (1 - ready[slot]);
            if (active & (1 - initf[slot])) {                // first active touch = the combine
                if (esc[Lc] | esc[Rc]) {                     // poison-propagate
                    esc[slot]=1; naN[slot]=0; naD[slot]=1; a[slot]=0; b[slot]=0;
                } else {
                    u64 nl=vN[Lc], dl=vD[Lc], nr=vN[Rc], dr=vD[Rc]; int mul=(op[slot]==1);
                    // PREDICT overflow from operand bit-widths = the SWAR W>=2L lane-spacing rule applied
                    // DYNAMICALLY: a k-bit times an m-bit value is < 2^(k+m), so the product fits the u64
                    // lane when the widths sum within it (mul: <=64; add: each product <=63 so their sum
                    // <2^64, and dl*dr<=64). When safe, native u64 CANNOT overflow -- no __int128, no check.
                    int bnl=bl(nl), bdl=bl(dl), bnr=bl(nr), bdr=bl(dr);
                    int safe = mul ? (bnl+bnr<=64 && bdl+bdr<=64)
                                   : (bnl+bdr<=63 && bnr+bdl<=63 && bdl+bdr<=64);
                    if (safe) {                              // FAST PATH: overflow impossible by construction
                        u64 na = mul ? (nl*nr) : (nl*dr + nr*dl); u64 D = dl*dr;
                        naN[slot]=na; naD[slot]=D; a[slot]=na; b[slot]=D;
                    } else {                                 // SLOW PATH: wide compute + EXACT detect + escalate
                        u128 na = mul ? ((u128)nl*nr) : ((u128)nl*dr + (u128)nr*dl); u128 D = (u128)dl*dr;
                        if (na >= TWO64 || D >= TWO64) {      // reduce WHEN THE LANE FORCES it
                            u128 x=na, y=D; while (y){ u128 t=x%y; x=y; y=t; } u128 g=x?x:1;
                            u128 rn=na/g, rd=D/g;
                            if (rn>=TWO64 || rd>=TWO64){ esc[slot]=1; naN[slot]=0; naD[slot]=1; } // ESCALATE
                            else { naN[slot]=(u64)rn; naD[slot]=(u64)rd; }                        // forced-reduced
                            a[slot]=0; b[slot]=0;             // a==b==0 marks "already final"
                        } else {
                            naN[slot]=(u64)na; naD[slot]=(u64)D; a[slot]=(u64)na; b[slot]=(u64)D;
                        }
                    }
                }
                initf[slot]=1;
            }
            int md=*mode, K=*Kbuf, nowdone=0, st=steps[slot];
            u64 aa=a[slot], bb=b[slot];
            if (active & initf[slot]) {
                if (esc[slot])              { vN[slot]=0; vD[slot]=1; nowdone=1; }            // escalated sentinel
                else if (aa==0 & bb==0)     { vN[slot]=naN[slot]; vD[slot]=naD[slot]; nowdone=1; } // forced-reduced
                else if (md==1) {                                                            // EAGER windowed gcd
                    for (int j=0;j<K;j++){ if (bb!=0){ u64 r=aa%bb; aa=bb; bb=r; st++; } }
                    a[slot]=aa; b[slot]=bb; steps[slot]=st;
                    if (bb==0){ u64 g=aa?aa:1ULL; vN[slot]=naN[slot]/g; vD[slot]=naD[slot]/g; nowdone=1; } // reduced
                } else {                                                                     // LAZY: emit unreduced
                    vN[slot]=naN[slot]; vD[slot]=naD[slot]; nowdone=1;
                }
            }
            int wasready=ready[slot]; ready[slot]=wasready|nowdone;
            atomicSub((int*)pending, ready[slot]-wasready);
            est = nowdone ? (st>0?st:1) : 0;
        }
        atomicMax((int*)obsmax, est);
        *Kbuf = relax_q(*Kbuf, *obsmax);
        __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
    cycles_by[w] = c;
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_dag_mode", int128=True)
residency = jea_core.residency


def run_g_mode(g, mode, K0=4, maxcyc=4_000_000):
    """Evaluate a DAG dict under the given reduction MODE (1=eager, 0=lazy) on the cooperative
    generators. Returns the root (possibly UNREDUCED in lazy mode -- reduce at readout for canonical),
    the measured gcd-work, the non-canonical count, and the escalate flags."""
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = min(20, nsm)
    N = g["N"]; L = g["L"]
    per_sm, max_resident, _n, regs = residency(_kern, 32)
    assert nblocks <= max_resident, f"residency: {nblocks} launched > {max_resident} resident"

    vN = cp.asarray(g["vN"], cp.uint64); vD = cp.asarray(g["vD"], cp.uint64)
    lch = cp.asarray(g["lch"], cp.int32); rch = cp.asarray(g["rch"], cp.int32); op = cp.asarray(g["op"], cp.int32)
    ready = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    initf = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    a = cp.zeros(N, cp.uint64); b = cp.zeros(N, cp.uint64)
    naN = cp.zeros(N, cp.uint64); naD = cp.zeros(N, cp.uint64); steps = cp.zeros(N, cp.int32); esc = cp.zeros(N, cp.int32)
    combines = list(range(L, N))
    per_block = [[] for _ in range(nblocks)]
    for k, ci in enumerate(combines): per_block[k % nblocks].append(ci)
    maxown = max((len(x) for x in per_block), default=1) or 1
    own = np.full((nblocks, maxown), -1, np.int32)
    for w in range(nblocks):
        for j, ci in enumerate(per_block[w]): own[w, j] = ci
    own_count = cp.asarray([len(x) for x in per_block], cp.int32); own = cp.asarray(own.ravel(), cp.int32)

    Kbuf = cp.full(1, K0, cp.int32); obsmax = cp.zeros(1, cp.int32); modebuf = cp.full(1, mode, cp.int32)
    pending = cp.full(1, len(combines), cp.int32); cyc = cp.zeros(nblocks, cp.int64); err = cp.zeros(1, cp.int32)
    _kern((nblocks,), (32,),
          (Kbuf, obsmax, pending, modebuf, vN, vD, lch, rch, op, ready, initf, a, b, naN, naD, steps, esc,
           own, own_count, cyc, err, np.int32(nblocks), np.int32(maxown), np.int64(maxcyc)))
    cp.cuda.Stream.null.synchronize()
    root = g["root"]
    gn, gd, ge = vN.get(), vD.get(), esc.get()
    live_c = ge[L:] == 0                                       # over COMBINES only: the MODE knob acts on
    noncanon = int((np.gcd(gn[L:][live_c], gd[L:][live_c]) != 1).sum())  # combines, not the (maybe-unreduced) leaves
    return dict(rn=int(gn[root]), rd=int(gd[root]), esc_root=int(ge[root]), gwork=int(steps.get().sum()),
                noncanon=noncanon, nesc=int(ge.sum()), pending=int(pending.get()[0]), err=int(err.get()[0]),
                Kfinal=int(Kbuf.get()[0]), obsmax=int(obsmax.get()[0]), regs=regs, launched=nblocks)


def oracle_decide(eager, lazy, C, W_T=1.0, W_C=1.0):
    """The M2d nedge oracle: pick MODE from measured telemetry + the workload's canonicality-demand C.
    cost = throughput-resistance (gcd-work) + C-weighted canonicality-resistance (non-canonical count);
    geodesic/min-dissipation settle = argmin. Crossover f*=C* is the value<->trace bridge-null."""
    cost = lambda r, C: W_T * r["gwork"] + C * W_C * r["noncanon"]
    fstar = (W_T * (eager["gwork"] - lazy["gwork"])) / (W_C * max(lazy["noncanon"], 1))
    chosen = 1 if cost(eager, C) <= cost(lazy, C) else 0
    return chosen, fstar


if __name__ == "__main__":
    g = build_dag(L=128, seed=3); truth = g["truth"]          # L=128 fits u64; L>=256 overflows -> the 128-bit carrier's job
    eager = run_g_mode(g, 1); lazy = run_g_mode(g, 0)
    e_ok = (Fraction(eager["rn"], eager["rd"]) == truth) and eager["err"] == 0 and eager["pending"] == 0
    l_ok = (Fraction(lazy["rn"], lazy["rd"]) == truth) and lazy["err"] == 0 and lazy["pending"] == 0  # reduce-at-readout
    fstar = oracle_decide(eager, lazy, 0)[1]
    dec_lo, _ = oracle_decide(eager, lazy, 0.0); dec_hi, _ = oracle_decide(eager, lazy, max(2 * fstar, 1.0))

    print(f"INTEGRATION: eager/lazy MODE knob in the production cooperative evaluator — {g['L']} leaves, "
          f"{g['N']-g['L']} combines, {eager['launched']} blocks ({eager['regs']} regs)\n")
    print(f"  EAGER: gcd-work={eager['gwork']:>7}  non-canonical={eager['noncanon']:>4}  root={eager['rn']}/{eager['rd']}  exact={e_ok}")
    print(f"  LAZY : gcd-work={lazy['gwork']:>7}  non-canonical={lazy['noncanon']:>4}  root(unreduced)={lazy['rn']}/{lazy['rd']}  exact(reduced)={l_ok}")
    print(f"  oracle f* (value<->trace bridge-null) C*={fstar:.4f};  decide(C=0)={'eager' if dec_lo else 'lazy'}, "
          f"decide(C={max(2*fstar,1.0):.2f})={'eager' if dec_hi else 'lazy'}")
    w_pareto = (lazy["gwork"] < eager["gwork"]) and (lazy["noncanon"] > 0) and (eager["noncanon"] == 0)
    w_flip = (dec_lo == 0) and (dec_hi == 1)
    ok = e_ok and l_ok and w_pareto and w_flip
    print(f"\n  exact both modes={e_ok and l_ok}  Pareto real={w_pareto}  oracle flips across f*={w_flip}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the M2d eager/lazy reduction-mode Pareto now lives in the PRODUCTION")
    print(f"  cooperative-generator evaluator (alongside the K-window control), exact both ways, escalate-")
    print(f"  don't-truncate preserved. jea_agda_dispatch drives an Agda-emitted term through this.")
