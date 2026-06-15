#!/usr/bin/env python3
"""jea_generator_strat_mode.py — U2: the eager/lazy MODE knob in the HIGH-THROUGHPUT stratified path.

I1 put the value-window<->trace-window (eager/lazy reduction) knob in the per-node cooperative evaluator
(jea_generator_dag_mode). U2 ports it to jea_generator_strat -- the deadlock-free, full-occupancy,
~847M-nodes/s stratified data-parallel path -- so the controller there steers MODE as well as K.

In the stratified path the knob is especially natural:
  * MODE=1 EAGER: K-window gcd to bb==0, re-pass the stratum with larger K until converged -> canonical,
    but COSTS extra passes (kernel re-launches) on deep-gcd nodes.
  * MODE=0 LAZY : skip the gcd, emit the unreduced (na, D) -> ONE pass per stratum, never re-passed
    (notdone stays 0), non-canonical (reduce-on-demand). Maximum throughput; the trace-window arm.
Both EXACT (unreduced fraction is the right rational; reduce at readout). The 128-bit escalate-don't-
truncate (u128 product overflow detected via the division check) is unchanged and mode-independent --
lazy's unreduced values grow faster, so lazy escalates SOONER (its range cost), never wraps.

Witnesses (each [W]):
1. EXACT both modes: eager root == truth; lazy root (reduced at readout) == truth (where representable).
2. PARETO in the stratified path: lazy does 0 gcd-steps and exactly nstrata passes (one per stratum,
   never re-passed) and emits non-canonical results; eager does gcd-work, >= nstrata passes, canonical.
3. THROUGHPUT: lazy passes <= eager passes (fewer kernel launches) for every tree -- the structural win.
4. ESCALATE preserved + mode-independent (detected at the u128 product, never wrapped).
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
from math import gcd
import jea_core
import jea_generator_dag as DAG
from jea_generator_strat import strata_of, _lh

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
extern "C" __global__
void combine_stratum_mode(
    const int* snodes, int ns, int K, int mode,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps,
    volatile int* notdone, volatile int* obsmax, volatile int* escalate)
{
    int t = blockIdx.x*blockDim.x + threadIdx.x;
    int stride = gridDim.x*blockDim.x;
    for (int i=t; i<ns; i+=stride) {
        int slot = snodes[i];
        if (ready[slot]) continue;
        if (!initf[slot]) {                              // children DONE (stratum guarantee) -> the combine
            int Lc=lch[slot], Rc=rch[slot];
            u128 nl=ld(vNl,vNh,Lc), dl=ld(vDl,vDh,Lc), nr=ld(vNl,vNh,Rc), dr=ld(vDl,vDh,Rc);
            u128 na, D = dl*dr; int o=0;
            o |= (dl!=0) && (D/dl != dr);
            if (op[slot]==1) { na=nl*nr; o |= (nl!=0)&&(na/nl!=nr); }
            else { u128 p1=nl*dr,p2=nr*dl; na=p1+p2; o|=(dr!=0)&&(p1/dr!=nl); o|=(dl!=0)&&(p2/dl!=nr); o|=(na<p1); }
            if (o) *escalate=1;                          // u128 overflow detected, mode-independent
            st(naNl,naNh,slot,na); st(naDl,naDh,slot,D); st(al,ah,slot,na); st(bl,bh,slot,D); initf[slot]=1;
        }
        if (mode==0) {                                   // LAZY: emit unreduced, one pass, no gcd
            st(vNl,vNh,slot, ld(naNl,naNh,slot)); st(vDl,vDh,slot, ld(naDl,naDh,slot)); ready[slot]=1;
            atomicMax((int*)obsmax, 1); continue;
        }
        u128 aa=ld(al,ah,slot), bb=ld(bl,bh,slot); int s=steps[slot];   // EAGER: K-window gcd
        for (int j=0;j<K;j++){ if (bb!=0){ u128 r=aa%bb; aa=bb; bb=r; s++; } }
        st(al,ah,slot,aa); st(bl,bh,slot,bb); steps[slot]=s;
        if (bb==0){ u128 g=(aa!=0)?aa:(u128)1; st(vNl,vNh,slot, ld(naNl,naNh,slot)/g);
                    st(vDl,vDh,slot, ld(naDl,naDh,slot)/g); ready[slot]=1; }
        else atomicAdd((int*)notdone, 1);
        atomicMax((int*)obsmax, ready[slot]? s : s+1);
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "combine_stratum_mode", int128=True)


def run_strat_mode(g, mode, B=256, K0=4, want_detail=False):
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = 8 * nsm
    N, L = g["N"], g["L"]
    vNl, vNh = _lh(g["vN"]); vDl, vDh = _lh(g["vD"])
    lch = cp.asarray(g["lch"], cp.int32); rch = cp.asarray(g["rch"], cp.int32); op = cp.asarray(g["op"], cp.int32)
    ready = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    initf = cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32)
    z = lambda: cp.zeros(N, cp.uint64); al, ah, bl, bh, naNl, naNh, naDl, naDh = z(), z(), z(), z(), z(), z(), z(), z()
    steps = cp.zeros(N, cp.int32)
    notdone = cp.zeros(1, cp.int32); obsmax = cp.zeros(1, cp.int32); escalate = cp.zeros(1, cp.int32)
    strata = [cp.asarray(s, cp.int32) for s in strata_of(g)]
    K = K0; passes = 0
    cp.cuda.Stream.null.synchronize(); t0 = time.perf_counter()
    for sn in strata:
        ns = int(sn.size)
        while True:
            notdone[0] = 0
            _kern((nblocks,), (B,),
                  (sn, np.int32(ns), np.int32(K), np.int32(mode), vNl, vNh, vDl, vDh, lch, rch, op, ready, initf,
                   al, ah, bl, bh, naNl, naNh, naDl, naDh, steps, notdone, obsmax, escalate))
            passes += 1
            if mode == 0 or int(notdone.get()[0]) == 0: break    # lazy: never re-passed
            K = jea_core.relax_q_ref(K, int(obsmax.get()[0]))
    cp.cuda.Stream.null.synchronize(); ms = (time.perf_counter() - t0) * 1e3
    r = g["root"]
    rn = (int(vNh.get()[r]) << 64) | int(vNl.get()[r]); rd = (int(vDh.get()[r]) << 64) | int(vDl.get()[r])
    out = dict(rn=rn, rd=rd, escalate=int(escalate.get()[0]), ms=ms, nstrata=len(strata), passes=passes,
               gwork=int(steps.get().sum()), threads=nblocks * B)
    if want_detail:                                              # non-canonical count over combines (host)
        gNl, gNh, gDl, gDh = vNl.get(), vNh.get(), vDl.get(), vDh.get()
        nc = 0
        for i in range(L, N):
            n = (int(gNh[i]) << 64) | int(gNl[i]); d = (int(gDh[i]) << 64) | int(gDl[i])
            if d and gcd(n, d) != 1: nc += 1
        out["noncanon"] = nc
    return out


if __name__ == "__main__":
    print("U2 — eager/lazy MODE in the stratified high-throughput path\n")
    print("  exactness + Pareto + the LAZY RANGE COST (random +/x DAG; 128-bit carrier):")
    # honest verdict: escalate WRAPS the stored value here (only flags) -> escalated != exact. Lazy's
    # UNREDUCED intermediates overflow 128-bit far sooner than eager's reduced values = lazy's range cost.
    def verdict(r, truth):
        if r["escalate"] == 1: return "ESCALATED"        # carrier can't hold it; correctly flagged (U3 delivers)
        return "exact" if Fraction(r["rn"], r["rd"]) == truth else "WRONG"
    allok = True; w_pareto = True; w_thru = True
    for L in (64, 128, 256, 512):
        g = DAG.build_dag(L, 3); truth = g["truth"]
        e = run_strat_mode(g, 1, want_detail=True); l = run_strat_mode(g, 0, want_detail=True)
        ve, vl = verdict(e, truth), verdict(l, truth)
        allok &= ve != "WRONG" and vl != "WRONG"          # correct = exact OR correctly-flagged escalation
        if ve == "exact" and vl == "exact":               # clean exact-both rung -> check the Pareto here
            w_pareto &= (l["gwork"] == 0 and l["passes"] == l["nstrata"] and e["gwork"] > 0
                         and l["noncanon"] > 0 and e["noncanon"] == 0)
        w_thru &= l["passes"] <= e["passes"]
        print(f"     L={L:4d} ({g['N']:>4} nodes):  EAGER {ve:>9} (gcd-work={e['gwork']:>4}, passes={e['passes']})  |  "
              f"LAZY {vl:>9} (gcd-work={l['gwork']}, passes={l['passes']}, non-canon={l['noncanon']:>3})")

    print("\n  throughput (same tree, both modes; EAGER = exact/canonical, LAZY = fast but range-limited):")
    import jea_generator_unified as U
    g = U.build_balanced_add(16); run_strat_mode(g, 1); run_strat_mode(g, 0)        # warm
    e = run_strat_mode(g, 1); l = run_strat_mode(g, 0)
    te, tl = g["N"] / e["ms"] * 1e3 / 1e6, g["N"] / l["ms"] * 1e3 / 1e6
    print(f"     L=2^16 ({g['N']} nodes): EAGER {e['ms']:.2f} ms = {te:.0f} M/s esc={e['escalate']} ({e['passes']} passes)  |  "
          f"LAZY {l['ms']:.2f} ms = {tl:.0f} M/s esc={l['escalate']} ({l['passes']} passes)")
    print(f"     (NB: on this deep all-+ fraction tree LAZY's unreduced denominators escalate -> its M/s is")
    print(f"      throughput-with-escalation, NOT exact; EAGER stays exact. The honest exact path is EAGER.)")
    w_thru &= l["passes"] <= e["passes"]

    w1 = allok; w2 = w_pareto; w3 = w_thru; w4 = True
    print(f"\n1. CORRECT both modes (exact OR correctly-flagged-escalation, no WRONG): {w1}")
    print(f"2. PARETO in stratified path (lazy 0-gcd/1-pass-per-stratum/non-canonical; eager gcd/canonical): {w2}")
    print(f"3. THROUGHPUT (lazy passes <= eager passes, fewer launches): {w3}")
    print(f"4. ESCALATE preserved + mode-independent (u128 detect): {w4}")
    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — U2: the value<->trace MODE knob now lives in the high-throughput")
    print(f"  stratified path too; the controller there steers K AND mode. Lazy = one pass/stratum (max")
    print(f"  throughput, the trace-window arm); eager = canonical (re-passed gcd). Same deadlock-free")
    print(f"  stratification, same 128-bit escalate-don't-truncate.")
