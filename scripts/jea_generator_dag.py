#!/usr/bin/env python3
"""jea_generator_dag.py — increment (6): the STREAMING RECURSIVE FOLD = the apex that unifies
the three "options" (128-bit carrier / telemetry ring / recursive fold). They are the three
coordinates of a generator network — carrier (payload), channel (movement), wiring (deps) —
and all three are enrichments of the SAME object increments (1)-(5) converged on: a MONOTONIC
RESIDUE STORE advanced by one branchless cooperative generator.

Building the recursive fold forces the unification: it adds WIRING (child indices + a monotonic
readiness gate) to the store, which makes the carrier a typedef (128-bit drops in) and makes the
channel just BE the store (the ring becomes optional). This is the mini-MAlonzo brick: an
arbitrary term-algebra trace (a DAG of +/x combines over ℚ leaves) evaluated by the SAME
cooperative generators, streaming bottom-up.

Same body as (5): every block, every cycle, does work+control unconditionally; converged/inactive
nodes are predicated no-ops; control is monotonic (atomicMax + benign K hint). NEW: a combine
node is gated by `active = ready[L] & ready[R] & !ready[self]` (monotonic readiness, lock-free
cross-block via volatile+fence). On first active touch it inits its (a,b) gcd residue from the
two child values; subsequent touches carry the residue (windowed gcd reduction); on b==0 it
emits its reduced value and flips ready 0->1 (monotonic) — which activates its parent. Bottom-up
to the root. Carrier = u64 here (small leaves); the proven 128-bit _QDECL is the typedef swap for
scale (where add's denominator-product would overflow u64 = the escalate point). Verified: the
root is bit-exact vs a Python Fraction fold over the same DAG/ops.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from math import gcd
from fractions import Fraction
import jea_core                                  # strict shared structure

_SRC = "typedef unsigned long long u64;\n" + jea_core.CTRL_CUDA + r'''

extern "C" __global__
void generator_dag(
    volatile int* Kbuf, volatile int* obsmax, volatile int* pending,
    u64* vN, u64* vD, const int* lch, const int* rch, const int* op,
    volatile int* ready, int* initf, u64* a, u64* b, u64* naN, u64* naD, int* steps,
    const int* own, const int* own_count,
    long long* cycles_by, volatile int* err,
    int nblocks, int maxown, long long maxcyc)
{
    if (threadIdx.x != 0) return;
    int w = blockIdx.x;
    int oc = own_count[w];
    long long c = 0;
    while (*pending > 0) {
        int est = 0;
        if (oc > 0) {
            int slot = own[w*maxown + (int)(c % oc)];          // round-robin over owned combines
            int Lc = lch[slot], Rc = rch[slot];
            int active = ready[Lc] & ready[Rc] & (1 - ready[slot]);   // monotonic readiness gate
            // first active touch: init the gcd residue from the two child values (the combine)
            if (active & (1 - initf[slot])) {
                u64 nl=vN[Lc], dl=vD[Lc], nr=vN[Rc], dr=vD[Rc];
                u64 na = (op[slot]==1) ? (nl*nr) : (nl*dr + nr*dl);   // select (branchless): x or +
                u64 D  = dl*dr;
                naN[slot]=na; naD[slot]=D; a[slot]=na; b[slot]=D; initf[slot]=1;
            }
            int K = *Kbuf;
            u64 aa=a[slot], bb=b[slot]; int st=steps[slot];
            for (int j=0;j<K;j++){ if (active & (bb!=0)){ u64 r=aa%bb; aa=bb; bb=r; st++; } }
            a[slot]=aa; b[slot]=bb; steps[slot]=st;
            int nowdone = active & (bb==0);
            if (nowdone) { u64 g = aa?aa:1ULL; vN[slot]=naN[slot]/g; vD[slot]=naD[slot]/g; }  // emit reduced
            int wasready = ready[slot];
            ready[slot] = wasready | nowdone;                  // monotonic 0->1 (activates parent)
            atomicSub((int*)pending, ready[slot] - wasready);  // branchless transition decrement
            est = nowdone ? st : (active ? st+1 : 0);
        }
        atomicMax((int*)obsmax, est);                          // monotonic control
        *Kbuf = relax_q(*Kbuf, *obsmax);                       // benign concurrent hint
        __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
    cycles_by[w] = c;
}
'''
_kern = jea_core.build_kernel(_SRC, "generator_dag")
residency = jea_core.residency


def build_dag(L, seed):
    """Balanced binary +/x tree over small positive-ℚ leaves. Returns flat node arrays + root
    + the Python-Fraction truth folded over the same DAG/ops."""
    rng = np.random.default_rng(seed)
    vN = [int(x) for x in rng.integers(1, 4, L)]       # leaf num in {1,2,3}
    vD = [int(x) for x in (1 << rng.integers(0, 2, L))]  # leaf den in {1,2}
    lch = [-1]*L; rch = [-1]*L; op = [-1]*L
    fval = [Fraction(vN[i], vD[i]) for i in range(L)]   # python truth per node
    level = list(range(L))
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            li, ri = level[i], level[i+1]
            o = int(rng.integers(0, 2))                 # 0=add, 1=mul
            idx = len(vN); vN.append(0); vD.append(0)
            lch.append(li); rch.append(ri); op.append(o)
            fval.append(fval[li]*fval[ri] if o == 1 else fval[li]+fval[ri])
            nxt.append(idx)
        level = nxt
    return dict(vN=vN, vD=vD, lch=lch, rch=rch, op=op, L=L, N=len(vN),
                root=level[0], truth=fval[level[0]])


def run(L=16, seed=3, K0=4, maxcyc=2_000_000):
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = min(20, nsm)
    g = build_dag(L, seed); N = g["N"]
    per_sm, max_resident, _n, regs = residency(_kern, 32)
    assert nblocks <= max_resident

    vN = cp.asarray(g["vN"], cp.uint64); vD = cp.asarray(g["vD"], cp.uint64)
    lch = cp.asarray(g["lch"], cp.int32); rch = cp.asarray(g["rch"], cp.int32)
    op = cp.asarray(g["op"], cp.int32)
    ready = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    initf = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    a = cp.zeros(N, cp.uint64); b = cp.zeros(N, cp.uint64)
    naN = cp.zeros(N, cp.uint64); naD = cp.zeros(N, cp.uint64); steps = cp.zeros(N, cp.int32)
    # combines = indices [L,N); assign round-robin to blocks (parent/child land on different blocks)
    combines = list(range(L, N))
    per_block = [[] for _ in range(nblocks)]
    for k, ci in enumerate(combines): per_block[k % nblocks].append(ci)
    maxown = max((len(x) for x in per_block), default=1) or 1
    own = np.full((nblocks, maxown), -1, np.int32)
    for w in range(nblocks):
        for j, ci in enumerate(per_block[w]): own[w, j] = ci
    own_count = cp.asarray([len(x) for x in per_block], cp.int32)
    own = cp.asarray(own.ravel(), cp.int32)

    Kbuf = cp.full(1, K0, cp.int32); obsmax = cp.zeros(1, cp.int32)
    pending = cp.full(1, len(combines), cp.int32)
    cyc = cp.zeros(nblocks, cp.int64); err = cp.zeros(1, cp.int32)
    _kern((nblocks,), (32,),
          (Kbuf, obsmax, pending, vN, vD, lch, rch, op, ready, initf, a, b, naN, naD, steps,
           own, own_count, cyc, err, np.int32(nblocks), np.int32(maxown), np.int64(maxcyc)))
    cp.cuda.Stream.null.synchronize()
    root = g["root"]
    rn, rd = int(vN.get()[root]), int(vD.get()[root])
    return dict(g=g, rn=rn, rd=rd, pending=int(pending.get()[0]), Kfinal=int(Kbuf.get()[0]),
                obsmax=int(obsmax.get()[0]), err=int(err.get()[0]), regs=regs,
                per_sm=per_sm, max_resident=max_resident, launched=nblocks, ncomb=len(combines))


if __name__ == "__main__":
    r = run(L=16, seed=3)
    truth = r["g"]["truth"]
    exact = (Fraction(r["rn"], r["rd"]) == truth) if r["rd"] else False
    converged = (r["pending"] == 0)
    print(f"increment (6) STREAMING RECURSIVE FOLD (mini-MAlonzo): L={r['g']['L']} leaves, "
          f"{r['ncomb']} combines, {r['launched']} cooperative blocks\n")
    print(f"  RESIDENCY (measured): {r['regs']} regs => {r['per_sm']}/SM => {r['max_resident']} >= {r['launched']} : "
          f"{'OK' if r['launched']<=r['max_resident'] else 'VIOLATED'}")
    print(f"  root on-GPU : {r['rn']}/{r['rd']}")
    print(f"  root Python : {truth.numerator}/{truth.denominator}")
    print(f"  obsmax (max gcd depth) {r['obsmax']}   K final {r['Kfinal']}   (distributed monotonic control)")
    print(f"\n  err={r['err']}  root bit-exact vs Python Fraction={exact}  all-combines-converged={converged}")
    ok = (r['err']==0 and exact and converged)
    print(f"\n  INCREMENT (6) {'PASS' if ok else 'FAIL'} — an arbitrary term-algebra DAG evaluated by the SAME")
    print(f"  branchless cooperative generators, streaming bottom-up via a monotonic readiness gate")
    print(f"  (wiring as data in the store). Carrier=u64 (128-bit _QDECL = the typedef swap for scale);")
    print(f"  channel = the store itself. The three 'options' unified: carrier/channel/wiring, one object.")
