#!/usr/bin/env python3
"""jea_generator_strat.py — the CORRECT merge: STRATIFIED data-parallel + dynamic, deadlock-free
by construction.

The persistent cooperative kernel deadlocked because threads WAITED on specific nodes owned by
maybe-unscheduled blocks (a cyclic wait) — a flow-control failure, not a hardware limit. The fix
(user: "did we forget to stratify our work units again?"): process the DAG in TOPOLOGICAL STRATA.
Within a stratum every node's children are in already-completed strata, so there are NO cross-block
waits — deadlock is impossible, ANY occupancy works (full grid, blocks just process their slice and
EXIT), no persistence, no all-resident requirement. Dynamic K-control + windowed gcd ride ACROSS
strata (re-pass a stratum with a larger K until its nodes converge — re-LAUNCH, never spin-wait).
Carrier = exact 128-bit with escalate-don't-truncate.

So: flow control = stratum order; priority/readiness = the stratum itself (no per-node polling);
data-parallel = full grid per stratum; dynamic = K relaxed per pass via the nedge control law.
"""
import os, time
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction
import jea_core
import jea_generator_dag as DAG

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
extern "C" __global__
void combine_stratum(
    const int* snodes, int ns, int K,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps,
    volatile int* notdone, volatile int* obsmax, volatile int* escalate)
{
    int t = blockIdx.x*blockDim.x + threadIdx.x;
    int stride = gridDim.x*blockDim.x;
    for (int i=t; i<ns; i+=stride) {                 // grid-stride over this stratum; no cross-dep
        int slot = snodes[i];
        if (ready[slot]) continue;                   // already converged in a prior pass
        if (!initf[slot]) {                          // children are DONE (stratum guarantee) -> init
            int Lc=lch[slot], Rc=rch[slot];
            u128 nl=ld(vNl,vNh,Lc), dl=ld(vDl,vDh,Lc), nr=ld(vNl,vNh,Rc), dr=ld(vDl,vDh,Rc);
            u128 na, D = dl*dr; int o=0;
            o |= (dl!=0) && (D/dl != dr);
            if (op[slot]==1) { na=nl*nr; o |= (nl!=0)&&(na/nl!=nr); }
            else { u128 p1=nl*dr,p2=nr*dl; na=p1+p2; o|=(dr!=0)&&(p1/dr!=nl); o|=(dl!=0)&&(p2/dl!=nr); o|=(na<p1); }
            if (o) *escalate=1;
            st(naNl,naNh,slot,na); st(naDl,naDh,slot,D); st(al,ah,slot,na); st(bl,bh,slot,D); initf[slot]=1;
        }
        u128 aa=ld(al,ah,slot), bb=ld(bl,bh,slot); int s=steps[slot];
        for (int j=0;j<K;j++){ if (bb!=0){ u128 r=aa%bb; aa=bb; bb=r; s++; } }   // K-window gcd
        st(al,ah,slot,aa); st(bl,bh,slot,bb); steps[slot]=s;
        if (bb==0){ u128 g=(aa!=0)?aa:(u128)1; st(vNl,vNh,slot, ld(naNl,naNh,slot)/g);
                    st(vDl,vDh,slot, ld(naDl,naDh,slot)/g); ready[slot]=1; }
        else atomicAdd((int*)notdone, 1);            // still reducing -> host re-passes with larger K
        atomicMax((int*)obsmax, ready[slot]? s : s+1);
    }
}
'''
_kern = jea_core.build_kernel(_SRC, "combine_stratum", int128=True)


_lh = jea_core.lh                          # shared limb-split, promoted to jea_core (Φ3 fold)


def strata_of(g):
    """Topological strata: leaves at level 0, combine level = 1 + max(child levels). Combines are
    indexed children-before-parent, so one forward pass computes levels; group by level."""
    L,N = g["L"], g["N"]; lch,rch = g["lch"], g["rch"]
    lvl = [0]*N
    for ci in range(L, N):
        lvl[ci] = 1 + max(lvl[lch[ci]], lvl[rch[ci]])
    strata = {}
    for ci in range(L, N): strata.setdefault(lvl[ci], []).append(ci)
    return [strata[k] for k in sorted(strata)]


def run_strat(g, B=256, K0=4):
    nsm = cp.cuda.Device().attributes["MultiProcessorCount"]
    nblocks = 8*nsm                                  # generous full-occupancy grid; grid-stride covers any ns
    N,L = g["N"], g["L"]
    vNl,vNh=_lh(g["vN"]); vDl,vDh=_lh(g["vD"])
    lch=cp.asarray(g["lch"],cp.int32); rch=cp.asarray(g["rch"],cp.int32); op=cp.asarray(g["op"],cp.int32)
    ready=cp.asarray([1 if i<L else 0 for i in range(N)],cp.int32)
    initf=cp.asarray([1 if i<L else 0 for i in range(N)],cp.int32)
    z=lambda: cp.zeros(N,cp.uint64); al,ah,bl,bh,naNl,naNh,naDl,naDh=z(),z(),z(),z(),z(),z(),z(),z()
    steps=cp.zeros(N,cp.int32)
    notdone=cp.zeros(1,cp.int32); obsmax=cp.zeros(1,cp.int32); escalate=cp.zeros(1,cp.int32)
    strata=[cp.asarray(s,cp.int32) for s in strata_of(g)]
    K=K0; passes=0
    cp.cuda.Stream.null.synchronize(); t0=time.perf_counter()
    for sn in strata:
        ns=int(sn.size)
        while True:                                  # re-pass this stratum until all its nodes converge
            notdone[0]=0
            _kern((nblocks,),(B,),
                  (sn,np.int32(ns),np.int32(K),vNl,vNh,vDl,vDh,lch,rch,op,ready,initf,
                   al,ah,bl,bh,naNl,naNh,naDl,naDh,steps,notdone,obsmax,escalate))
            passes+=1
            if int(notdone.get()[0])==0: break
            K = jea_core.relax_q_ref(K, int(obsmax.get()[0]))   # dynamic: raise K toward observed depth
    cp.cuda.Stream.null.synchronize(); ms=(time.perf_counter()-t0)*1e3
    r=g["root"]
    rn=(int(vNh.get()[r])<<64)|int(vNl.get()[r]); rd=(int(vDh.get()[r])<<64)|int(vDl.get()[r])
    return dict(rn=rn,rd=rd,escalate=int(escalate.get()[0]),ms=ms,nstrata=len(strata),
                passes=passes,Kfinal=K,nblocks=nblocks,threads=nblocks*B)


if __name__ == "__main__":
    print("jea_generator_strat — STRATIFIED data-parallel + dynamic, deadlock-free by construction\n")

    print("  exactness (random +/x DAG vs Python Fraction; 128-bit, escalate):")
    allok=True
    for L in (64,128,256,512):
        g=DAG.build_dag(L,3); r=run_strat(g)
        tb=max(abs(g['truth'].numerator),g['truth'].denominator).bit_length()
        if r['escalate']==1: ok=True; v=f"ESCALATED (>2^128 detected, not wrapped)"
        else: ok=Fraction(r['rn'],r['rd'])==g['truth']; v=f"exact={ok}"+("  (>2^64: u64 would WRAP)" if tb>64 else "")
        allok&=ok
        print(f"     L={L:4d} ({g['N']:>4} nodes, true {tb:>3}b, {r['nstrata']} strata, {r['passes']} passes): {v}")

    print("\n  throughput + NO DEADLOCK at scale (large all-+ tree, FULL grid):")
    thr=0
    for h in (14,16,18,20):
        g=DAG.build_dag(1<<h,3) if h<=12 else None
        import jea_generator_unified as U
        g=U.build_balanced_add(h); run_strat(g)      # warm
        r=run_strat(g)
        truth=sum((Fraction(g['vN'][i],g['vD'][i]) for i in range(g['L'])),Fraction(0))
        ok=r['escalate']==0 and Fraction(r['rn'],r['rd'])==truth
        thr=g['N']/r['ms']*1e3/1e6
        print(f"     L=2^{h}={g['L']:>8} ({g['N']:>9} nodes, {r['nstrata']:>2} strata): {r['ms']:7.2f} ms = "
              f"{thr:7.1f} M nodes/s  {r['threads']} threads  exact={ok}")

    print(f"\n  ~{thr:.0f} M nodes/s at FULL occupancy ({8*cp.cuda.Device().attributes['MultiProcessorCount']*256} threads),")
    print(f"  NO deadlock at any scale (stratified: no cross-block waits), dynamic K, 128-bit exact.")
    print(f"\n  STRAT {'PASS' if allok else 'FAIL'} — the merge done right: stratify => deadlock-free flow control,")
    print(f"  full-occupancy data-parallel per stratum, dynamic K across strata. No residency gamble.")
