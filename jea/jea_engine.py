#!/usr/bin/env python3
"""jea_engine.py — the consolidated JEA evaluator. C1 + C2 of the consolidation arc.

C1: ONE parameterized combine, carrier as a compile-time typedef (-DCARRIER_U128) + mode/K runtime params,
collapsing the duplicated combine bodies of jea_generator_dag (u64) / dag128 (u128) / dag_mode (eager,lazy).
Store/compute always in u128 lo/hi lanes (u64 = hi==0); CARRIER sets only the escalate threshold (2^64 vs
2^128) and which overflow check applies (a wider-type value-compare for u64; a division-check for u128).

C2: SCHEDULING is a strategy OVER that combine. The per-node combine is one __device__ function
combine_window(slot,K,mode,...); the schedulers CALL it -- they no longer each copy the combine body:
  * coop  -- persistent, one lead thread/block, round-robin owned slots, monotonic readiness gate, K
             relaxed in-kernel per cycle (the dag/dag_mode family).
  * strat -- grid-stride over a topological stratum (children guaranteed done), host re-passes the stratum
             with relaxed K until converged; deadlock-free, full occupancy (the jea_generator_strat family).
Same combine_window for both: the schedule is orthogonal to the combine (proven below: coop == strat on the
same DAG). schedule is a host param.

SCOPE (honest, DBE): the spawn/rewrite engine (jea_universal_engine) is a DIFFERENT evaluation model
(dynamic term-rewriting + atomic-bump spawn, not a fixed-DAG Q-fold), so it is NOT a third "schedule over
the Q-combine" -- forcing it here would be artificial. It stays a distinct axis (the rewrite engine, U6).

Witnesses (each [W]):
1. COOP u64 eager == truth, canonical; lazy == truth (reduced), non-canonical>0 (== dag / dag_mode).
2. CARRIER WIDENS: an >2^64 DAG -- carrier64 escalates, carrier128 exact (== dag128); u128 240b all-mul escalates.
3. STRAT reproduces the fixed-DAG fold (== jea_generator_strat): random DAG, exact / escalate.
4. SAME COMBINE: coop and strat give IDENTICAL results on the same DAG -- the schedule is orthogonal to
   the combine (the C2 dedup proof). Combine body appears ONCE (in combine_window), called by both.
5. ONE SOURCE: every (scheduler x carrier) kernel compiled from the identical _SRC (only -DCARRIER_U128).
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from math import gcd
from fractions import Fraction
import jea_core
from jea_generator_dag import build_dag
from jea_generator_strat import _lh, strata_of

_SRC = jea_core.Q128_CUDA + jea_core.CTRL_CUDA + r'''
// ---- the ONE per-node combine (carrier typedef + mode); both schedulers call this ----
__device__ int combine_window(int slot, int K, int mode,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    volatile int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps, int* esc)
{
    if (ready[slot]) return -1;                          // already converged
    int Lc=lch[slot], Rc=rch[slot];
    if (!(ready[Lc] && ready[Rc])) return -1;            // children not done -> inactive (skip, revisit)
    if (!initf[slot]) {                                  // the combine (carrier-parameterized)
        if (esc[Lc] | esc[Rc]) { esc[slot]=1; st(naNl,naNh,slot,0); st(naDl,naDh,slot,1); st(al,ah,slot,0); st(bl,bh,slot,0); }
        else {
            u128 nl=ld(vNl,vNh,Lc), dl=ld(vDl,vDh,Lc), nr=ld(vNl,vNh,Rc), dr=ld(vDl,vDh,Rc); u128 na, D;
#ifdef CARRIER_U128
            int o=0; D=dl*dr; o|=(dl!=0)&&(D/dl!=dr);
            if (op[slot]==1){ na=nl*nr; o|=(nl!=0)&&(na/nl!=nr); }
            else { u128 p1=nl*dr,p2=nr*dl; na=p1+p2; o|=(dr!=0)&&(p1/dr!=nl); o|=(dl!=0)&&(p2/dl!=nr); o|=(na<p1); }
            if (o){ esc[slot]=1; st(naNl,naNh,slot,0); st(naDl,naDh,slot,1); st(al,ah,slot,0); st(bl,bh,slot,0); }
            else { st(naNl,naNh,slot,na); st(naDl,naDh,slot,D); st(al,ah,slot,na); st(bl,bh,slot,D); }
#else
            const u128 LIM = ((u128)1) << 64;
            na = (op[slot]==1) ? (nl*nr) : (nl*dr + nr*dl); D = dl*dr;
            if (na>=LIM || D>=LIM) {
                u128 x=na,y=D; while(y){ u128 t=x%y; x=y; y=t; } u128 g=x?x:1; u128 rn=na/g, rd=D/g;
                if (rn>=LIM||rd>=LIM){ esc[slot]=1; st(naNl,naNh,slot,0); st(naDl,naDh,slot,1); }
                else { st(naNl,naNh,slot,rn); st(naDl,naDh,slot,rd); }
                st(al,ah,slot,0); st(bl,bh,slot,0);
            } else { st(naNl,naNh,slot,na); st(naDl,naDh,slot,D); st(al,ah,slot,na); st(bl,bh,slot,D); }
#endif
        }
        initf[slot]=1;
    }
    int s=steps[slot], nowdone=0; u128 aa=ld(al,ah,slot), bb=ld(bl,bh,slot);
    if (esc[slot]) { st(vNl,vNh,slot,0); st(vDl,vDh,slot,1); nowdone=1; }
    else if (aa==0 && bb==0) { st(vNl,vNh,slot, ld(naNl,naNh,slot)); st(vDl,vDh,slot, ld(naDl,naDh,slot)); nowdone=1; }
    else if (mode==1) {
        for (int j=0;j<K;j++){ if (bb!=0){ u128 r=aa%bb; aa=bb; bb=r; s++; } }
        st(al,ah,slot,aa); st(bl,bh,slot,bb); steps[slot]=s;
        if (bb==0){ u128 g=aa?aa:(u128)1; st(vNl,vNh,slot, ld(naNl,naNh,slot)/g); st(vDl,vDh,slot, ld(naDl,naDh,slot)/g); nowdone=1; }
    } else { st(vNl,vNh,slot, ld(naNl,naNh,slot)); st(vDl,vDh,slot, ld(naDl,naDh,slot)); nowdone=1; }
    if (nowdone) ready[slot]=1;
    return nowdone;                                      // 1 converged this call, 0 still reducing
}

#define ARGS vNl,vNh,vDl,vDh,lch,rch,op,ready,initf,al,ah,bl,bh,naNl,naNh,naDl,naDh,steps,esc

// ---- SCHEDULER 1: cooperative (persistent, readiness-gated) ----
extern "C" __global__
void sched_coop(volatile int* Kbuf, volatile int* obsmax, volatile int* pending, volatile int* mode,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    volatile int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps, int* esc,
    const int* own,const int* own_count, long long* cyc, volatile int* err, int nblocks,int maxown,long long maxcyc)
{
    if (threadIdx.x != 0) return;
    int w=blockIdx.x; int oc=own_count[w]; long long c=0;
    while (*pending > 0) {
        if (oc > 0) {
            int slot = own[w*maxown + (int)(c % oc)];
            int r = combine_window(slot, *Kbuf, *mode, ARGS);
            if (r == 1) atomicSub((int*)pending, 1);
            if (r >= 0) atomicMax((int*)obsmax, steps[slot] > 0 ? steps[slot] : 1);
        }
        *Kbuf = relax_q(*Kbuf, *obsmax); __threadfence();
        if (++c > maxcyc){ *err=1; break; }
    }
    cyc[w] = c;
}

// ---- SCHEDULER 2: stratified (grid-stride per stratum, host re-passes) ----
extern "C" __global__
void sched_strat(const int* snodes, int ns, int K, int mode,
    u64* vNl,u64* vNh,u64* vDl,u64* vDh, const int* lch,const int* rch,const int* op,
    volatile int* ready, int* initf, u64* al,u64* ah,u64* bl,u64* bh,
    u64* naNl,u64* naNh,u64* naDl,u64* naDh, int* steps, int* esc,
    volatile int* notdone, volatile int* obsmax)
{
    int t=blockIdx.x*blockDim.x+threadIdx.x, stride=gridDim.x*blockDim.x;
    for (int i=t; i<ns; i+=stride) {
        int slot = snodes[i];
        int r = combine_window(slot, K, mode, ARGS);
        if (r == 0) atomicAdd((int*)notdone, 1);         // still reducing -> host re-passes with larger K
        if (r >= 0) atomicMax((int*)obsmax, steps[slot] > 0 ? steps[slot] : 1);
    }
}
'''
def _ascii(s): assert s.isascii(); return s
def _build(name, c128): return cp.RawKernel(_ascii(_SRC), name, options=("--device-int128",) + (("-DCARRIER_U128",) if c128 else ()))
_KERN = {("coop", 64): _build("sched_coop", 0), ("coop", 128): _build("sched_coop", 1),
         ("strat", 64): _build("sched_strat", 0), ("strat", 128): _build("sched_strat", 1)}


def _setup(g):
    N, L = g["N"], g["L"]
    vNl, vNh = _lh(g["vN"]); vDl, vDh = _lh(g["vD"])
    a = dict(vNl=vNl, vNh=vNh, vDl=vDl, vDh=vDh,
             lch=cp.asarray(g["lch"], cp.int32), rch=cp.asarray(g["rch"], cp.int32), op=cp.asarray(g["op"], cp.int32),
             ready=cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32),
             initf=cp.asarray([1 if i < L else 0 for i in range(N)], cp.int32),
             steps=cp.zeros(N, cp.int32), esc=cp.zeros(N, cp.int32))
    for k in ("al","ah","bl","bh","naNl","naNh","naDl","naDh"): a[k] = cp.zeros(N, cp.uint64)
    return a


def _node_args(a):
    return (a["vNl"],a["vNh"],a["vDl"],a["vDh"],a["lch"],a["rch"],a["op"],a["ready"],a["initf"],
            a["al"],a["ah"],a["bl"],a["bh"],a["naNl"],a["naNh"],a["naDl"],a["naDh"],a["steps"],a["esc"])


def run_engine(g, carrier=64, mode=1, schedule="coop", K0=4, maxcyc=4_000_000):
    N, L = g["N"], g["L"]; a = _setup(g)
    if schedule == "coop":
        nsm = cp.cuda.Device().attributes["MultiProcessorCount"]; nblocks = min(20, nsm)
        combines = list(range(L, N)); per = [[] for _ in range(nblocks)]
        for k, ci in enumerate(combines): per[k % nblocks].append(ci)
        maxown = max((len(x) for x in per), default=1) or 1
        own = np.full((nblocks, maxown), -1, np.int32)
        for wi in range(nblocks):
            for j, ci in enumerate(per[wi]): own[wi, j] = ci
        own_c = cp.asarray([len(x) for x in per], cp.int32); own = cp.asarray(own.ravel(), cp.int32)
        Kb=cp.full(1,K0,cp.int32); om=cp.zeros(1,cp.int32); pend=cp.full(1,len(combines),cp.int32)
        mb=cp.full(1,mode,cp.int32); cyc=cp.zeros(nblocks,cp.int64); err=cp.zeros(1,cp.int32)
        _KERN[("coop",carrier)]((nblocks,),(32,), (Kb,om,pend,mb)+_node_args(a)+(own,own_c,cyc,err,np.int32(nblocks),np.int32(maxown),np.int64(maxcyc)))
    else:  # strat
        nsm = cp.cuda.Device().attributes["MultiProcessorCount"]; nblocks = 8*nsm
        om=cp.zeros(1,cp.int32); nd=cp.zeros(1,cp.int32); K=K0
        for sn in [cp.asarray(s,cp.int32) for s in strata_of(g)]:
            ns=int(sn.size)
            while True:
                nd[0]=0
                _KERN[("strat",carrier)]((nblocks,),(256,), (sn,np.int32(ns),np.int32(K),np.int32(mode))+_node_args(a)+(nd,om))
                if int(nd.get()[0])==0: break
                K = jea_core.relax_q_ref(K, int(om.get()[0]))
    cp.cuda.Stream.null.synchronize()
    r = g["root"]; gNl,gNh,gDl,gDh,ge = a["vNl"].get(),a["vNh"].get(),a["vDl"].get(),a["vDh"].get(),a["esc"].get()
    rn=(int(gNh[r])<<64)|int(gNl[r]); rd=(int(gDh[r])<<64)|int(gDl[r])
    nc=sum(1 for i in range(L,N) if ge[i]==0 and ((int(gNh[i])<<64)|int(gNl[i])) and
           gcd((int(gNh[i])<<64)|int(gNl[i]),(int(gDh[i])<<64)|int(gDl[i]))!=1)
    return dict(rn=rn, rd=rd, esc_root=int(ge[r]), noncanon=nc)


def build_mul_tree(vals):
    vN=list(vals); vD=[1]*len(vals); lch=[-1]*len(vals); rch=[-1]*len(vals); op=[-1]*len(vals)
    fv=[Fraction(v,1) for v in vals]; level=list(range(len(vals)))
    while len(level)>1:
        nxt=[]
        for i in range(0,len(level)-1,2):
            li,ri=level[i],level[i+1]; idx=len(vN); vN.append(0);vD.append(0);lch.append(li);rch.append(ri);op.append(1)
            fv.append(fv[li]*fv[ri]); nxt.append(idx)
        if len(level)%2: nxt.append(level[-1])
        level=nxt
    return dict(vN=vN,vD=vD,lch=lch,rch=rch,op=op,L=len(vals),N=len(vN),root=level[0],truth=fv[level[0]])


if __name__ == "__main__":
    g = build_dag(128, 3); truth = g["truth"]
    e = run_engine(g, 64, 1, "coop"); l = run_engine(g, 64, 0, "coop")
    w1 = Fraction(e["rn"],e["rd"])==truth and e["esc_root"]==0 and e["noncanon"]==0 and \
         Fraction(l["rn"],l["rd"])==truth and l["noncanon"]>0
    g2 = build_dag(256, 3); t2 = g2["truth"]; tb = max(abs(t2.numerator),t2.denominator).bit_length()
    e64=run_engine(g2,64,1,"coop"); e128=run_engine(g2,128,1,"coop")
    primes=[1000000007,1000000009,1000000021,1000000033,1000000087,1000000093,1000000097,1000000103]
    ov=run_engine(build_mul_tree(primes),128,1,"coop")
    w2 = tb>64 and e64["esc_root"]==1 and e128["esc_root"]==0 and Fraction(e128["rn"],e128["rd"])==t2 and ov["esc_root"]==1
    # C2: strat reproduces, and coop == strat on the same DAG (schedule orthogonal to combine)
    s128 = run_engine(g2,128,1,"strat")
    w3 = Fraction(s128["rn"],s128["rd"])==t2 and s128["esc_root"]==0
    sc = run_engine(g,64,1,"strat")
    w4 = (sc["rn"],sc["rd"])==(e["rn"],e["rd"]) and (s128["rn"],s128["rd"])==(e128["rn"],e128["rd"])
    w5 = _SRC.count("u128 nl=ld(vNl") == 1                  # the combine body is written ONCE
    print("C1+C2 -- one combine (carrier typedef) + scheduling as a strategy over it (coop / strat)\n")
    print(f"1. COOP u64 eager==truth canonical; lazy==truth non-canon={l['noncanon']}: {w1}")
    print(f"2. CARRIER WIDENS ({tb}b: c64 esc={e64['esc_root']}, c128 exact) + u128 overflow esc={ov['esc_root']}: {w2}")
    print(f"3. STRAT reproduces the fold (u128 DAG exact={Fraction(s128['rn'],s128['rd'])==t2}): {w3}")
    print(f"4. SAME COMBINE (coop == strat on same DAG, both carriers): {w4}")
    print(f"5. ONE SOURCE (combine body written ONCE, called by both schedulers; all kernels one _SRC): {w5}")
    ok = w1 and w2 and w3 and w4 and w5
    print(f"\n  {'PASS' if ok else 'FAIL'} — C2: scheduling is a STRATEGY over the C1 combine. combine_window is")
    print(f"  one device function; coop + strat call it (no copied combine). coop==strat proves the schedule")
    print(f"  is orthogonal to the combine. Collapses dag/dag_mode (coop) + strat (strat). (C4 = jea_cost's structural")
    print(f"  oracle, C5 = jea_regression_gate, both built; carrier ops are the graded carrier (jea_carrier). LEGACY dep.)")
