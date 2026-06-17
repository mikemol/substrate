#!/usr/bin/env python3
"""jea_generator_coop.py — increment (5): BRANCHLESS cooperative generators. The completion
of role-as-data — there is no role distinction left at all.

Earlier draft branched: `if (have work) chew; else adopt-controller-via-token`. That is a
data-dependent control-flow branch plus an atomicCAS lock — both violate the branchless
charter. The fix (user): every generator just DOES THE THING every cycle. It is all async and
MONOTONIC anyway, so the part with nothing to do is a NO-OP, not a branch.

So every block, every cycle, UNCONDITIONALLY does both:
  * WORK  — one gcd K-window on a round-robin node slot. The step `if(bb!=0)` is inherent
            predication: a converged node is a no-op, no skip-branch, no ring/empty-check.
  * CONTROL — atomicMax(obsmax, my_depth) (race-free, MONOTONIC up) then relax K off it. No
            token; concurrent K writes are benign (K is a HINT; exactness is K-independent).
Bookkeeping stays branchless via monotonicity:
  * atomicSub(pending, nowdone - wasdone) decrements EXACTLY on the 0->1 transition (delta is
    1 only then, never -1 since doneN is monotonic).
  * outN = Na/(aa?aa:1) written unconditionally — garbage while pending, overwritten with Na/g
    once aa IS the gcd, read only at the end. No emit-branch.
There is ONE generator body; control is just part of what every generator does each cycle. The
scheduler has no distinguished node and no role switch — role dissolved, not floated.
Verified: reductions bit-exact, all converge, K climbed via the distributed monotonic control.
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
import jea_core                                  # strict shared structure

_SRC = "typedef unsigned long long u64;\n" + jea_core.CTRL_CUDA + r'''

extern "C" __global__
void generator_coop(
    volatile int* Kbuf, volatile int* obsmax, volatile int* pending,
    const u64* Na, const u64* Da, u64* a, u64* b, int* steps, int* doneN,
    u64* outN, u64* outD, long long* cycles_by, volatile int* err,
    int nblocks, int npr, long long maxcyc)
{
    if (threadIdx.x != 0) return;
    int w = blockIdx.x;                          // ONE generator body; no role distinction
    long long c = 0;
    while (*pending > 0) {                        // inherent termination (monotonic pending)
        int idx = w*npr + (int)(c % npr);        // round-robin over this block's nodes (branchless)
        int K = *Kbuf;
        // ---- WORK (predicated: converged node => no-op, no skip-branch) ----
        u64 aa=a[idx], bb=b[idx]; int st=steps[idx];
        for (int j=0;j<K;j++){ if(bb!=0){ u64 r=aa%bb; aa=bb; bb=r; st++; } }
        a[idx]=aa; b[idx]=bb; steps[idx]=st;
        int wasdone = doneN[idx];
        int nowdone = (bb==0);
        doneN[idx] = nowdone;                                  // monotonic 0->1
        u64 g = aa?aa:1ULL; outN[idx]=Na[idx]/g; outD[idx]=Da[idx]/g;   // unconditional emit
        atomicSub((int*)pending, nowdone - wasdone);           // branchless transition decrement
        // ---- CONTROL (every generator, every cycle, monotonic) ----
        int est = nowdone ? st : st+1;
        atomicMax((int*)obsmax, est);                          // monotonic global depth, O(1)
        *Kbuf = relax_q(*Kbuf, *obsmax);                       // benign concurrent hint
        __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
    cycles_by[w] = c;
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_coop")
residency = jea_core.residency


def run(K0=4, maxcyc=2_000_000):
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = min(20, nsm)
    deep    = [(6,4), (100,60), (6765,4181), (8,6)]    # w%4==0 holds the deep Fibonacci node
    shallow = [(6,4), (100,60), (30,18),     (8,6)]    # else all shallow
    npr = 4; total = nblocks * npr
    per_sm, max_resident, _n, regs = residency(_kern, 32)
    assert nblocks <= max_resident

    rows = [deep if (w % 4 == 0) else shallow for w in range(nblocks)]
    Na = cp.asarray([N for r in rows for (N,_d) in r], cp.uint64)
    Da = cp.asarray([D for r in rows for (_n2,D) in r], cp.uint64)
    a = Na.copy(); b = Da.copy()
    steps = cp.zeros(total, cp.int32); doneN = cp.zeros(total, cp.int32)
    outN = cp.zeros(total, cp.uint64); outD = cp.zeros(total, cp.uint64)
    Kbuf = cp.full(1, K0, cp.int32); obsmax = cp.zeros(1, cp.int32)
    pending = cp.full(1, total, cp.int32); cyc = cp.zeros(nblocks, cp.int64); err = cp.zeros(1, cp.int32)
    _kern((nblocks,), (32,),
          (Kbuf, obsmax, pending, Na, Da, a, b, steps, doneN, outN, outD, cyc, err,
           np.int32(nblocks), np.int32(npr), np.int64(maxcyc)))
    cp.cuda.Stream.null.synchronize()
    return dict(nblocks=nblocks, npr=npr, rows=rows, outN=outN.get(), outD=outD.get(),
                doneN=doneN.get(), pending=int(pending.get()[0]), Kfinal=int(Kbuf.get()[0]),
                obsmax=int(obsmax.get()[0]), cyc=cyc.get(), err=int(err.get()[0]),
                regs=regs, per_sm=per_sm, max_resident=max_resident, launched=nblocks)


if __name__ == "__main__":
    r = run(K0=4)
    exact = all((int(r['outN'][w*r['npr']+n]), int(r['outD'][w*r['npr']+n])) == (N//gcd(N,D), D//gcd(N,D))
                for w in range(r['nblocks']) for n,(N,D) in enumerate(r['rows'][w]))
    converged = bool(r['doneN'].all()) and r['pending'] == 0
    print(f"increment (5) BRANCHLESS cooperative generators: {r['nblocks']} symmetric blocks, NO role distinction\n")
    print(f"  RESIDENCY (measured): {r['regs']} regs => {r['per_sm']}/SM => {r['max_resident']} >= {r['launched']} : "
          f"{'OK' if r['launched']<=r['max_resident'] else 'VIOLATED'}")
    print(f"  reduced (block 0=deep): {[(int(r['outN'][n]), int(r['outD'][n])) for n in range(r['npr'])]}")
    print(f"  obsmax (max depth seen): {r['obsmax']}   K final: {r['Kfinal']}  (grown by distributed monotonic control)")
    print(f"  cycles/block: min={int(r['cyc'].min())} max={int(r['cyc'].max())}  (every block ran the SAME body: work+control each cycle)")
    print(f"\n  err={r['err']}  exact-vs-Python-gcd={exact}  all-converged={converged}")
    ok = (r['err']==0 and exact and converged)
    print(f"\n  INCREMENT (5) {'PASS' if ok else 'FAIL'} — BRANCHLESS: no work/control branch, no token/lock.")
    print(f"  every generator does work+control unconditionally each cycle; converged nodes are predicated")
    print(f"  no-ops, control is monotonic (atomicMax + benign hint). Role dissolved, not floated. Bit-exact.")
